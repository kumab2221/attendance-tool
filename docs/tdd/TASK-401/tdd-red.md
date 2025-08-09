# TASK-401: エラーハンドリング統合 - Red Phase (失敗するテスト実装)

## 概要

統一されたエラーハンドリング機構の失敗するテストを実装する。この段階では実装コードは存在しないため、すべてのテストが失敗することを確認する。

## 実装ファイル構造

まず、エラーハンドリング機能の実装ディレクトリを作成し、基本的なファイル構造を準備する。

```
src/attendance_tool/errors/
├── __init__.py
├── exceptions.py      # カスタム例外クラス
├── handler.py         # エラーハンドラー  
├── recovery.py        # リカバリー機能
├── messages.py        # メッセージ管理
└── logger.py          # エラーログ機能
```

## テスト実装

### 1. テスト用ディレクトリ作成

```bash
mkdir -p tests/unit/errors
mkdir -p tests/integration/errors
```

### 2. エラー分類・重要度判定テスト実装

**ファイル**: `tests/unit/errors/test_error_classification.py`

```python
"""
エラー分類・重要度判定のテスト

このテストはRed Phase用で、すべて失敗することを確認する
"""

import unittest
import sys
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from attendance_tool.errors.handler import ErrorHandler
from attendance_tool.errors.exceptions import (
    AttendanceToolError, 
    SystemError, 
    DataError, 
    BusinessError,
    UserError
)


class TestErrorClassification(unittest.TestCase):
    """エラー分類テストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        # ErrorHandlerは未実装なので、インスタンス化で失敗するはず
        self.error_handler = ErrorHandler()
    
    def test_system_error_classification(self):
        """システムエラーの分類テスト (TC-401-001)"""
        test_cases = [
            {
                "exception": FileNotFoundError("/path/to/missing.csv"),
                "expected_category": "SYSTEM",
                "expected_code": "SYS-001",
                "expected_severity": "ERROR"
            },
            {
                "exception": PermissionError("Access denied"),
                "expected_category": "SYSTEM", 
                "expected_code": "SYS-004",
                "expected_severity": "CRITICAL"
            },
            {
                "exception": MemoryError("Out of memory"),
                "expected_category": "SYSTEM",
                "expected_code": "SYS-003", 
                "expected_severity": "CRITICAL"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # classify_errorメソッドは未実装なので失敗するはず
                result = self.error_handler.classify_error(case["exception"])
                
                self.assertEqual(result.category, case["expected_category"])
                self.assertEqual(result.code, case["expected_code"])
                self.assertEqual(result.severity, case["expected_severity"])
    
    def test_data_error_classification(self):
        """データエラーの分類テスト (TC-401-002)"""
        from attendance_tool.validation.models import ValidationError, TimeLogicError
        
        test_cases = [
            {
                "exception": ValidationError("Invalid date format", field="date"),
                "expected_category": "DATA",
                "expected_code": "DATA-001",
                "expected_severity": "WARNING"
            },
            {
                "exception": TimeLogicError("Start time > End time"),
                "expected_category": "DATA",
                "expected_code": "DATA-201",
                "expected_severity": "ERROR"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # 未実装なので失敗するはず
                result = self.error_handler.classify_error(case["exception"])
                
                self.assertEqual(result.category, case["expected_category"])
                self.assertEqual(result.code, case["expected_code"])
                self.assertEqual(result.severity, case["expected_severity"])
    
    def test_business_error_classification(self):
        """ビジネスロジックエラーの分類テスト (TC-401-003)"""
        from attendance_tool.validation.models import WorkHoursError
        
        test_cases = [
            {
                "exception": WorkHoursError("Work hours exceed 24h"),
                "expected_category": "BUSINESS",
                "expected_code": "BIZ-104",
                "expected_severity": "WARNING"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # 未実装なので失敗するはず
                result = self.error_handler.classify_error(case["exception"])
                
                self.assertEqual(result.category, case["expected_category"])
                self.assertEqual(result.code, case["expected_code"])
                self.assertEqual(result.severity, case["expected_severity"])


if __name__ == "__main__":
    unittest.main()
```

### 3. リカバリー機能テスト実装

**ファイル**: `tests/unit/errors/test_recovery_manager.py`

