"""
期間仕様モデル単体テスト - Red Phase実装
"""

import pytest
from datetime import date, datetime

# テスト対象のインポート（Red Phase実装時点では失敗する）
try:
    from src.attendance_tool.filtering.models import (
        PeriodSpecification,
        PeriodType,
        InvalidPeriodError,
    )
except ImportError as e:
    pytest.skip(f"期間仕様モデル未実装: {e}", allow_module_level=True)


class TestPeriodSpecification:
    """期間仕様モデルテスト"""

    def test_month_period_specification(self):
        """月単位期間仕様テスト"""
        spec = PeriodSpecification(period_type=PeriodType.MONTH, month_string="2024-01")

        assert spec.period_type == PeriodType.MONTH
        assert spec.month_string == "2024-01"

        # 日付範囲変換テスト
        start_date, end_date = spec.to_date_range()
        assert start_date == date(2024, 1, 1)
        assert end_date == date(2024, 1, 31)

    def test_date_range_period_specification(self):
        """日付範囲期間仕様テスト"""
        spec = PeriodSpecification(
            period_type=PeriodType.DATE_RANGE,
            start_date=date(2024, 1, 15),
            end_date=date(2024, 1, 25),
        )

        assert spec.period_type == PeriodType.DATE_RANGE
        assert spec.start_date == date(2024, 1, 15)
        assert spec.end_date == date(2024, 1, 25)

        # 日付範囲変換テスト
        start_date, end_date = spec.to_date_range()
        assert start_date == date(2024, 1, 15)
        assert end_date == date(2024, 1, 25)

    def test_relative_period_specification(self):
        """相対期間仕様テスト"""
        spec = PeriodSpecification(
            period_type=PeriodType.RELATIVE, relative_string="last_month"
        )

        assert spec.period_type == PeriodType.RELATIVE
        assert spec.relative_string == "last_month"

    def test_validation(self):
        """期間仕様バリデーションテスト"""
        # 有効な仕様
        valid_spec = PeriodSpecification(
            period_type=PeriodType.MONTH, month_string="2024-01"
        )
        assert valid_spec.validate() == True

        # 無効な仕様 - 月指定なのにmonth_stringがない
        invalid_spec = PeriodSpecification(period_type=PeriodType.MONTH)
        assert invalid_spec.validate() == False
