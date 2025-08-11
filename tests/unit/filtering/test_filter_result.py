"""
フィルタリング結果モデル単体テスト - Red Phase実装
"""

import pytest
import pandas as pd
from datetime import date

# テスト対象のインポート（Red Phase実装時点では失敗する）
try:
    from src.attendance_tool.filtering.models import FilterResult
except ImportError as e:
    pytest.skip(f"フィルタ結果モデル未実装: {e}", allow_module_level=True)


class TestFilterResult:
    """フィルタリング結果モデルテスト"""

    def test_filter_result_creation(self):
        """フィルタリング結果作成テスト"""
        test_df = pd.DataFrame(
            [
                {"work_date": "2024-01-15", "employee_id": "EMP001"},
                {"work_date": "2024-01-20", "employee_id": "EMP002"},
            ]
        )

        result = FilterResult(
            filtered_data=test_df,
            original_count=5,
            filtered_count=2,
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            processing_time=0.123,
            earliest_date=date(2024, 1, 15),
            latest_date=date(2024, 1, 20),
            excluded_records=3,
        )

        assert result.original_count == 5
        assert result.filtered_count == 2
        assert result.excluded_records == 3
        assert result.processing_time == 0.123
        assert len(result.filtered_data) == 2

    def test_get_summary(self):
        """サマリー情報取得テスト"""
        test_df = pd.DataFrame([{"work_date": "2024-01-15", "employee_id": "EMP001"}])

        result = FilterResult(
            filtered_data=test_df,
            original_count=10,
            filtered_count=1,
            date_range=(date(2024, 1, 1), date(2024, 1, 31)),
            processing_time=0.05,
            earliest_date=date(2024, 1, 15),
            latest_date=date(2024, 1, 15),
            excluded_records=9,
        )

        summary = result.get_summary()

        assert summary["filtered_ratio"] == 0.1  # 1/10
        assert summary["processing_time"] == 0.05
        assert summary["date_span_days"] == 30  # 1月の日数
