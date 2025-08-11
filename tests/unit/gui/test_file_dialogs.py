"""
ファイルダイアログの単体テスト
"""

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

try:
    from attendance_tool.gui.file_dialogs import FileDialogs
except ImportError:
    FileDialogs = None


class TestFileDialogs(unittest.TestCase):
    """ファイルダイアログのテストクラス"""

    def setUp(self):
        """テストの前準備"""
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.temp_dir):
            import shutil

            shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(FileDialogs is None, "FileDialogs module not available")
    @patch("attendance_tool.gui.file_dialogs.FileDialogs.validate_csv_file")
    @patch("tkinter.filedialog.askopenfilename")
    def test_select_csv_file(self, mock_open, mock_validate):
        """CSVファイル選択テスト"""
        # モックの戻り値を設定
        mock_open.return_value = "test_file.csv"
        mock_validate.return_value = True

        try:
            dialogs = FileDialogs()
            result = dialogs.select_csv_file()
            self.assertEqual(result, "test_file.csv")
        except Exception:
            self.fail("FileDialogs クラスが実装されていません")

    @unittest.skipIf(FileDialogs is None, "FileDialogs module not available")
    @patch("attendance_tool.gui.file_dialogs.FileDialogs._check_directory_writable")
    @patch("tkinter.filedialog.askdirectory")
    def test_select_output_directory(self, mock_dir, mock_check):
        """出力ディレクトリ選択テスト"""
        mock_dir.return_value = self.temp_dir
        mock_check.return_value = True

        try:
            dialogs = FileDialogs()
            result = dialogs.select_output_directory()
            self.assertEqual(result, self.temp_dir)
        except Exception:
            self.fail("出力ディレクトリ選択機能が実装されていません")

    @unittest.skipIf(FileDialogs is None, "FileDialogs module not available")
    def test_validate_csv_file(self):
        """CSVファイル検証テスト"""
        try:
            dialogs = FileDialogs()

            # 存在しないファイルのテスト
            self.assertFalse(dialogs.validate_csv_file("nonexistent.csv"))

            # 有効なファイルのテスト
            test_csv = Path(self.temp_dir) / "test.csv"
            test_csv.write_text("header1,header2\nvalue1,value2", encoding="utf-8")

            self.assertTrue(dialogs.validate_csv_file(str(test_csv)))

        except Exception:
            self.fail("ファイル検証機能が実装されていません")


if __name__ == "__main__":
    unittest.main()
