# TASK-401: エラーハンドリング統合 - Green Phase (最小実装)

## 概要

Red Phaseで作成した失敗するテストを通すための最小限の実装を行う。この段階では機能の完全性よりも、テストが通ることを優先する。

## 実装戦略

1. **エラーハンドリングモジュール構造の作成**
2. **基本的な例外クラスの実装**
3. **最小限のエラーハンドラー実装**
4. **テストが通る最小限の機能実装**

## ディレクトリ構造作成

```bash
mkdir -p src/attendance_tool/errors
```

## 実装ファイル

### 1. パッケージ初期化

**ファイル**: `src/attendance_tool/errors/__init__.py`

```python
"""
エラーハンドリング統合モジュール

統一されたエラー処理とリカバリー機能を提供する
"""

from .exceptions import (
    AttendanceToolError,
    SystemError,
    DataError, 
    BusinessError,
    UserError
)
from .handler import ErrorHandler
from .recovery import RecoveryManager
from .messages import MessageFormatter
from .logger import ErrorLogger

__all__ = [
    'AttendanceToolError',
    'SystemError', 
    'DataError',
    'BusinessError',
    'UserError',
    'ErrorHandler',
    'RecoveryManager', 
    'MessageFormatter',
    'ErrorLogger'
]
```

### 2. カスタム例外クラス

**ファイル**: `src/attendance_tool/errors/exceptions.py`

```python
"""
カスタム例外クラス

アプリケーション固有の例外を定義
"""

from typing import Any, Optional


class AttendanceToolError(Exception):
    """勤怠管理ツール基底例外クラス"""
    
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class SystemError(AttendanceToolError):
    """システムエラー (SYS-XXX)"""
    pass


class DataError(AttendanceToolError):
    """データエラー (DATA-XXX)"""
    pass


class BusinessError(AttendanceToolError):
    """ビジネスロジックエラー (BIZ-XXX)"""
    pass


class UserError(AttendanceToolError):
    """ユーザーエラー (USER-XXX)"""
    pass
```

### 3. エラー分類結果クラス

**ファイル**: `src/attendance_tool/errors/models.py`

```python
"""
エラーハンドリング用データモデル
"""

from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class ErrorClassification:
    """エラー分類結果"""
    category: str
    code: str
    severity: str
    original_exception: Exception
    
    
@dataclass
class RecoveryResult:
    """リカバリー結果"""
    gc_executed: bool = False
    memory_freed: int = 0
    recovery_success: Optional[bool] = None


@dataclass 
class ProcessingResult:
    """処理結果（エラー継続処理用）"""
    successful_results: List[Any]
    error_records: List['ErrorRecord']


@dataclass
class ErrorRecord:
    """エラーレコード"""
    record_id: str
    error: Exception
    timestamp: str
```

### 4. エラーハンドラー (最小実装)

**ファイル**: `src/attendance_tool/errors/handler.py`

```python
"""
エラーハンドラー

統一されたエラー処理機構を提供
"""

from typing import Dict, Any
from .exceptions import AttendanceToolError, SystemError, DataError, BusinessError
from .models import ErrorClassification
from attendance_tool.validation.models import ValidationError, TimeLogicError, WorkHoursError


class ErrorHandler:
    """統一エラーハンドラー"""
    
    def __init__(self):
        # エラー分類マッピング（最小実装）
        self._classification_map = {
            FileNotFoundError: ("SYSTEM", "SYS-001", "ERROR"),
            PermissionError: ("SYSTEM", "SYS-004", "CRITICAL"),
            MemoryError: ("SYSTEM", "SYS-003", "CRITICAL"),
            ValidationError: ("DATA", "DATA-001", "WARNING"),
            TimeLogicError: ("DATA", "DATA-201", "ERROR"),
            WorkHoursError: ("BUSINESS", "BIZ-104", "WARNING")
        }
    
    def classify_error(self, exception: Exception) -> ErrorClassification:
        """エラーを分類する (最小実装)"""
        exception_type = type(exception)
        
        if exception_type in self._classification_map:
            category, code, severity = self._classification_map[exception_type]
        else:
            # デフォルト分類
            category, code, severity = ("SYSTEM", "SYS-999", "ERROR")
        
        return ErrorClassification(
            category=category,
            code=code,
            severity=severity,
            original_exception=exception
        )
```

