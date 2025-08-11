"""
エラーログ機能

構造化ログとマスキング機能を提供
"""

import json
import re
from datetime import datetime
from typing import Dict, Any, List


class ErrorLogger:
    """エラーログ機能"""

    def __init__(self):
        pass

    def log_structured_error(self, error_info: Dict[str, Any]) -> Dict[str, Any]:
        """構造化エラーログ (最小実装)"""
        log_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": error_info.get("severity", "ERROR"),
            "category": error_info.get("category", "UNKNOWN"),
            "code": error_info.get("code", "UNKNOWN"),
            "message": str(error_info.get("exception", "")),
            "details": {
                "operation": error_info.get("operation", "unknown"),
                "user_id": self.mask_personal_info(
                    error_info.get("user_id", "unknown")
                ),
            },
            "stack_trace": str(error_info.get("exception", "")),
            "recovery_attempted": False,
            "recovery_success": False,
        }

        return log_entry

    def mask_personal_info(self, text: str) -> str:
        """個人情報マスキング (最小実装)"""
        # 日本語名前のマスキング
        text = re.sub(r"[一-龯]{2,4}", "******", text)

        # メールアドレスのマスキング
        text = re.sub(r"[\w.-]+@", "******@", text)

        # 電話番号のマスキング
        text = re.sub(r"\d{3}-\d{4}-\d{4}", "***-****-****", text)

        return text

    def log_with_level(self, message: str, level: str) -> List[str]:
        """レベル別ログ出力 (最小実装)"""
        outputs = []

        if level == "CRITICAL":
            outputs = ["console", "file", "system_log"]
        elif level == "ERROR":
            outputs = ["console", "file"]
        elif level == "WARNING":
            outputs = ["file"]
        elif level == "INFO":
            outputs = ["file"]

        return outputs
