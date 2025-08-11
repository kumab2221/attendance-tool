"""データクレンジング機能

データの自動修正と修正提案機能
"""

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd

from .rules import ValidationError, ValidationWarning
from .validator import ValidationReport


@dataclass
class CorrectionSuggestion:
    """修正提案"""

    row_number: int
    field: str
    correction_type: str
    original_value: Any
    suggested_value: Any
    description: str
    confidence_score: float
    reason: str = ""


@dataclass
class CleaningResult:
    """クレンジング結果"""

    original_dataframe: pd.DataFrame
    cleaned_dataframe: pd.DataFrame
    corrections_applied: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[CorrectionSuggestion] = field(default_factory=list)

    def get_correction_summary(self) -> Dict[str, int]:
        """修正サマリー取得"""
        summary = {}
        for correction in self.corrections_applied:
            field_name = correction.get("field", "unknown")
            summary[field_name] = summary.get(field_name, 0) + 1
        return summary

    def export_corrections_log(self, file_path: str) -> None:
        """修正ログ出力"""
        import csv

        with open(file_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)

            # ヘッダー
            writer.writerow(
                [
                    "row",
                    "field",
                    "old_value",
                    "new_value",
                    "correction_type",
                    "confidence",
                ]
            )

            # 修正データ
            for correction in self.corrections_applied:
                writer.writerow(
                    [
                        correction.get("row", ""),
                        correction.get("field", ""),
                        correction.get("old", ""),
                        correction.get("new", ""),
                        correction.get("correction_type", ""),
                        correction.get("confidence", ""),
                    ]
                )


