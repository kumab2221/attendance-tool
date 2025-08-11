"""勤怠集計計算機 - Red Phase実装"""
from __future__ import annotations

from typing import List, Optional, Dict, Any
from datetime import date

from ..validation.models import AttendanceRecord
from .summary import AttendanceSummary


class AttendanceCalculationError(Exception):
    """勤怠集計エラー"""
    pass


class AttendanceCalculator:
    """勤怠集計計算機
    
    Red Phase: メソッドシグネチャのみ定義、NotImplementedErrorを発生
    """
    
    def __init__(self, work_rules: Optional[Dict[str, Any]] = None):
        """初期化
        
        Args:
            work_rules: 就業規則設定（ConfigManagerから取得想定）
        """
        self.work_rules = work_rules or {}
        from .work_rules_engine import WorkRulesEngine
        self.rules_engine = WorkRulesEngine(self.work_rules)
    
    def calculate(self, records: List[AttendanceRecord], period: Optional[str] = None) -> AttendanceSummary:
        """勤怠集計メイン処理
        
        Args:
            records: 検証済み勤怠レコードリスト
            period: 集計期間（"2024-01"形式）
            
        Returns:
            AttendanceSummary: 集計結果
            
        Raises:
            AttendanceCalculationError: 集計処理エラー
        """
        # Green Phase: 最小実装
        if not records:
            # 空のレコードの場合
            return AttendanceSummary(
                employee_id="",
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                total_days=0,
                business_days=0
            )
        
        # 最初のレコードから基本情報を取得
        first_record = records[0]
        employee_id = first_record.employee_id
        
        # 期間の計算（Refactor Phase改善）
        period_start, period_end = self._determine_period(records, period)
        total_days = (period_end - period_start).days + 1
        business_days = self._calculate_business_days(period_start, period_end)
        
        # 出勤日数の計算
        attendance_days = self._calculate_attendance_days(records)
        
        # 欠勤日数の計算
        absence_days = self._calculate_absence_days(records)
        
        # 遅刻・早退の計算
        tardiness_early_leave = self._calculate_tardiness_and_early_leave(records)
        
        # 残業時間の計算
        overtime = self._calculate_overtime_minutes(records)
        
        # 出勤率の計算
        attendance_rate = (attendance_days / business_days * 100) if business_days > 0 else 0.0
        absence_rate = (absence_days / business_days * 100) if business_days > 0 else 0.0
        
        # 総勤務時間の計算
        total_work_minutes = sum(
            record.get_work_duration_minutes() or 0 
            for record in records
        )
        average_work_hours = (total_work_minutes / 60 / attendance_days) if attendance_days > 0 else 0.0
        
        return AttendanceSummary(
            employee_id=employee_id,
            period_start=period_start,
            period_end=period_end,
            total_days=total_days,
            business_days=business_days,
            attendance_days=attendance_days,
            attendance_rate=attendance_rate,
            absence_days=absence_days,
            absence_rate=absence_rate,
            average_work_hours=average_work_hours,
            total_work_minutes=total_work_minutes,
            tardiness_count=tardiness_early_leave["tardiness_count"],
            early_leave_count=tardiness_early_leave["early_leave_count"],
            tardiness_minutes=tardiness_early_leave["tardiness_minutes"],
            early_leave_minutes=tardiness_early_leave["early_leave_minutes"],
            scheduled_overtime_minutes=overtime["scheduled_overtime_minutes"],
            legal_overtime_minutes=overtime["legal_overtime_minutes"],
            late_night_work_minutes=overtime["late_night_work_minutes"],
            holiday_work_minutes=overtime["holiday_work_minutes"]
        )
    
    def calculate_batch(self, records_by_employee: Dict[str, List[AttendanceRecord]]) -> List[AttendanceSummary]:
        """複数社員の一括集計
        
        Args:
            records_by_employee: 社員別勤怠レコード辞書
            
        Returns:
            List[AttendanceSummary]: 社員別集計結果
        """
        # Red Phase: 実装なし
        raise NotImplementedError("calculate_batch method not implemented yet")
    
    def _calculate_attendance_days(self, records: List[AttendanceRecord]) -> int:
        """出勤日数計算 - Green Phase最小実装"""
        count = 0
        for record in records:
            # work_status="出勤" または 勤務時間が4時間以上の場合
            if record.work_status == "出勤":
                count += 1
            elif record.start_time is not None and record.end_time is not None:
                # 最小勤務時間チェック（4時間=240分）
                work_minutes = record.get_work_duration_minutes()
                if work_minutes is not None and work_minutes >= 240:  # 4時間
                    count += 1
        return count
    
    def _calculate_absence_days(self, records: List[AttendanceRecord]) -> int:
        """欠勤日数計算 - Green Phase最小実装"""
        count = 0
        for record in records:
            if record.work_status == "欠勤":
                count += 1
        return count
    
    def _calculate_overtime_minutes(self, records: List[AttendanceRecord]) -> Dict[str, int]:
        """残業時間計算 - Green Phase最小実装"""
        scheduled_overtime = 0
        
        for record in records:
            work_minutes = record.get_work_duration_minutes()
            if work_minutes and work_minutes > 480:  # 8時間=480分
                scheduled_overtime += (work_minutes - 480)
        
        return {
            "scheduled_overtime_minutes": scheduled_overtime,
            "legal_overtime_minutes": 0,  # 後で実装
            "late_night_work_minutes": 0,  # 後で実装
            "holiday_work_minutes": 0      # 後で実装
        }
    
    def _calculate_tardiness_and_early_leave(self, records: List[AttendanceRecord]) -> Dict[str, int]:
        """遅刻・早退計算 - Green Phase最小実装"""
        tardiness_count = 0
        early_leave_count = 0
        tardiness_minutes = 0
        early_leave_minutes = 0
        
        # 設定ファイルから標準時間を取得（Refactor Phase改善）
        standard_start = self.rules_engine.get_standard_start_time()
        standard_end = self.rules_engine.get_standard_end_time()
        late_threshold = self.rules_engine.get_late_threshold_minutes()
        early_threshold = self.rules_engine.get_early_leave_threshold_minutes()
        rounding_config = self.rules_engine.get_rounding_config()
        
        for record in records:
            # 遅刻チェック
            if record.start_time and record.start_time > standard_start:
                tardiness_count += 1
                # 遅刻時間計算（分単位）
                start_minutes = record.start_time.hour * 60 + record.start_time.minute
                standard_start_minutes = standard_start.hour * 60 + standard_start.minute
                late_minutes = start_minutes - standard_start_minutes
                # 15分単位切り上げ
                tardiness_minutes += ((late_minutes + 14) // 15) * 15
            
            # 早退チェック
            if record.end_time and record.end_time < standard_end:
                early_leave_count += 1
                # 早退時間計算（分単位）
                end_minutes = record.end_time.hour * 60 + record.end_time.minute
                standard_end_minutes = standard_end.hour * 60 + standard_end.minute
                early_minutes = standard_end_minutes - end_minutes
                # 15分単位切り上げ
                early_leave_minutes += ((early_minutes + 14) // 15) * 15
        
        return {
            "tardiness_count": tardiness_count,
            "early_leave_count": early_leave_count,
            "tardiness_minutes": tardiness_minutes,
            "early_leave_minutes": early_leave_minutes
        }
    
    def _determine_period(self, records: List[AttendanceRecord], period: Optional[str]) -> tuple[date, date]:
        """期間を決定する - Refactor Phase追加"""
        if period:
            return self._parse_period_parameter(period)
        elif records:
            dates = [record.work_date for record in records if record.work_date]
            if dates:
                return (min(dates), max(dates))
        
        # デフォルト：今月
        today = date.today()
        return (today.replace(day=1), today)
    
    def _parse_period_parameter(self, period: str) -> tuple[date, date]:
        """period文字列を日付範囲に変換"""
        try:
            from datetime import timedelta
            year, month = map(int, period.split('-'))
            start_date = date(year, month, 1)
            
            # 月末日を計算
            if month == 12:
                next_month_start = date(year + 1, 1, 1)
            else:
                next_month_start = date(year, month + 1, 1)
            
            end_date = next_month_start - timedelta(days=1)
            return (start_date, end_date)
        except (ValueError, IndexError):
            raise AttendanceCalculationError(f"無効な期間フォーマット: {period}")
    
    def _calculate_business_days(self, start_date: date, end_date: date) -> int:
        """期間内の営業日数を計算 - Refactor Phase追加"""
        from datetime import timedelta
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            # 土日チェック（月-金のみ）
            if current_date.weekday() < 5:
                # 祝日チェック
                if not self.rules_engine.is_holiday(current_date):
                    business_days += 1
            current_date += timedelta(days=1)
            
        return business_days
    
    def _apply_rounding(self, minutes: int, rounding_config: Dict[str, Any]) -> int:
        """時間の丸め処理 - Refactor Phase追加"""
        unit = rounding_config.get("unit_minutes", 15)
        method = rounding_config.get("method", "up")
        
        if method == "up":
            return ((minutes + unit - 1) // unit) * unit
        elif method == "down":
            return (minutes // unit) * unit
        else:  # round
            return round(minutes / unit) * unit
    
    # TASK-202 Red Phase: 違反チェック統合メソッド追加
    
    def calculate_with_violations(self, records: List[AttendanceRecord], period: Optional[str] = None) -> tuple[AttendanceSummary, List['WorkRuleViolation']]:
        """集計結果と違反情報を同時生成 - Green Phase最小実装"""
        # 通常の集計を実行
        summary = self.calculate(records, period)
        
        # 違反チェックを実行
        violations = self.rules_engine.check_all_violations(records)
        
        # 違反情報をサマリーに統合
        updated_summary = self._integrate_violation_warnings(summary, violations)
        
        return updated_summary, violations

    def _integrate_violation_warnings(self, summary: AttendanceSummary, violations: List['WorkRuleViolation']) -> AttendanceSummary:
        """違反情報をサマリーに統合 - Green Phase最小実装"""
        from .violations import ViolationLevel
        
        # 既存のwarningsとviolationsに追加
        if summary.warnings is None:
            summary.warnings = []
        if summary.violations is None:
            summary.violations = []
        
        # 違反レベル別に分類
        for violation in violations:
            message = f"{violation.violation_type}: {violation.message}"
            if violation.level in [ViolationLevel.WARNING, ViolationLevel.INFO]:
                summary.warnings.append(message)
            elif violation.level in [ViolationLevel.VIOLATION, ViolationLevel.CRITICAL]:
                summary.violations.append(message)
        
        return summary