```python
"""
リカバリー機能のテスト

このテストはRed Phase用で、すべて失敗することを確認する
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import time

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from attendance_tool.errors.recovery import RecoveryManager


class TestRecoveryManager(unittest.TestCase):
    """リカバリー機能テストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        # RecoveryManagerは未実装なので、インスタンス化で失敗するはず
        self.recovery_manager = RecoveryManager()
    
    def test_io_error_retry(self):
        """I/Oエラーリトライ機能テスト (TC-401-010)"""
        # モックファイル読み込み関数（最初の2回は失敗、3回目で成功）
        mock_file_read = Mock(side_effect=[
            IOError("Network issue"),
            IOError("Temporary failure"), 
            "Success"
        ])
        
        # retry_operationメソッドは未実装なので失敗するはず
        result = self.recovery_manager.retry_operation(
            operation=mock_file_read,
            max_retries=3,
            delay=0.1
        )
        
        # 期待結果
        self.assertEqual(result, "Success")
        self.assertEqual(mock_file_read.call_count, 3)
    
    def test_memory_error_recovery(self):
        """メモリ不足時の自動回復テスト (TC-401-011)"""
        # メモリエラーのシミュレーション
        def memory_intensive_operation():
            raise MemoryError("Out of memory")
        
        # handle_memory_errorメソッドは未実装なので失敗するはず
        recovery_result = self.recovery_manager.handle_memory_error(
            operation=memory_intensive_operation
        )
        
        # 期待結果
        self.assertTrue(recovery_result.gc_executed)
        self.assertTrue(recovery_result.memory_freed > 0)
        self.assertIsNotNone(recovery_result.recovery_success)
    
    def test_partial_data_error_continuation(self):
        """部分的データエラーでの継続処理テスト (TC-401-012)"""
        # テストデータ（一部にエラーを含む）
        test_data = [
            {"employee_id": "001", "date": "2024-01-01", "valid": True},
            {"employee_id": "002", "date": "invalid-date", "valid": False},  # エラー
            {"employee_id": "003", "date": "2024-01-01", "valid": True}
        ]
        
        def process_record(record):
            if not record["valid"]:
                raise ValueError("Invalid data")
            return f"Processed {record['employee_id']}"
        
        # process_with_error_continuationメソッドは未実装なので失敗するはず
        result = self.recovery_manager.process_with_error_continuation(
            data=test_data,
            processor=process_record
        )
        
        # 期待結果
        self.assertEqual(len(result.successful_results), 2)
        self.assertEqual(len(result.error_records), 1)
        self.assertIn("002", result.error_records[0].record_id)


if __name__ == "__main__":
    unittest.main()
```

### 4. メッセージフォーマッターテスト実装

**ファイル**: `tests/unit/errors/test_message_formatter.py`

```python
"""
メッセージフォーマッターのテスト

このテストはRed Phase用で、すべて失敗することを確認する
"""

import unittest
import sys
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from attendance_tool.errors.messages import MessageFormatter


class TestMessageFormatter(unittest.TestCase):
    """メッセージフォーマッターテストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        # MessageFormatterは未実装なので、インスタンス化で失敗するはず
        self.formatter = MessageFormatter(language="ja")
    
    def test_japanese_error_messages(self):
        """日本語エラーメッセージテスト (TC-401-020)"""
        test_cases = [
            {
                "input": FileNotFoundError("/data/input.csv"),
                "expected_message": "ファイルが見つかりません\\n詳細: /data/input.csvが存在しないか、アクセスできません\\n解決方法: ファイルパスを確認し、ファイルが存在することを確認してください"
            },
            {
                "input": PermissionError("Access denied"),
                "expected_message": "ファイルへのアクセス権限がありません\\n詳細: ファイルまたはフォルダへの読み書き権限がない可能性があります\\n解決方法: 管理者権限で実行するか、ファイルの権限設定を確認してください"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # format_messageメソッドは未実装なので失敗するはず
                message = self.formatter.format_message(case["input"])
                self.assertEqual(message, case["expected_message"])
    
    def test_technical_term_simplification(self):
        """技術用語の平易な表現テスト (TC-401-021)"""
        from attendance_tool.validation.models import ValidationError
        
        test_cases = [
            {
                "input": ValidationError("Invalid format"),
                "expected_simple": "データの形式に問題があります"
            },
            {
                "input": MemoryError("Out of memory"), 
                "expected_simple": "メモリ不足により処理を継続できません"
            },
            {
                "input": TimeoutError("Operation timeout"),
                "expected_simple": "処理に時間がかかりすぎました"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # simplify_messageメソッドは未実装なので失敗するはず
                simple_message = self.formatter.simplify_message(case["input"])
                self.assertIn(case["expected_simple"], simple_message)
    
    def test_solution_suggestions(self):
        """解決方法の提案テスト (TC-401-022)"""
        test_cases = [
            {
                "error_type": "FileNotFoundError",
                "expected_solutions": [
                    "ファイルパスを確認してください",
                    "ファイルが存在することを確認してください",
                    "ファイル名にタイプミスがないか確認してください"
                ]
            },
            {
                "error_type": "PermissionError",
                "expected_solutions": [
                    "管理者権限で実行してください",
                    "ファイルの権限設定を確認してください",
                    "他のプロセスがファイルを使用していないか確認してください"
                ]
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # get_solution_suggestionsメソッドは未実装なので失敗するはず
                solutions = self.formatter.get_solution_suggestions(case["error_type"])
                
                for expected_solution in case["expected_solutions"]:
                    self.assertIn(expected_solution, solutions)


if __name__ == "__main__":
    unittest.main()
```

