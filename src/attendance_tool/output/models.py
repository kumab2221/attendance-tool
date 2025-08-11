"""CSV出力関連のデータモデル"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ExportResult:
    """CSV出力結果"""

    success: bool
    file_path: Path
    record_count: int
    file_size: int = 0
    processing_time: float = 0.0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(self, error: str) -> None:
        """エラーを追加"""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """警告を追加"""
        self.warnings.append(warning)


@dataclass
class CSVColumnConfig:
    """CSV列設定"""

    name: str
    field: str
    format: Optional[str] = None


@dataclass
class CSVExportConfig:
    """CSV出力設定"""

    filename_pattern: str
    encoding: str = "utf-8-sig"
    delimiter: str = ","
    columns: List[CSVColumnConfig] = field(default_factory=list)

    def get_filename(self, year: int, month: int) -> str:
        """ファイル名を生成"""
        return self.filename_pattern.format(
            year=year, month=month, month_02d=f"{month:02d}"
        )


@dataclass
class ReportMetadata:
    """レポートメタデータ"""

    report_type: str
    generation_time: datetime
    data_period_start: str
    data_period_end: str
    total_records: int
    data_source: str = "勤怠管理システム"


@dataclass
class ExcelExportConfig:
    """Excel出力設定"""

    filename_pattern: str
    worksheet_names: Dict[str, str] = field(default_factory=dict)
    header_style: Dict[str, Any] = field(default_factory=dict)
    cell_formats: Dict[str, str] = field(default_factory=dict)
    conditional_formats: List["ConditionalFormat"] = field(default_factory=list)
    chart_settings: Dict[str, Any] = field(default_factory=dict)

    def get_filename(self, year: int, month: int) -> str:
        """ファイル名を生成"""
        return self.filename_pattern.format(
            year=year, month=month, month_02d=f"{month:02d}"
        )


@dataclass
class ConditionalFormat:
    """条件付き書式設定"""

    column: str
    condition_type: str
    values: List[Any]
    format_style: Dict[str, Any]
