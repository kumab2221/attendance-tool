"""
構造化ログ機能
TASK-402: Green Phase - 最小実装
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, List


class StructuredLogger:
    """構造化ログ機能の最小実装"""
    
    def __init__(self):
        self.session_id = None
        self.config = {"debug_mode": False}
    
    def start_session(self):
        """新しいセッションを開始"""
        self.session_id = str(uuid.uuid4())
    
    def get_session_id(self) -> str:
        """現在のセッションIDを取得"""
        if self.session_id is None:
            self.start_session()
        return self.session_id
    
    def log_structured(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """JSON形式でログ出力"""
        correlation_id = str(uuid.uuid4())
        
        if self.session_id is None:
            self.start_session()
        
        # 構造化ログエントリの作成
        structured_entry = {
            "timestamp": datetime.now().isoformat() + "Z",
            "level": log_data.get("level", "INFO"),
            "module": log_data.get("module", "unknown"),
            "operation": log_data.get("operation", "unknown"), 
            "message": log_data.get("message", ""),
            "details": log_data.get("details", {}),
            "correlation_id": correlation_id,
            "session_id": self.session_id
        }
        
        return structured_entry
    
    def determine_outputs(self, level: str) -> List[str]:
        """ログレベルに応じた出力先の決定"""
        if level == "DEBUG":
            if self.config.get("debug_mode", False):
                return ["file"]
            else:
                return []
        elif level == "INFO":
            return ["file"]
        elif level == "WARNING":
            return ["file", "console"] 
        elif level == "ERROR":
            return ["file", "console"]
        elif level == "CRITICAL":
            return ["file", "console", "email"]
        else:
            return ["file"]
    
    def info(self, message: str):
        """INFO レベルログの出力"""
        log_data = {
            "level": "INFO",
            "message": message
        }
        return self.log_structured(log_data)
    
    def get_recent_logs(self) -> List[Dict[str, Any]]:
        """最近のログを取得（テスト用）"""
        # 最小実装: 空のリストを返す
        return []