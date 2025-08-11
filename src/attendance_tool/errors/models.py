"""
エラーハンドリング用データモデル (改善版)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class ErrorContext:
    """エラー発生時のコンテキスト情報"""

    operation: str = "unknown"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorClassification:
    """エラー分類結果 (改善版)"""

    category: str
    code: str
    severity: str
    original_exception: Exception
    context: Optional[ErrorContext] = None
    retry_enabled: bool = False

    @property
    def is_critical(self) -> bool:
        """クリティカルエラーかどうか"""
        return self.severity == "CRITICAL"

    @property
    def can_continue(self) -> bool:
        """処理継続可能かどうか"""
        return self.severity in ["WARNING", "INFO"]


@dataclass
class RecoveryResult:
    """リカバリー結果 (改善版)"""

    success: bool = False
    gc_executed: bool = False
    memory_freed: int = 0
    attempts: int = 0
    final_exception: Optional[Exception] = None
    recovery_time: float = 0.0

    # 既存テスト互換性のためのプロパティ
    @property
    def recovery_success(self) -> Optional[bool]:
        return self.success


@dataclass
class ProcessingResult:
    """処理結果（エラー継続処理用） (改善版)"""

    successful_results: List[Any] = field(default_factory=list)
    error_records: List["ErrorRecord"] = field(default_factory=list)
    total_processed: int = 0
    success_rate: float = 0.0

    def __post_init__(self):
        """後処理でメトリクス計算"""
        if self.total_processed == 0:
            self.total_processed = len(self.successful_results) + len(
                self.error_records
            )

        if self.total_processed > 0:
            self.success_rate = len(self.successful_results) / self.total_processed


@dataclass
class ErrorRecord:
    """エラーレコード (改善版)"""

    record_id: str
    error: Exception
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[ErrorContext] = None
    recovery_attempted: bool = False
    recovery_success: bool = False
