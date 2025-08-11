"""就業規則違反情報モデル - Red Phase実装"""

from dataclasses import dataclass
from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional


class ViolationLevel(Enum):
    """違反レベル定義"""

    INFO = "info"  # 情報・推奨事項
    WARNING = "warning"  # 警告・注意事項
    VIOLATION = "violation"  # 違反・即座の対応が必要
    CRITICAL = "critical"  # 重大違反・法的リスク


@dataclass
class WorkRuleViolation:
    """就業規則違反情報

    Red Phase: 基本的なデータ構造のみ定義
    """

    violation_type: str  # 違反種別
    level: ViolationLevel  # 違反レベル
    message: str  # 違反メッセージ
    affected_date: date  # 対象日付
    actual_value: Any  # 実際の値
    threshold_value: Any  # 閾値
    suggestion: str  # 改善提案
    legal_reference: str  # 法的根拠

    # メタデータ
    detected_at: Optional[datetime] = None
    employee_id: Optional[str] = None
    rule_id: Optional[str] = None

    def __post_init__(self):
        """初期化後処理"""
        if self.detected_at is None:
            self.detected_at = datetime.now()


@dataclass
class ComplianceReport:
    """法令遵守レポート

    Red Phase: 基本構造のみ定義
    """

    employee_id: str
    period_start: date
    period_end: date
    total_violations: int
    critical_violations: int
    warnings: int
    info_items: int

    # 違反詳細
    violations: List[WorkRuleViolation]

    # 法令遵守スコア（0-100）
    compliance_score: float = 0.0

    def __post_init__(self):
        """初期化後処理 - Red Phase: 未実装"""
        # 実装は Green Phase で行う
        pass
