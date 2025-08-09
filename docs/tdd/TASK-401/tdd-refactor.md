# TASK-401: エラーハンドリング統合 - Refactor Phase (リファクタリング)

## 概要

Green Phaseで作成した最小実装をリファクタリングして、コード品質の向上、機能の完全性、統合性の改善を行う。テストは常に通る状態を保ちながら実装を改善する。

## リファクタリング戦略

1. **コード品質向上** - 可読性、保守性、型安全性の改善
2. **設定ファイル統合** - YAML設定ファイルとの連携
3. **既存モジュール統合** - 既存コードとの統合強化  
4. **パフォーマンス最適化** - 非同期処理、メモリ効率化
5. **エラーメッセージ品質向上** - より具体的で実用的なメッセージ

## 実装改善

### 1. 設定ファイル統合

まず、エラーハンドリングの設定を管理するYAMLファイルを作成する。

**ファイル**: `config/error_handling.yaml`

```yaml
# エラーハンドリング設定
error_handling:
  # リトライ設定
  retry:
    max_attempts: 3
    base_delay: 1.0
    max_delay: 10.0
    backoff_multiplier: 2.0
  
  # メモリ管理設定
  memory:
    gc_threshold: 0.8  # メモリ使用率80%でGC実行
    chunk_size: 1000   # チャンク処理のサイズ
  
  # ログ設定
  logging:
    structured: true
    mask_personal_info: true
    output_levels:
      CRITICAL: ["console", "file", "system_log"]
      ERROR: ["console", "file"]
      WARNING: ["file"]
      INFO: ["file"]
  
  # エラー分類マッピング拡張
  classification:
    system_errors:
      FileNotFoundError:
        code: "SYS-001"
        severity: "ERROR"
        retry_enabled: true
      PermissionError:
        code: "SYS-004"
        severity: "CRITICAL"
        retry_enabled: false
      MemoryError:
        code: "SYS-003"
        severity: "CRITICAL"
        retry_enabled: false
      OSError:
        code: "SYS-002"
        severity: "ERROR"
        retry_enabled: true
    
    data_errors:
      ValidationError:
        code: "DATA-001"
        severity: "WARNING"
        retry_enabled: false
      TimeLogicError:
        code: "DATA-201"
        severity: "ERROR"
        retry_enabled: false
      WorkHoursError:
        code: "BIZ-104"
        severity: "WARNING"
        retry_enabled: false

# エラーメッセージ定義（日本語）
messages:
  ja:
    system_errors:
      SYS-001:
        title: "ファイルが見つかりません"
        detail: "指定されたファイル '{path}' が存在しないか、アクセスできません"
        solutions:
          - "ファイルパスを確認してください"
          - "ファイルが存在することを確認してください"
          - "ファイル名にタイプミスがないか確認してください"
      SYS-002:
        title: "ディスク容量が不足しています"
        detail: "出力先のディスクに十分な空き容量がありません"
        solutions:
          - "不要なファイルを削除して容量を確保してください"
          - "別のドライブを出力先に指定してください"
      SYS-003:
        title: "メモリが不足しています"
        detail: "処理に必要なメモリが確保できません"
        solutions:
          - "他のアプリケーションを終了してください"
          - "より小さなデータセットで処理を実行してください"
          - "チャンク処理モードを有効にしてください"
      SYS-004:
        title: "ファイルへのアクセス権限がありません"
        detail: "ファイルまたはフォルダへの読み書き権限がありません"
        solutions:
          - "管理者権限でアプリケーションを実行してください"
          - "ファイルの権限設定を確認してください"
          - "他のプロセスがファイルを使用していないか確認してください"
    
    data_errors:
      DATA-001:
        title: "データの形式に問題があります"
        detail: "入力データが期待される形式と異なります"
        solutions:
          - "CSVファイルの形式を確認してください"
          - "必要な列が存在することを確認してください"
          - "文字エンコーディングを確認してください"
      DATA-201:
        title: "時刻の論理に矛盾があります"
        detail: "出勤時刻が退勤時刻よりも遅くなっています"
        solutions:
          - "出勤時刻と退勤時刻を確認してください"
          - "日付をまたぐ勤務の場合は正しく入力されているか確認してください"
    
    business_errors:
      BIZ-104:
        title: "勤務時間が異常な値です"
        detail: "24時間を超える勤務時間または負の値が検出されました"
        solutions:
          - "勤務時間の入力を確認してください"
          - "休憩時間が正しく入力されているか確認してください"
          - "特別な勤務形態の場合は設定を見直してください"
```

