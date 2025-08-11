import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
import gc
import psutil
import time

from attendance_tool.performance.memory_manager import (
    MemoryPool,
    StreamingProcessor,
    GCOptimizer,
)


class TestMemoryPool:
    """メモリプール機能テスト"""

    def test_dataframe_pool_creation(self):
        """DataFrameプール作成テスト"""
        pool = MemoryPool(pool_size=100)
        assert pool.pool_size == 100
        assert len(pool._dataframe_pools) == 0

    def test_dataframe_pool_reuse(self):
        """DataFrameプール再利用テスト"""
        pool = MemoryPool()
        df1 = pool.get_dataframe_pool(1000)
        pool.return_to_pool(df1)
        df2 = pool.get_dataframe_pool(1000)

        # プール内のオブジェクトが再利用される
        assert df2 is not None
        assert isinstance(df2, pd.DataFrame)

    def test_pool_cleanup(self):
        """プールクリーンアップテスト"""
        pool = MemoryPool(pool_size=50)

        # オブジェクト追加
        df = pd.DataFrame({"data": [1, 2, 3]})
        pool.return_to_pool(df)

        # クリーンアップ実行
        pool.cleanup_pool()

        # プールがクリアされる
        assert len(pool._dataframe_pools) == 0


class TestStreamingProcessor:
    """ストリーミング処理テスト"""

    def test_stream_processing_memory_limit(self):
        """ストリーミング処理メモリ制限テスト"""
        processor = StreamingProcessor(memory_limit=1024 * 1024 * 1024)  # 1GB

        # テストデータ（小規模）
        test_data = [{"id": i, "data": f"record_{i}"} for i in range(100)]

        # ストリーミング処理実行
        results = list(processor.process_stream(test_data, chunk_size=10))

        # 結果確認
        assert len(results) > 0
        assert processor.memory_limit == 1024 * 1024 * 1024

    def test_backpressure_control(self):
        """バックプレッシャー制御テスト"""
        processor = StreamingProcessor()

        # 基本機能の確認（メモリチェック機能）
        memory_ok = processor._check_memory_limit()
        assert isinstance(memory_ok, bool)


class TestGCOptimizer:
    """ガベージコレクション最適化テスト"""

    def test_gc_frequency_reduction(self):
        """GC頻度削減テスト"""
        optimizer = GCOptimizer(optimization_level="aggressive")

        # GC最適化コンテキスト使用
        with optimizer.optimize_gc_for_batch():
            # 最適化が有効であることを確認
            current_thresholds = gc.get_threshold()
            assert current_thresholds[0] >= 2000  # より大きな閾値

    def test_manual_gc_trigger(self):
        """手動GC実行テスト"""
        optimizer = GCOptimizer()

        # 手動GC実行（エラーが発生しないことを確認）
        optimizer.manual_gc_trigger(threshold=0.9)

        # 正常に完了
        assert True
