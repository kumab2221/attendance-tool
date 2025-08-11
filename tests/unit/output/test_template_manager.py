"""テンプレート管理機能のテスト - TASK-303"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import date

from attendance_tool.output.template_manager import TemplateManager
from attendance_tool.output.models import ExportResult
from attendance_tool.calculation.summary import AttendanceSummary
from attendance_tool.calculation.department_summary import DepartmentSummary


class TestTemplateManager:
    """TemplateManagerのテスト"""

    @pytest.fixture
    def temp_output_dir(self):
        """テスト用一時出力ディレクトリ"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def template_manager(self):
        """TemplateManagerインスタンス"""
        return TemplateManager()

    @pytest.fixture
    def sample_employee_data(self):
        """サンプル社員データ"""
        return [
            AttendanceSummary(
                employee_id="EMP001",
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                total_days=31,
                business_days=22,
                employee_name="田中太郎",
                department="営業部",
                attendance_days=22,
                tardiness_count=1,
                early_leave_count=0,
                total_work_minutes=10560,
                scheduled_overtime_minutes=960,
                legal_overtime_minutes=0,
                paid_leave_days=2,
            )
        ]

    @pytest.fixture
    def sample_department_data(self):
        """サンプル部門データ"""
        return [
            DepartmentSummary(
                department_code="SALES",
                department_name="営業部",
                period_start=date(2024, 1, 1),
                period_end=date(2024, 1, 31),
                employee_count=10,
                total_work_minutes=105600,
                total_overtime_minutes=9600,
                attendance_rate=95.5,
                average_work_minutes=528,
                violation_count=0,
                compliance_score=95.0,
            )
        ]

    def test_template_manager_initialization(self, template_manager):
        """テンプレートマネージャ初期化テスト"""
        assert template_manager is not None
        assert hasattr(template_manager, "template_config")
        assert hasattr(template_manager, "excel_exporter")
        assert hasattr(template_manager, "csv_exporter")

    def test_list_available_templates(self, template_manager):
        """利用可能テンプレート一覧テスト"""
        templates = template_manager.list_available_templates()
        assert isinstance(templates, list)
        assert "default" in templates

    def test_get_template_info(self, template_manager):
        """テンプレート情報取得テスト"""
        info = template_manager.get_template_info("default")
        assert isinstance(info, dict)

        # 存在しないテンプレート
        info = template_manager.get_template_info("nonexistent")
        assert info == {}

    def test_generate_templated_excel_report(
        self,
        template_manager,
        temp_output_dir,
        sample_employee_data,
        sample_department_data,
    ):
        """テンプレート付きExcelレポート生成テスト"""
        result = template_manager.generate_templated_report(
            employee_summaries=sample_employee_data,
            department_summaries=sample_department_data,
            output_path=temp_output_dir,
            year=2024,
            month=1,
            template_name="default",
            output_format="excel",
            include_comparison=False,
            include_charts=True,
        )

        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.file_path.exists()
        assert result.file_path.suffix == ".xlsx"
        assert result.record_count == len(sample_employee_data)

    def test_generate_templated_csv_report(
        self,
        template_manager,
        temp_output_dir,
        sample_employee_data,
        sample_department_data,
    ):
        """テンプレート付きCSVレポート生成テスト"""
        result = template_manager.generate_templated_report(
            employee_summaries=sample_employee_data,
            department_summaries=sample_department_data,
            output_path=temp_output_dir,
            year=2024,
            month=1,
            template_name="default",
            output_format="csv",
            include_comparison=False,
        )

        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.file_path.exists()
        assert result.file_path.suffix == ".csv"

    def test_generate_report_with_comparison(
        self,
        template_manager,
        temp_output_dir,
        sample_employee_data,
        sample_department_data,
    ):
        """比較機能付きレポート生成テスト"""
        result = template_manager.generate_templated_report(
            employee_summaries=sample_employee_data,
            department_summaries=sample_department_data,
            output_path=temp_output_dir,
            year=2024,
            month=1,
            template_name="default",
            output_format="excel",
            include_comparison=True,
            include_charts=True,
        )

        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.file_path.exists()

    def test_generate_multi_month_report(
        self,
        template_manager,
        temp_output_dir,
        sample_employee_data,
        sample_department_data,
    ):
        """複数月統合レポート生成テスト"""

        # 複数月データの準備
        data_by_month = {
            "2024-01": {
                "employee_summaries": sample_employee_data,
                "department_summaries": sample_department_data,
            },
            "2024-02": {
                "employee_summaries": sample_employee_data,
                "department_summaries": sample_department_data,
            },
        }

        result = template_manager.generate_multi_month_report(
            data_by_month=data_by_month,
            output_path=temp_output_dir,
            start_year=2024,
            start_month=1,
            end_year=2024,
            end_month=2,
            template_name="default",
        )

        assert isinstance(result, ExportResult)
        assert result.success is True
        assert result.file_path.exists()

    def test_create_custom_template(self, template_manager):
        """カスタムテンプレート作成テスト"""

        custom_settings = {
            "excel": {
                "header_info": {
                    "company_name": "Test Company",
                    "report_title": "Test Report",
                }
            },
            "csv": {"header_format": {"include_company_info": True}},
        }

        success = template_manager.create_custom_template(
            template_name="test_template",
            settings=custom_settings,
            save_to_config=False,  # ファイル保存はスキップ
        )

        assert success is True

        # 作成したテンプレートが利用可能になっていることを確認
        templates = template_manager.list_available_templates()
        assert "test_template" in templates

        # テンプレート情報の取得
        info = template_manager.get_template_info("test_template")
        assert info == custom_settings

    def test_invalid_template_settings(self, template_manager):
        """無効なテンプレート設定テスト"""

        # 無効な設定（文字列）
        success = template_manager.create_custom_template(
            template_name="invalid_template",
            settings="invalid",  # 辞書ではない
            save_to_config=False,
        )

        assert success is False

    def test_unsupported_output_format(
        self,
        template_manager,
        temp_output_dir,
        sample_employee_data,
        sample_department_data,
    ):
        """サポートされていない出力形式テスト"""

        result = template_manager.generate_templated_report(
            employee_summaries=sample_employee_data,
            department_summaries=sample_department_data,
            output_path=temp_output_dir,
            year=2024,
            month=1,
            template_name="default",
            output_format="pdf",  # サポートされていない形式
            include_comparison=False,
        )

        assert isinstance(result, ExportResult)
        assert result.success is False
        assert "サポートされていない出力形式" in result.errors[0]

    def test_nonexistent_template(
        self,
        template_manager,
        temp_output_dir,
        sample_employee_data,
        sample_department_data,
    ):
        """存在しないテンプレート使用テスト"""

        result = template_manager.generate_templated_report(
            employee_summaries=sample_employee_data,
            department_summaries=sample_department_data,
            output_path=temp_output_dir,
            year=2024,
            month=1,
            template_name="nonexistent_template",
            output_format="excel",
            include_comparison=False,
        )

        # 存在しないテンプレートの場合はデフォルトにフォールバック
        assert isinstance(result, ExportResult)
        assert result.success is True  # デフォルトテンプレートで生成される

    def test_multi_month_limit_exceeded(self, template_manager, temp_output_dir):
        """複数月制限超過テスト"""

        # 13ヶ月のデータ（制限は12ヶ月）
        data_by_month = {}
        for i in range(13):
            month = (i % 12) + 1
            year = 2024 + (i // 12)
            data_by_month[f"{year}-{month:02d}"] = {
                "employee_summaries": [],
                "department_summaries": [],
            }

        result = template_manager.generate_multi_month_report(
            data_by_month=data_by_month,
            output_path=temp_output_dir,
            start_year=2024,
            start_month=1,
            end_year=2025,
            end_month=1,
            template_name="default",
        )

        assert isinstance(result, ExportResult)
        assert result.success is False
        assert "月数制限を超過" in result.errors[0]

    def test_comparison_data_generation(
        self, template_manager, sample_employee_data, sample_department_data
    ):
        """比較データ生成テスト"""

        comparison_data = template_manager._generate_comparison_data(
            sample_employee_data, sample_department_data, 2024, 1
        )

        assert isinstance(comparison_data, dict)
        assert "current_period" in comparison_data
        assert "previous_periods" in comparison_data
        assert "trends" in comparison_data
        assert comparison_data["current_period"] == "2024-01"
        assert len(comparison_data["previous_periods"]) == 3  # デフォルト設定

    def test_month_count_calculation(self, template_manager):
        """月数計算テスト"""

        # 同一月
        count = template_manager._calculate_month_count(2024, 1, 2024, 1)
        assert count == 1

        # 3ヶ月
        count = template_manager._calculate_month_count(2024, 1, 2024, 3)
        assert count == 3

        # 年を跨ぐ場合
        count = template_manager._calculate_month_count(2024, 12, 2025, 2)
        assert count == 3
