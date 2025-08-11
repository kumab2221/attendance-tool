"""
期間フィルタリング機能 - メインクラス実装
TASK-103 Green Phase実装
"""

import time
from datetime import date, datetime
from typing import List, Optional, Union

import pandas as pd
from dateutil.parser import parse as date_parse
from dateutil.relativedelta import relativedelta

from .models import (
    DateFilterConfig,
    DateFilterError,
    DateRangeError,
    FilterResult,
    InvalidPeriodError,
    PeriodSpecification,
    PeriodType,
)


class DateFilter:
    """期間フィルタリングメインクラス"""

    def __init__(self, config: Optional[DateFilterConfig] = None):
        """初期化"""
        self.config = config or DateFilterConfig()

    def filter_by_month(
        self, df: pd.DataFrame, month: str, date_column: str = None
    ) -> FilterResult:
        """月単位フィルタリング

        Args:
            df: 対象DataFrame
            month: "YYYY-MM" または "YYYY-M"
            date_column: 日付列名（自動検出可）

        Returns:
            FilterResult: フィルタリング結果
        """
        start_time = time.time()

        # 日付列の取得
        date_col = self._get_date_column(df, date_column)

        # DataFrame準備
        df_work = df.copy()
        self._prepare_dataframe(df_work, date_col)

        # 期間仕様作成
        spec = PeriodSpecification(period_type=PeriodType.MONTH, month_string=month)

        # フィルタリング実行
        result = self._execute_filter(df_work, spec, date_col)
        result.processing_time = time.time() - start_time

        return result

    def filter_by_range(
        self,
        df: pd.DataFrame,
        start_date: Union[str, date],
        end_date: Union[str, date],
        date_column: str = None,
    ) -> FilterResult:
        """日付範囲フィルタリング"""
        start_time = time.time()

        # 日付変換
        start_date_obj = self._parse_date(start_date)
        end_date_obj = self._parse_date(end_date)

        # 範囲検証
        if start_date_obj > end_date_obj:
            raise DateRangeError("開始日が終了日より後です")

        # 日付列の取得
        date_col = self._get_date_column(df, date_column)

        # DataFrame準備
        df_work = df.copy()
        self._prepare_dataframe(df_work, date_col)

        # 期間仕様作成
        spec = PeriodSpecification(
            period_type=PeriodType.DATE_RANGE,
            start_date=start_date_obj,
            end_date=end_date_obj,
        )

        # フィルタリング実行
        result = self._execute_filter(df_work, spec, date_col)
        result.processing_time = time.time() - start_time

        return result

    def filter_by_relative(
        self,
        df: pd.DataFrame,
        relative_period: str,
        date_column: str = None,
        reference_date: Optional[date] = None,
    ) -> FilterResult:
        """相対期間フィルタリング"""
        start_time = time.time()

        # 日付列の取得
        date_col = self._get_date_column(df, date_column)

        # DataFrame準備
        df_work = df.copy()
        self._prepare_dataframe(df_work, date_col)

        # 期間仕様作成
        spec = PeriodSpecification(
            period_type=PeriodType.RELATIVE, relative_string=relative_period
        )

        # フィルタリング実行
        result = self._execute_filter(df_work, spec, date_col)
        result.processing_time = time.time() - start_time

        return result

    def filter_by_specification(
        self, df: pd.DataFrame, spec: PeriodSpecification, date_column: str = None
    ) -> FilterResult:
        """期間仕様によるフィルタリング"""
        start_time = time.time()

        # 日付列の取得
        date_col = self._get_date_column(df, date_column)

        # DataFrame準備
        df_work = df.copy()
        self._prepare_dataframe(df_work, date_col)

        # フィルタリング実行
        result = self._execute_filter(df_work, spec, date_col)
        result.processing_time = time.time() - start_time

        return result

    # === プライベートメソッド ===

    def _get_date_column(self, df: pd.DataFrame, date_column: str = None) -> str:
        """日付列名の取得（自動検出対応）"""
        if date_column:
            if date_column not in df.columns:
                raise InvalidPeriodError(
                    f"指定された日付列が見つかりません: {date_column}"
                )
            return date_column

        # 自動検出
        date_candidates = [
            self.config.default_date_column,
            "work_date",
            "date",
            "勤務日",
            "日付",
        ]

        for candidate in date_candidates:
            if candidate in df.columns:
                return candidate

        # 日付型の列を探す
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                return col

        raise InvalidPeriodError(
            "日付列が見つかりません。date_columnを明示的に指定してください"
        )

    def _prepare_dataframe(self, df: pd.DataFrame, date_column: str):
        """DataFrame前処理"""
        # 日付列の型変換
        if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
            try:
                df[date_column] = pd.to_datetime(df[date_column], errors="coerce")
            except Exception as e:
                raise InvalidPeriodError(f"日付列の変換に失敗しました: {e}")

        # 無効な日付の処理
        invalid_dates = df[date_column].isna()
        if invalid_dates.any():
            if self.config.invalid_date_handling == "error":
                raise InvalidPeriodError("無効な日付が含まれています")
            elif self.config.invalid_date_handling == "skip":
                df.drop(df[invalid_dates].index, inplace=True)
            # 'adjust'の場合は特に処理しない（NaTとして残す）

    def _execute_filter(
        self, df: pd.DataFrame, spec: PeriodSpecification, date_column: str
    ) -> FilterResult:
        """フィルタリング実行"""
        original_count = len(df)

        # 期間範囲取得
        start_date, end_date = spec.to_date_range()

        # フィルタリング実行
        date_mask = (df[date_column] >= pd.Timestamp(start_date)) & (
            df[date_column] <= pd.Timestamp(end_date)
        )
        filtered_df = df[date_mask].copy()

        filtered_count = len(filtered_df)
        excluded_records = original_count - filtered_count

        # 統計情報計算
        if filtered_count > 0:
            earliest_date = filtered_df[date_column].min().date()
            latest_date = filtered_df[date_column].max().date()
        else:
            earliest_date = None
            latest_date = None

        return FilterResult(
            filtered_data=filtered_df,
            original_count=original_count,
            filtered_count=filtered_count,
            date_range=(start_date, end_date),
            processing_time=0.0,  # 呼び出し元で設定
            earliest_date=earliest_date,
            latest_date=latest_date,
            excluded_records=excluded_records,
        )

    def _parse_date(self, date_input: Union[str, date]) -> date:
        """日付解析"""
        if isinstance(date_input, date):
            return date_input
        elif isinstance(date_input, str):
            try:
                parsed = date_parse(date_input)
                return parsed.date()
            except Exception as e:
                # Check if this is a "day is out of range for month" error (nonexistent date)
                error_msg = str(e).lower()
                if (
                    "day is out of range for month" in error_msg
                    or "存在しない" in error_msg
                ):
                    raise InvalidPeriodError(f"存在しない日付: {date_input}")
                else:
                    raise InvalidPeriodError(f"無効な日付フォーマット: {date_input}")
        else:
            raise InvalidPeriodError(f"サポートされていない日付型: {type(date_input)}")
