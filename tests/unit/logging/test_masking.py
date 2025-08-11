"""
個人情報マスキング機能のテスト
TASK-402: Red Phase - 失敗するテスト実装
"""

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
                "masking_level": "STRICT",
            },
            {
                "category": "氏名",
                "input": "処理対象: 田中太郎さんのデータ",
                "expected": "処理対象: 田中***さんのデータ",
                "masking_level": "MEDIUM",
            },
            {
                "category": "メールアドレス",
                "input": "連絡先: tanaka@company.com",
                "expected": "連絡先: ***@company.com",
                "masking_level": "MEDIUM",
            },
            {
                "category": "電話番号",
                "input": "電話: 090-1234-5678",
                "expected": "電話: 090-****-5678",
                "masking_level": "MEDIUM",
            },
            {
                "category": "社員ID",
                "input": "社員ID: EMP001234",
                "expected": "社員ID: EM*****34",
                "masking_level": "MEDIUM",
            },
        ]

        for test_case in test_cases:
            masker.set_level(test_case["masking_level"])
            result = masker.mask_text(test_case["input"])
            assert (
                result == test_case["expected"]
            ), f"Failed for {test_case['category']}"

    def test_masking_level_processing(self):
        """TC-402-011: マスキングレベル別処理"""
        masker = PIIMasker()
        test_input = "田中太郎 (tanaka@company.com, 090-1234-5678)"

        test_cases = [
            {"level": "STRICT", "expected": "**** (***@company.com, 090-****-5678)"},
            {"level": "MEDIUM", "expected": "田中*** (***@company.com, 090-****-5678)"},
            {
                "level": "LOOSE",
                "expected": "田中太郎 (tanaka@company.com, 090-1234-5678)",
            },
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
                "expected": "社員 **** (EM*****34) からメール ***@company.com で連絡あり。電話番号: 090-****-5678",
            },
            {
                "input": "処理結果: 佐藤花子さん、鈴木一郎さん、田中太郎さんのデータを処理完了",
                "expected": "処理結果: ****さん、****さん、****さんのデータを処理完了",
            },
        ]

        for test_case in complex_inputs:
            result = masker.mask_text(test_case["input"])
            assert result == test_case["expected"]
