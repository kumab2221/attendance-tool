"""
パフォーマンス関連のデータモデル
"""

import time
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class PerformanceConfig:
    """パフォーマンス設定"""

    memory_limit: int = 1024 * 1024 * 1024  # 1GB
    chunk_size: int = 10000
    parallel_workers: int = 4
    enable_optimization: bool = True
    timeout_seconds: int = 300


@dataclass
class PerformanceMetrics:
    """パフォーマンス指標"""

    processing_time: float = 0.0
    memory_usage: float = 0.0
    records_processed: int = 0
    throughput: float = 0.0  # records/second
    cpu_usage: float = 0.0

    def calculate_throughput(self) -> float:
        """スループット計算"""
        if self.processing_time > 0:
            self.throughput = self.records_processed / self.processing_time
        return self.throughput


@dataclass
class PerformanceReport:
    """パフォーマンスレポート"""

    start_time: float
    end_time: float
    config: PerformanceConfig
    metrics: PerformanceMetrics
    success: bool = True
    error_message: Optional[str] = None
    additional_data: Dict[str, Any] = None

    def __post_init__(self):
        if self.additional_data is None:
            self.additional_data = {}

    @property
    def total_time(self) -> float:
        """総実行時間"""
        return self.end_time - self.start_time

    @property
    def efficiency_score(self) -> float:
        """効率スコア（0.0-1.0）"""
        if self.metrics.throughput <= 0:
            return 0.0
        # 簡易的な効率計算
        expected_throughput = 1000  # records/second
        return min(1.0, self.metrics.throughput / expected_throughput)

    def to_dict(self) -> Dict[str, Any]:
        """辞書形式で出力"""
        return {
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_time": self.total_time,
            "config": {
                "memory_limit": self.config.memory_limit,
                "chunk_size": self.config.chunk_size,
                "parallel_workers": self.config.parallel_workers,
                "enable_optimization": self.config.enable_optimization,
                "timeout_seconds": self.config.timeout_seconds,
            },
            "metrics": {
                "processing_time": self.metrics.processing_time,
                "memory_usage": self.metrics.memory_usage,
                "records_processed": self.metrics.records_processed,
                "throughput": self.metrics.throughput,
                "cpu_usage": self.metrics.cpu_usage,
            },
            "success": self.success,
            "error_message": self.error_message,
            "efficiency_score": self.efficiency_score,
            "additional_data": self.additional_data,
        }