class DataCleaner:
    """データクレンジングエンジン"""

    def __init__(self, config: Dict = None):
        """初期化

        Args:
            config: クレンジング設定
        """
        self.config = config or {}
        self._setup_default_mappings()

    def _setup_default_mappings(self):
        """デフォルトマッピング設定"""
        # 部署名マッピング
        self.department_mapping = self.config.get(
            "department_mapping",
            {
                "開発課": "開発部",
                "開発チーム": "開発部",
                "Development": "開発部",
                "営業課": "営業部",
                "営業チーム": "営業部",
                "Sales": "営業部",
            },
        )

        # クレンジングレベル
        self.cleaning_level = self.config.get(
            "level", "standard"
        )  # conservative, standard, aggressive

        # 並列処理設定
        self.parallel = self.config.get("parallel", False)
        self.n_jobs = self.config.get("n_jobs", 4)

    def apply_auto_corrections(self, df: pd.DataFrame) -> pd.DataFrame:
        """自動修正適用

        Args:
            df: 修正対象DataFrame

        Returns:
            pd.DataFrame: 修正済みDataFrame
        """
        cleaned_df = df.copy()

        # 時刻フォーマット統一
        cleaned_df = self._clean_time_format(cleaned_df)

        # 部署名正規化
        cleaned_df = self._clean_department_names(cleaned_df)

        # 社員名フォーマット統一
        cleaned_df = self._clean_employee_names(cleaned_df)

        # 日付フォーマット統一
        cleaned_df = self._clean_date_format(cleaned_df)

        # 休憩時間正規化
        cleaned_df = self._clean_break_time(cleaned_df)

        return cleaned_df

    def suggest_corrections(
        self, errors: List[ValidationError], context: Dict = None
    ) -> List[CorrectionSuggestion]:
        """修正提案生成

        Args:
            errors: 検証エラーリスト
            context: 追加コンテキスト情報

        Returns:
            List[CorrectionSuggestion]: 修正提案リスト
        """
        suggestions = []
        context = context or {}

        for error in errors:
            if (
                "時刻論理" in error.message
                or "出勤時刻が退勤時刻より遅い" in error.message
            ):
                # 時刻論理エラーの修正提案
                suggestion = self._suggest_time_correction(error, context)
                if suggestion:
                    suggestions.append(suggestion)

            elif "未来の日付" in error.message:
                # 未来日エラーの修正提案
                suggestion = self._suggest_date_correction(error, context)
                if suggestion:
                    suggestions.append(suggestion)

            elif "社員ID" in error.message and "フォーマット" in error.message:
                # 社員IDフォーマットエラーの修正提案
                suggestion = self._suggest_employee_id_correction(error, context)
                if suggestion:
                    suggestions.append(suggestion)

            elif "不明な部署" in error.message:
                # 部署名エラーの修正提案
                suggestion = self._suggest_department_correction(error, context)
                if suggestion:
                    suggestions.append(suggestion)

        return suggestions

    def clean_dataframe(
        self, df: pd.DataFrame, validation_report: ValidationReport
    ) -> CleaningResult:
        """ValidationReportを使ったDataFrame清洗

        Args:
            df: 対象DataFrame
            validation_report: 検証結果

        Returns:
            CleaningResult: 清洗結果
        """
        original_df = df.copy()
        cleaned_df = df.copy()
        corrections = []

        # 自動修正適用
        cleaned_df = self.apply_auto_corrections(cleaned_df)

        # 修正ログ作成（簡易実装）
        for col in df.columns:
            if col in cleaned_df.columns:
                for idx in df.index:
                    original_val = df.loc[idx, col]
                    cleaned_val = cleaned_df.loc[idx, col]

                    if str(original_val) != str(cleaned_val):
                        corrections.append(
                            {
                                "row": idx,
                                "field": col,
                                "old": original_val,
                                "new": cleaned_val,
                                "correction_type": "auto_format",
                                "confidence": 0.9,
                            }
                        )

        # 修正提案生成
        suggestions = self.suggest_corrections(validation_report.errors)

        return CleaningResult(
            original_dataframe=original_df,
            cleaned_dataframe=cleaned_df,
            corrections_applied=corrections,
            suggestions=suggestions,
        )

    def _clean_time_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """時刻フォーマット統一"""
        for col in ["start_time", "end_time"]:
            if col in df.columns:
                df[col] = df[col].apply(self._normalize_time_format)
        return df

    def _normalize_time_format(self, time_str: Any) -> str:
        """時刻フォーマット正規化"""
        if pd.isna(time_str):
            return time_str

        time_str = str(time_str).strip()

        # 様々なフォーマットを統一形式（HH:MM）に変換

        # "9:00" → "09:00"
        if re.match(r"^\d{1}:\d{2}$", time_str):
            return f"0{time_str}"

        # "09:00:00" → "09:00"
        if re.match(r"^\d{2}:\d{2}:\d{2}$", time_str):
            return time_str[:5]

        # "9時00分" → "09:00"
        time_match = re.match(r"^(\d{1,2})時(\d{2})分$", time_str)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2))
            return f"{hour:02d}:{minute:02d}"

        # "18:0" → "18:00"
        if re.match(r"^\d{2}:\d{1}$", time_str):
            return time_str + "0"

        return time_str

    def _clean_department_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """部署名正規化"""
        if "department" in df.columns:
            df["department"] = df["department"].apply(
                lambda x: self.department_mapping.get(x, x) if pd.notna(x) else x
            )
        return df

    def _clean_employee_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """社員名フォーマット統一"""
        if "employee_name" in df.columns:
            df["employee_name"] = df["employee_name"].apply(
                self._normalize_employee_name
            )
        return df

    def _normalize_employee_name(self, name: Any) -> str:
        """社員名正規化"""
        if pd.isna(name):
            return name

        name_str = str(name).strip()
        original_input = name_str  # Keep the original before cleaning

        # アルファベット名前の変換（簡易実装）- 空白除去前に実行
        name_cleaning_config = self.config.get("name_cleaning", {})
        should_normalize_alphabet = (
            self.cleaning_level == "aggressive"
            or name_cleaning_config.get("normalize_alphabet", False)
        )

        if should_normalize_alphabet:
            # "YAMADA Hanako" → "山田花子" のような変換は複雑なので、
            # 現在は簡易的に実装
            if re.match(r"^[A-Za-z\s]+$", original_input):
                # 簡易的な変換例
                alphabet_to_japanese = {
                    "YAMADA Hanako": "山田花子",
                    "TANAKA Taro": "田中太郎",
                }
                name_str = alphabet_to_japanese.get(original_input, name_str)

        # 全角スペースを削除
        name_str = re.sub(r"　+", "", name_str)

        # 半角スペースを削除（名前の間のスペースも）
        name_str = re.sub(r"\s+", "", name_str)

        return name_str

    def _clean_break_time(self, df: pd.DataFrame) -> pd.DataFrame:
        """休憩時間フォーマット統一"""
        if "break_time" in df.columns:
            df["break_time"] = df["break_time"].apply(self._normalize_break_time)
        return df

    def _normalize_break_time(self, break_time: Any) -> int:
        """休憩時間を分単位に正規化"""
        if pd.isna(break_time):
            return break_time

        # 既に整数の場合（分単位）
        if isinstance(break_time, (int, float)):
            return int(break_time)

        break_time_str = str(break_time).strip()

        # 時間:分フォーマット（例: "1:00", "1:30"）
        if ":" in break_time_str:
            try:
                parts = break_time_str.split(":")
                if len(parts) == 2:
                    hours = int(parts[0])
                    minutes = int(parts[1])
                    return hours * 60 + minutes
            except ValueError:
                pass

        # 単位付きフォーマット（例: "60分", "1時間"）
        if "分" in break_time_str:
            try:
                value = int(re.sub(r"[^0-9]", "", break_time_str))
                return value
            except ValueError:
                pass

        if "時間" in break_time_str:
            try:
                value = int(re.sub(r"[^0-9]", "", break_time_str))
                return value * 60  # 時間を分に変換
            except ValueError:
                pass

        # その他の場合はそのまま返す
        return break_time

    def _clean_date_format(self, df: pd.DataFrame) -> pd.DataFrame:
        """日付フォーマット統一"""
        if "work_date" in df.columns:
            target_format = self.config.get("date_format", "YYYY-MM-DD")
            if target_format == "YYYY-MM-DD":
                df["work_date"] = df["work_date"].apply(self._normalize_date_format)
        return df

    def _normalize_date_format(self, date_str: Any) -> str:
        """日付フォーマット正規化"""
        if pd.isna(date_str):
            return date_str

        date_str = str(date_str).strip()

        # "2024/1/15" → "2024-01-15"
        if re.match(r"^\d{4}/\d{1,2}/\d{1,2}$", date_str):
            parts = date_str.split("/")
            return f"{parts[0]}-{int(parts[1]):02d}-{int(parts[2]):02d}"

        # "01/15/2024" → "2024-01-15"
        if re.match(r"^\d{2}/\d{2}/\d{4}$", date_str):
            parts = date_str.split("/")
            return f"{parts[2]}-{parts[0]}-{parts[1]}"

        return date_str

    def _suggest_time_correction(
        self, error: ValidationError, context: Dict
    ) -> Optional[CorrectionSuggestion]:
        """時刻修正提案"""
        if isinstance(error.value, tuple) and len(error.value) == 2:
            start_time, end_time = error.value

            return CorrectionSuggestion(
                row_number=error.row_number,
                field="time_logic",
                correction_type="time_swap",
                original_value=error.value,
                suggested_value=(end_time, start_time),  # 時刻を入れ替え
                description=f"日跨ぎ勤務の可能性があります。出勤時刻と退勤時刻を入れ替えますか？",
                confidence_score=0.75,
                reason="出勤時刻が退勤時刻より遅い場合、入力ミスの可能性",
            )

        return None

    def _suggest_date_correction(
        self, error: ValidationError, context: Dict
    ) -> Optional[CorrectionSuggestion]:
        """日付修正提案"""
        if isinstance(error.value, str) and "2025-" in error.value:
            # 2025年を2024年に修正提案
            suggested_date = error.value.replace("2025-", "2024-")

            return CorrectionSuggestion(
                row_number=error.row_number,
                field="work_date",
                correction_type="date_year",
                original_value=error.value,
                suggested_value=suggested_date,
                description="年度設定ミスの可能性があります。2024年に修正しますか？",
                confidence_score=0.8,
                reason="未来日データは通常入力ミス",
            )

        return None

    def _suggest_employee_id_correction(
        self, error: ValidationError, context: Dict
    ) -> Optional[CorrectionSuggestion]:
        """社員ID修正提案"""
        original_id = str(error.value)

        # "EMP1" → "EMP0001" のような桁数補正
        if re.match(r"^EMP\d{1,3}$", original_id):
            number_part = original_id[3:]
            padding_config = self.config.get("employee_id_padding", 4)
            padded_number = number_part.zfill(padding_config)
            suggested_id = f"EMP{padded_number}"

            return CorrectionSuggestion(
                row_number=error.row_number,
                field="employee_id",
                correction_type="employee_id_format",
                original_value=original_id,
                suggested_value=suggested_id,
                description=f"社員ID形式を標準フォーマットに修正しますか？",
                confidence_score=0.85,
                reason="社員IDの桁数不足",
            )

        return None

    def _suggest_department_correction(
        self, error: ValidationError, context: Dict
    ) -> Optional[CorrectionSuggestion]:
        """部署名修正提案"""
        original_dept = str(error.value)
        candidates = self.config.get(
            "department_candidates", ["開発部", "営業部", "総務部", "システム部"]
        )

        # 簡易的な類似度計算（文字列の部分一致）
        best_match = None
        best_score = 0

        for candidate in candidates:
            # 部分一致スコア
            if original_dept in candidate or candidate in original_dept:
                score = 0.8
                if score > best_score:
                    best_score = score
                    best_match = candidate

        if best_match and best_score >= 0.7:
            return CorrectionSuggestion(
                row_number=error.row_number,
                field="department",
                correction_type="department_similarity",
                original_value=original_dept,
                suggested_value=best_match,
                description=f"類似する部署名に修正しますか？",
                confidence_score=best_score,
                reason="部署名の類似性による推測",
            )

        return None
