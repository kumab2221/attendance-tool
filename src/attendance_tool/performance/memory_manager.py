"""
メモリ最適化管理機能 - リファクタリング版
"""

import gc
import pandas as pd
import psutil
import threading
from contextlib import contextmanager
from typing import Any, Optional, Dict, List, Iterator, TypeVar, Generic
from datetime import datetime
from collections import defaultdict
from weakref import WeakSet

T = TypeVar("T")


class MemoryPool(Generic[T]):
    """オブジェクト再利用によるメモリ効率化（改良版）"""

    def __init__(self, pool_size: int = 1000, enable_monitoring: bool = True):
        """メモリプール初期化

        Args:
            pool_size: プールサイズ
            enable_monitoring: 監視機能有効化
        """
        self.pool_size = pool_size
        self.enable_monitoring = enable_monitoring

        # 改良: タイプ別プール管理
        self._dataframe_pools: Dict[str, List[pd.DataFrame]] = defaultdict(list)
        self._pool_usage: Dict[int, pd.DataFrame] = {}
        self._pool_stats = {"created": 0, "reused": 0, "returned": 0, "memory_saved": 0}

        # スレッドセーフ対応
        self._lock = threading.RLock()

        # メモリ監視
        if self.enable_monitoring:
            self._monitor_memory_usage()

    def get_dataframe_pool(
        self, size_hint: int, dtype_hint: Optional[str] = None
    ) -> pd.DataFrame:
        """DataFrameプール取得（改良版）

        Args:
            size_hint: データサイズヒント
            dtype_hint: データ型ヒント

        Returns:
            再利用可能なDataFrame
        """
        with self._lock:
            # 改良: サイズとデータ型に基づくプール選択
            pool_key = f"{self._size_category(size_hint)}_{dtype_hint or 'mixed'}"

            if self._dataframe_pools[pool_key]:
                df = self._dataframe_pools[pool_key].pop()
                self._pool_stats["reused"] += 1
                return df

            # 新規DataFrame作成
            df = self._create_optimized_dataframe(size_hint, dtype_hint)
            self._pool_stats["created"] += 1
            return df

    def return_to_pool(self, obj: Any, obj_type: Optional[str] = None) -> None:
        """オブジェクトプール返却（改良版）

        Args:
            obj: 返却するオブジェクト
            obj_type: オブジェクトタイプ
        """
        with self._lock:
            if isinstance(obj, pd.DataFrame):
                pool_key = self._get_pool_key(obj, obj_type)

                if len(self._dataframe_pools[pool_key]) < self.pool_size:
                    # 改良: データクリアの最適化
                    self._reset_dataframe_efficiently(obj)
                    self._dataframe_pools[pool_key].append(obj)
                    self._pool_stats["returned"] += 1

    def cleanup_pool(self) -> None:
        """プールクリーンアップ（改良版）"""
        with self._lock:
            memory_before = self._get_memory_usage()

            # 改良: 段階的クリーンアップ
            self._cleanup_unused_pools()
            self._compact_active_pools()

            self._dataframe_pools.clear()
            self._pool_usage.clear()

            # 改良: 効率的なGC実行
            gc.collect()

            memory_after = self._get_memory_usage()
            self._pool_stats["memory_saved"] += memory_before - memory_after

    def get_pool_statistics(self) -> Dict[str, Any]:
        """プール統計情報取得（新機能）"""
        with self._lock:
            return {
                **self._pool_stats,
                "active_pools": len(self._dataframe_pools),
                "total_objects": sum(
                    len(pool) for pool in self._dataframe_pools.values()
                ),
                "memory_usage_mb": self._get_memory_usage() / 1024 / 1024,
                "efficiency_ratio": self._pool_stats["reused"]
                / max(self._pool_stats["created"], 1),
            }

    def _size_category(self, size_hint: int) -> str:
        """サイズカテゴリ分類"""
        if size_hint < 1000:
            return "small"
        elif size_hint < 10000:
            return "medium"
        else:
            return "large"

    def _create_optimized_dataframe(
        self, size_hint: int, dtype_hint: Optional[str]
    ) -> pd.DataFrame:
        """最適化DataFrame作成"""
        if dtype_hint == "numeric":
            # 数値データ用最適化
            return pd.DataFrame(index=pd.RangeIndex(0, 0), dtype="float64")
        elif dtype_hint == "string":
            # 文字列データ用最適化
            return pd.DataFrame(index=pd.RangeIndex(0, 0), dtype="object")
        else:
            # 汎用
            return pd.DataFrame()

    def _cleanup_unused_pools(self) -> None:
        """未使用プールクリーンアップ"""
        # 改良: 使用頻度の低いプールを削除
        empty_pools = [key for key, pool in self._dataframe_pools.items() if not pool]
        for key in empty_pools:
            del self._dataframe_pools[key]

    def _compact_active_pools(self) -> None:
        """アクティブプール最適化"""
        # 改良: プールサイズの動的調整
        for pool in self._dataframe_pools.values():
            if len(pool) > self.pool_size:
                # 超過分を削除
                excess = len(pool) - self.pool_size
                del pool[:excess]

    def _monitor_memory_usage(self) -> None:
        """メモリ使用量監視"""
        if self.enable_monitoring:
            self._initial_memory = self._get_memory_usage()

    def _get_memory_usage(self) -> int:
        """現在のメモリ使用量取得"""
        return psutil.Process().memory_info().rss

    def _get_pool_key(self, df: pd.DataFrame, obj_type: Optional[str]) -> str:
        """プールキー生成"""
        size_cat = self._size_category(len(df))
        dtype_info = (
            "numeric" if df.select_dtypes(include=["number"]).shape[1] > 0 else "mixed"
        )
        return f"{size_cat}_{dtype_info}"

    def _reset_dataframe_efficiently(self, df: pd.DataFrame) -> None:
        """効率的DataFrame リセット"""
        # インデックスとカラムの高速リセット
        df.drop(df.index, inplace=True)
        if len(df.columns) > 10:  # 大量カラムの場合のみ再構築
            df.drop(df.columns, axis=1, inplace=True)


