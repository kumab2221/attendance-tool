"""就業規則エンジン - Red Phase実装"""

from typing import Dict, Any, List
from datetime import date, time

from ..validation.models import AttendanceRecord


class WorkRulesEngine:
    """就業規則適用エンジン
    
    Red Phase: 各種規則チェックメソッドのスタブ
    """
    
    def __init__(self, work_rules: Dict[str, Any]):
        """初期化
        
        Args:
            work_rules: work_rules.yamlから読み込んだ設定
        """
        self.work_rules = work_rules
    
    def get_standard_work_minutes(self) -> int:
        """所定労働時間（分）を取得 - Green Phase最小実装"""
        # work_rules.yamlから取得、なければデフォルト値
        return self.work_rules.get("working_hours", {}).get("standard_daily_minutes", 480)
    
    def get_standard_start_time(self) -> time:
        """標準開始時刻を取得 - Green Phase最小実装"""
        start_time_str = self.work_rules.get("working_hours", {}).get("standard_start_time", "09:00")
        hour, minute = map(int, start_time_str.split(':'))
        return time(hour, minute)
    
    def get_standard_end_time(self) -> time:
        """標準終了時刻を取得 - Green Phase最小実装"""
        end_time_str = self.work_rules.get("working_hours", {}).get("standard_end_time", "18:00")
        hour, minute = map(int, end_time_str.split(':'))
        return time(hour, minute)
    
    def is_holiday(self, work_date: date) -> bool:
        """祝日判定 - Green Phase最小実装"""
        # 固定の祝日リストから判定（最小実装）
        holidays_list = self.work_rules.get("holidays", {}).get("national_holidays", [])
        date_str = work_date.strftime("%Y-%m-%d")
        return date_str in holidays_list
    
    def calculate_overtime_premium(self, overtime_minutes: int, work_date: date, 
                                 start_time: time, end_time: time) -> int:
        """残業割増計算 - Green Phase最小実装"""
        # 最小実装：基本の割増率のみ適用
        rates = self.work_rules.get("overtime", {}).get("rates", {})
        weekday_rate = rates.get("weekday_overtime", 1.25)
        return int(overtime_minutes * weekday_rate)
    
    def check_violations(self, records: List[AttendanceRecord]) -> List[str]:
        """就業規則違反チェック - Green Phase最小実装"""
        # 最小実装：空のリストを返す
        return []
    
    def get_late_threshold_minutes(self) -> int:
        """遅刻閾値（分）を取得 - Refactor Phase追加"""
        return self.work_rules.get("tardiness", {}).get("late_threshold_minutes", 1)

    def get_early_leave_threshold_minutes(self) -> int:
        """早退閾値（分）を取得 - Refactor Phase追加"""
        return self.work_rules.get("tardiness", {}).get("early_leave_threshold_minutes", 1)

    def get_rounding_config(self) -> Dict[str, Any]:
        """時間丸め設定を取得 - Refactor Phase追加"""
        return self.work_rules.get("tardiness", {}).get("rounding", {
            "unit_minutes": 15,
            "method": "up"
        })

    def get_legal_work_minutes(self) -> int:
        """法定労働時間（分）を取得 - Refactor Phase追加"""
        return self.work_rules.get("working_hours", {}).get("legal_daily_minutes", 480)

    def get_monthly_overtime_limit(self) -> int:
        """月間残業時間上限（分）を取得 - Refactor Phase追加"""
        return self.work_rules.get("overtime", {}).get("limits", {}).get("monthly_overtime_limit", 2700)

    def get_max_consecutive_work_days(self) -> int:
        """連続勤務日数上限を取得 - Refactor Phase追加"""
        return self.work_rules.get("validation", {}).get("warnings", {}).get("consecutive_work_days", 6)