### 5. リカバリーマネージャー (最小実装)

**ファイル**: `src/attendance_tool/errors/recovery.py`

```python
"""
リカバリー機能

エラー回復とリトライ機能を提供
"""

import gc
import time
from typing import Callable, Any, List
from .models import RecoveryResult, ProcessingResult, ErrorRecord


class RecoveryManager:
    """リカバリー機能管理"""
    
    def __init__(self):
        pass
    
    def retry_operation(self, operation: Callable, max_retries: int = 3, delay: float = 1.0) -> Any:
        """操作のリトライ実行 (最小実装)"""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay)
        
        # 最終的に失敗した場合は例外を再発生
        raise last_exception
    
    def handle_memory_error(self, operation: Callable) -> RecoveryResult:
        """メモリエラーハンドリング (最小実装)"""
        # ガベージコレクション実行
        before_gc = gc.get_count()[0]
        gc.collect()
        after_gc = gc.get_count()[0]
        
        memory_freed = max(0, before_gc - after_gc)
        
        # 回復試行
        recovery_success = None
        try:
            operation()
            recovery_success = True
        except Exception:
            recovery_success = False
        
        return RecoveryResult(
            gc_executed=True,
            memory_freed=memory_freed,
            recovery_success=recovery_success
        )
    
    def process_with_error_continuation(self, data: List[dict], processor: Callable) -> ProcessingResult:
        """エラー継続処理 (最小実装)"""
        successful_results = []
        error_records = []
        
        for i, record in enumerate(data):
            try:
                result = processor(record)
                successful_results.append(result)
            except Exception as e:
                error_record = ErrorRecord(
                    record_id=record.get('employee_id', str(i)),
                    error=e,
                    timestamp=str(time.time())
                )
                error_records.append(error_record)
        
        return ProcessingResult(
            successful_results=successful_results,
            error_records=error_records
        )
```

### 6. メッセージフォーマッター (最小実装)

**ファイル**: `src/attendance_tool/errors/messages.py`

```python
"""
メッセージフォーマッター

ユーザーフレンドリーなエラーメッセージを提供
"""

from typing import List
from attendance_tool.validation.models import ValidationError


class MessageFormatter:
    """メッセージフォーマッター"""
    
    def __init__(self, language: str = "ja"):
        self.language = language
        
        # 日本語メッセージマッピング (最小実装)
        self._message_templates = {
            FileNotFoundError: "ファイルが見つかりません\n詳細: {path}が存在しないか、アクセスできません\n解決方法: ファイルパスを確認し、ファイルが存在することを確認してください",
            PermissionError: "ファイルへのアクセス権限がありません\n詳細: ファイルまたはフォルダへの読み書き権限がない可能性があります\n解決方法: 管理者権限で実行するか、ファイルの権限設定を確認してください"
        }
        
        # 簡易化マッピング
        self._simplification_map = {
            ValidationError: "データの形式に問題があります",
            MemoryError: "メモリ不足により処理を継続できません",
            TimeoutError: "処理に時間がかかりすぎました"
        }
        
        # 解決方法マッピング
        self._solution_map = {
            "FileNotFoundError": [
                "ファイルパスを確認してください",
                "ファイルが存在することを確認してください", 
                "ファイル名にタイプミスがないか確認してください"
            ],
            "PermissionError": [
                "管理者権限で実行してください",
                "ファイルの権限設定を確認してください",
                "他のプロセスがファイルを使用していないか確認してください"
            ]
        }
    
    def format_message(self, exception: Exception) -> str:
        """メッセージフォーマット (最小実装)"""
        exception_type = type(exception)
        
        if exception_type in self._message_templates:
            template = self._message_templates[exception_type]
            # 簡単な文字列置換（最小実装）
            if hasattr(exception, 'filename') and exception.filename:
                return template.format(path=exception.filename)
            else:
                return template.format(path=str(exception))
        
        return f"エラーが発生しました: {str(exception)}"
    
    def simplify_message(self, exception: Exception) -> str:
        """技術用語の簡易化 (最小実装)"""
        exception_type = type(exception)
        
        if exception_type in self._simplification_map:
            return self._simplification_map[exception_type]
        
        return str(exception)
    
    def get_solution_suggestions(self, error_type: str) -> List[str]:
        """解決方法の提案 (最小実装)"""
        return self._solution_map.get(error_type, ["サポートに問い合わせてください"])
```

