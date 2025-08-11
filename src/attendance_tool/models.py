"""
共通データモデル
"""

from dataclasses import dataclass
from datetime import date, datetime, time
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class AttendanceRecord:
    """勤怠レコード"""

    employee_id: str
    employee_name: str
    department: str
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    break_minutes: int = 0
    notes: Optional[str] = None

    @property
    def work_minutes(self) -> int:
        """勤務時間（分）"""
        if self.start_time and self.end_time:
            total_minutes = int((self.end_time - self.start_time).total_seconds() / 60)
            return max(0, total_minutes - self.break_minutes)
        return 0

    @property
    def work_hours(self) -> float:
        """勤務時間（時間）"""
        return self.work_minutes / 60.0


@dataclass
class AttendanceSummary:
    """勤怠サマリー"""

    employee_id: str
    employee_name: str
    department: str
    period_start: date
    period_end: date
    total_work_days: int = 0
    total_work_hours: float = 0.0
    total_overtime_hours: float = 0.0
    total_late_count: int = 0
    total_early_leave_count: int = 0
    total_absent_days: int = 0
    total_paid_leave_days: int = 0

    @property
    def average_daily_hours(self) -> float:
        """平均日次勤務時間"""
        if self.total_work_days > 0:
            return self.total_work_hours / self.total_work_days
        return 0.0

    @property
    def attendance_rate(self) -> float:
        """出勤率"""
        total_days = (self.period_end - self.period_start).days + 1
        if total_days > 0:
            return self.total_work_days / total_days
        return 0.0


@dataclass
class DepartmentSummary:
    """部門サマリー"""

    department: str
    period_start: date
    period_end: date
    employee_count: int = 0
    total_work_hours: float = 0.0
    total_overtime_hours: float = 0.0
    average_attendance_rate: float = 0.0
    employee_summaries: List[AttendanceSummary] = None

    def __post_init__(self):
        if self.employee_summaries is None:
            self.employee_summaries = []

    @property
    def average_hours_per_employee(self) -> float:
        """従業員平均勤務時間"""
        if self.employee_count > 0:
            return self.total_work_hours / self.employee_count
        return 0.0


@dataclass
class ValidationResult:
    """バリデーション結果"""

    is_valid: bool
    errors: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

    def add_error(self, message: str):
        """エラー追加"""
        self.errors.append(message)
        self.is_valid = False

    def add_warning(self, message: str):
        """警告追加"""
        self.warnings.append(message)


@dataclass
class ProcessingResult:
    """処理結果"""

    success: bool
    records_processed: int = 0
    records_failed: int = 0
    processing_time: float = 0.0
    error_message: Optional[str] = None
    warnings: List[str] = None
    output_files: List[str] = None

    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []
        if self.output_files is None:
            self.output_files = []

    @property
    def total_records(self) -> int:
        """総レコード数"""
        return self.records_processed + self.records_failed

    @property
    def success_rate(self) -> float:
        """成功率"""
        if self.total_records > 0:
            return self.records_processed / self.total_records
        return 0.0
