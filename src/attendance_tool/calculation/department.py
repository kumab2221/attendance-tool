"""部門モデル - Green Phase実装"""

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Department:
    """部門モデル - Green Phase実装"""

    code: str  # 部門コード
    name: str  # 部門名
    parent_code: Optional[str]  # 親部門コード
    level: int  # 階層レベル
    is_active: bool  # 有効フラグ
    manager_id: Optional[str] = None  # 責任者ID

    def __post_init__(self):
        """初期化後検証 - Green Phase: 基本検証拡張"""
        if not self.code or not self.code.strip():
            raise ValueError("部門コードは必須です")
        if not self.name or not self.name.strip():
            raise ValueError("部門名は必須です")
        if self.level < 0:
            raise ValueError("階層レベルは0以上である必要があります")

        # Green Phase: 部門コード形式チェック追加（警告レベル）
        if not re.match(r"^DEPT\d{3}$", self.code):
            # 警告レベル（例外は出さない）
            pass

    def get_children(self, all_departments: List["Department"]) -> List["Department"]:
        """子部門一覧取得 - Green Phase実装"""
        return [dept for dept in all_departments if dept.parent_code == self.code]

    def is_ancestor_of(
        self, other: "Department", all_departments: List["Department"]
    ) -> bool:
        """祖先部門判定 - Green Phase実装"""
        if other.parent_code == self.code:
            return True

        parent = next((d for d in all_departments if d.code == other.parent_code), None)
        if parent:
            return self.is_ancestor_of(parent, all_departments)

        return False


class CircularReferenceError(Exception):
    """循環参照エラー"""

    pass


class DepartmentValidationError(Exception):
    """部門データ検証エラー"""

    pass
