# TASK-402: ログ機能・監査対応 - Red Phase (失敗するテスト実装)

## 概要

構造化ログ出力、個人情報マスキング、パフォーマンス計測、監査ログ生成機能の失敗するテストを実装する。
TDDのRed Phaseとして、実装前にテストを作成し、すべてのテストが失敗することを確認する。

## 実装対象モジュール

- `src/attendance_tool/logging/structured_logger.py` - 構造化ログ機能
- `src/attendance_tool/logging/masking.py` - 個人情報マスキング
- `src/attendance_tool/logging/performance_tracker.py` - パフォーマンス計測
- `src/attendance_tool/logging/audit_logger.py` - 監査ログ
- `src/attendance_tool/logging/formatters.py` - ログフォーマッター

## テスト実装

### 1. テストディレクトリ作成

テスト用ディレクトリ構造:
```
tests/unit/logging/
├── __init__.py
├── test_structured_logger.py
├── test_masking.py  
├── test_performance_tracker.py
├── test_audit_logger.py
└── test_integration.py
```

### 2. 構造化ログテスト実装

```python
# tests/unit/logging/test_structured_logger.py
import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

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
            "details": {
                "file_path": "/data/input.csv",
                "record_count": 1000
            }
        }
        
        # JSON形式でログ出力
        result = logger.log_structured(log_data)
        
        # JSON形式であることを確認
        assert isinstance(result, dict)
        
        # 必須フィールドの存在確認
        required_fields = [
            "timestamp", "level", "module", "operation",
            "message", "details", "correlation_id", "session_id"
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
                "config": {"debug_mode": True}
            },
            {
                "level": "INFO",
                "expected_outputs": ["file"], 
                "config": {"debug_mode": False}
            },
            {
                "level": "WARNING",
                "expected_outputs": ["file", "console"],
                "config": {"debug_mode": False}
            },
            {
                "level": "ERROR",
                "expected_outputs": ["file", "console"],
                "config": {"debug_mode": False}
            },
            {
                "level": "CRITICAL",
                "expected_outputs": ["file", "console", "email"],
                "config": {"debug_mode": False}
            }
        ]
        
        for test_case in test_cases:
            with patch.object(logger, 'config', test_case["config"]):
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
                "message": f"Test message {i}"
            }
            entry = logger.log_structured(log_data)
            log_entries.append(entry)
        
        # セッションIDが全エントリで同一であることを確認
        for entry in log_entries:
            assert entry["session_id"] == session_id
            
        # 相関IDが処理ごとに一意であることを確認
        correlation_ids = [entry["correlation_id"] for entry in log_entries]
        assert len(set(correlation_ids)) == len(correlation_ids)  # 全て異なる
```

### 3. 個人情報マスキングテスト実装

```python
# tests/unit/logging/test_masking.py
import pytest
from attendance_tool.logging.masking import PIIMasker


class TestPIIMasker:
    """個人情報マスキング機能のテスト"""
    
    def test_basic_masking_functionality(self):
        """TC-402-010: 基本マスキング機能"""
        masker = PIIMasker()
        
        test_cases = [
            {
                "category": "氏名",
                "input": "処理対象: 田中太郎さんのデータ",
                "expected": "処理対象: ****さんのデータ",
                "masking_level": "STRICT"
            },
            {
                "category": "氏名",
                "input": "処理対象: 田中太郎さんのデータ", 
                "expected": "処理対象: 田中***さんのデータ",
                "masking_level": "MEDIUM"
            },
            {
                "category": "メールアドレス",
                "input": "連絡先: tanaka@company.com",
                "expected": "連絡先: ***@company.com",
                "masking_level": "MEDIUM"
            },
            {
                "category": "電話番号",
                "input": "電話: 090-1234-5678", 
                "expected": "電話: 090-****-5678",
                "masking_level": "MEDIUM"
            },
            {
                "category": "社員ID",
                "input": "社員ID: EMP001234",
                "expected": "社員ID: EM*****34",
                "masking_level": "MEDIUM"
            }
        ]
        
        for test_case in test_cases:
            masker.set_level(test_case["masking_level"])
            result = masker.mask_text(test_case["input"])
            assert result == test_case["expected"], f"Failed for {test_case['category']}"

    def test_masking_level_processing(self):
        """TC-402-011: マスキングレベル別処理"""
        masker = PIIMasker()
        test_input = "田中太郎 (tanaka@company.com, 090-1234-5678)"
        
        test_cases = [
            {
                "level": "STRICT",
                "expected": "**** (*@company.com, ***-****-****)"
            },
            {
                "level": "MEDIUM",
                "expected": "田中*** (***@company.com, 090-****-5678)"
            },
            {
                "level": "LOOSE", 
                "expected": "田中太郎 (tanaka@company.com, 090-1234-5678)"
            }
        ]
        
        for test_case in test_cases:
            masker.set_level(test_case["level"])
            result = masker.mask_text(test_input)
            assert result == test_case["expected"]

    def test_complex_pattern_masking(self):
        """TC-402-012: 複合パターンマスキング"""
        masker = PIIMasker()
        masker.set_level("STRICT")
        
        complex_inputs = [
            {
                "input": "社員 田中太郎 (EMP001234) からメール tanaka@company.com で連絡あり。電話番号: 090-1234-5678",
                "expected": "社員 **** (EM*****34) からメール ***@company.com で連絡あり。電話番号: 090-****-5678"
            },
            {
                "input": "処理結果: 佐藤花子さん、鈴木一郎さん、田中太郎さんのデータを処理完了",
                "expected": "処理結果: ****さん、****さん、****さんのデータを処理完了"
            }
        ]
        
        for test_case in complex_inputs:
            result = masker.mask_text(test_case["input"])
            assert result == test_case["expected"]
```

