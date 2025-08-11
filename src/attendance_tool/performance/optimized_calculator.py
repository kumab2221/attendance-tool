"""
パフォーマンス最適化勤怠計算機
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

from attendance_tool.performance.chunk_processor import AdaptiveChunking
from attendance_tool.performance.memory_manager import GCOptimizer, MemoryPool
from attendance_tool.performance.parallel_processor import ParallelBatchProcessor


class PerformanceOptimizedCalculator:
    """性能最適化勤怠計算機"""

    def __init__(self, config: Optional[Any] = None):
        """最適化設定付き初期化

        Args:
            config: パフォーマンス設定
        """
        self.config = config or self._default_config()
        self.memory_pool = MemoryPool()
        self.gc_optimizer = GCOptimizer()
        self.parallel_processor = ParallelBatchProcessor()
        self.chunk_processor = AdaptiveChunking()

        self._memory_limit_gb = 1.0  # デフォルト1GB制限

    def calculate_batch_optimized(
        self, records_by_employee: Dict[str, List[Any]], parallel: bool = True
    ) -> List[Any]:
        """最適化バッチ計算

        Args:
            records_by_employee: 社員別レコード
            parallel: 並列処理フラグ

        Returns:
            計算結果リスト
        """
        with self.gc_optimizer.optimize_gc_for_batch():
            if parallel and len(records_by_employee) > 5:  # 5名以上で並列処理
                return self._parallel_batch_calculate(records_by_employee)
            else:
                return self._sequential_batch_calculate(records_by_employee)

    def calculate_with_chunking(self, large_dataset: pd.DataFrame) -> List[Any]:
        """チャンク処理計算

        Args:
            large_dataset: 大容量データセット

        Returns:
            計算結果リスト
        """
        results = []

        for chunk_result in self.chunk_processor.process_with_adaptive_chunking(
            large_dataset
        ):
            results.append(chunk_result)

            # メモリクリーンアップ
            if len(results) % 10 == 0:  # 10チャンクごとにクリーンアップ
                self.memory_pool.cleanup_pool()

        return results

    def set_memory_limit(self, limit_gb: float) -> None:
        """メモリ制限設定

        Args:
            limit_gb: メモリ制限（GB）
        """
        self._memory_limit_gb = limit_gb
        self.chunk_processor.memory_limit = int(limit_gb * 1024 * 1024 * 1024)

    def cleanup(self) -> None:
        """リソースクリーンアップ"""
        self.memory_pool.cleanup_pool()
        self.gc_optimizer.manual_gc_trigger()

    def _parallel_batch_calculate(
        self, records_by_employee: Dict[str, List[Any]]
    ) -> List[Any]:
        """並列バッチ計算"""
        return self.parallel_processor.process_employee_batches(records_by_employee)

    def _sequential_batch_calculate(
        self, records_by_employee: Dict[str, List[Any]]
    ) -> List[Any]:
        """順次バッチ計算"""
        results = []
        for employee_id, records in records_by_employee.items():
            result = {
                "employee_id": employee_id,
                "record_count": len(records),
                "processing_mode": "sequential",
            }
            results.append(result)
        return results

    def _default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "memory_limit_gb": 1.0,
            "parallel_threshold": 5,
            "chunk_size": 10000,
            "gc_optimization": True,
        }
