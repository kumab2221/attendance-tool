"""
監査ログ機能
TASK-402: Green Phase - 最小実装
"""

import hashlib
import json
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional


class AuditLogger:
    """監査ログ機能の最小実装"""

    def __init__(self):
        self._audit_logs: List[Dict[str, Any]] = []

    def log_audit_event(
        self,
        event_type: str,
        action: str,
        resource: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """監査イベントをログに記録"""
        if details is None:
            details = {}

        # 監査ログエントリの作成
        audit_entry = {
            "audit_id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat() + "Z",
            "event_type": event_type,
            "actor": {
                "user_id": "system_user",  # 最小実装
                "session_id": str(uuid.uuid4()),
                "client_info": "attendance-tool v1.0.0",
            },
            "resource": {
                "type": self._determine_resource_type(resource),
                "identifier": resource,
                "properties": {},
            },
            "action": action,
            "result": "success",  # 最小実装では常に成功
            "details": details,
            "risk_level": self._assess_risk_level_simple(event_type, action),
        }

        # 完全性ハッシュの生成
        audit_entry["integrity_hash"] = self._generate_integrity_hash(audit_entry)

        # メモリ内保存（最小実装）
        self._audit_logs.append(audit_entry)

        return audit_entry

    def _determine_resource_type(self, resource: str) -> str:
        """リソースタイプの判定"""
        if resource.endswith(".csv"):
            return "file"
        elif resource == "employee_data":
            return "data"
        elif resource == "system":
            return "system"
        else:
            return "unknown"

    def _assess_risk_level_simple(self, event_type: str, action: str) -> str:
        """簡易的なリスクレベル判定"""
        if event_type == "ERROR_OCCURRED":
            return "high"
        elif event_type == "FILE_ACCESS" and action == "write":
            return "medium"
        else:
            return "low"

    def assess_risk_level(
        self,
        event: str,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
        user_role: Optional[str] = None,
        error_type: Optional[str] = None,
        frequency: Optional[str] = None,
    ) -> str:
        """詳細なリスクレベル判定"""

        # 高リスク条件
        if error_type == "SecurityError" or frequency == "repeated":
            return "high"

        if (
            event == "FILE_ACCESS"
            and action == "write"
            and resource_type == "employee_data"
        ):
            if user_role == "viewer":
                return "high"
            elif user_role == "admin":
                return "low"

        if event == "FILE_ACCESS" and action == "read" and user_role == "admin":
            return "low"

        # デフォルトは中リスク
        return "medium"

    def _generate_integrity_hash(self, audit_entry: Dict[str, Any]) -> str:
        """完全性ハッシュの生成"""
        # integrity_hashフィールドを除いてハッシュ化
        hash_data = {k: v for k, v in audit_entry.items() if k != "integrity_hash"}
        hash_string = json.dumps(hash_data, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(hash_string.encode()).hexdigest()

    def verify_integrity(self, audit_entry: Dict[str, Any]) -> bool:
        """監査ログの完全性検証"""
        stored_hash = audit_entry.get("integrity_hash")
        if not stored_hash:
            return False

        # ハッシュを再計算
        calculated_hash = self._generate_integrity_hash(audit_entry)
        return stored_hash == calculated_hash

    def get_recent_logs(self) -> List[Dict[str, Any]]:
        """最近の監査ログを取得"""
        return self._audit_logs.copy()
