"""就業規則エンジンテスト - Red Phase実装"""

import pytest
from datetime import date, time
from src.attendance_tool.calculation.work_rules_engine import WorkRulesEngine


class TestWorkRulesEngine:
    """就業規則エンジンテスト"""
    
    def setup_method(self):
        """各テストメソッド前の準備"""
        # テスト用就業規則設定
        self.work_rules = {
            "working_hours": {
                "standard_daily_minutes": 480,
                "standard_start_time": "09:00",
                "standard_end_time": "18:00"
            },
            "holidays": {
                "national_holidays": ["2024-01-01", "2024-01-08"]
            },
            "overtime": {
                "rates": {
                    "weekday_overtime": 1.25,
                    "legal_overtime": 1.25,
                    "late_night": 1.25,
                    "holiday_work": 1.35
                }
            }
        }
        self.engine = WorkRulesEngine(self.work_rules)
    
    def test_get_standard_work_minutes(self):
        """所定労働時間取得テスト"""
        # When: 所定労働時間取得
        minutes = self.engine.get_standard_work_minutes()
        
        # Then: 480分(8時間)が返される
        assert minutes == 480
    
    def test_get_standard_times(self):
        """標準勤務時間取得テスト"""
        # When: 標準勤務時間取得
        start_time = self.engine.get_standard_start_time()
        end_time = self.engine.get_standard_end_time()
        
        # Then: 設定された時間が返される
        assert start_time == time(9, 0)
        assert end_time == time(18, 0)
    
    def test_is_holiday(self):
        """祝日判定テスト"""
        # When: 祝日判定実行
        is_holiday = self.engine.is_holiday(date(2024, 1, 1))
        is_not_holiday = self.engine.is_holiday(date(2024, 1, 15))
        
        # Then: 正しい判定結果が返される
        assert is_holiday is True  # 2024-01-01は設定された祝日
        assert is_not_holiday is False
    
    def test_calculate_overtime_premium(self):
        """残業割増計算テスト"""
        # When: 残業割増計算実行
        premium = self.engine.calculate_overtime_premium(
            120, date(2024, 1, 15), time(9, 0), time(20, 0)
        )
        
        # Then: 割増金額が返される
        assert premium >= 0