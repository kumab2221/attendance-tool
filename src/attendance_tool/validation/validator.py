"""データ検証エンジン

DataFrameとレコードレベルでのデータ検証機能
"""

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pandas as pd

from .models import AttendanceRecord
from .rules import RuleRegistry, ValidationError, ValidationRule, ValidationWarning


@dataclass
class ValidationReport:
    """データ検証結果"""

    total_records: int
    valid_records: int
    errors: List[ValidationError]
    warnings: List[ValidationWarning]
    processing_time: float
    quality_score: float

    def get_error_summary(self) -> Dict[str, int]:
        """エラーサマリーを取得"""
        summary = {}
        for error in self.errors:
            field = error.field
            summary[field] = summary.get(field, 0) + 1
        return summary

    def get_critical_errors(self) -> List[ValidationError]:
        """重大エラーを取得"""
        return [error for error in self.errors if error.level == "CRITICAL"]

    def export_to_csv(self, file_path: str) -> None:
        """CSV出力"""
        import csv

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)

            # ヘッダー
            writer.writerow(["row_number", "field", "level", "message", "value"])

            # エラー
            for error in self.errors:
                writer.writerow(
                    [
                        error.row_number,
                        error.field,
                        error.level,
                        error.message,
                        str(error.value),
                    ]
                )

            # 警告
            for warning in self.warnings:
                writer.writerow(
                    [
                        warning.row_number,
                        warning.field,
                        "WARNING",
                        warning.message,
                        str(warning.value),
                    ]
                )


class DataValidator:
    """データ検証エンジン"""

    def __init__(self, config: Dict = None, rules: List[ValidationRule] = None):
        """初期化

        Args:
            config: 検証設定
            rules: 検証ルールリスト
        """
        self.config = config or {}
        self.rule_registry = RuleRegistry()
        self.logger = logging.getLogger(__name__)

        # カスタムルール追加
        if rules:
            for rule in rules:
                self.rule_registry.add_rule(rule)

        # 設定から並列処理フラグを取得
        self.parallel = self.config.get("parallel", False)

        # 警告を保存するためのリスト
        self._current_warnings: List[ValidationWarning] = []

    @property
    def rules(self) -> List[ValidationRule]:
        """登録済みルール取得"""
        return self.rule_registry.rules

    def add_custom_rule(self, rule: ValidationRule) -> None:
        """カスタムルール追加"""
        self.rule_registry.add_rule(rule)

    def validate_dataframe(self, df: pd.DataFrame) -> ValidationReport:
        """DataFrame検証

        Args:
            df: 検証対象DataFrame

        Returns:
            ValidationReport: 検証結果
        """
        start_time = time.time()

        errors = []
        warnings = []
        valid_records = 0
        total_records = len(df)

        if total_records == 0:
            # 空のDataFrameの場合
            return ValidationReport(
                total_records=0,
                valid_records=0,
                errors=[],
                warnings=[],
                processing_time=0.0,
                quality_score=1.0,
            )

        # 必須カラムチェック
        required_columns = ["employee_id", "employee_name", "work_date"]
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            for col in missing_columns:
                errors.append(
                    ValidationError(
                        row_number=-1,
                        field=col,
                        message=f"必須カラム不足: {col}",
                        value=None,
                        level="CRITICAL",
                    )
                )

        # 各行を検証
        for idx, row in df.iterrows():
            row_errors, row_warnings = self._validate_row(row, idx)
            errors.extend(row_errors)
            warnings.extend(row_warnings)

            # 行が有効かどうか判定（エラーがない場合）
            if not row_errors:
                valid_records += 1

        processing_time = time.time() - start_time

        # 品質スコア計算（簡易版）
        if total_records > 0:
            quality_score = valid_records / total_records
        else:
            quality_score = 1.0

        return ValidationReport(
            total_records=total_records,
            valid_records=valid_records,
            errors=errors,
            warnings=warnings,
            processing_time=processing_time,
            quality_score=quality_score,
        )

    def validate_record(self, record: Dict[str, Any]) -> List[ValidationError]:
        """個別レコード検証

        Args:
            record: 検証対象レコード

        Returns:
            List[ValidationError]: 検証エラーリスト
        """
        self._current_warnings = []  # 警告をリセット

        try:
            # pydanticモデルによる検証を試行
            attendance_record = AttendanceRecord(**record)

            # 追加のカスタムルール適用
            custom_errors = self.rule_registry.apply_all_rules(record)

            return custom_errors

        except ValueError as e:
            # pydanticバリデーションエラーを変換
            return [
                ValidationError(
                    row_number=record.get("_row_number", -1),
                    field="validation",
                    message=str(e),
                    value=None,
                    level="ERROR",
                )
            ]
        except Exception as e:
            # その他のエラー
            return [
                ValidationError(
                    row_number=record.get("_row_number", -1),
                    field="system",
                    message=f"予期しないエラー: {str(e)}",
                    value=None,
                    level="CRITICAL",
                )
            ]

    def get_warnings(self, record: Dict[str, Any]) -> List[ValidationWarning]:
        """レコードの警告を取得"""
        # 簡易実装：時間チェックベースの警告
        warnings = []

        # 異常に早い出勤時刻
        start_time_str = record.get("start_time", "")
        if start_time_str and start_time_str < "07:00":
            warnings.append(
                ValidationWarning(
                    row_number=record.get("_row_number", -1),
                    field="start_time",
                    message="異常に早い出勤時刻です",
                    value=start_time_str,
                )
            )

        # 異常に遅い退勤時刻
        end_time_str = record.get("end_time", "")
        if end_time_str and end_time_str > "22:00":
            warnings.append(
                ValidationWarning(
                    row_number=record.get("_row_number", -1),
                    field="end_time",
                    message="異常に遅い退勤時刻です（長時間勤務の可能性）",
                    value=end_time_str,
                )
            )

        # 短い休憩時間
        break_minutes = record.get("break_minutes")
        if isinstance(break_minutes, int) and break_minutes < 30:
            warnings.append(
                ValidationWarning(
                    row_number=record.get("_row_number", -1),
                    field="break_minutes",
                    message="休憩時間が短いです",
                    value=break_minutes,
                )
            )

        return warnings

    def get_validation_summary(self) -> Dict[str, Any]:
        """検証サマリー取得"""
        return {
            "total_rules": len(self.rules),
            "config": self.config,
            "parallel_enabled": self.parallel,
        }

    def _validate_row(self, row: pd.Series, row_idx: int) -> tuple:
        """行レベル検証

        Args:
            row: 検証対象行
            row_idx: 行インデックス

        Returns:
            tuple: (errors, warnings)
        """
        # 行データを辞書に変換
        record = row.to_dict()
        record["_row_number"] = row_idx

        # レコード検証
        errors = self.validate_record(record)

        # 警告取得
        warnings = self.get_warnings(record)

        # 行番号を更新
        for error in errors:
            if error.row_number == -1:
                error.row_number = row_idx

        for warning in warnings:
            if warning.row_number == -1:
                warning.row_number = row_idx

        return errors, warnings