### 7. エラーログ (最小実装)

**ファイル**: `src/attendance_tool/errors/logger.py`

```python
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
                "user_id": self.mask_personal_info(error_info.get("user_id", "unknown"))
            },
            "stack_trace": str(error_info.get("exception", "")),
            "recovery_attempted": False,
            "recovery_success": False
        }
        
        return log_entry
    
    def mask_personal_info(self, text: str) -> str:
        """個人情報マスキング (最小実装)"""
        # 日本語名前のマスキング
        text = re.sub(r'[一-龯]{2,4}', '******', text)
        
        # メールアドレスのマスキング
        text = re.sub(r'[\w.-]+@', '******@', text)
        
        # 電話番号のマスキング
        text = re.sub(r'\d{3}-\d{4}-\d{4}', '***-****-****', text)
        
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
```

## テスト実行と確認

### 1. モジュール作成

上記のファイルをすべて作成する。

### 2. テスト実行

```bash
# 単体テスト実行
python -m pytest tests/unit/errors/ -v

# テスト結果確認
# 最小実装なので、基本的なテストは通るはず
```

### 3. 期待される結果

```
tests/unit/errors/test_error_classification.py::TestErrorClassification::test_system_error_classification PASSED
tests/unit/errors/test_error_classification.py::TestErrorClassification::test_data_error_classification PASSED
tests/unit/errors/test_error_classification.py::TestErrorClassification::test_business_error_classification PASSED

tests/unit/errors/test_recovery_manager.py::TestRecoveryManager::test_io_error_retry PASSED
tests/unit/errors/test_recovery_manager.py::TestRecoveryManager::test_memory_error_recovery PASSED
tests/unit/errors/test_recovery_manager.py::TestRecoveryManager::test_partial_data_error_continuation PASSED

tests/unit/errors/test_message_formatter.py::TestMessageFormatter::test_japanese_error_messages PASSED
tests/unit/errors/test_message_formatter.py::TestMessageFormatter::test_technical_term_simplification PASSED
tests/unit/errors/test_message_formatter.py::TestMessageFormatter::test_solution_suggestions PASSED

tests/unit/errors/test_error_logger.py::TestErrorLogger::test_structured_log_output PASSED
tests/unit/errors/test_error_logger.py::TestErrorLogger::test_personal_info_masking PASSED
tests/unit/errors/test_error_logger.py::TestErrorLogger::test_log_level_output_routing PASSED

========================== 12 passed ==========================
```

## Green Phase成功基準

- [ ] すべてのテストが通る
- [ ] 最小限の機能が実装されている
- [ ] コードが簡潔で理解しやすい
- [ ] 過度な実装を避けている

## 実装上の注意点

### 1. 最小実装の原則

- テストを通すのに必要な最小限の機能のみ実装
- エラーハンドリング、フォーマット、ログ機能の基本骨格を提供
- 詳細な機能やエッジケース対応は次のRefactorフェーズで実装

### 2. 既存コードとの互換性

- 既存の`ValidationError`等の例外クラスをそのまま利用
- 既存のコード構造に影響を与えない設計
- インポートエラーを避けるための適切なパス設定

### 3. テスト駆動の確認

- 各実装後にテストを実行して動作確認
- 失敗するテストがあれば最小限の修正で対応
- 新しい機能は追加せず、テスト要求のみに応答

## 次フェーズへの準備

Green Phaseが完了したら、Refactorフェーズで：

1. **コード品質の向上** - リファクタリング、最適化
2. **機能の完全性** - エッジケース対応、エラー処理強化  
3. **統合性の向上** - 既存モジュールとの連携強化
4. **設定ファイル対応** - YAML設定ファイルとの統合
5. **パフォーマンス最適化** - 非同期処理、メモリ効率化

現段階では、テストが通ることを最優先に最小実装を完成させる。