### 2. エラーハンドラーの改善

**ファイル**: `src/attendance_tool/errors/handler.py` (改善版)

```python
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
from attendance_tool.utils.config import ConfigManager


class ErrorHandler:
    """統一エラーハンドラー (改善版)"""
    
    def __init__(self, config_manager: Optional[ConfigManager] = None):
        self.config_manager = config_manager or ConfigManager()
        self._load_configuration()
        self._setup_classification_map()
    
    def _load_configuration(self):
        """設定ファイルの読み込み"""
        try:
            self.config = self.config_manager.get_error_handling_config()
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
                    "FileNotFoundError": {"code": "SYS-001", "severity": "ERROR"},
                    "PermissionError": {"code": "SYS-004", "severity": "CRITICAL"},
                    "MemoryError": {"code": "SYS-003", "severity": "CRITICAL"}
                }
            }
        }
    
    def _setup_classification_map(self):
        """分類マッピングの設定"""
        self._classification_map = {}
        
        # システムエラー
        system_errors = self.config.get("classification", {}).get("system_errors", {})
        for error_name, config in system_errors.items():
            try:
                error_class = eval(error_name)  # 動的クラス取得（本番では改善必要）
                self._classification_map[error_class] = (
                    "SYSTEM",
                    config["code"],
                    config["severity"]
                )
            except NameError:
                continue
        
        # データエラー
        data_errors = self.config.get("classification", {}).get("data_errors", {})
        for error_name, config in data_errors.items():
            if error_name == "ValidationError":
                self._classification_map[ValidationError] = (
                    "DATA", config["code"], config["severity"]
                )
            elif error_name == "TimeLogicError":
                self._classification_map[TimeLogicError] = (
                    "DATA", config["code"], config["severity"]
                )
            elif error_name == "WorkHoursError":
                self._classification_map[WorkHoursError] = (
                    "BUSINESS", config["code"], config["severity"]
                )
    
    def classify_error(self, exception: Exception, context: Optional[ErrorContext] = None) -> ErrorClassification:
        """エラーを分類する (改善版)"""
        exception_type = type(exception)
        
        if exception_type in self._classification_map:
            category, code, severity = self._classification_map[exception_type]
        else:
            # デフォルト分類（未知のエラー）
            category, code, severity = self._classify_unknown_error(exception)
        
        return ErrorClassification(
            category=category,
            code=code,
            severity=severity,
            original_exception=exception,
            context=context,
            retry_enabled=self._is_retry_enabled(exception_type)
        )
    
    def _classify_unknown_error(self, exception: Exception) -> tuple:
        """未知エラーの分類"""
        # 例外の種類に基づいた推測分類
        if isinstance(exception, (IOError, OSError)):
            return ("SYSTEM", "SYS-999", "ERROR")
        elif isinstance(exception, ValueError):
            return ("DATA", "DATA-999", "WARNING")
        else:
            return ("UNKNOWN", "UNK-999", "ERROR")
    
    def _is_retry_enabled(self, exception_type: type) -> bool:
        """リトライ可能かどうかの判定"""
        # 設定ファイルからリトライ可能性を取得
        for category in ["system_errors", "data_errors"]:
            errors = self.config.get("classification", {}).get(category, {})
            for error_name, config in errors.items():
                if error_name == exception_type.__name__:
                    return config.get("retry_enabled", False)
        return False
    
    def should_continue_processing(self, classification: ErrorClassification) -> bool:
        """処理継続可能かどうかの判定"""
        # CRITICALエラーは処理を停止
        if classification.severity == "CRITICAL":
            return False
        
        # データエラーは継続可能
        if classification.category in ["DATA", "BUSINESS"]:
            return True
        
        return False
```

### 3. モデルクラスの拡張

