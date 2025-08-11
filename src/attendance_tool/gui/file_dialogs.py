"""
ファイルダイアログクラス

ファイル選択やディレクトリ選択のダイアログを提供します。
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional
import os


class FileDialogs:
    """ファイルダイアログ管理クラス"""

    def __init__(self, parent=None):
        """ファイルダイアログを初期化

        Args:
            parent: 親ウィンドウ（オプション）
        """
        self.parent = parent

    def select_csv_file(self, initial_dir: Optional[str] = None) -> Optional[str]:
        """CSVファイル選択ダイアログを表示

        Args:
            initial_dir: 初期ディレクトリ

        Returns:
            選択されたファイルパス、またはNone
        """
        if initial_dir is None:
            initial_dir = os.getcwd()

        file_path = filedialog.askopenfilename(
            parent=self.parent,
            title="入力CSVファイルを選択",
            initialdir=initial_dir,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if file_path:
            # ファイルの基本検証
            if self.validate_csv_file(file_path):
                return file_path
            else:
                messagebox.showerror(
                    "エラー", "選択されたファイルは有効なCSVファイルではありません。"
                )
                return None

        return None

    def select_output_directory(
        self, initial_dir: Optional[str] = None
    ) -> Optional[str]:
        """出力ディレクトリ選択ダイアログを表示

        Args:
            initial_dir: 初期ディレクトリ

        Returns:
            選択されたディレクトリパス、またはNone
        """
        if initial_dir is None:
            initial_dir = os.getcwd()

        dir_path = filedialog.askdirectory(
            parent=self.parent, title="出力ディレクトリを選択", initialdir=initial_dir
        )

        if dir_path:
            # ディレクトリの書き込み権限確認
            if self._check_directory_writable(dir_path):
                return dir_path
            else:
                messagebox.showerror(
                    "エラー", "選択されたディレクトリに書き込み権限がありません。"
                )
                return None

        return None

    def validate_csv_file(self, file_path: str) -> bool:
        """CSVファイルの基本検証

        Args:
            file_path: ファイルパス

        Returns:
            ファイルが有効かどうか
        """
        try:
            path = Path(file_path)

            # ファイル存在チェック
            if not path.exists():
                return False

            # ファイルサイズチェック（0バイトでない）
            if path.stat().st_size == 0:
                return False

            # 拡張子チェック
            if path.suffix.lower() != ".csv":
                return False

            # ファイル読み込みテスト
            try:
                with open(path, "r", encoding="utf-8") as f:
                    first_line = f.readline()
                    # 最低限ヘッダーらしきものがある
                    if "," not in first_line:
                        return False
            except UnicodeDecodeError:
                # UTF-8で読めない場合はcp932を試す
                try:
                    with open(path, "r", encoding="cp932") as f:
                        first_line = f.readline()
                        if "," not in first_line:
                            return False
                except UnicodeDecodeError:
                    return False

            return True

        except Exception:
            return False

    def _check_directory_writable(self, dir_path: str) -> bool:
        """ディレクトリの書き込み権限をチェック

        Args:
            dir_path: ディレクトリパス

        Returns:
            書き込み可能かどうか
        """
        try:
            path = Path(dir_path)

            # ディレクトリ存在チェック
            if not path.exists():
                return False

            if not path.is_dir():
                return False

            # 書き込みテスト
            test_file = path / "test_write.tmp"
            try:
                test_file.write_text("test", encoding="utf-8")
                test_file.unlink()  # テストファイル削除
                return True
            except Exception:
                return False

        except Exception:
            return False

    def save_csv_file(
        self,
        initial_dir: Optional[str] = None,
        initial_filename: str = "attendance_report.csv",
    ) -> Optional[str]:
        """CSV保存ダイアログを表示

        Args:
            initial_dir: 初期ディレクトリ
            initial_filename: 初期ファイル名

        Returns:
            保存先ファイルパス、またはNone
        """
        if initial_dir is None:
            initial_dir = os.getcwd()

        file_path = filedialog.asksaveasfilename(
            parent=self.parent,
            title="レポートファイルを保存",
            initialdir=initial_dir,
            initialfile=initial_filename,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            defaultextension=".csv",
        )

        return file_path if file_path else None