### 4. パフォーマンス計測テスト実装

```python
# tests/unit/logging/test_performance_tracker.py  
import pytest
import time
from unittest.mock import patch, MagicMock

from attendance_tool.logging.performance_tracker import PerformanceTracker


class TestPerformanceTracker:
    """パフォーマンス計測機能のテスト"""
    
    def test_processing_time_measurement(self):
        """TC-402-020: 処理時間計測"""
        def dummy_process():
            time.sleep(1.0)  # 1秒間の処理
        
        # パフォーマンストラッカーで計測
        with PerformanceTracker() as tracker:
            dummy_process()
        
        # 計測精度確認（±50ms以内）
        assert 950 <= tracker.duration_ms <= 1050

    def test_memory_usage_measurement(self):
        """TC-402-021: メモリ使用量計測"""  
        def memory_intensive_process():
            # 10MB相当のデータを作成
            large_data = [0] * (10 * 1024 * 1024 // 8)
            return large_data
        
        with PerformanceTracker() as tracker:
            data = memory_intensive_process()
        
        # メモリ使用量の増加を確認
        assert tracker.memory_peak_mb >= 10.0

    def test_performance_threshold_alerts(self):
        """TC-402-022: パフォーマンス閾値アラート"""
        tracker = PerformanceTracker()
        
        test_cases = [
            {
                "metric": "processing_time",
                "threshold": 30000,  # 30秒
                "test_value": 35000,  # 35秒
                "expected_alert": "WARNING"
            },
            {
                "metric": "memory_usage", 
                "threshold": 512,     # 512MB
                "test_value": 800,    # 800MB
                "expected_alert": "WARNING"
            },
            {
                "metric": "error_rate",
                "threshold": 0.05,    # 5%
                "test_value": 0.08,   # 8%
                "expected_alert": "WARNING"
            }
        ]
        
        for test_case in test_cases:
            alert = tracker.check_threshold(
                test_case["metric"],
                test_case["test_value"], 
                test_case["threshold"]
            )
            assert alert == test_case["expected_alert"]

    def test_cpu_usage_measurement(self):
        """CPU使用率計測"""
        def cpu_intensive_process():
            # CPU集約的な処理
            result = 0
            for i in range(1000000):
                result += i * i
            return result
        
        with PerformanceTracker() as tracker:
            cpu_intensive_process()
        
        # CPU使用率が記録されていることを確認
        assert tracker.cpu_usage_percent is not None
        assert tracker.cpu_usage_percent > 0
```

### 5. 監査ログテスト実装

```python
# tests/unit/logging/test_audit_logger.py
import pytest
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

from attendance_tool.logging.audit_logger import AuditLogger


class TestAuditLogger:
    """監査ログ機能のテスト"""
    
    def test_audit_event_recording(self):
        """TC-402-030: 監査イベント記録"""
        logger = AuditLogger()
        
        audit_events = [
            {
                "event_type": "FILE_ACCESS",
                "action": "read",
                "resource": "/data/input.csv",
                "expected_fields": [
                    "audit_id", "timestamp", "event_type", "actor",
                    "resource", "action", "result", "risk_level"
                ]
            },
            {
                "event_type": "DATA_PROCESSING",
                "action": "process",
                "resource": "employee_data",
                "details": {
                    "record_count": 1000,
                    "processing_type": "attendance_calculation"
                }
            },
            {
                "event_type": "ERROR_OCCURRED",
                "action": "error_handling", 
                "resource": "system",
                "details": {
                    "error_type": "ValidationError",
                    "error_code": "DATA-001"
                }
            }
        ]
        
        for event in audit_events:
            audit_entry = logger.log_audit_event(
                event["event_type"],
                event["action"], 
                event["resource"],
                event.get("details", {})
            )
            
            # 必須フィールドの存在確認
            expected_fields = event.get("expected_fields", [
                "audit_id", "timestamp", "event_type", "actor",
                "resource", "action", "result", "risk_level"
            ])
            
            for field in expected_fields:
                assert field in audit_entry

    def test_risk_level_assessment(self):
        """TC-402-031: リスクレベル判定"""
        logger = AuditLogger()
        
        risk_assessment_cases = [
            {
                "event": "FILE_ACCESS",
                "action": "read", 
                "resource_type": "employee_data",
                "user_role": "admin",
                "expected_risk": "low"
            },
            {
                "event": "FILE_ACCESS",
                "action": "write",
                "resource_type": "employee_data", 
                "user_role": "viewer",
                "expected_risk": "high"
            },
            {
                "event": "ERROR_OCCURRED",
                "error_type": "SecurityError",
                "frequency": "repeated", 
                "expected_risk": "high"
            }
        ]
        
        for case in risk_assessment_cases:
            risk_level = logger.assess_risk_level(
                case["event"],
                case.get("action"),
                case.get("resource_type"),
                case.get("user_role"),
                case.get("error_type"),
                case.get("frequency")
            )
            assert risk_level == case["expected_risk"]

    def test_audit_log_integrity(self):
        """TC-402-032: 監査ログ完全性"""
        logger = AuditLogger()
        
        # 監査ログエントリを生成
        audit_entry = logger.log_audit_event(
            "FILE_ACCESS",
            "read", 
            "/data/test.csv",
            {}
        )
        
        # ハッシュ値の生成確認
        assert "integrity_hash" in audit_entry
        assert len(audit_entry["integrity_hash"]) > 0
        
        # 完全性検証
        is_valid = logger.verify_integrity(audit_entry)
        assert is_valid == True
        
        # 改竄テスト
        audit_entry["message"] = "tampered message"
        is_valid_after_tampering = logger.verify_integrity(audit_entry)
        assert is_valid_after_tampering == False
```

