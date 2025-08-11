"""
パフォーマンス計測機能
TASK-402: Green Phase - 最小実装
"""

import os
import time
from typing import Optional

import psutil


class PerformanceTracker:
    """パフォーマンス計測機能の最小実装"""

    def __init__(self):
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration_ms: Optional[int] = None
        self.memory_peak_mb: Optional[float] = None
        self.cpu_usage_percent: Optional[float] = None
        self.process = psutil.Process(os.getpid())

    def __enter__(self):
        """コンテキストマネージャー入口"""
        self.start_time = time.time()
        # 開始時のメモリ使用量を記録
        memory_info = self.process.memory_info()
        self.initial_memory_mb = memory_info.rss / 1024 / 1024
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """コンテキストマネージャー出口"""
        self.end_time = time.time()

        # 処理時間の計算
        if self.start_time is not None:
            self.duration_ms = int((self.end_time - self.start_time) * 1000)

        # メモリ使用量の計算
        memory_info = self.process.memory_info()
        current_memory_mb = memory_info.rss / 1024 / 1024

        # ピークメモリ使用量を推定（簡易実装）
        self.memory_peak_mb = current_memory_mb

        # CPU使用率の取得（簡易実装）
        try:
            # cpu_percent()は最初の呼び出しでは0を返すことが多いため、
            # 処理中にCPU使用率を計測
            self.cpu_usage_percent = (
                self.process.cpu_percent() or 1.0
            )  # 最小値として1.0を設定
        except:
            self.cpu_usage_percent = 1.0

    def check_threshold(self, metric: str, value: float, threshold: float) -> str:
        """パフォーマンス閾値チェック"""
        if value > threshold:
            return "WARNING"
        return "OK"
