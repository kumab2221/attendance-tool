"""
構造化ログ機能のテスト
TASK-402: Red Phase - 失敗するテスト実装
"""

import json
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from attendance_tool.logging.structured_logger import StructuredLogger


class TestStructuredLogger:
    """構造化ログ機能のテスト"""

    def test_json_format_log_output(self):
        """TC-402-001: JSON形式ログ出力"""
        logger = StructuredLogger()

        # ログエントリ作成
        log_data = {
            "level": "INFO",
            "module": "csv_reader",
            "operation": "file_read",
            "message": "CSVファイル読み込み開始",
            "details": {"file_path": "/data/input.csv", "record_count": 1000},
        }

        # JSON形式でログ出力
        result = logger.log_structured(log_data)

        # JSON形式であることを確認
        assert isinstance(result, dict)

        # 必須フィールドの存在確認
        required_fields = [
            "timestamp",
            "level",
            "module",
            "operation",
            "message",
            "details",
            "correlation_id",
            "session_id",
        ]
        for field in required_fields:
            assert field in result

        # タイムスタンプがISO8601形式であることを確認
        timestamp_str = result["timestamp"]
        datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))

        # correlation_idとsession_idが生成されていることを確認
        assert result["correlation_id"] is not None
        assert result["session_id"] is not None
        assert len(result["correlation_id"]) > 0
        assert len(result["session_id"]) > 0

    def test_log_level_output_control(self):
        """TC-402-002: ログレベル別出力制御"""
        logger = StructuredLogger()

        test_cases = [
            {
                "level": "DEBUG",
                "expected_outputs": ["file"],
                "config": {"debug_mode": True},
            },
            {
                "level": "INFO",
                "expected_outputs": ["file"],
                "config": {"debug_mode": False},
            },
            {
                "level": "WARNING",
                "expected_outputs": ["file", "console"],
                "config": {"debug_mode": False},
            },
            {
                "level": "ERROR",
                "expected_outputs": ["file", "console"],
                "config": {"debug_mode": False},
            },
            {
                "level": "CRITICAL",
                "expected_outputs": ["file", "console", "email"],
                "config": {"debug_mode": False},
            },
        ]

        for test_case in test_cases:
            with patch.object(logger, "config", test_case["config"]):
                outputs = logger.determine_outputs(test_case["level"])
                assert outputs == test_case["expected_outputs"]

    def test_correlation_session_id_management(self):
        """TC-402-003: 相関ID・セッションID管理"""
        logger = StructuredLogger()

        # 新しいセッション開始
        logger.start_session()
        session_id = logger.get_session_id()

        # 複数のログエントリを出力
        log_entries = []
        for i in range(3):
            log_data = {
                "level": "INFO",
                "module": "test_module",
                "operation": f"operation_{i}",
                "message": f"Test message {i}",
            }
            entry = logger.log_structured(log_data)
            log_entries.append(entry)

        # セッションIDが全エントリで同一であることを確認
        for entry in log_entries:
            assert entry["session_id"] == session_id

        # 相関IDが処理ごとに一意であることを確認
        correlation_ids = [entry["correlation_id"] for entry in log_entries]
        assert len(set(correlation_ids)) == len(correlation_ids)  # 全て異なる
