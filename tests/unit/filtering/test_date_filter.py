"""
TASK-103: 期間フィルタリング機能テスト - Red Phase実装
境界値テスト・エッジケーステストを重点的に実装

実行方法:
    pytest tests/unit/filtering/test_date_filter.py -v
"""

import pytest
import pandas as pd
from datetime import date, datetime, timedelta
from freezegun import freeze_time
import time
import psutil
import os
from typing import List, Dict, Any

# テスト対象のインポート（Red Phase実装時点では失敗する）
try:
    from src.attendance_tool.filtering.date_filter import DateFilter
    from src.attendance_tool.filtering.models import (
        PeriodSpecification, 
        PeriodType,
        FilterResult,
        DateFilterConfig,
        DateFilterError,
        InvalidPeriodError, 
        DateRangeError
    )
    from src.attendance_tool.filtering.integrated_filter import IntegratedDateFilter
except ImportError as e:
    pytest.skip(f"期間フィルタリングモジュール未実装: {e}", allow_module_level=True)


class TestFilterByMonth:
    """月単位フィルタリング単体テスト"""
    
    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.filter = DateFilter()
        
    def create_test_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """テスト用DataFrame作成ヘルパー"""
        df = pd.DataFrame(data)
        if 'work_date' in df.columns:
            df['work_date'] = pd.to_datetime(df['work_date'])
        return df
    
    def test_filter_standard_month(self):
        """標準月フィルタリング - 2024年1月"""
        # テストデータ準備
        df = self.create_test_dataframe([
            {"work_date": "2023-12-31", "employee_id": "EMP001"},
            {"work_date": "2024-01-01", "employee_id": "EMP001"}, 
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
        ])
        
        # テスト実行（Red Phase: 失敗が期待される）
        result = self.filter.filter_by_month(df, "2024-01")
        
        # 検証（期待値）
        assert result.filtered_count == 3, "1月のデータ数が正しくない"
        assert result.original_count == 5, "元データ数が正しくない"
        assert result.date_range == (date(2024, 1, 1), date(2024, 1, 31)), "期間範囲が正しくない"
        assert len(result.filtered_data) == 3, "フィルタ結果のデータ数が正しくない"
        
        # 1月のデータのみ含まれることを確認
        filtered_dates = result.filtered_data["work_date"].dt.strftime("%Y-%m")
        assert all(d == "2024-01" for d in filtered_dates), "1月以外のデータが含まれている"
    
    def test_filter_february_normal_year(self):
        """2月フィルタリング - 平年(2023年)"""
        df = self.create_test_dataframe([
            {"work_date": "2023-01-31", "employee_id": "EMP001"},
            {"work_date": "2023-02-01", "employee_id": "EMP001"},
            {"work_date": "2023-02-28", "employee_id": "EMP001"},
            {"work_date": "2023-03-01", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_month(df, "2023-02")
        
        assert result.filtered_count == 2, "2月のデータ数が正しくない"
        assert result.date_range == (date(2023, 2, 1), date(2023, 2, 28)), "平年2月の期間が正しくない"
        assert result.latest_date == date(2023, 2, 28), "平年2月の最終日が正しくない"
    
    def test_filter_february_leap_year(self):
        """🎯 2月フィルタリング - うるう年(2024年) - 重要境界値テスト"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},  # うるう年特有
            {"work_date": "2024-03-01", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_month(df, "2024-02")
        
        # うるう年の2月29日が正しく含まれることを検証
        assert result.filtered_count == 3, "うるう年2月のデータ数が正しくない"
        assert result.date_range == (date(2024, 2, 1), date(2024, 2, 29)), "うるう年2月の期間が正しくない"
        assert result.latest_date == date(2024, 2, 29), "うるう年2月の最終日が正しくない"
        
        # 2024年2月29日のデータが確実に含まれていることを確認
        feb29_data = result.filtered_data[
            result.filtered_data["work_date"].dt.strftime("%Y-%m-%d") == "2024-02-29"
        ]
        assert len(feb29_data) == 1, "うるう年2月29日のデータが含まれていない"


class TestMonthFilterBoundaries:
    """月フィルタリング境界値テスト - うるう年・月末日重点"""
    
    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.filter = DateFilter()
    
    def create_test_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """テスト用DataFrame作成ヘルパー"""
        # Noneエントリをフィルタアウト
        filtered_data = [item for item in data if item is not None]
        df = pd.DataFrame(filtered_data)
        if 'work_date' in df.columns:
            df['work_date'] = pd.to_datetime(df['work_date'])
        return df

    @pytest.mark.parametrize("year,expected_last_day", [
        (2020, 29),  # うるう年
        (2021, 28),  # 平年
        (2022, 28),  # 平年  
        (2023, 28),  # 平年
        (2024, 29),  # うるう年
        (2025, 28),  # 平年
        (2100, 28),  # 100年ルール（うるう年でない）
        (2000, 29),  # 400年ルール（うるう年）
    ])
    def test_february_last_day_detection(self, year, expected_last_day):
        """🎯 2月末日検出テスト - うるう年判定完全網羅"""
        test_data = [
            {"work_date": f"{year}-02-28", "employee_id": "EMP001"},
            {"work_date": f"{year}-03-01", "employee_id": "EMP001"},
        ]
        
        # うるう年の場合のみ2/29データを追加
        if expected_last_day == 29:
            test_data.insert(1, {"work_date": f"{year}-02-29", "employee_id": "EMP001"})
        
        df = self.create_test_dataframe(test_data)
        result = self.filter.filter_by_month(df, f"{year}-02")
        
        # 2月末日が正しく検出されることを検証
        assert result.date_range[1] == date(year, 2, expected_last_day), f"{year}年の2月末日検出が正しくない"
        
        # うるう年の場合29日データが含まれることを確認
        if expected_last_day == 29:
            assert result.filtered_count >= 2, f"{year}年うるう年で2月データ数が不正"
        else:
            assert result.filtered_count >= 1, f"{year}年平年で2月データ数が不正"

    @pytest.mark.parametrize("month,expected_days", [
        (1, 31),   # 1月 - 31日
        (3, 31),   # 3月 - 31日
        (4, 30),   # 4月 - 30日
        (5, 31),   # 5月 - 31日
        (6, 30),   # 6月 - 30日
        (7, 31),   # 7月 - 31日
        (8, 31),   # 8月 - 31日
        (9, 30),   # 9月 - 30日
        (10, 31),  # 10月 - 31日
        (11, 30),  # 11月 - 30日
        (12, 31),  # 12月 - 31日
    ])
    def test_month_end_days_all_months(self, month, expected_days):
        """🎯 全月の月末日数テスト - 30/31日月の正確な処理"""
        year = 2023  # 平年を使用
        
        # 各月の最後の日のデータを作成
        last_day_str = f"{year}-{month:02d}-{expected_days:02d}"
        next_month_start = date(year, month, expected_days) + timedelta(days=1)
        next_month_str = next_month_start.strftime("%Y-%m-%d")
        
        df = self.create_test_dataframe([
            {"work_date": last_day_str, "employee_id": "EMP001"},
            {"work_date": next_month_str, "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_month(df, f"{year}-{month:02d}")
        
        # 月末日の正確な検出を検証
        assert result.date_range == (date(year, month, 1), date(year, month, expected_days)), f"{month}月の期間範囲が正しくない"
        assert result.filtered_count == 1, f"{month}月のデータ数が正しくない"
        assert result.latest_date == date(year, month, expected_days), f"{month}月の最終日が正しくない"
    
    def test_year_boundary_crossing(self):
        """🎯 年跨ぎ境界テスト - 12月→1月の正確な処理"""
        df = self.create_test_dataframe([
            {"work_date": "2023-12-29", "employee_id": "EMP001"},
            {"work_date": "2023-12-30", "employee_id": "EMP001"},
            {"work_date": "2023-12-31", "employee_id": "EMP001"},  # 年末
            {"work_date": "2024-01-01", "employee_id": "EMP001"},  # 年始
            {"work_date": "2024-01-02", "employee_id": "EMP001"},
        ])
        
        # 2023年12月のフィルタリング
        result_dec = self.filter.filter_by_month(df, "2023-12")
        assert result_dec.filtered_count == 3, "2023年12月のデータ数が正しくない"
        assert result_dec.latest_date == date(2023, 12, 31), "2023年12月の最終日が正しくない"
        
        # 2024年1月のフィルタリング
        result_jan = self.filter.filter_by_month(df, "2024-01")
        assert result_jan.filtered_count == 2, "2024年1月のデータ数が正しくない"
        assert result_jan.earliest_date == date(2024, 1, 1), "2024年1月の開始日が正しくない"
        
        # 重複データがないことを確認
        dec_dates = set(result_dec.filtered_data["work_date"].dt.strftime("%Y-%m-%d"))
        jan_dates = set(result_jan.filtered_data["work_date"].dt.strftime("%Y-%m-%d"))
        assert dec_dates.isdisjoint(jan_dates), "年跨ぎで重複データが存在する"


class TestFilterByRange:
    """日付範囲フィルタリング単体テスト"""
    
    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.filter = DateFilter()
    
    def create_test_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """テスト用DataFrame作成ヘルパー"""
        df = pd.DataFrame(data)
        if 'work_date' in df.columns:
            df['work_date'] = pd.to_datetime(df['work_date'])
        return df
    
    def test_filter_standard_range(self):
        """標準日付範囲フィルタリング"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-10", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-20", "employee_id": "EMP001"},
            {"work_date": "2024-01-25", "employee_id": "EMP001"},
            {"work_date": "2024-01-30", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_range(df, "2024-01-15", "2024-01-25")
        
        assert result.filtered_count == 3, "範囲フィルタのデータ数が正しくない"  # 15, 20, 25
        assert result.date_range == (date(2024, 1, 15), date(2024, 1, 25)), "範囲フィルタの期間が正しくない"
        assert result.earliest_date == date(2024, 1, 15), "範囲フィルタの開始日が正しくない"
        assert result.latest_date == date(2024, 1, 25), "範囲フィルタの終了日が正しくない"
    
    def test_filter_cross_month_range(self):
        """月跨ぎ日付範囲フィルタリング"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-25", "employee_id": "EMP001"},
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
            {"work_date": "2024-02-15", "employee_id": "EMP001"},
            {"work_date": "2024-02-20", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_range(df, "2024-01-30", "2024-02-10")
        
        assert result.filtered_count == 2, "月跨ぎ範囲フィルタのデータ数が正しくない"  # 1/31, 2/1
        
    def test_filter_cross_year_range(self):
        """🎯 年跨ぎ日付範囲フィルタリング - 重要境界値テスト"""
        df = self.create_test_dataframe([
            {"work_date": "2023-12-25", "employee_id": "EMP001"},
            {"work_date": "2023-12-31", "employee_id": "EMP001"},
            {"work_date": "2024-01-01", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_range(df, "2023-12-30", "2024-01-10")
        
        assert result.filtered_count == 2, "年跨ぎ範囲フィルタのデータ数が正しくない"  # 12/31, 1/1
        assert result.date_range == (date(2023, 12, 30), date(2024, 1, 10)), "年跨ぎ範囲の期間が正しくない"


class TestRangeFilterBoundaries:
    """日付範囲境界値・エラーケーステスト"""
    
    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.filter = DateFilter()
    
    def create_test_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """テスト用DataFrame作成ヘルパー"""
        df = pd.DataFrame(data)
        if 'work_date' in df.columns:
            df['work_date'] = pd.to_datetime(df['work_date'])
        return df
    
    def test_leap_year_february_range(self):
        """🎯 うるう年2月を含む範囲テスト"""
        df = self.create_test_dataframe([
            {"work_date": "2024-02-27", "employee_id": "EMP001"},
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},  # うるう年のみ存在
            {"work_date": "2024-03-01", "employee_id": "EMP001"},
            {"work_date": "2024-03-02", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_range(df, "2024-02-28", "2024-03-01")
        
        # うるう年の2月29日が含まれることを確認
        assert result.filtered_count == 3, "うるう年2月29日を含む範囲フィルタのデータ数が正しくない"  # 2/28, 2/29, 3/1
        
        # 2024年2月29日が確実に含まれることを確認
        filtered_dates = result.filtered_data["work_date"].dt.strftime("%Y-%m-%d").tolist()
        assert "2024-02-29" in filtered_dates, "うるう年2月29日が範囲フィルタに含まれていない"
    
    def test_invalid_date_range_start_after_end(self):
        """🎯 無効範囲 - 開始日 > 終了日のエラーテスト"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
        ])
        
        with pytest.raises(DateRangeError, match="開始日が終了日より後です"):
            self.filter.filter_by_range(df, "2024-01-20", "2024-01-10")
    
    def test_invalid_date_format(self):
        """🎯 無効日付フォーマットのエラーテスト"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
        ])
        
        with pytest.raises(InvalidPeriodError, match="無効な日付フォーマット"):
            self.filter.filter_by_range(df, "2024/13/45", "2024-01-31")
    
    def test_nonexistent_date_handling(self):
        """🎯 存在しない日付の処理テスト"""
        df = self.create_test_dataframe([
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},
        ])
        
        # 平年の2月29日を指定した場合の処理
        with pytest.raises(InvalidPeriodError, match="存在しない日付"):
            self.filter.filter_by_range(df, "2023-02-29", "2023-03-01")  # 2023年は平年
    
    def test_same_date_range(self):
        """同一日付範囲テスト"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-16", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_range(df, "2024-01-15", "2024-01-15")
        
        assert result.filtered_count == 1, "同一日付範囲フィルタのデータ数が正しくない"
        assert result.earliest_date == result.latest_date == date(2024, 1, 15), "同一日付範囲の開始・終了日が正しくない"


class TestFilterByRelative:
    """相対期間フィルタリング単体テスト"""
    
    def setup_method(self):
        """各テストメソッド実行前のセットアップ"""
        self.filter = DateFilter()
    
    def create_test_dataframe(self, data: List[Dict[str, Any]]) -> pd.DataFrame:
        """テスト用DataFrame作成ヘルパー"""
        df = pd.DataFrame(data)
        if 'work_date' in df.columns:
            df['work_date'] = pd.to_datetime(df['work_date'])
        return df

    @freeze_time("2024-02-15")  # 現在時刻を固定
    def test_filter_last_month(self):
        """先月フィルタリング"""
        df = self.create_test_dataframe([
            {"work_date": "2023-12-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-05", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-01-25", "employee_id": "EMP001"},
            {"work_date": "2024-02-05", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_relative(df, "last_month")
        
        # 2024-02-15の先月は2024-01
        assert result.filtered_count == 3, "先月フィルタのデータ数が正しくない"
        assert result.date_range == (date(2024, 1, 1), date(2024, 1, 31)), "先月の期間範囲が正しくない"
    
    @freeze_time("2024-03-10")  # うるう年3月での先月テスト
    def test_filter_last_month_leap_february(self):
        """🎯 先月フィルタリング - うるう年2月の検証"""
        df = self.create_test_dataframe([
            {"work_date": "2024-01-31", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
            {"work_date": "2024-02-28", "employee_id": "EMP001"},
            {"work_date": "2024-02-29", "employee_id": "EMP001"},  # うるう年
            {"work_date": "2024-03-01", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_relative(df, "last_month")
        
        # 2024-03-10の先月は2024-02（うるう年なので29日まで）
        assert result.filtered_count == 3, "うるう年2月の先月フィルタデータ数が正しくない"  # 2/1, 2/28, 2/29
        assert result.date_range == (date(2024, 2, 1), date(2024, 2, 29)), "うるう年2月の先月期間が正しくない"
        assert result.latest_date == date(2024, 2, 29), "うるう年2月の最終日が正しくない"
    
    @freeze_time("2024-01-10")
    def test_filter_this_month(self):
        """今月フィルタリング"""
        df = self.create_test_dataframe([
            {"work_date": "2023-12-25", "employee_id": "EMP001"},
            {"work_date": "2024-01-05", "employee_id": "EMP001"},
            {"work_date": "2024-01-15", "employee_id": "EMP001"},
            {"work_date": "2024-02-01", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_relative(df, "this_month")
        
        assert result.filtered_count == 2, "今月フィルタのデータ数が正しくない"
        filtered_dates = result.filtered_data["work_date"].dt.strftime("%Y-%m")
        assert all(d == "2024-01" for d in filtered_dates), "今月以外のデータが含まれている"
    
    @freeze_time("2024-12-15")
    def test_filter_next_month_year_crossing(self):
        """🎯 来月フィルタリング - 年跨ぎケース"""
        df = self.create_test_dataframe([
            {"work_date": "2024-11-25", "employee_id": "EMP001"},
            {"work_date": "2024-12-15", "employee_id": "EMP001"},
            {"work_date": "2025-01-05", "employee_id": "EMP001"},
            {"work_date": "2025-01-15", "employee_id": "EMP001"},
            {"work_date": "2025-02-01", "employee_id": "EMP001"},
        ])
        
        result = self.filter.filter_by_relative(df, "next_month")
        
        # 2024-12-15の来月は2025-01
        assert result.filtered_count == 2, "年跨ぎ来月フィルタのデータ数が正しくない"
        assert result.date_range == (date(2025, 1, 1), date(2025, 1, 31)), "年跨ぎ来月の期間が正しくない"


# Red Phase実行確認用スクリプト
if __name__ == "__main__":
    print("🔴 TASK-103 Red Phase テスト実行")
    print("=" * 50)
    
    # pytest実行（失敗が期待される）
    pytest.main([
        __file__,
        "-v",
        "--tb=short",
        "--no-header",
        "-x"  # 最初の失敗で停止
    ])