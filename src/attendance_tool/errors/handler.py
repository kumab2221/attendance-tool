"""
エラーハンドラー (改善版)

統一されたエラー処理機構を提供
設定ファイルベースで柔軟な分類とハンドリング
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from .exceptions import AttendanceToolError, SystemError, DataError, BusinessError
from .models import ErrorClassification, ErrorContext
from attendance_tool.validation.models import ValidationError, TimeLogicError, WorkHoursError


class ErrorHandler:
    """統一エラーハンドラー (改善版)"""
    
    def __init__(self):
        self._load_configuration()
        self._setup_classification_map()
    
    def _load_configuration(self):
        """設定ファイルの読み込み"""
        try:
            config_path = Path(__file__).parent.parent.parent.parent / "config" / "error_handling.yaml"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    self.config = config_data.get("error_handling", {})
            else:
                self.config = self._get_default_config()
        except Exception:
            # フォールバック設定
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "retry": {"max_attempts": 3, "base_delay": 1.0},
            "logging": {"structured": True, "mask_personal_info": True},
            "classification": {
                "system_errors": {
                    "FileNotFoundError": {"code": "SYS-001", "severity": "ERROR", "retry_enabled": True},
                    "PermissionError": {"code": "SYS-004", "severity": "CRITICAL", "retry_enabled": False},
                    "MemoryError": {"code": "SYS-003", "severity": "CRITICAL", "retry_enabled": False}
                },
                "data_errors": {
                    "ValidationError": {"code": "DATA-001", "severity": "WARNING", "retry_enabled": False},
                    "TimeLogicError": {"code": "DATA-201", "severity": "ERROR", "retry_enabled": False},
                    "WorkHoursError": {"code": "BIZ-104", "severity": "WARNING", "retry_enabled": False}
                }
            }
        }
    
    def _setup_classification_map(self):
        """分類マッピングの設定"""
        self._classification_map = {}
        
        # システムエラー
        system_errors = self.config.get("classification", {}).get("system_errors", {})
        for error_name, config in system_errors.items():
            if error_name == "FileNotFoundError":
                self._classification_map[FileNotFoundError] = (
                    "SYSTEM", config["code"], config["severity"], config.get("retry_enabled", False)
                )
            elif error_name == "PermissionError":
                self._classification_map[PermissionError] = (
                    "SYSTEM", config["code"], config["severity"], config.get("retry_enabled", False)
                )
            elif error_name == "MemoryError":
                self._classification_map[MemoryError] = (
                    "SYSTEM", config["code"], config["severity"], config.get("retry_enabled", False)
                )
        
        # データエラー
        data_errors = self.config.get("classification", {}).get("data_errors", {})
        for error_name, config in data_errors.items():
            if error_name == "ValidationError":
                self._classification_map[ValidationError] = (
                    "DATA", config["code"], config["severity"], config.get("retry_enabled", False)
                )
            elif error_name == "TimeLogicError":
                self._classification_map[TimeLogicError] = (
                    "DATA", config["code"], config["severity"], config.get("retry_enabled", False)
                )
            elif error_name == "WorkHoursError":
                self._classification_map[WorkHoursError] = (
                    "BUSINESS", config["code"], config["severity"], config.get("retry_enabled", False)
                )
    
    def classify_error(self, exception: Exception, context: Optional[ErrorContext] = None) -> ErrorClassification:
        """エラーを分類する (改善版)"""
        exception_type = type(exception)
        
        if exception_type in self._classification_map:
            category, code, severity, retry_enabled = self._classification_map[exception_type]
        else:
            # デフォルト分類（未知のエラー）
            category, code, severity, retry_enabled = self._classify_unknown_error(exception)
        
        return ErrorClassification(
            category=category,
            code=code,
            severity=severity,
            original_exception=exception,
            context=context,
            retry_enabled=retry_enabled
        )
    
    def _classify_unknown_error(self, exception: Exception) -> tuple:
        """未知エラーの分類"""
        # 例外の種類に基づいた推測分類
        if isinstance(exception, (IOError, OSError)):
            return ("SYSTEM", "SYS-999", "ERROR", True)
        elif isinstance(exception, ValueError):
            return ("DATA", "DATA-999", "WARNING", False)
        else:
            return ("UNKNOWN", "UNK-999", "ERROR", False)
    
    def should_continue_processing(self, classification: ErrorClassification) -> bool:
        """処理継続可能かどうかの判定"""
        # CRITICALエラーは処理を停止
        if classification.severity == "CRITICAL":
            return False
        
        # データエラーは継続可能
        if classification.category in ["DATA", "BUSINESS"]:
            return True
        
        return False