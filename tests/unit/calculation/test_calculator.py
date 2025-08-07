"""勤怠集計計算機テスト - Red Phase実装

このテストは失敗することを確認するためのもの
"""

import pytest
from datetime import date, time
from src.attendance_tool.calculation.calculator import AttendanceCalculator, AttendanceCalculationError
from src.attendance_tool.calculation.summary import AttendanceSummary
from src.attendance_tool.validation.models import AttendanceRecord


class TestAttendanceCalculatorBasic:
    """基本集計機能テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.calculator = AttendanceCalculator()
    
    def test_calculate_attendance_days_normal(self):
        """通常の出勤日数集計テスト - 現在は失敗する"""
        # Given: 20日間の勤怠データ（18日出勤、2日欠勤）
        records = self._create_test_records()
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_attendance_by_minimum_work_time(self):
        """最小勤務時間(4時間)による出勤判定テスト - 現在は失敗する"""
        # Given: work_statusが空だが4時間以上勤務
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(13, 30),
                break_minutes=30
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_calculate_absence_days_and_rate(self):
        """欠勤日数・欠勤率集計テスト - 現在は失敗する"""
        # Given: 欠勤データを含む勤怠レコード
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                work_status="欠勤"
            ),
            self._create_attendance_record(
                work_date=date(2024, 1, 2),
                work_status="出勤",
                start_time=time(9, 0),
                end_time=time(18, 0)
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_calculate_tardiness(self):
        """遅刻回数・時間集計テスト - 現在は失敗する"""
        # Given: 遅刻データを含むレコード
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                start_time=time(9, 5),  # 5分遅刻
                end_time=time(18, 0)
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_calculate_overtime(self):
        """残業時間計算テスト - 現在は失敗する"""
        # Given: 10時間勤務（2時間残業）
        records = [
            self._create_attendance_record(
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(20, 0),  # 11時間後（休憩1時間込み）
                break_minutes=60
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def _create_test_records(self) -> list[AttendanceRecord]:
        """テスト用レコード作成"""
        records = []
        
        # 18日出勤データ
        for day in range(1, 19):
            record = self._create_attendance_record(
                work_date=date(2024, 1, day),
                work_status="出勤",
                start_time=time(9, 0),
                end_time=time(18, 0),
                break_minutes=60
            )
            records.append(record)
        
        # 2日欠勤データ
        for day in range(19, 21):
            record = self._create_attendance_record(
                work_date=date(2024, 1, day),
                work_status="欠勤"
            )
            records.append(record)
        
        return records
    
    def _create_attendance_record(self, work_date: date, work_status: str = None,
                                start_time: time = None, end_time: time = None,
                                break_minutes: int = None) -> AttendanceRecord:
        """テスト用AttendanceRecord作成"""
        return AttendanceRecord(
            employee_id="EMP001",
            employee_name="テスト太郎",
            work_date=work_date,
            work_status=work_status,
            start_time=start_time,
            end_time=end_time,
            break_minutes=break_minutes
        )


class TestAttendanceCalculatorEdgeCases:
    """境界値テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.calculator = AttendanceCalculator()
    
    def test_zero_work_time(self):
        """0分勤務処理テスト - 現在は失敗する"""
        # Given: 同一時刻の出退勤
        records = [
            AttendanceRecord(
                employee_id="EMP001",
                employee_name="テスト太郎",
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(9, 0)
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)
    
    def test_24_hour_work(self):
        """24時間勤務処理テスト - 現在は失敗する"""
        # Given: 24時間連続勤務（日跨ぎ）
        records = [
            AttendanceRecord(
                employee_id="EMP001",
                employee_name="テスト太郎",
                work_date=date(2024, 1, 1),
                start_time=time(9, 0),
                end_time=time(9, 0),  # 翌日同時刻
                break_minutes=60
            )
        ]
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summary = self.calculator.calculate(records)


class TestAttendanceCalculatorBatch:
    """バッチ処理テスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        self.calculator = AttendanceCalculator()
    
    def test_calculate_batch_multiple_employees(self):
        """複数社員一括処理テスト - 現在は失敗する"""
        # Given: 複数社員のデータ
        records_by_employee = {
            "EMP001": [
                AttendanceRecord(
                    employee_id="EMP001",
                    employee_name="社員１",
                    work_date=date(2024, 1, 1),
                    start_time=time(9, 0),
                    end_time=time(18, 0)
                )
            ],
            "EMP002": [
                AttendanceRecord(
                    employee_id="EMP002",
                    employee_name="社員２",
                    work_date=date(2024, 1, 1),
                    start_time=time(9, 0),
                    end_time=time(17, 0)
                )
            ]
        }
        
        # When & Then: NotImplementedErrorで失敗する
        with pytest.raises(NotImplementedError):
            summaries = self.calculator.calculate_batch(records_by_employee)