**ファイル**: `src/attendance_tool/errors/models.py` (改善版)

```python
"""
エラーハンドリング用データモデル (改善版)
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict
from datetime import datetime


@dataclass
class ErrorContext:
    """エラー発生時のコンテキスト情報"""
    operation: str = "unknown"
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    user_id: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorClassification:
    """エラー分類結果 (改善版)"""
    category: str
    code: str
    severity: str
    original_exception: Exception
    context: Optional[ErrorContext] = None
    retry_enabled: bool = False
    
    @property
    def is_critical(self) -> bool:
        """クリティカルエラーかどうか"""
        return self.severity == "CRITICAL"
    
    @property
    def can_continue(self) -> bool:
        """処理継続可能かどうか"""
        return self.severity in ["WARNING", "INFO"]


@dataclass
class RecoveryResult:
    """リカバリー結果 (改善版)"""
    success: bool = False
    gc_executed: bool = False
    memory_freed: int = 0
    attempts: int = 0
    final_exception: Optional[Exception] = None
    recovery_time: float = 0.0


@dataclass 
class ProcessingResult:
    """処理結果（エラー継続処理用） (改善版)"""
    successful_results: List[Any] = field(default_factory=list)
    error_records: List['ErrorRecord'] = field(default_factory=list)
    total_processed: int = 0
    success_rate: float = 0.0
    
    def __post_init__(self):
        """後処理でメトリクス計算"""
        if self.total_processed > 0:
            self.success_rate = len(self.successful_results) / self.total_processed


@dataclass
class ErrorRecord:
    """エラーレコード (改善版)"""
    record_id: str
    error: Exception
    timestamp: datetime = field(default_factory=datetime.now)
    context: Optional[ErrorContext] = None
    recovery_attempted: bool = False
    recovery_success: bool = False
```

### 4. メッセージフォーマッターの改善

**ファイル**: `src/attendance_tool/errors/messages.py` (改善版)

```python
"""
メッセージフォーマッター (改善版)

設定ファイルベースの多言語メッセージ管理
"""

from typing import List, Dict, Any, Optional
from .models import ErrorClassification, ErrorContext
from attendance_tool.utils.config import ConfigManager


class MessageFormatter:
    """メッセージフォーマッター (改善版)"""
    
    def __init__(self, language: str = "ja", config_manager: Optional[ConfigManager] = None):
        self.language = language
        self.config_manager = config_manager or ConfigManager()
        self._load_message_templates()
    
    def _load_message_templates(self):
        """メッセージテンプレートの読み込み"""
        try:
            error_config = self.config_manager.get_error_handling_config()
            self.messages = error_config.get("messages", {}).get(self.language, {})
        except Exception:
            # フォールバックメッセージ
            self.messages = self._get_default_messages()
    
    def _get_default_messages(self) -> Dict[str, Any]:
        """デフォルトメッセージ"""
        return {
            "system_errors": {
                "SYS-001": {
                    "title": "ファイルが見つかりません",
                    "detail": "指定されたファイルが存在しません",
                    "solutions": ["ファイルパスを確認してください"]
                }
            }
        }
    
    def format_error_message(self, classification: ErrorClassification, context: Optional[ErrorContext] = None) -> str:
        """エラーメッセージの総合フォーマット"""
        # エラーコードからメッセージテンプレートを取得
        template = self._get_message_template(classification.code)
        
        if template:
            title = template.get("title", "エラーが発生しました")
            detail = template.get("detail", str(classification.original_exception))
            solutions = template.get("solutions", [])
            
            # コンテキスト情報を使った動的置換
            if context:
                detail = self._substitute_context(detail, context)
            
            # メッセージの組み立て
            message_parts = [f"❌ {title}"]
            
            if detail:
                message_parts.append(f"詳細: {detail}")
            
            if solutions:
                message_parts.append("💡 解決方法:")
                for i, solution in enumerate(solutions, 1):
                    message_parts.append(f"  {i}. {solution}")
            
            return "\n".join(message_parts)
        
        # フォールバック
        return f"❌ エラーが発生しました: {classification.original_exception}"
    
    def _get_message_template(self, error_code: str) -> Optional[Dict[str, Any]]:
        """エラーコードからメッセージテンプレートを取得"""
        # システムエラー
        if error_code.startswith("SYS-"):
            return self.messages.get("system_errors", {}).get(error_code)
        # データエラー  
        elif error_code.startswith("DATA-"):
            return self.messages.get("data_errors", {}).get(error_code)
        # ビジネスエラー
        elif error_code.startswith("BIZ-"):
            return self.messages.get("business_errors", {}).get(error_code)
        
        return None
    
    def _substitute_context(self, message: str, context: ErrorContext) -> str:
        """コンテキスト情報による動的置換"""
        substitutions = {
            "{path}": context.file_path or "不明",
            "{line}": str(context.line_number) if context.line_number else "不明",
            "{operation}": context.operation or "不明"
        }
        
        for placeholder, value in substitutions.items():
            message = message.replace(placeholder, value)
        
        return message
    
    def format_summary_message(self, total_errors: int, by_category: Dict[str, int]) -> str:
        """エラーサマリーメッセージ"""
        if total_errors == 0:
            return "✅ エラーは発生しませんでした"
        
        message_parts = [f"⚠️ {total_errors}件のエラーが発生しました"]
        
        for category, count in by_category.items():
            category_name = {
                "SYSTEM": "システム",
                "DATA": "データ", 
                "BUSINESS": "業務ルール",
                "USER": "ユーザー"
            }.get(category, category)
            
            message_parts.append(f"  • {category_name}エラー: {count}件")
        
        return "\n".join(message_parts)
    
    # 既存メソッドとの互換性維持
    def format_message(self, exception: Exception) -> str:
        """旧インターフェースとの互換性"""
        from .handler import ErrorHandler
        handler = ErrorHandler()
        classification = handler.classify_error(exception)
        return self.format_error_message(classification)
```