### 5. エラーログテスト実装

**ファイル**: `tests/unit/errors/test_error_logger.py`

```python
"""
エラーログのテスト

このテストはRed Phase用で、すべて失敗することを確認する
"""

import unittest
import sys
import json
from pathlib import Path
from unittest.mock import Mock, patch

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from attendance_tool.errors.logger import ErrorLogger


class TestErrorLogger(unittest.TestCase):
    """エラーログテストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        # ErrorLoggerは未実装なので、インスタンス化で失敗するはず
        self.logger = ErrorLogger()
    
    def test_structured_log_output(self):
        """構造化ログの出力テスト (TC-401-030)"""
        # テストエラー情報
        error_info = {
            "exception": FileNotFoundError("/data/input.csv"),
            "category": "SYSTEM",
            "code": "SYS-001",
            "severity": "ERROR",
            "user_id": "test_user",
            "operation": "csv_read"
        }
        
        # log_structured_errorメソッドは未実装なので失敗するはず
        log_entry = self.logger.log_structured_error(error_info)
        
        # 期待されるログフォーマット
        expected_fields = [
            "timestamp", "level", "category", "code", "message",
            "details", "stack_trace", "recovery_attempted", "recovery_success"
        ]
        
        for field in expected_fields:
            self.assertIn(field, log_entry)
        
        # JSON形式での出力可能性確認
        json_log = json.dumps(log_entry, ensure_ascii=False)
        self.assertIsInstance(json_log, str)
    
    def test_personal_info_masking(self):
        """個人情報マスキングテスト (TC-401-031)"""
        test_cases = [
            {
                "input": "Employee 田中太郎 has invalid data",
                "expected": "Employee ****** has invalid data"
            },
            {
                "input": "email: tanaka@example.com failed",
                "expected": "email: ******@example.com failed"
            },
            {
                "input": "Phone: 090-1234-5678 validation error",
                "expected": "Phone: ***-****-**** validation error"
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # mask_personal_infoメソッドは未実装なので失敗するはず
                masked_message = self.logger.mask_personal_info(case["input"])
                self.assertEqual(masked_message, case["expected"])
    
    def test_log_level_output_routing(self):
        """ログレベル別出力テスト (TC-401-032)"""
        test_cases = [
            {
                "level": "CRITICAL",
                "expected_outputs": ["console", "file", "system_log"]
            },
            {
                "level": "ERROR", 
                "expected_outputs": ["console", "file"]
            },
            {
                "level": "WARNING",
                "expected_outputs": ["file"]
            },
            {
                "level": "INFO",
                "expected_outputs": ["file"]  # デバッグモード時のみ
            }
        ]
        
        for case in test_cases:
            with self.subTest(case=case):
                # log_with_levelメソッドは未実装なので失敗するはず
                outputs = self.logger.log_with_level(
                    message="Test message",
                    level=case["level"]
                )
                
                self.assertEqual(set(outputs), set(case["expected_outputs"]))


if __name__ == "__main__":
    unittest.main()
```

### 6. 統合テスト実装

**ファイル**: `tests/integration/errors/test_error_integration.py`