### 6. 統合テスト実装

```python
# tests/unit/logging/test_integration.py
import pytest
import time
from unittest.mock import patch, MagicMock

from attendance_tool.errors import ErrorHandler
from attendance_tool.logging.structured_logger import StructuredLogger
from attendance_tool.logging.audit_logger import AuditLogger


class TestLoggingIntegration:
    """ログ機能統合テスト"""
    
    def test_error_handling_integration(self):
        """TC-402-050: エラーハンドリング統合"""
        # エラー発生
        error_handler = ErrorHandler()
        structured_logger = StructuredLogger()
        audit_logger = AuditLogger()
        
        try:
            raise FileNotFoundError("/missing/file.csv")
        except Exception as e:
            classification = error_handler.classify_error(e)
            
        # 監査ログ確認
        audit_logs = audit_logger.get_recent_logs()
        assert any(log["event_type"] == "ERROR_OCCURRED" for log in audit_logs)
        
        # 構造化ログ確認
        structured_logs = structured_logger.get_recent_logs()
        error_log = next((log for log in structured_logs if log["level"] == "ERROR"), None)
        assert error_log is not None
        assert error_log["details"]["error_code"] == "SYS-001"

    def test_logging_performance_impact(self):
        """TC-402-051: パフォーマンス影響測定"""
        def process_sample_data_without_logging():
            # ログ機能を無効にして処理を実行
            time.sleep(0.1)  # サンプル処理
            
        def process_sample_data_with_logging():
            # ログ機能を有効にして処理を実行
            logger = StructuredLogger()
            logger.info("Processing started")
            time.sleep(0.1)  # サンプル処理
            logger.info("Processing completed")
        
        # ログ無効時の処理時間測定
        start_time = time.time()
        process_sample_data_without_logging()
        baseline_time = time.time() - start_time
        
        # ログ有効時の処理時間測定
        start_time = time.time()
        process_sample_data_with_logging()
        with_logging_time = time.time() - start_time
        
        # オーバーヘッド確認（3%以内）
        overhead = (with_logging_time - baseline_time) / baseline_time
        assert overhead <= 0.03  # 3%以内
```

## テスト実行確認

### テスト実行前の状態確認
以下のコマンドでテストが失敗することを確認:

```bash
# 個別モジュールテスト
python -m pytest tests/unit/logging/test_structured_logger.py -v
python -m pytest tests/unit/logging/test_masking.py -v
python -m pytest tests/unit/logging/test_performance_tracker.py -v
python -m pytest tests/unit/logging/test_audit_logger.py -v

# 統合テスト
python -m pytest tests/unit/logging/test_integration.py -v

# 全ログ関連テスト
python -m pytest tests/unit/logging/ -v
```

### 期待される結果
- **全テストケースが失敗する** (ImportError, AttributeError等)
- 実装されていないクラス・メソッドに対するエラーが発生
- テスト数: 約15-20件すべてがFAIL状態

### 失敗理由の確認
1. **ImportError**: 実装ファイルが存在しない
2. **AttributeError**: クラス・メソッドが実装されていない  
3. **AssertionError**: 期待値と実際値の不一致

## Red Phaseの完了条件

- [ ] すべてのテストファイルが作成されている
- [ ] 全テストケースが実行される（失敗してOK）
- [ ] 実装すべきクラス・メソッドが明確になっている
- [ ] テストが論理的に正しく設計されている

## 次のステップ

Red Phaseの完了後、Green Phaseで以下を実装:
1. 構造化ログ機能の最小実装
2. 個人情報マスキング機能の最小実装  
3. パフォーマンス計測機能の最小実装
4. 監査ログ機能の最小実装
5. 統合部分の最小実装

各実装でテストが段階的に通るようにし、すべてのテストがGREENになることを確認する。