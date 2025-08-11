"""CSVファイル読み込み・検証機能

このモジュールは勤怠データのCSVファイルを読み込み、
データの検証とクレンジングを行う機能を提供します。
"""

import logging
import os
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import chardet
import pandas as pd
import yaml


class CSVProcessingError(Exception):
    """CSV処理基底例外"""

    pass


class FileAccessError(CSVProcessingError):
    """ファイルアクセスエラー"""

    pass


class ValidationError(CSVProcessingError):
    """データ検証エラー"""

    pass


class EncodingError(CSVProcessingError):
    """エンコーディングエラー"""

    pass


@dataclass
class ValidationWarning:
    """検証警告"""

    row_number: int
    column: str
    message: str
    value: Any


@dataclass
class ValidationErrorDetail:
    """検証エラー詳細"""

    row_number: int
    column: str
    message: str
    value: Any
    expected_format: Optional[str] = None


@dataclass
class ValidationResult:
    """データ検証結果"""

    is_valid: bool
    errors: List[ValidationErrorDetail]
    warnings: List[ValidationWarning]
    processed_rows: int
    valid_rows: int
    column_mapping: Dict[str, str]

    def has_critical_errors(self) -> bool:
        """重大エラーの有無を確認"""
        # 重大エラー: ファイルアクセス不可、必須カラム不足、処理継続不可能なエラー
        critical_error_keywords = ["ファイル不存在", "必須カラム不足", "アクセス権限"]
        return any(
            any(keyword in error.message for keyword in critical_error_keywords)
            for error in self.errors
        )

    def get_summary(self) -> str:
        """検証結果サマリーを取得"""
        status = "✅ 成功" if self.is_valid else "❌ エラー"
        return (
            f"検証結果: {status}\n"
            f"処理行数: {self.processed_rows}\n"
            f"有効行数: {self.valid_rows}\n"
            f"エラー数: {len(self.errors)}\n"
            f"警告数: {len(self.warnings)}"
        )