class StreamingProcessor:
    """大容量データのストリーミング処理"""

    def __init__(self, memory_limit: Optional[int] = None):
        """ストリーミング処理初期化

        Args:
            memory_limit: メモリ制限（バイト）
        """
        self.memory_limit = memory_limit or (1024 * 1024 * 1024)  # 1GB default

    def process_stream(
        self, data_source: Iterator[Any], chunk_size: int = 1000
    ) -> Iterator[Any]:
        """レコードストリーム処理

        Args:
            data_source: データソース
            chunk_size: チャンクサイズ

        Yields:
            処理済みデータ
        """
        chunk = []
        for record in data_source:
            chunk.append(record)

            if len(chunk) >= chunk_size:
                # メモリチェック
                if self._check_memory_limit():
                    yield self._process_chunk(chunk)
                    chunk = []

        # 残りのデータ処理
        if chunk:
            yield self._process_chunk(chunk)

    def aggregate_stream(self, summaries: Iterator[Any]) -> Any:
        """集計結果ストリーム統合

        Args:
            summaries: サマリーストリーム

        Returns:
            統合結果
        """
        # 最小実装：単純な統合
        results = list(summaries)
        return {"total_summaries": len(results), "summaries": results}

    def _check_memory_limit(self) -> bool:
        """メモリ制限チェック"""
        current_memory = psutil.Process().memory_info().rss
        return current_memory < self.memory_limit

    def _process_chunk(self, chunk: List[Any]) -> Any:
        """チャンク処理（プレースホルダー）"""
        return {"processed_count": len(chunk), "data": chunk}


class GCOptimizer:
    """ガベージコレクション制御"""

    def __init__(self, optimization_level: str = "balanced"):
        """GC最適化レベル設定

        Args:
            optimization_level: 最適化レベル（basic/balanced/aggressive）
        """
        self.optimization_level = optimization_level
        self._original_thresholds = gc.get_threshold()
        self._gc_disabled = False

    @contextmanager
    def optimize_gc_for_batch(self):
        """バッチ処理用GC最適化コンテキスト"""
        # GC最適化設定
        if self.optimization_level == "aggressive":
            gc.set_threshold(10000, 10, 10)  # より少ないGC頻度
        elif self.optimization_level == "balanced":
            gc.set_threshold(2000, 10, 10)  # バランス型

        try:
            yield
        finally:
            # 元の設定に復元
            gc.set_threshold(*self._original_thresholds)
            gc.collect()  # 明示的GC実行

    def manual_gc_trigger(self, threshold: float = 0.8) -> None:
        """手動GC実行

        Args:
            threshold: 実行閾値（メモリ使用率）
        """
        memory_info = psutil.virtual_memory()
        current_usage = memory_info.percent / 100.0

        if current_usage >= threshold:
            gc.collect()
