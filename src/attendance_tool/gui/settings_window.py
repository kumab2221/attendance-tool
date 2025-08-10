"""
設定ウィンドウクラス

アプリケーションの設定画面を提供します。
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import json
from typing import Dict, Any
import os


class SettingsWindow:
    """設定ウィンドウクラス"""
    
    def __init__(self, parent=None):
        """設定ウィンドウを初期化
        
        Args:
            parent: 親ウィンドウ
        """
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title("設定")
        self.window.geometry("500x400")
        self.window.resizable(True, True)
        
        # ウィンドウを中央に配置
        self._center_window()
        
        # ウィンドウを最前面に
        if parent:
            self.window.transient(parent)
        
        # 設定データの初期化
        self.settings = self._load_settings()
        
        # GUI要素を作成
        self._create_widgets()
        
        # 現在の設定を表示
        self._load_current_settings()
    
    def _center_window(self):
        """ウィンドウを画面中央に配置"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_widgets(self):
        """GUI要素を作成"""
        # ノートブック（タブ）を作成
        notebook = ttk.Notebook(self.window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 一般設定タブ
        self._create_general_tab(notebook)
        
        # ファイル設定タブ
        self._create_file_tab(notebook)
        
        # 出力設定タブ
        self._create_output_tab(notebook)
        
        # ボタンフレーム
        self._create_button_frame()
    
    def _create_general_tab(self, notebook):
        """一般設定タブを作成"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="一般")
        
        # デフォルトディレクトリ設定
        ttk.Label(frame, text="デフォルト入力ディレクトリ:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.default_input_dir = tk.StringVar()
        entry_frame = ttk.Frame(frame)
        entry_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Entry(entry_frame, textvariable=self.default_input_dir, width=40).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(entry_frame, text="参照", 
                  command=self._browse_input_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # デフォルト出力ディレクトリ設定
        ttk.Label(frame, text="デフォルト出力ディレクトリ:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.default_output_dir = tk.StringVar()
        entry_frame2 = ttk.Frame(frame)
        entry_frame2.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5)
        ttk.Entry(entry_frame2, textvariable=self.default_output_dir, width=40).pack(
            side=tk.LEFT, fill=tk.X, expand=True
        )
        ttk.Button(entry_frame2, text="参照", 
                  command=self._browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))
        
        # 自動バックアップ設定
        self.auto_backup = tk.BooleanVar()
        ttk.Checkbutton(
            frame, 
            text="出力時に自動バックアップを作成", 
            variable=self.auto_backup
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        # グリッドの重みを設定
        frame.columnconfigure(1, weight=1)
    
    def _create_file_tab(self, notebook):
        """ファイル設定タブを作成"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="ファイル")
        
        # 文字エンコーディング設定
        ttk.Label(frame, text="CSVファイル文字エンコーディング:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        self.csv_encoding = tk.StringVar(value="utf-8-sig")
        encoding_combo = ttk.Combobox(
            frame, 
            textvariable=self.csv_encoding,
            values=["utf-8-sig", "utf-8", "cp932", "shift_jis"],
            state="readonly",
            width=20
        )
        encoding_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # 日付フォーマット設定
        ttk.Label(frame, text="日付フォーマット:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.date_format = tk.StringVar(value="YYYY-MM-DD")
        date_combo = ttk.Combobox(
            frame,
            textvariable=self.date_format,
            values=["YYYY-MM-DD", "YYYY/MM/DD", "DD/MM/YYYY", "MM/DD/YYYY"],
            state="readonly",
            width=20
        )
        date_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        # ファイルサイズ制限
        ttk.Label(frame, text="最大ファイルサイズ (MB):").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.max_file_size = tk.StringVar(value="100")
        ttk.Entry(frame, textvariable=self.max_file_size, width=10).grid(
            row=2, column=1, sticky=tk.W, padx=5, pady=5
        )
    
    def _create_output_tab(self, notebook):
        """出力設定タブを作成"""
        frame = ttk.Frame(notebook, padding="10")
        notebook.add(frame, text="出力")
        
        # 出力ファイル形式
        ttk.Label(frame, text="出力ファイル形式:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        format_frame = ttk.Frame(frame)
        format_frame.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.output_csv = tk.BooleanVar(value=True)
        self.output_excel = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(format_frame, text="CSV", variable=self.output_csv).pack(
            side=tk.LEFT, padx=(0, 10)
        )
        ttk.Checkbutton(format_frame, text="Excel", variable=self.output_excel).pack(
            side=tk.LEFT
        )
        
        # ファイル名テンプレート
        ttk.Label(frame, text="ファイル名テンプレート:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.filename_template = tk.StringVar(value="attendance_report_{YYYY}_{MM}")
        ttk.Entry(frame, textvariable=self.filename_template, width=40).grid(
            row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=5
        )
        
        # タイムスタンプ追加
        self.add_timestamp = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame,
            text="ファイル名にタイムスタンプを追加",
            variable=self.add_timestamp
        ).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=10)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_button_frame(self):
        """ボタンフレームを作成"""
        button_frame = ttk.Frame(self.window)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="OK", command=self._save_and_close).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="キャンセル", command=self._cancel).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="適用", command=self._apply_settings).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="デフォルトに戻す", command=self._reset_to_default).pack(
            side=tk.LEFT, padx=5
        )
    
    def _browse_input_dir(self):
        """入力ディレクトリを参照"""
        dir_path = filedialog.askdirectory(title="デフォルト入力ディレクトリを選択")
        if dir_path:
            self.default_input_dir.set(dir_path)
    
    def _browse_output_dir(self):
        """出力ディレクトリを参照"""
        dir_path = filedialog.askdirectory(title="デフォルト出力ディレクトリを選択")
        if dir_path:
            self.default_output_dir.set(dir_path)
    
    def _load_settings(self) -> Dict[str, Any]:
        """設定ファイルを読み込み"""
        settings_file = Path.home() / ".attendance_tool" / "settings.json"
        
        default_settings = {
            "default_input_dir": str(Path.home()),
            "default_output_dir": str(Path.home() / "Documents"),
            "auto_backup": True,
            "csv_encoding": "utf-8-sig",
            "date_format": "YYYY-MM-DD",
            "max_file_size": 100,
            "output_csv": True,
            "output_excel": False,
            "filename_template": "attendance_report_{YYYY}_{MM}",
            "add_timestamp": False
        }
        
        try:
            if settings_file.exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # デフォルト設定とマージ
                default_settings.update(settings)
            return default_settings
        except Exception:
            return default_settings
    
    def _save_settings(self) -> bool:
        """設定ファイルに保存"""
        try:
            settings_file = Path.home() / ".attendance_tool" / "settings.json"
            settings_file.parent.mkdir(exist_ok=True)
            
            settings = {
                "default_input_dir": self.default_input_dir.get(),
                "default_output_dir": self.default_output_dir.get(),
                "auto_backup": self.auto_backup.get(),
                "csv_encoding": self.csv_encoding.get(),
                "date_format": self.date_format.get(),
                "max_file_size": int(self.max_file_size.get()),
                "output_csv": self.output_csv.get(),
                "output_excel": self.output_excel.get(),
                "filename_template": self.filename_template.get(),
                "add_timestamp": self.add_timestamp.get()
            }
            
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            self.settings = settings
            return True
            
        except Exception as e:
            messagebox.showerror("エラー", f"設定の保存に失敗しました:\n{str(e)}")
            return False
    
    def _load_current_settings(self):
        """現在の設定をGUIに反映"""
        self.default_input_dir.set(self.settings.get("default_input_dir", ""))
        self.default_output_dir.set(self.settings.get("default_output_dir", ""))
        self.auto_backup.set(self.settings.get("auto_backup", True))
        self.csv_encoding.set(self.settings.get("csv_encoding", "utf-8-sig"))
        self.date_format.set(self.settings.get("date_format", "YYYY-MM-DD"))
        self.max_file_size.set(str(self.settings.get("max_file_size", 100)))
        self.output_csv.set(self.settings.get("output_csv", True))
        self.output_excel.set(self.settings.get("output_excel", False))
        self.filename_template.set(self.settings.get("filename_template", "attendance_report_{YYYY}_{MM}"))
        self.add_timestamp.set(self.settings.get("add_timestamp", False))
    
    def _save_and_close(self):
        """設定を保存して閉じる"""
        if self._apply_settings():
            self.window.destroy()
    
    def _cancel(self):
        """変更を破棄して閉じる"""
        self.window.destroy()
    
    def _apply_settings(self) -> bool:
        """設定を適用"""
        # 入力値の検証
        try:
            max_size = int(self.max_file_size.get())
            if max_size <= 0:
                raise ValueError("ファイルサイズは正の数値である必要があります")
        except ValueError as e:
            messagebox.showerror("入力エラー", str(e))
            return False
        
        # 少なくとも一つの出力形式が選択されているかチェック
        if not (self.output_csv.get() or self.output_excel.get()):
            messagebox.showerror("入力エラー", "少なくとも一つの出力形式を選択してください")
            return False
        
        # 設定を保存
        if self._save_settings():
            messagebox.showinfo("設定", "設定を保存しました")
            return True
        return False
    
    def _reset_to_default(self):
        """デフォルト設定に戻す"""
        result = messagebox.askyesno("確認", "設定をデフォルトに戻しますか？")
        if result:
            self.settings = self._load_settings()  # デフォルト設定を再読み込み
            self._load_current_settings()  # GUIに反映
            messagebox.showinfo("設定", "設定をデフォルトに戻しました")
    
    def get_setting(self, key: str, default=None):
        """設定値を取得
        
        Args:
            key: 設定キー
            default: デフォルト値
            
        Returns:
            設定値
        """
        return self.settings.get(key, default)