class CSVReader:
    """CSVファイル読み込み・検証クラス"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Args:
            config_path: 設定ファイルパス（csv_format.yaml）
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)

    def _load_config(self) -> Dict:
        """設定ファイルを読み込む"""
        if not self.config_path:
            # デフォルト設定パス
            default_config = (
                Path(__file__).parent.parent.parent.parent
                / "config"
                / "csv_format.yaml"
            )
            if default_config.exists():
                self.config_path = str(default_config)
            else:
                # 設定ファイルが見つからない場合のデフォルト設定
                return self._get_default_config()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"設定ファイル読み込みエラー: {e}")
            return self._get_default_config()

    def _get_default_config(self) -> Dict:
        """デフォルト設定を返す"""
        return {
            "input": {
                "required_columns": {
                    "employee_id": {
                        "names": ["社員ID", "employee_id", "emp_id", "社員番号"],
                        "required": True,
                    },
                    "employee_name": {
                        "names": ["氏名", "社員名", "employee_name", "name", "名前"],
                        "required": True,
                    },
                    "work_date": {
                        "names": ["日付", "勤務日", "work_date", "date", "年月日"],
                        "required": True,
                    },
                },
                "validation": {
                    "date_range": {"past_years": 5, "future_days": 0},
                    "time_validation": {"max_work_minutes": 1440},
                },
            }
        }

    def load_file(self, file_path: str, encoding: Optional[str] = None) -> pd.DataFrame:
        """
        CSVファイルを読み込み、検証済みDataFrameを返す

        Args:
            file_path: CSVファイルパス
            encoding: 文字エンコーディング（自動検出の場合None）

        Returns:
            pd.DataFrame: 検証済み勤怠データ

        Raises:
            FileNotFoundError: ファイル不存在
            ValidationError: データ検証エラー
            EncodingError: エンコーディングエラー
        """
        # セキュリティチェック: パストラバーサル防止
        if (
            ".." in file_path
            or file_path.startswith("/dev/")
            or file_path.startswith("/etc/")
        ):
            raise ValueError(f"不正なファイルパス: {file_path}")

        # ファイル存在チェック
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"ファイルが見つかりません: {file_path}")

        # 権限チェック
        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"ファイル読み取り権限がありません: {file_path}")

        # ファイルサイズチェック（空ファイル）
        if os.path.getsize(file_path) == 0:
            raise CSVProcessingError(f"空のファイルです: {file_path}")

        # エンコーディング検出
        if encoding is None:
            encoding = self._detect_encoding(file_path)

        try:
            # CSVファイル読み込み
            df = pd.read_csv(file_path, encoding=encoding)

            # 空データフレームチェック
            if df.empty:
                raise CSVProcessingError(f"有効なデータが見つかりません: {file_path}")

            # カラムマッピング実行
            column_mapping = self.get_column_mapping(df)

            # 必須カラムチェック
            self._check_required_columns(column_mapping)

            # データ検証実行
            validation_result = self.validate_data(df)

            # 重大エラーがある場合は例外発生
            if validation_result.has_critical_errors():
                critical_errors = [
                    e.message
                    for e in validation_result.errors
                    if "必須" in e.message or "不存在" in e.message
                ]
                raise ValidationError(f"重大な検証エラー: {'; '.join(critical_errors)}")

            return df

        except UnicodeDecodeError as e:
            raise EncodingError(f"文字エンコーディングエラー: {e}")
        except pd.errors.EmptyDataError:
            raise CSVProcessingError(f"CSVファイルが空です: {file_path}")
        except pd.errors.ParserError as e:
            raise CSVProcessingError(f"CSVフォーマットエラー: {e}")

    def _detect_encoding(self, file_path: str) -> str:
        """ファイルのエンコーディングを検出"""
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read(10000)  # 最初の10KBを読み込み
                result = chardet.detect(raw_data)
                encoding = result["encoding"]

                # 一般的なエンコーディングにフォールバック
                if encoding is None or result["confidence"] < 0.7:
                    # UTF-8を試す
                    try:
                        with open(file_path, "r", encoding="utf-8") as test_f:
                            test_f.read(1000)
                        return "utf-8"
                    except UnicodeDecodeError:
                        # Shift_JISを試す
                        try:
                            with open(file_path, "r", encoding="shift_jis") as test_f:
                                test_f.read(1000)
                            return "shift_jis"
                        except UnicodeDecodeError:
                            return "utf-8"  # デフォルトとしてUTF-8を使用

                return encoding

        except Exception as e:
            self.logger.warning(f"エンコーディング検出エラー: {e}")
            return "utf-8"  # デフォルト

    def _check_required_columns(self, column_mapping: Dict[str, str]) -> None:
        """必須カラムの存在をチェック"""
        required_columns = self.config.get("input", {}).get("required_columns", {})
        missing_columns = []

        for col_key, col_config in required_columns.items():
            if col_config.get("required", False) and col_key not in column_mapping:
                missing_columns.append(col_key)

        if missing_columns:
            raise ValidationError(f"必須カラム不足: {', '.join(missing_columns)}")

    def validate_data(self, df: pd.DataFrame) -> ValidationResult:
        """
        データ品質検証を実行

        Args:
            df: 検証対象DataFrame

        Returns:
            ValidationResult: 検証結果（エラー・警告情報含む）
        """
        errors = []
        warnings = []
        processed_rows = len(df)
        valid_rows = 0
        column_mapping = self.get_column_mapping(df)

        # 各行を検証
        for idx, row in df.iterrows():
            row_valid = True

            # 日付検証
            if "work_date" in column_mapping:
                date_col = column_mapping["work_date"]
                if date_col in df.columns:
                    date_value = row[date_col]
                    date_error = self._validate_date(date_value, idx)
                    if date_error:
                        if "未来" in date_error.message:
                            warnings.append(
                                ValidationWarning(
                                    row_number=idx,
                                    column=date_col,
                                    message=date_error.message,
                                    value=date_value,
                                )
                            )
                        else:
                            errors.append(date_error)
                            row_valid = False

            # 時刻検証
            self._validate_time_fields(row, idx, column_mapping, errors, warnings)

            # 勤務時間検証
            self._validate_work_hours(row, idx, column_mapping, warnings)

            if row_valid:
                valid_rows += 1

        is_valid = len(errors) == 0

        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            processed_rows=processed_rows,
            valid_rows=valid_rows,
            column_mapping=column_mapping,
        )

    def _validate_date(
        self, date_value: Any, row_idx: int
    ) -> Optional[ValidationErrorDetail]:
        """日付値を検証"""
        if pd.isna(date_value):
            return ValidationErrorDetail(
                row_number=row_idx,
                column="work_date",
                message="日付が空です",
                value=date_value,
            )

        try:
            # 日付文字列をパース
            if isinstance(date_value, str):
                # 複数の日付フォーマットを試す
                date_formats = ["%Y-%m-%d", "%Y/%m/%d", "%m/%d/%Y"]
                parsed_date = None

                for fmt in date_formats:
                    try:
                        parsed_date = datetime.strptime(str(date_value), fmt)
                        break
                    except ValueError:
                        continue

                if parsed_date is None:
                    return ValidationErrorDetail(
                        row_number=row_idx,
                        column="work_date",
                        message=f"無効な日付フォーマット: {date_value}",
                        value=date_value,
                        expected_format="YYYY-MM-DD, YYYY/MM/DD, MM/DD/YYYY",
                    )

                # 日付範囲チェック
                today = datetime.now()
                past_limit = today - timedelta(days=365 * 5)  # 5年前
                future_limit = today  # 未来日は警告

                if parsed_date < past_limit:
                    return ValidationErrorDetail(
                        row_number=row_idx,
                        column="work_date",
                        message=f"過去の日付です（5年以上前）: {date_value}",
                        value=date_value,
                    )

                if parsed_date > future_limit:
                    return ValidationErrorDetail(
                        row_number=row_idx,
                        column="work_date",
                        message=f"未来の日付です: {date_value}",
                        value=date_value,
                    )

        except Exception as e:
            return ValidationErrorDetail(
                row_number=row_idx,
                column="work_date",
                message=f"日付処理エラー: {str(e)}",
                value=date_value,
            )

        return None

    def _validate_time_fields(
        self,
        row: pd.Series,
        row_idx: int,
        column_mapping: Dict[str, str],
        errors: List[ValidationErrorDetail],
        warnings: List[ValidationWarning],
    ) -> None:
        """時刻フィールドを検証"""
        if "start_time" in column_mapping and "end_time" in column_mapping:
            start_col = column_mapping["start_time"]
            end_col = column_mapping["end_time"]

            if start_col in row and end_col in row:
                start_time = row[start_col]
                end_time = row[end_col]

                # 無効な時刻チェック
                if self._is_invalid_time(start_time):
                    errors.append(
                        ValidationErrorDetail(
                            row_number=row_idx,
                            column=start_col,
                            message=f"無効な時刻: {start_time}",
                            value=start_time,
                            expected_format="HH:MM または HH:MM:SS",
                        )
                    )

                if self._is_invalid_time(end_time):
                    errors.append(
                        ValidationErrorDetail(
                            row_number=row_idx,
                            column=end_col,
                            message=f"無効な時刻: {end_time}",
                            value=end_time,
                            expected_format="HH:MM または HH:MM:SS",
                        )
                    )

    def _is_invalid_time(self, time_value: Any) -> bool:
        """時刻値が無効かどうか判定"""
        if pd.isna(time_value):
            return False  # 空の時刻は許可（オプショナル）

        if isinstance(time_value, str):
            # 25:00 のような無効な時刻をチェック
            time_pattern = r"^([0-2]?[0-9]):([0-5][0-9])(:([0-5][0-9]))?$"
            match = re.match(time_pattern, time_value)

            if not match:
                return True

            hour = int(match.group(1))
            minute = int(match.group(2))

            # 24時間制チェック（25:00等は無効）
            if hour >= 24 or minute >= 60:
                return True

        return False

    def _validate_work_hours(
        self,
        row: pd.Series,
        row_idx: int,
        column_mapping: Dict[str, str],
        warnings: List[ValidationWarning],
    ) -> None:
        """勤務時間を検証"""
        if "start_time" in column_mapping and "end_time" in column_mapping:
            start_col = column_mapping["start_time"]
            end_col = column_mapping["end_time"]

            if start_col in row and end_col in row:
                start_time = row[start_col]
                end_time = row[end_col]

                if not pd.isna(start_time) and not pd.isna(end_time):
                    # 簡易的な勤務時間チェック（出勤時刻が退勤時刻より遅い場合）
                    if str(start_time) > str(end_time):  # 簡易比較
                        warnings.append(
                            ValidationWarning(
                                row_number=row_idx,
                                column=f"{start_col}, {end_col}",
                                message="出勤時刻が退勤時刻より遅いか、24時間を超える勤務時間の可能性があります",
                                value=f"{start_time} - {end_time}",
                            )
                        )

    def get_column_mapping(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        カラムマッピングを取得

        Args:
            df: 対象DataFrame

        Returns:
            Dict[str, str]: 標準フィールド名→実際のカラム名のマッピング
        """
        mapping = {}
        required_columns = self.config.get("input", {}).get("required_columns", {})

        # DataFrameのカラム名を正規化（大文字小文字を統一）
        df_columns_lower = [col.lower() for col in df.columns]

        for standard_name, col_config in required_columns.items():
            candidate_names = col_config.get("names", [])

            # 候補名の中から一致するものを探す
            for candidate in candidate_names:
                candidate_lower = candidate.lower()

                # 完全一致チェック
                if candidate in df.columns:
                    mapping[standard_name] = candidate
                    break
                # 大文字小文字を無視した一致チェック
                elif candidate_lower in df_columns_lower:
                    idx = df_columns_lower.index(candidate_lower)
                    mapping[standard_name] = df.columns[idx]
                    break

        return mapping
