"""検証ルール定義

カスタム検証ルールとルール管理機能
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


class ValidationLevel(Enum):
    """検証レベル"""

    CRITICAL = "CRITICAL"
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationError:
    """検証エラー詳細"""

    row_number: int
    field: str
    message: str
    value: Any
    level: str = "ERROR"
    expected_format: Optional[str] = None


@dataclass
class ValidationWarning:
    """検証警告詳細"""

    row_number: int
    field: str
    message: str
    value: Any


@dataclass
class ValidationRule:
    """検証ルール定義"""

    name: str
    validator: Callable[[Dict[str, Any]], Optional[ValidationError]]
    priority: int = 1
    level: ValidationLevel = ValidationLevel.ERROR
    description: str = ""

    def __post_init__(self):
        """初期化後処理"""
        if not self.description:
            self.description = f"検証ルール: {self.name}"

    def apply(self, record: Dict[str, Any]) -> Optional[ValidationError]:
        """ルールを適用"""
        try:
            return self.validator(record)
        except Exception as e:
            # バリデーター実行中のエラーをキャッチ
            return ValidationError(
                row_number=record.get("_row_number", -1),
                field=self.name,
                message=f"検証ルール実行エラー: {str(e)}",
                value=None,
                level=self.level.value,
            )


class RuleRegistry:
    """検証ルール管理"""

    def __init__(self):
        self.rules: List[ValidationRule] = []
        self._setup_default_rules()

    def _setup_default_rules(self):
        """デフォルトルールの設定"""
        # 現在は空実装（後で拡張）
        pass

    def add_rule(self, rule: ValidationRule):
        """ルールを追加"""
        self.rules.append(rule)
        # 優先度でソート
        self.rules.sort(key=lambda r: r.priority)

    def remove_rule(self, name: str):
        """ルールを削除"""
        self.rules = [r for r in self.rules if r.name != name]

    def get_rule(self, name: str) -> Optional[ValidationRule]:
        """ルールを取得"""
        for rule in self.rules:
            if rule.name == name:
                return rule
        return None

    def get_rules_by_level(self, level: ValidationLevel) -> List[ValidationRule]:
        """レベル別ルール取得"""
        return [r for r in self.rules if r.level == level]

    def apply_all_rules(self, record: Dict[str, Any]) -> List[ValidationError]:
        """全ルールを適用"""
        errors = []
        for rule in self.rules:
            error = rule.apply(record)
            if error:
                errors.append(error)
        return errors
