"""
ログ設定管理
TASK-402: Refactor Phase - 設定管理システム
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class LoggingConfig:
    """ログ機能設定管理クラス"""

    DEFAULT_CONFIG = {
        "masking": {
            "level": "MEDIUM",
            "enabled": True,
            "patterns": {
                "name": r"[田中佐藤鈴木][一-龯]{1,3}",
                "email": r"[\w.-]+@",
                "phone": r"(\d{3})-(\d{4})-(\d{4})",
                "employee_id": r"(EMP)(\d{4})(\d{2})",
            },
        },
        "performance": {
            "enabled": True,
            "thresholds": {
                "processing_time_ms": 30000,
                "memory_usage_mb": 512,
                "error_rate": 0.05,
            },
        },
        "audit": {"enabled": True, "integrity_check": True, "risk_assessment": True},
        "structured": {
            "format": "json",
            "timezone": "UTC",
            "fields": [
                "timestamp",
                "level",
                "module",
                "operation",
                "message",
                "details",
                "correlation_id",
                "session_id",
            ],
        },
    }

    def __init__(self, config_path: Optional[str] = None):
        self.config = self.DEFAULT_CONFIG.copy()
        if config_path:
            self.load_config(config_path)
        self.load_env_overrides()

    def load_config(self, config_path: str) -> None:
        """設定ファイルから読み込み"""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f)
                self._merge_config(self.config, user_config)
        except Exception as e:
            # 設定ファイル読み込みエラーは警告として扱い、デフォルト設定を使用
            print(f"Warning: Could not load config from {config_path}: {e}")

    def load_env_overrides(self) -> None:
        """環境変数からのオーバーライド"""
        env_mappings = {
            "ATTENDANCE_TOOL_LOG_MASKING_LEVEL": ["masking", "level"],
            "ATTENDANCE_TOOL_LOG_MASKING_ENABLED": ["masking", "enabled"],
            "ATTENDANCE_TOOL_LOG_PERFORMANCE_ENABLED": ["performance", "enabled"],
            "ATTENDANCE_TOOL_LOG_AUDIT_ENABLED": ["audit", "enabled"],
        }

        for env_key, config_path in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value is not None:
                self._set_nested_value(
                    self.config, config_path, self._convert_env_value(env_value)
                )

    def _merge_config(self, base: Dict[str, Any], override: Dict[str, Any]) -> None:
        """設定をマージ"""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_config(base[key], value)
            else:
                base[key] = value

    def _set_nested_value(self, config: Dict[str, Any], path: list, value: Any) -> None:
        """ネストした設定値を設定"""
        current = config
        for key in path[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[path[-1]] = value

    def _convert_env_value(self, value: str) -> Any:
        """環境変数の値を適切な型に変換"""
        if value.lower() in ("true", "yes", "1"):
            return True
        elif value.lower() in ("false", "no", "0"):
            return False
        elif value.isdigit():
            return int(value)
        else:
            return value

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得"""
        keys = key.split(".")
        current = self.config
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        return current
