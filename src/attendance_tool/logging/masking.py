"""
個人情報マスキング機能
TASK-402: Refactor Phase - 設定ベース改善版
"""

import re
from typing import Dict, List, Pattern, Optional
from .config import LoggingConfig


class PIIMasker:
    """個人情報マスキング機能（改善版）"""

    def __init__(self, config: Optional[LoggingConfig] = None):
        self.config = config or LoggingConfig()
        self.masking_level = self.config.get("masking.level", "MEDIUM")
        self.enabled = self.config.get("masking.enabled", True)
        self._compiled_patterns: Dict[str, Pattern] = {}
        self._compile_patterns()

    def set_level(self, level: str) -> None:
        """マスキングレベルを設定"""
        if level in ("STRICT", "MEDIUM", "LOOSE"):
            self.masking_level = level
        else:
            raise ValueError(f"Invalid masking level: {level}")

    def _compile_patterns(self) -> None:
        """マスキングパターンのコンパイル（パフォーマンス向上）"""
        if not self.enabled:
            return

        patterns = self.config.get("masking.patterns", {})
        for pattern_name, pattern_str in patterns.items():
            try:
                self._compiled_patterns[pattern_name] = re.compile(pattern_str)
            except re.error as e:
                print(f"Warning: Invalid regex pattern '{pattern_name}': {e}")

        # フォールバック: 基本パターンが設定されていない場合
        if not self._compiled_patterns:
            self._compiled_patterns = {
                "name": re.compile(r"[田中佐藤鈴木][一-龯]{1,3}"),
                "email": re.compile(r"[\w.-]+@"),
                "phone": re.compile(r"(\d{3})-(\d{4})-(\d{4})"),
                "employee_id": re.compile(r"(EMP)(\d{4})(\d{2})"),
            }

    def mask_text(self, text: str) -> str:
        """テキスト内の個人情報をマスキング（最適化版）"""
        if not self.enabled or self.masking_level == "LOOSE":
            return text

        masked_text = text

        # パターンベースのマスキング処理
        for pattern_name, compiled_pattern in self._compiled_patterns.items():
            masked_text = self._apply_masking_pattern(
                masked_text, pattern_name, compiled_pattern
            )

        return masked_text

    def _apply_masking_pattern(
        self, text: str, pattern_name: str, pattern: Pattern
    ) -> str:
        """個別のマスキングパターンを適用"""
        if pattern_name == "name":
            return self._mask_names(text, pattern)
        elif pattern_name == "email":
            return pattern.sub("***@", text)
        elif pattern_name == "phone":
            return pattern.sub(r"\1-****-\3", text)
        elif pattern_name == "employee_id":
            return pattern.sub(r"EM*****\3", text)
        else:
            # カスタムパターンの場合は全て****で置換
            return pattern.sub("****", text)

    def _mask_names(self, text: str, pattern: Pattern) -> str:
        """氏名のマスキング処理"""
        if self.masking_level == "STRICT":
            return pattern.sub("****", text)
        else:  # MEDIUM

            def name_replacer(match):
                name = match.group(0)
                if len(name) >= 3:
                    return name[:2] + "***"  # 最初の2文字を保持
                elif len(name) == 2:
                    return name[0] + "***"  # 2文字の場合は最初の1文字を保持
                return "****"

            return pattern.sub(name_replacer, text)
