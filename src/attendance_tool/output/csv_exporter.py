"""CSV出力機能 - Green Phase 最小実装"""

import logging
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import pandas as pd

from .models import ExportResult, CSVExportConfig, CSVColumnConfig
from ..utils.config import ConfigManager
from ..calculation.summary import AttendanceSummary
from ..calculation.department_summary import DepartmentSummary


logger = logging.getLogger(__name__)


class CSVExporter:
    """CSV形式でのレポート出力機能"""

    def __init__(self):
        """CSVExporter初期化"""
        self.config_manager = ConfigManager()
        self._load_csv_config()

    def _load_csv_config(self) -> None:
        """CSV設定の読み込み"""
        try:
            csv_format_config = self.config_manager.get_csv_format()
            self.employee_config = self._build_export_config(
                csv_format_config.get("output", {}).get("employee_report", {})
            )
            self.department_config = self._build_export_config(
                csv_format_config.get("output", {}).get("department_report", {})
            )
            self.daily_config = self._build_export_config(
                csv_format_config.get("output", {}).get("daily_detail_report", {})
            )
        except Exception as e:
            logger.warning(
                f"CSV設定の読み込みに失敗しました。デフォルト設定を使用します: {e}"
            )
            self._use_default_config()

    def _build_export_config(self, config_dict: Dict[str, Any]) -> CSVExportConfig:
        """設定辞書からCSVExportConfigを構築"""
        columns = []
        for col_config in config_dict.get("columns", []):
            columns.append(
                CSVColumnConfig(
                    name=col_config.get("name", ""),
                    field=col_config.get("field", ""),
                    format=col_config.get("format"),
                )
            )

        return CSVExportConfig(
            filename_pattern=config_dict.get(
                "filename_pattern", "report_{year}_{month:02d}.csv"
            ),
            encoding=config_dict.get("encoding", "utf-8-sig"),
            delimiter=config_dict.get("delimiter", ","),
            columns=columns,
        )

    def _use_default_config(self) -> None:
        """デフォルト設定を使用"""
        # 社員別レポートのデフォルト設定
        employee_columns = [
            CSVColumnConfig("社員ID", "employee_id"),
            CSVColumnConfig("氏名", "employee_name"),
            CSVColumnConfig("部署", "department"),
            CSVColumnConfig("対象年月", "target_period"),
            CSVColumnConfig("出勤日数", "attendance_days"),
            CSVColumnConfig("欠勤日数", "absence_days"),
            CSVColumnConfig("遅刻回数", "tardiness_count"),
            CSVColumnConfig("早退回数", "early_leave_count"),
            CSVColumnConfig("総労働時間", "total_work_hours", "%.2f"),
            CSVColumnConfig("所定労働時間", "standard_work_hours", "%.2f"),
            CSVColumnConfig("残業時間", "overtime_hours", "%.2f"),
            CSVColumnConfig("深夜労働時間", "late_night_hours", "%.2f"),
            CSVColumnConfig("有給取得日数", "paid_leave_days", "%.1f"),
        ]

        self.employee_config = CSVExportConfig(
            filename_pattern="employee_report_{year}_{month_02d}.csv",
            columns=employee_columns,
        )

        # 部門別レポートのデフォルト設定
        department_columns = [
            CSVColumnConfig("部署", "department"),
            CSVColumnConfig("対象年月", "target_period"),
            CSVColumnConfig("所属人数", "employee_count"),
            CSVColumnConfig("総出勤日数", "total_work_days"),
            CSVColumnConfig("総欠勤日数", "total_absent_days"),
            CSVColumnConfig("総労働時間", "total_work_hours", "%.2f"),
            CSVColumnConfig("総残業時間", "total_overtime_hours", "%.2f"),
            CSVColumnConfig("平均出勤率", "average_attendance_rate", "%.1f%%"),
        ]

        self.department_config = CSVExportConfig(
            filename_pattern="department_report_{year}_{month_02d}.csv",
            columns=department_columns,
        )

        # 日別詳細レポートのデフォルト設定（簡易版）
        self.daily_config = CSVExportConfig(
            filename_pattern="daily_detail_{year}_{month_02d}.csv",
            columns=[],  # 今回は実装しない
        )

    def export_employee_report(
        self,
        summaries: List[AttendanceSummary],
        output_path: Path,
        year: int,
        month: int,
    ) -> ExportResult:
        """社員別CSVレポート出力"""
        start_time = time.time()

        try:
            # 出力ディレクトリの作成
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)

            # ファイル名生成
            filename = self.employee_config.get_filename(year, month)
            file_path = output_path / filename

            # データの変換
            data_rows = []
            for summary in summaries:
                row_data = self._convert_employee_summary_to_row(summary, year, month)
                data_rows.append(row_data)

            # DataFrame作成
            if data_rows:
                df = pd.DataFrame(data_rows)
            else:
                # 空データセットの場合はヘッダーのみ
                column_names = [col.name for col in self.employee_config.columns]
                df = pd.DataFrame(columns=column_names)

            # CSV出力
            df.to_csv(
                file_path,
                index=False,
                encoding=self.employee_config.encoding,
                sep=self.employee_config.delimiter,
                quoting=1,  # QUOTE_ALL で特殊文字を適切に処理
            )

            # ファイルサイズ取得
            file_size = file_path.stat().st_size if file_path.exists() else 0
            processing_time = time.time() - start_time

            result = ExportResult(
                success=True,
                file_path=file_path,
                record_count=len(summaries),
                file_size=file_size,
                processing_time=processing_time,
            )

            logger.info(
                f"社員別レポートを出力しました: {file_path} ({len(summaries)}件)"
            )
            return result

        except Exception as e:
            return self._handle_export_error(
                e,
                output_path / self.employee_config.get_filename(year, month),
                len(summaries),
                "社員別レポート出力",
            )

    def export_department_report(
        self,
        summaries: List[DepartmentSummary],
        output_path: Path,
        year: int,
        month: int,
    ) -> ExportResult:
        """部門別CSVレポート出力"""
        start_time = time.time()

        try:
            # 出力ディレクトリの作成
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)

            # ファイル名生成
            filename = self.department_config.get_filename(year, month)
            file_path = output_path / filename

            # データの変換
            data_rows = []
            for summary in summaries:
                row_data = self._convert_department_summary_to_row(summary, year, month)
                data_rows.append(row_data)

            # DataFrame作成
            if data_rows:
                df = pd.DataFrame(data_rows)
            else:
                # 空データセットの場合はヘッダーのみ
                column_names = [col.name for col in self.department_config.columns]
                df = pd.DataFrame(columns=column_names)

            # CSV出力
            df.to_csv(
                file_path,
                index=False,
                encoding=self.department_config.encoding,
                sep=self.department_config.delimiter,
                quoting=1,
            )

            # ファイルサイズ取得
            file_size = file_path.stat().st_size if file_path.exists() else 0
            processing_time = time.time() - start_time

            result = ExportResult(
                success=True,
                file_path=file_path,
                record_count=len(summaries),
                file_size=file_size,
                processing_time=processing_time,
            )

            logger.info(
                f"部門別レポートを出力しました: {file_path} ({len(summaries)}件)"
            )
            return result

        except Exception as e:
            return self._handle_export_error(
                e,
                output_path / self.department_config.get_filename(year, month),
                len(summaries),
                "部門別レポート出力",
            )

    def export_daily_detail_report(
        self,
        records: List[Any],  # AttendanceRecordが実装されたら型を変更
        output_path: Path,
        year: int,
        month: int,
    ) -> ExportResult:
        """日別詳細CSVレポート出力（スタブ実装）"""
        # Green Phase: 基本構造のみ実装
        logger.info("日別詳細レポート出力は未実装です")

        file_path = output_path / self.daily_config.get_filename(year, month)
        result = ExportResult(success=True, file_path=file_path, record_count=0)
        result.add_warning("日別詳細レポート機能は未実装です")
        return result

    def _safe_get_value(self, value: Any, default: Any) -> Any:
        """安全な値の取得（None や空文字列の場合はデフォルト値を返す）"""
        if value is None or (isinstance(value, str) and not value.strip()):
            return default
        return value

    def _minutes_to_hours(self, minutes: int) -> float:
        """分を時間に換算"""
        return minutes / 60.0

    def _calculate_total_overtime_hours(self, summary: AttendanceSummary) -> float:
        """総残業時間を計算（分→時間）"""
        total_overtime_minutes = getattr(
            summary, "scheduled_overtime_minutes", 0
        ) + getattr(summary, "legal_overtime_minutes", 0)
        return self._minutes_to_hours(total_overtime_minutes)

    def _format_period_string(self, year: int, month: int) -> str:
        """期間文字列をフォーマット"""
        return f"{year}-{month:02d}"

    def _estimate_total_work_days(self, summary: DepartmentSummary) -> int:
        """総出勤日数を推定（平均労働時間から逆算）"""
        if summary.average_work_minutes <= 0:
            return 0
        # 8時間=480分で割算して出勤日数を推定
        return int(summary.employee_count * summary.average_work_minutes / 480)

    def _estimate_total_absent_days(
        self, summary: DepartmentSummary, total_work_days: int
    ) -> int:
        """総欠勤日数を推定"""
        # 22営業日と仮定して欠勤日数を推定
        expected_total_days = summary.employee_count * 22
        return max(0, expected_total_days - total_work_days)

    def _handle_export_error(
        self, error: Exception, file_path: Path, record_count: int, operation: str
    ) -> ExportResult:
        """CSV出力エラーの統一処理"""
        if isinstance(error, PermissionError):
            logger.error(f"{operation}でファイル書き込み権限エラー: {error}")
            error_msg = f"Permission denied: {str(error)}"
        elif isinstance(error, OSError):
            logger.error(f"{operation}でファイルシステムエラー: {error}")
            error_msg = f"OS Error: {str(error)}"
        else:
            logger.error(f"{operation}中に予期しないエラー: {error}")
            error_msg = f"Unexpected error: {str(error)}"

        result = ExportResult(
            success=False, file_path=file_path, record_count=record_count
        )
        result.add_error(error_msg)
        return result

    def _convert_employee_summary_to_row(
        self, summary: AttendanceSummary, year: int, month: int
    ) -> Dict[str, Any]:
        """AttendanceSummaryをCSV行データに変換"""
        # データバリデーション関数を使用
        employee_id = self._safe_get_value(summary.employee_id, "UNKNOWN")
        employee_name = self._safe_get_value(summary.employee_name, "Unknown User")
        department = self._safe_get_value(summary.department, "未設定")

        # 欠勤日数計算
        absence_days = max(0, summary.business_days - summary.attendance_days)

        # 時間換算関数を使用
        total_work_hours = self._minutes_to_hours(summary.total_work_minutes)
        overtime_hours = self._calculate_total_overtime_hours(summary)

        # 標準労働時間（仮定：8時間/日）
        standard_work_hours = summary.attendance_days * 8.0

        return {
            "社員ID": employee_id,
            "氏名": employee_name,
            "部署": department,
            "対象年月": self._format_period_string(year, month),
            "出勤日数": summary.attendance_days,
            "欠勤日数": absence_days,
            "遅刻回数": summary.tardiness_count,
            "早退回数": summary.early_leave_count,
            "総労働時間": f"{total_work_hours:.2f}",
            "所定労働時間": f"{standard_work_hours:.2f}",
            "残業時間": f"{overtime_hours:.2f}",
            "深夜労働時間": f"{getattr(summary, 'late_night_work_minutes', 0) / 60.0:.2f}",
            "有給取得日数": f"{summary.paid_leave_days:.1f}",
        }

    def _convert_department_summary_to_row(
        self, summary: DepartmentSummary, year: int, month: int
    ) -> Dict[str, Any]:
        """DepartmentSummaryをCSV行データに変換"""
        department_name = self._safe_get_value(summary.department_name, "未設定部門")

        # 時間換算（ヘルパーメソッド使用）
        total_work_hours = self._minutes_to_hours(summary.total_work_minutes)
        total_overtime_hours = self._minutes_to_hours(summary.total_overtime_minutes)

        # 推定値計算
        total_work_days = self._estimate_total_work_days(summary)
        total_absent_days = self._estimate_total_absent_days(summary, total_work_days)

        return {
            "部署": department_name,
            "対象年月": self._format_period_string(year, month),
            "所属人数": summary.employee_count,
            "総出勤日数": total_work_days,
            "総欠勤日数": total_absent_days,
            "総労働時間": f"{total_work_hours:.2f}",
            "総残業時間": f"{total_overtime_hours:.2f}",
            "平均出勤率": f"{summary.attendance_rate:.1f}%",
        }
