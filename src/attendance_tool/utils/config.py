"""設定管理モジュール

環境変数による設定オーバーライド機能を提供する。
YAMLファイルの設定値を環境変数で上書きできる。
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """設定に関するエラー"""

    pass


class ConfigManager:
    """設定管理クラス

    YAMLファイルからの設定読み込みと
    環境変数による設定オーバーライドを行う。
    """

    def __init__(self, config_dir: Optional[Path] = None):
        """初期化

        Args:
            config_dir: 設定ファイルディレクトリのパス
        """
        if config_dir is None:
            # 実行ファイル対応: 複数のパスを試行
            possible_paths = [
                # 開発環境: プロジェクトルートのconfig
                Path(__file__).parent.parent.parent.parent / "config",
                # 実行ファイル: 実行ファイルと同じディレクトリのconfig
                Path(__file__).parent / "config",
                # 実行ファイル: sys.executableベース
                Path(os.path.dirname(os.path.abspath(__file__))) / "config",
                # 現在の作業ディレクトリ
                Path.cwd() / "config",
            ]

            # 存在するパスを見つける
            config_dir = None
            for path in possible_paths:
                if path.exists() and path.is_dir():
                    config_dir = path
                    break

            # どれも見つからない場合はデフォルトパスを作成
            if config_dir is None:
                config_dir = Path.cwd() / "config"
                config_dir.mkdir(exist_ok=True)

        self.config_dir = Path(config_dir)
        self._configs: Dict[str, Dict[str, Any]] = {}

        # ログディレクトリを作成
        self._ensure_log_directory()

    def _ensure_log_directory(self) -> None:
        """ログディレクトリが存在することを確認"""
        # 複数のパスを試行（実行ファイル対応）
        possible_log_dirs = [
            Path(__file__).parent.parent.parent.parent / "logs",
            Path.cwd() / "logs",
            Path.home() / ".attendance-tool" / "logs",
        ]

        for log_dir in possible_log_dirs:
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                if log_dir.exists():
                    break
            except (OSError, PermissionError):
                continue

    def load_config(self, config_name: str, reload: bool = False) -> Dict[str, Any]:
        """設定ファイルを読み込む

        Args:
            config_name: 設定ファイル名（.yaml拡張子なし）
            reload: 既に読み込まれた設定を再読み込みするかどうか

        Returns:
            設定辞書

        Raises:
            ConfigError: 設定ファイルの読み込みに失敗した場合
        """
        if config_name in self._configs and not reload:
            return self._configs[config_name]

        config_file = self.config_dir / f"{config_name}.yaml"

        if not config_file.exists():
            # 設定ファイルが見つからない場合は、デフォルト設定があるかチェック
            default_config = self._get_default_config(config_name)
            if not default_config:  # 空の辞書の場合（未知の設定名）
                raise ConfigError(f"設定ファイルが見つかりません: {config_file}")

            # デフォルト設定を使用
            config_data = default_config
            self._configs[config_name] = config_data
            logger.warning(
                f"設定ファイルが見つからないため、デフォルト設定を使用します: {config_file}"
            )
            return config_data

        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f)

            if config_data is None:
                config_data = {}

            # 環境変数による設定オーバーライドを適用
            config_data = self._apply_env_overrides(config_data, config_name)

            self._configs[config_name] = config_data
            logger.info(f"設定ファイルを読み込みました: {config_file}")

            return config_data

        except yaml.YAMLError as e:
            raise ConfigError(f"YAML形式エラー ({config_file}): {e}")
        except Exception as e:
            raise ConfigError(f"設定ファイル読み込みエラー ({config_file}): {e}")

    def _apply_env_overrides(
        self, config: Dict[str, Any], config_name: str
    ) -> Dict[str, Any]:
        """環境変数による設定オーバーライドを適用

        環境変数名の形式:
        ATTENDANCE_TOOL_{CONFIG_NAME}_{SECTION}_{KEY}

        例: ATTENDANCE_TOOL_WORK_RULES_WORKING_HOURS_STANDARD_DAILY_MINUTES

        Args:
            config: 設定辞書
            config_name: 設定名

        Returns:
            環境変数で上書きされた設定辞書
        """
        env_prefix = f"ATTENDANCE_TOOL_{config_name.upper().replace('-', '_')}_"

        for env_key, env_value in os.environ.items():
            if not env_key.startswith(env_prefix):
                continue

            # 環境変数名からキーパスを構築
            # 例: WORKING_HOURS_STANDARD_DAILY_MINUTES -> working_hours.standard_daily_minutes
            remaining_key = env_key[len(env_prefix) :].lower()

            # YAMLの実際のキー構造に合わせて調整
            key_parts = remaining_key.split("_")
            key_path = []

            # 設定ファイルの実際の構造に合わせてマッピング
            if (
                len(key_parts) >= 4
                and key_parts[0] == "working"
                and key_parts[1] == "hours"
            ):
                # WORKING_HOURS_STANDARD_DAILY_MINUTES -> working_hours.standard_daily_minutes
                if key_parts[2] == "standard" and key_parts[3] == "daily":
                    key_path = [
                        "working_hours",
                        "standard_daily_" + "_".join(key_parts[4:]),
                    ]
                elif key_parts[2] == "standard" and key_parts[3] == "weekly":
                    key_path = [
                        "working_hours",
                        "standard_weekly_" + "_".join(key_parts[4:]),
                    ]
                elif key_parts[2] == "legal" and key_parts[3] == "daily":
                    key_path = [
                        "working_hours",
                        "legal_daily_" + "_".join(key_parts[4:]),
                    ]
                elif key_parts[2] == "legal" and key_parts[3] == "weekly":
                    key_path = [
                        "working_hours",
                        "legal_weekly_" + "_".join(key_parts[4:]),
                    ]
                elif key_parts[2] == "standard" and key_parts[3] == "start":
                    key_path = [
                        "working_hours",
                        "standard_start_" + "_".join(key_parts[4:]),
                    ]
                elif key_parts[2] == "standard" and key_parts[3] == "end":
                    key_path = [
                        "working_hours",
                        "standard_end_" + "_".join(key_parts[4:]),
                    ]
                elif key_parts[2] == "break":
                    key_path = ["working_hours", "break_" + "_".join(key_parts[3:])]
                else:
                    # デフォルトのネスト構造
                    key_path = key_parts
            elif (
                len(key_parts) >= 4
                and key_parts[0] == "overtime"
                and key_parts[1] == "rates"
            ):
                # OVERTIME_RATES_WEEKDAY_OVERTIME -> overtime.rates.weekday_overtime
                key_path = ["overtime", "rates", "_".join(key_parts[2:])]
            else:
                # その他の場合はそのまま
                key_path = key_parts

            try:
                # 値の型変換
                converted_value = self._convert_env_value(env_value)

                # ネストした辞書に値を設定
                self._set_nested_value(config, key_path, converted_value)

                logger.info(
                    f"環境変数による設定オーバーライド: {'.'.join(key_path)} = {converted_value}"
                )

            except Exception as e:
                logger.warning(
                    f"環境変数の処理に失敗: {env_key} = {env_value}, エラー: {e}"
                )

        return config

    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """環境変数の値を適切な型に変換

        Args:
            value: 環境変数の値

        Returns:
            変換された値
        """
        # bool値の変換
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False

        # 数値の変換
        try:
            if "." in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass

        # 文字列として返す
        return value

    def _set_nested_value(
        self, config: Dict[str, Any], key_path: list, value: Any
    ) -> None:
        """ネストした辞書に値を設定

        Args:
            config: 設定辞書
            key_path: キーのパス（リスト）
            value: 設定する値
        """
        current = config

        # 最後のキー以外を辿る
        for key in key_path[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # 既存の値が辞書でない場合は辞書に変換
                current[key] = {}
            current = current[key]

        # 最後のキーに値を設定
        current[key_path[-1]] = value

    def _get_default_config(self, config_name: str) -> Dict[str, Any]:
        """デフォルト設定を取得

        Args:
            config_name: 設定名

        Returns:
            デフォルト設定辞書
        """
        default_configs = {
            "work_rules": {
                "working_hours": {
                    "standard_daily_minutes": 480,  # 8時間
                    "standard_weekly_minutes": 2400,  # 40時間
                    "legal_daily_limit_minutes": 960,  # 16時間
                    "legal_weekly_limit_minutes": 3000,  # 50時間
                    "overtime_threshold_minutes": 480,  # 8時間
                },
                "break_time": {
                    "default_break_minutes": 60,  # 1時間
                    "minimum_break_minutes": 30,  # 30分
                    "break_threshold_hours": 6,  # 6時間以上で休憩必須
                },
                "validation": {
                    "allow_past_days": 90,  # 90日前まで入力可能
                    "allow_future_days": 7,  # 7日後まで入力可能
                    "minimum_work_minutes": 30,  # 最低勤務時間
                },
            },
            "logging": {
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "standard": {
                        "format": "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
                    }
                },
                "handlers": {
                    "console": {
                        "class": "logging.StreamHandler",
                        "level": "INFO",
                        "formatter": "standard",
                        "stream": "ext://sys.stdout",
                    }
                },
                "loggers": {
                    "attendance_tool": {
                        "level": "INFO",
                        "handlers": ["console"],
                        "propagate": False,
                    }
                },
                "root": {"level": "WARNING", "handlers": ["console"]},
            },
            "csv_format": {
                "encoding": "utf-8",
                "delimiter": ",",
                "date_format": "%Y-%m-%d",
                "time_format": "%H:%M",
                "required_columns": [
                    "社員ID",
                    "氏名",
                    "部署",
                    "日付",
                    "出勤時刻",
                    "退勤時刻",
                ],
            },
        }

        return default_configs.get(config_name, {})

    def get_work_rules(self) -> Dict[str, Any]:
        """就業規則設定を取得

        Returns:
            就業規則設定辞書
        """
        return self.load_config("work_rules")

    def get_csv_format(self) -> Dict[str, Any]:
        """CSVフォーマット設定を取得

        Returns:
            CSVフォーマット設定辞書
        """
        return self.load_config("csv_format")

    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定を取得

        Returns:
            ログ設定辞書
        """
        return self.load_config("logging")

    def get_environment(self) -> str:
        """実行環境を取得

        Returns:
            実行環境名（development, testing, production）
        """
        return os.getenv("ATTENDANCE_TOOL_ENV", "development")

    def setup_logging(self) -> None:
        """ログ設定を適用

        logging.yamlの設定を使用してログを初期化する。
        """
        try:
            import logging.config

            log_config = self.get_logging_config()

            # 環境固有設定の適用
            env = self.get_environment()
            if "environments" in log_config and env in log_config["environments"]:
                env_config = log_config["environments"][env]

                # ルートレベルの調整
                if "root_level" in env_config:
                    log_config["root"]["level"] = env_config["root_level"]

                # コンソールレベルの調整
                if "console_level" in env_config:
                    if "console" in log_config["handlers"]:
                        log_config["handlers"]["console"]["level"] = env_config[
                            "console_level"
                        ]

                # ファイルレベルの調整
                if "file_level" in env_config:
                    if "file_main" in log_config["handlers"]:
                        log_config["handlers"]["file_main"]["level"] = env_config[
                            "file_level"
                        ]

                # デバッグファイルの有効/無効
                if not env_config.get("enable_debug_file", True):
                    if "file_debug" in log_config["handlers"]:
                        del log_config["handlers"]["file_debug"]

            logging.config.dictConfig(log_config)
            logger.info(f"ログ設定を適用しました (環境: {env})")

        except Exception as e:
            # ログ設定に失敗した場合は基本設定を使用
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
            )
            logger.error(f"ログ設定の適用に失敗しました: {e}")


# グローバル設定マネージャー
config_manager = ConfigManager()


def get_config(config_name: str) -> Dict[str, Any]:
    """設定を取得する便利関数

    Args:
        config_name: 設定名

    Returns:
        設定辞書
    """
    return config_manager.load_config(config_name)


def get_work_rules() -> Dict[str, Any]:
    """就業規則設定を取得する便利関数"""
    return config_manager.get_work_rules()


def get_csv_format() -> Dict[str, Any]:
    """CSVフォーマット設定を取得する便利関数"""
    return config_manager.get_csv_format()


def setup_logging() -> None:
    """ログ設定を適用する便利関数"""
    config_manager.setup_logging()


def get_environment() -> str:
    """実行環境を取得する便利関数"""
    return config_manager.get_environment()
