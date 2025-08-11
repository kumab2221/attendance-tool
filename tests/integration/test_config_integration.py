"""設定管理の統合テストモジュール

実際の設定ファイルを使用した統合テスト
"""

import pytest
from pathlib import Path
import logging

from attendance_tool.utils.config import ConfigManager, ConfigError


class TestConfigIntegration:
    """設定管理の統合テスト"""

    @pytest.fixture
    def project_root(self):
        """プロジェクトルートディレクトリ"""
        return Path(__file__).parent.parent.parent

    @pytest.fixture
    def config_manager(self, project_root):
        """実際の設定ディレクトリを使用したConfigManager"""
        config_dir = project_root / "config"
        return ConfigManager(config_dir)

    def test_load_work_rules_config(self, config_manager):
        """work_rules.yamlの読み込みテスト"""
        config = config_manager.get_work_rules()

        # 必須セクションの存在確認
        assert "working_hours" in config
        assert "overtime" in config
        assert "tardiness" in config
        assert "leave" in config
        assert "attendance" in config
        assert "validation" in config
        assert "holidays" in config
        assert "company" in config

        # 基本労働時間設定の検証
        working_hours = config["working_hours"]
        assert "standard_daily_minutes" in working_hours
        assert "standard_weekly_minutes" in working_hours
        assert "break_minutes" in working_hours
        assert "standard_start_time" in working_hours
        assert "standard_end_time" in working_hours

        # 値の型と妥当性チェック
        assert isinstance(working_hours["standard_daily_minutes"], int)
        assert working_hours["standard_daily_minutes"] > 0
        assert isinstance(working_hours["break_minutes"], int)
        assert working_hours["break_minutes"] >= 0

    def test_load_csv_format_config(self, config_manager):
        """csv_format.yamlの読み込みテスト"""
        config = config_manager.get_csv_format()

        # 必須セクションの存在確認
        assert "input" in config
        assert "output" in config
        assert "error_log" in config
        assert "format_validation" in config

        # 入力設定の検証
        input_config = config["input"]
        assert "file_settings" in input_config
        assert "required_columns" in input_config
        assert "optional_columns" in input_config
        assert "validation" in input_config

        # ファイル設定の検証
        file_settings = input_config["file_settings"]
        assert "encoding" in file_settings
        assert "delimiter" in file_settings
        assert "has_header" in file_settings

        # 必須カラムの検証
        required_columns = input_config["required_columns"]
        assert "employee_id" in required_columns
        assert "employee_name" in required_columns
        assert "work_date" in required_columns

        # 各カラム定義の検証
        for column_name, column_config in required_columns.items():
            assert "names" in column_config
            assert "type" in column_config
            assert "required" in column_config
            assert isinstance(column_config["names"], list)
            assert len(column_config["names"]) > 0

    def test_load_logging_config(self, config_manager):
        """logging.yamlの読み込みテスト"""
        config = config_manager.get_logging_config()

        # 必須セクションの存在確認
        assert "version" in config
        assert "formatters" in config
        assert "handlers" in config
        assert "loggers" in config

        # バージョンの検証
        assert config["version"] == 1

        # フォーマッターの検証
        formatters = config["formatters"]
        assert "standard" in formatters
        assert "detailed" in formatters
        assert "json" in formatters

        # ハンドラーの検証
        handlers = config["handlers"]
        assert "console" in handlers
        assert "file_main" in handlers
        assert "file_error" in handlers

        # ロガーの検証
        loggers = config["loggers"]
        assert "root" in loggers
        assert "attendance_tool" in loggers

    def test_environment_specific_logging(self, config_manager):
        """環境固有のログ設定テスト"""
        config = config_manager.get_logging_config()

        # 環境設定の存在確認
        assert "environments" in config
        environments = config["environments"]

        # 各環境の設定確認
        for env_name in ["development", "testing", "production"]:
            assert env_name in environments
            env_config = environments[env_name]
            assert "root_level" in env_config
            assert "console_level" in env_config
            assert "file_level" in env_config

    def test_config_validation_work_rules(self, config_manager):
        """就業規則設定の妥当性検証"""
        config = config_manager.get_work_rules()

        # 労働時間の論理チェック
        working_hours = config["working_hours"]
        assert working_hours["standard_daily_minutes"] <= 1440  # 24時間以内
        assert working_hours["standard_weekly_minutes"] <= 10080  # 週168時間以内
        assert working_hours["break_minutes"] >= 0

        # 残業割増率の妥当性チェック
        overtime_rates = config["overtime"]["rates"]
        for rate_name, rate_value in overtime_rates.items():
            assert isinstance(rate_value, (int, float))
            assert rate_value >= 1.0  # 100%以上である必要
            assert rate_value <= 3.0  # 現実的な上限

        # 時刻形式の検証
        start_time = working_hours["standard_start_time"]
        end_time = working_hours["standard_end_time"]
        assert self._is_valid_time_format(start_time)
        assert self._is_valid_time_format(end_time)

    def test_config_validation_csv_format(self, config_manager):
        """CSVフォーマット設定の妥当性検証"""
        config = config_manager.get_csv_format()

        # サポートされている文字エンコーディングの確認
        supported_encodings = config["format_validation"]["supported_encodings"]
        input_encoding = config["input"]["file_settings"]["encoding"]
        assert input_encoding in supported_encodings

        # 出力設定の各レポートタイプで必要なカラムが定義されているか
        output_config = config["output"]
        for report_type in [
            "employee_report",
            "department_report",
            "daily_detail_report",
        ]:
            assert report_type in output_config
            report_config = output_config[report_type]
            assert "columns" in report_config
            assert len(report_config["columns"]) > 0

            # 各カラム定義の検証
            for column in report_config["columns"]:
                assert "name" in column
                assert "field" in column

    def test_logging_setup_integration(self, config_manager, caplog):
        """ログ設定の統合テスト"""
        # ログ設定を適用
        config_manager.setup_logging()

        # ログが正常に出力されるかテスト
        logger = logging.getLogger("attendance_tool.test")

        with caplog.at_level(logging.INFO):
            logger.info("テストメッセージ")

        # ログメッセージが記録されていることを確認
        assert len(caplog.records) >= 1
        assert "テストメッセージ" in caplog.text

    def test_log_directory_creation(self, config_manager, project_root):
        """ログディレクトリの作成確認"""
        # ConfigManagerのインスタンス化でログディレクトリが作成される
        log_dir = project_root / "logs"
        assert log_dir.exists()
        assert log_dir.is_dir()

    def _is_valid_time_format(self, time_str: str) -> bool:
        """時刻形式の妥当性チェック（HH:MM形式）"""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False

            hour, minute = int(parts[0]), int(parts[1])
            return 0 <= hour <= 23 and 0 <= minute <= 59
        except (ValueError, AttributeError):
            return False


class TestConfigErrorHandling:
    """設定エラーハンドリングのテスト"""

    def test_missing_required_sections(self, project_root):
        """必須セクションが不足している場合のテスト"""
        # 存在しない設定ファイルを指定
        config_manager = ConfigManager(project_root / "nonexistent_config")

        with pytest.raises(ConfigError):
            config_manager.get_work_rules()

    def test_config_file_permissions(self, project_root):
        """設定ファイルのアクセス権限テスト"""
        config_dir = project_root / "config"
        config_manager = ConfigManager(config_dir)

        # 正常な読み込みができることを確認
        try:
            config_manager.get_work_rules()
            config_manager.get_csv_format()
            config_manager.get_logging_config()
        except ConfigError:
            pytest.fail("設定ファイルの読み込みに失敗しました")
