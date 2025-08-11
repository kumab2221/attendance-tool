"""CSV出力機能のテスト - Red Phase"""

import pytest
from pathlib import Path
from datetime import date
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os

# テスト対象モジュール
from attendance_tool.output.csv_exporter import CSVExporter, ExportResult
from attendance_tool.output.models import CSVExportConfig

from tests.fixtures.csv_export.standard_employee_data import (
    STANDARD_EMPLOYEE_DATA,
    STANDARD_DEPARTMENT_DATA,
    EDGE_CASE_DATA,
)


class TestCSVExporter:
    """CSVExporter クラスのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.exporter = CSVExporter()

    def teardown_method(self):
        """テストクリーンアップ"""
        # 一時ディレクトリをクリーンアップ
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_export_employee_report_normal_case(self):
        """TC-301-001: 社員別CSVレポート出力（正常ケース）"""
        # Given
        employee_data = STANDARD_EMPLOYEE_DATA
        output_path = self.temp_dir
        year = 2024
        month = 1

        # When
        result = self.exporter.export_employee_report(
            employee_data, output_path, year, month
        )

        # Then
        print(f"Result: {result}")
        print(f"Errors: {result.errors}")
        print(f"File path: {result.file_path}")
        print(f"Expected file: {output_path / 'employee_report_2024_01.csv'}")

        assert result.success is True
        assert result.record_count == 3

        # 実際に生成されたファイルを使用
        expected_file = result.file_path
        assert expected_file.exists()

        # CSVファイルの内容確認
        with open(expected_file, "r", encoding="utf-8-sig") as f:
            content = f.read()
            assert "社員ID" in content
            assert "EMP001" in content
            assert "田中太郎" in content
            assert "開発部" in content

    def test_export_department_report_normal_case(self):
        """TC-301-002: 部門別CSVレポート出力（正常ケース）"""
        # Given
        department_data = STANDARD_DEPARTMENT_DATA
        output_path = self.temp_dir
        year = 2024
        month = 1

        # When
        result = self.exporter.export_department_report(
            department_data, output_path, year, month
        )

        # Then
        assert result.success is True
        assert result.record_count == 2

        # 実際に生成されたファイルを使用
        expected_file = result.file_path
        assert expected_file.exists()

    def test_export_with_empty_dataset(self):
        """TC-301-101: 空データセット"""
        # Given
        empty_data = []
        output_path = self.temp_dir
        year = 2024
        month = 1

        # When
        result = self.exporter.export_employee_report(
            empty_data, output_path, year, month
        )

        # Then
        assert result.success is True
        assert result.record_count == 0

        # 実際に生成されたファイルを使用
        expected_file = result.file_path
        assert expected_file.exists()

        # ヘッダーのみのファイルかチェック
        with open(expected_file, "r", encoding="utf-8-sig") as f:
            lines = f.readlines()
            assert len(lines) == 1  # ヘッダー行のみ
            assert "社員ID" in lines[0]

    def test_export_nonexistent_directory(self):
        """TC-301-102: 出力ディレクトリが存在しない"""
        # Given
        nonexistent_path = self.temp_dir / "nonexistent" / "path"
        employee_data = STANDARD_EMPLOYEE_DATA[:1]  # 1件のみ

        # When
        result = self.exporter.export_employee_report(
            employee_data, nonexistent_path, 2024, 1
        )

        # Then
        assert result.success is True
        assert nonexistent_path.exists()  # ディレクトリが自動作成される

        # 実際に生成されたファイルを使用
        expected_file = result.file_path
        assert expected_file.exists()

    def test_export_permission_error(self):
        """TC-301-103: 書き込み権限なし"""
        # Given
        employee_data = STANDARD_EMPLOYEE_DATA[:1]

        with patch(
            "pandas.DataFrame.to_csv", side_effect=PermissionError("Permission denied")
        ):
            # When
            result = self.exporter.export_employee_report(
                employee_data, self.temp_dir, 2024, 1
            )

            # Then
            assert result.success is False
            assert "Permission denied" in str(result.errors)

    @patch("pandas.DataFrame.to_csv")
    def test_export_disk_full_error(self, mock_to_csv):
        """TC-301-104: ディスク容量不足シミュレーション"""
        # Given
        mock_to_csv.side_effect = OSError("No space left on device")
        employee_data = STANDARD_EMPLOYEE_DATA[:1]

        # When
        result = self.exporter.export_employee_report(
            employee_data, self.temp_dir, 2024, 1
        )

        # Then
        assert result.success is False
        assert "No space left on device" in str(result.errors)

    def test_export_with_invalid_data(self):
        """TC-301-105: 不正なデータ形式"""
        # Given
        from attendance_tool.calculation.summary import AttendanceSummary

        invalid_data = [
            AttendanceSummary(
                employee_id="",  # 空のID
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                total_days=31,
                business_days=22,
                employee_name="",  # 空の名前
                department="",  # 空の部署名
                total_work_minutes=-100,  # 負の値（実際は不正だが、処理は継続）
                attendance_days=22,
                tardiness_count=0,
                early_leave_count=0,
                paid_leave_days=0,
            )
        ]

        # When
        result = self.exporter.export_employee_report(
            invalid_data, self.temp_dir, 2024, 1
        )

        # Then
        # データバリデーションが実行され、デフォルト値で処理される
        assert result.success is True  # デフォルト値で成功

        # ファイルの存在確認
        expected_file = result.file_path
        assert expected_file.exists()

        # ファイル内容確認（デフォルト値が使用されている）
        with open(expected_file, "r", encoding="utf-8-sig") as f:
            content = f.read()
            assert "UNKNOWN" in content  # デフォルトID
            assert "Unknown User" in content  # デフォルト名前
            assert "未設定" in content  # デフォルト部署

    def test_export_special_characters(self):
        """TC-301-204: 特殊文字を含むデータ"""
        # Given
        special_char_data = EDGE_CASE_DATA[1:2]  # 特殊文字データのみ

        # When
        result = self.exporter.export_employee_report(
            special_char_data, self.temp_dir, 2024, 1
        )

        # Then
        assert result.success is True

        # 実際に生成されたファイルを使用
        expected_file = result.file_path
        assert expected_file.exists()

        # CSVファイルの内容確認（特殊文字が適切にエスケープされている）
        with open(expected_file, "r", encoding="utf-8-sig") as f:
            content = f.read()
            assert "EDGE002" in content
            # クォートやエスケープが正しく処理されている
            assert '"田中,""太郎""\n課長"' in content

    def test_export_large_dataset_performance(self):
        """TC-301-202: 大容量データセットの性能テスト"""
        # Given: 100件のデータを生成（テストを軽量化）
        from attendance_tool.calculation.summary import AttendanceSummary

        large_dataset = []
        for i in range(100):
            data = AttendanceSummary(
                employee_id=f"EMP{i:04d}",
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                total_days=31,
                business_days=22,
                employee_name=f"テストユーザー{i}",
                department="テスト部",
                attendance_days=20,
                attendance_rate=90.9,
                total_work_minutes=9600,
                scheduled_overtime_minutes=1200,
                tardiness_count=0,
                early_leave_count=0,
                paid_leave_days=0,
            )
            large_dataset.append(data)

        # When
        import time

        start_time = time.time()

        result = self.exporter.export_employee_report(
            large_dataset, self.temp_dir, 2024, 1
        )

        end_time = time.time()
        processing_time = end_time - start_time

        # Then
        assert result.success is True
        assert result.record_count == 100
        assert processing_time < 10.0  # 10秒以内

        # 実際に生成されたファイルを使用
        expected_file = result.file_path
        assert expected_file.exists()

        # ファイルサイズチェック
        file_size = expected_file.stat().st_size
        assert file_size > 0

    @patch("attendance_tool.utils.config.ConfigManager.get_csv_format")
    def test_export_with_config_error(self, mock_get_config):
        """TC-301-106: 設定ファイル読み込みエラー"""
        # Given
        mock_get_config.side_effect = FileNotFoundError("Config file not found")
        employee_data = STANDARD_EMPLOYEE_DATA[:1]

        # When
        result = self.exporter.export_employee_report(
            employee_data, self.temp_dir, 2024, 1
        )

        # Then
        # デフォルト設定が使用されて処理が継続される
        assert result.success is True

        # ファイルが生成されていることを確認
        expected_file = result.file_path
        assert expected_file.exists()


class TestExportResult:
    """ExportResult データクラスのテスト"""

    def test_export_result_creation(self):
        """ExportResult の基本的な作成テスト"""
        # Given & When
        result = ExportResult(
            success=True,
            file_path=Path("/tmp/test.csv"),
            record_count=100,
            file_size=1024,
            processing_time=1.5,
            errors=[],
            warnings=["設定ファイルが見つかりません"],
        )

        # Then
        assert result.success is True
        assert result.record_count == 100
        assert result.file_size == 1024
        assert result.processing_time == 1.5
        assert len(result.warnings) == 1


class TestCSVExportIntegration:
    """CSV出力の統合テスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.exporter = CSVExporter()

    def teardown_method(self):
        """テストクリーンアップ"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_multiple_reports_export(self):
        """TC-301-301: 3種類レポート同時出力"""
        # Given
        employee_data = STANDARD_EMPLOYEE_DATA
        department_data = STANDARD_DEPARTMENT_DATA
        # daily_detail_data = []  # 今回は未実装

        # When
        employee_result = self.exporter.export_employee_report(
            employee_data, self.temp_dir, 2024, 1
        )
        department_result = self.exporter.export_department_report(
            department_data, self.temp_dir, 2024, 1
        )

        # Then
        assert employee_result.success is True
        assert department_result.success is True

        # 両方のファイルが存在することを確認
        assert employee_result.file_path.exists()
        assert department_result.file_path.exists()


# Red Phase: これらのテストは現在すべて失敗する（実装がないため）
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