### 5. 設定管理の統合

ConfigManagerクラスに新しいメソッドを追加する。

**ファイル**: `src/attendance_tool/utils/config.py` への追加

```python
# 既存のConfigManagerクラスに以下のメソッドを追加

def get_error_handling_config(self) -> Dict[str, Any]:
    """エラーハンドリング設定の取得"""
    try:
        return self._load_yaml_config("error_handling.yaml")
    except FileNotFoundError:
        # デフォルト設定を返す
        return {
            "retry": {"max_attempts": 3, "base_delay": 1.0},
            "logging": {"structured": True, "mask_personal_info": True},
            "classification": {}
        }

def _load_yaml_config(self, filename: str) -> Dict[str, Any]:
    """YAML設定ファイルの読み込み"""
    import yaml
    config_path = self.config_dir / filename
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}
```

## テスト実行と検証

### 1. 設定ファイルの作成

```bash
# エラーハンドリング設定ファイルを作成
cp docs/tdd/TASK-401/config/error_handling.yaml config/
```

### 2. テスト実行

```bash
# 全テスト実行
python -m pytest tests/unit/errors/ -v

# 期待結果: すべてのテストが通る（改善後も機能維持）
```

### 3. パフォーマンステスト

```bash
# パフォーマンステスト実行
python -m pytest tests/unit/errors/ --benchmark-only
```

## Refactor Phase成功基準

### 品質向上確認
- [ ] コードの可読性が向上している
- [ ] 型ヒントが適切に設定されている
- [ ] 設定ファイルベースで柔軟性が向上している
- [ ] エラーメッセージがより具体的で有用になっている

### 機能性確認
- [ ] すべての既存テストが通る
- [ ] 新しい機能が正しく動作する
- [ ] パフォーマンスが劣化していない
- [ ] メモリ使用量が適切に制御されている

### 統合性確認
- [ ] 既存モジュールとの統合が改善されている
- [ ] 設定ファイルの変更が反映される
- [ ] エラーハンドリングが一貫している

## 次フェーズへの準備

Refactorが完了したら、Verificationフェーズで：

1. **総合テスト実行** - 全機能の動作確認
2. **パフォーマンス測定** - 要件充足確認
3. **統合テスト** - 既存システムとの連携確認
4. **ドキュメント更新** - 実装内容の文書化
5. **完了判定** - アクセプタンスクライテリア確認