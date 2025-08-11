"""
統合期間フィルタ - TASK-101/102連携実装
TASK-103 Green Phase実装
"""

from typing import Optional, Tuple

import pandas as pd

from .date_filter import DateFilter
from .models import DateFilterError, FilterResult, PeriodSpecification


class IntegratedDateFilter:
    """統合期間フィルタクラス"""

    def __init__(
        self,
        csv_reader=None,  # TASK-101 CSVReader
        validator=None,  # TASK-102 DataValidator
        date_filter: DateFilter = None,
    ):
        """統合フィルタ初期化"""
        self.csv_reader = csv_reader
        self.validator = validator
        self.date_filter = date_filter or DateFilter()

    def load_and_filter(
        self, file_path: str, period: PeriodSpecification
    ) -> FilterResult:
        """CSV読み込み→検証→フィルタリング統合処理"""
        if not self.csv_reader:
            raise DateFilterError("CSVReaderが設定されていません")

        # CSV読み込み
        df = self.csv_reader.load_file(file_path)

        # 検証実行（Validatorが設定されている場合）
        if self.validator:
            validation_report = self.validator.validate(df)
            if (
                hasattr(validation_report, "has_errors")
                and validation_report.has_errors
            ):
                raise DateFilterError("データ検証でエラーが発生しました")

        # フィルタリング実行
        result = self.date_filter.filter_by_specification(df, period)

        return result

    def validate_and_filter(
        self, df: pd.DataFrame, period: PeriodSpecification
    ) -> Tuple[object, FilterResult]:
        """検証→フィルタリング統合処理"""
        validation_report = None

        if self.validator:
            validation_report = self.validator.validate(df)

        # フィルタリング実行
        filter_result = self.date_filter.filter_by_specification(df, period)

        return validation_report, filter_result


class ValidatedDateFilter(DateFilter):
    """検証付き期間フィルタ"""

    def __init__(self, validator, config=None):
        """初期化"""
        super().__init__(config)
        self.validator = validator

    def filter_with_pre_validation(
        self, df: pd.DataFrame, period: PeriodSpecification
    ) -> FilterResult:
        """事前検証付きフィルタリング"""
        # 事前検証
        validation_report = self.validator.validate(df)

        if (
            hasattr(validation_report, "has_critical_errors")
            and validation_report.has_critical_errors
        ):
            raise DateFilterError(
                "検証で重大なエラーが発生したため、フィルタリングを中止します"
            )

        # フィルタリング実行
        return self.filter_by_specification(df, period)
