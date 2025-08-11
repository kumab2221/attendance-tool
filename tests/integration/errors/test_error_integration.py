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
            main(
                [
                    "--input",
                    non_existent_file,
                    "--output",
                    self.temp_dir,
                    "--period",
                    "2024-01",
                ]
            )

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
            ExcelExporter(),
        ]

        for module in modules:
            with self.subTest(module=module.__class__.__name__):
                # 統一されたエラーハンドリングパターンの確認
                # has_error_handlerメソッドは未実装なので失敗するはず
                self.assertTrue(hasattr(module, "error_handler"))
                self.assertIsInstance(module.error_handler, ErrorHandler)


if __name__ == "__main__":
    unittest.main()