```python
"""
エラーハンドリング統合テスト

このテストはRed Phase用で、すべて失敗することを確認する
"""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# パス設定
sys.path.append(str(Path(__file__).parent.parent.parent.parent / "src"))

from attendance_tool.errors.handler import ErrorHandler
from attendance_tool.cli.main import main


class TestErrorIntegration(unittest.TestCase):
    """エラーハンドリング統合テストクラス"""
    
    def setUp(self):
        """テスト前準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.error_handler = ErrorHandler()
    
    def tearDown(self):
        """テスト後クリーンアップ"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_cli_error_handling(self):
        """CLI統合エラーハンドリングテスト (TC-401-040)"""
        # 存在しないファイルを指定してCLI実行
        non_existent_file = os.path.join(self.temp_dir, "missing.csv")
        
        # mainは未実装のエラーハンドリング統合なので失敗するはず
        with self.assertRaises(SystemExit) as context:
            main([
                "--input", non_existent_file,
                "--output", self.temp_dir,
                "--period", "2024-01"
            ])
        
        # 適切な終了コードが設定される
        self.assertNotEqual(context.exception.code, 0)
    
    def test_module_error_consistency(self):
        """モジュール間エラーハンドリング一貫性テスト (TC-401-041)"""
        from attendance_tool.data.csv_reader import CSVReader
        from attendance_tool.validation.validator import DataValidator
        from attendance_tool.calculation.calculator import AttendanceCalculator
        from attendance_tool.output.excel_exporter import ExcelExporter
        
        # 各モジュールでのエラーハンドリング統一確認
        modules = [
            CSVReader(),
            DataValidator(),
            AttendanceCalculator(),
            ExcelExporter()
        ]
        
        for module in modules:
            with self.subTest(module=module.__class__.__name__):
                # 統一されたエラーハンドリングパターンの確認
                # has_error_handlerメソッドは未実装なので失敗するはず
                self.assertTrue(hasattr(module, 'error_handler'))
                self.assertIsInstance(module.error_handler, ErrorHandler)


if __name__ == "__main__":
    unittest.main()
```

## テスト実行とRed Phase確認

### 1. テストファイルの作成

上記のテストファイルをすべて作成し、実行可能な状態にする。

### 2. テスト実行

```bash
# 単体テスト実行
python -m pytest tests/unit/errors/ -v

# 統合テスト実行  
python -m pytest tests/integration/errors/ -v

# 全テスト実行
python -m pytest tests/ -v
```

### 3. 失敗確認

すべてのテストが以下の理由で失敗することを確認する：

1. **ImportError**: エラーハンドリングモジュールが存在しない
2. **AttributeError**: 必要なクラスやメソッドが未実装
3. **NotImplementedError**: 意図的に未実装とマークされたメソッド

## 期待される失敗結果

```
FAILED tests/unit/errors/test_error_classification.py::TestErrorClassification::test_system_error_classification - ModuleNotFoundError: No module named 'attendance_tool.errors'

FAILED tests/unit/errors/test_recovery_manager.py::TestRecoveryManager::test_io_error_retry - ModuleNotFoundError: No module named 'attendance_tool.errors'

FAILED tests/unit/errors/test_message_formatter.py::TestMessageFormatter::test_japanese_error_messages - ModuleNotFoundError: No module named 'attendance_tool.errors'

FAILED tests/unit/errors/test_error_logger.py::TestErrorLogger::test_structured_log_output - ModuleNotFoundError: No module named 'attendance_tool.errors'

FAILED tests/integration/errors/test_error_integration.py::TestErrorIntegration::test_cli_error_handling - ModuleNotFoundError: No module named 'attendance_tool.errors'

========================== 5 failed, 0 passed ==========================
```

## Red Phase成功基準

- [ ] すべてのテストが実行可能な状態で作成されている
- [ ] すべてのテストが期待される理由で失敗している
- [ ] テストケースが要件とアクセプタンスクライテリアをカバーしている
- [ ] テストコードが読みやすく、保守しやすい構造になっている

## 次のフェーズへの準備

Red Phaseが完了したら、Green Phaseで最小実装を行い、テストが通る状態を作る。実装する主要コンポーネント：

1. `src/attendance_tool/errors/exceptions.py` - カスタム例外クラス
2. `src/attendance_tool/errors/handler.py` - エラーハンドラー
3. `src/attendance_tool/errors/recovery.py` - リカバリー機能  
4. `src/attendance_tool/errors/messages.py` - メッセージフォーマッター
5. `src/attendance_tool/errors/logger.py` - エラーログ機能