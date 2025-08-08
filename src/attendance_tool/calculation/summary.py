"""勤怠集計結果モデル - Red Phase実装"""

from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class AttendanceSummary:
    """勤怠集計結果
    
    Red Phase: 必要なフィールドのみ定義、計算ロジックは未実装
    """
    
    # 基本情報
    employee_id: str
    period_start: date
    period_end: date
    total_days: int
    business_days: int
    employee_name: str = "Unknown User"  # Green Phase: テストのために追加
    department: str = "未設定"           # Green Phase: テストのために追加
    
    # 出勤関連
    attendance_days: int = 0
    attendance_rate: float = 0.0
    average_work_hours: float = 0.0
    total_work_minutes: int = 0
    
    # 欠勤関連
    absence_days: int = 0
    absence_rate: float = 0.0
    
    # 遅刻・早退
    tardiness_count: int = 0
    early_leave_count: int = 0
    tardiness_minutes: int = 0
    early_leave_minutes: int = 0
    
    # 残業時間
    scheduled_overtime_minutes: int = 0     # 所定残業
    legal_overtime_minutes: int = 0         # 法定残業
    late_night_work_minutes: int = 0        # 深夜労働
    holiday_work_minutes: int = 0           # 休日労働
    
    # 割増残業時間（支給対象）
    overtime_pay_minutes: int = 0
    late_night_pay_minutes: int = 0
    holiday_pay_minutes: int = 0
    
    # 休暇
    paid_leave_days: int = 0
    paid_leave_hours: float = 0.0
    remaining_paid_leave: int = 0
    special_leave_days: int = 0
    
    # 警告・注意事項
    warnings: List[str] = None
    violations: List[str] = None
    
    def __post_init__(self):
        """初期化後処理"""
        if self.warnings is None:
            self.warnings = []
        if self.violations is None:
            self.violations = []