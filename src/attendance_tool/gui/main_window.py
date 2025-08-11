"""
メインウィンドウクラス

勤怠管理ツールのメインGUIウィンドウを提供します。
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
from typing import Optional, Callable
import logging
import threading

from .file_dialogs import FileDialogs
from .progress_window import ProgressWindow
from .settings_window import SettingsWindow


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self):
        """メインウィンドウを初期化"""
        self.root = tk.Tk()
        self.root.title("勤怠管理ツール")
        self.root.geometry("800x600")
        
        # 変数の初期化（GUI要素作成前に実行）
        self.input_file_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()
        
        # コンポーネントの初期化
        self.file_dialogs = FileDialogs()
        self.progress_window = None
        self.settings_window = None
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        
        # GUI要素の作成
        self._create_widgets()
        
    def _create_widgets(self):
        """GUI要素を作成"""
        # メニューバー
        self._create_menu_bar()
        
        # メインフレーム
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ファイル選択フレーム
        self._create_file_selection_frame(main_frame)
        
        # オプションフレーム
        self._create_options_frame(main_frame)
        
        # 実行ボタンフレーム
        self._create_execute_frame(main_frame)
        
        # ログ表示フレーム
        self._create_log_frame(main_frame)
        
        # グリッドの重みを設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
    
    def _create_menu_bar(self):
        """メニューバーを作成"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # ファイルメニュー
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ファイル", menu=file_menu)
        file_menu.add_command(label="終了", command=self.root.quit)
        
        # 設定メニュー
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="設定", menu=settings_menu)
        settings_menu.add_command(label="設定を開く", command=self.open_settings)
        
        # ヘルプメニュー
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="ヘルプ", menu=help_menu)
        help_menu.add_command(label="バージョン情報", command=self._show_about)
    
    def _create_file_selection_frame(self, parent):
        """ファイル選択フレームを作成"""
        frame = ttk.LabelFrame(parent, text="ファイル選択", padding="5")
        frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 入力ファイル
        ttk.Label(frame, text="入力CSVファイル:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.input_entry = ttk.Entry(frame, textvariable=self.input_file_path, width=60)
        self.input_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(frame, text="参照", command=self.select_input_file).grid(row=0, column=2, padx=5, pady=2)
        
        # 出力ディレクトリ
        ttk.Label(frame, text="出力ディレクトリ:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.output_entry = ttk.Entry(frame, textvariable=self.output_dir_path, width=60)
        self.output_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=5, pady=2)
        ttk.Button(frame, text="参照", command=self.select_output_directory).grid(row=1, column=2, padx=5, pady=2)
        
        frame.columnconfigure(1, weight=1)
    
    def _create_options_frame(self, parent):
        """オプションフレームを作成"""
        frame = ttk.LabelFrame(parent, text="処理オプション", padding="5")
        frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # 対象月
        ttk.Label(frame, text="対象月:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.month_var = tk.StringVar(value="2024-01")
        month_entry = ttk.Entry(frame, textvariable=self.month_var, width=20)
        month_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
    
    def _create_execute_frame(self, parent):
        """実行ボタンフレームを作成"""
        frame = ttk.Frame(parent)
        frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        self.execute_button = ttk.Button(
            frame, 
            text="集計実行", 
            command=self._execute_processing,
            style="Accent.TButton"
        )
        self.execute_button.pack()
    
    def _create_log_frame(self, parent):
        """ログ表示フレームを作成"""
        frame = ttk.LabelFrame(parent, text="実行ログ", padding="5")
        frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        # ログテキストエリア
        self.log_text = scrolledtext.ScrolledText(frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ログクリアボタン
        ttk.Button(frame, text="ログクリア", command=self._clear_log).grid(row=1, column=0, pady=5)
        
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)
    
    def select_input_file(self) -> Optional[str]:
        """入力CSVファイルを選択"""
        file_path = self.file_dialogs.select_csv_file()
        if file_path:
            self.input_file_path.set(file_path)
            self.add_log(f"入力ファイルを選択: {file_path}")
        return file_path
    
    def select_output_directory(self) -> Optional[str]:
        """出力ディレクトリを選択"""
        dir_path = self.file_dialogs.select_output_directory()
        if dir_path:
            self.output_dir_path.set(dir_path)
            self.add_log(f"出力ディレクトリを選択: {dir_path}")
        return dir_path
    
    def show_progress(self, progress: int, message: str):
        """プログレスを表示"""
        if not self.progress_window:
            self.progress_window = ProgressWindow()
        self.progress_window.update_progress(progress, message)
    
    def open_settings(self):
        """設定画面を開く"""
        if not self.settings_window or not self.settings_window.window.winfo_exists():
            self.settings_window = SettingsWindow()
        else:
            self.settings_window.window.lift()
    
    def add_log(self, message: str, level: str = "info"):
        """ログメッセージを追加"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        if level == "error":
            log_message = f"[{timestamp}] ERROR: {message}\n"
        elif level == "warning":
            log_message = f"[{timestamp}] WARNING: {message}\n"
        else:
            log_message = f"[{timestamp}] INFO: {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
        # ファイルログにも出力
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def _execute_processing(self):
        """集計処理を実行"""
        input_file = self.input_file_path.get()
        output_dir = self.output_dir_path.get()
        target_month = self.month_var.get()
        
        # 入力検証
        if not input_file:
            messagebox.showerror("エラー", "入力CSVファイルを選択してください")
            return
        
        if not output_dir:
            messagebox.showerror("エラー", "出力ディレクトリを選択してください")
            return
        
        # ファイル存在チェック
        if not Path(input_file).exists():
            messagebox.showerror("エラー", "入力ファイルが存在しません")
            return
        
        # バックグラウンドで実行
        self.execute_button.config(state="disabled")
        self.add_log(f"集計処理を開始します（対象月: {target_month}）")
        
        def execute_in_background():
            try:
                self._run_attendance_processing(input_file, output_dir, target_month)
            except Exception as e:
                self.add_log(f"処理中にエラーが発生しました: {str(e)}", "error")
            finally:
                self.execute_button.config(state="normal")
                if self.progress_window:
                    self.progress_window.close()
        
        # バックグラウンドで実行
        thread = threading.Thread(target=execute_in_background, daemon=True)
        thread.start()
    
    def _run_attendance_processing(self, input_file: str, output_dir: str, target_month: str):
        """勤怠集計処理の実行（簡易版）"""
        from attendance_tool.e2e.workflow_coordinator import E2EWorkflowCoordinator
        
        # プログレス表示
        self.show_progress(10, "CSVファイルを読み込み中...")
        
        coordinator = E2EWorkflowCoordinator()
        result = coordinator.execute_complete_workflow(
            Path(input_file), Path(output_dir), target_month
        )
        
        self.show_progress(50, "データを検証中...")
        self.show_progress(80, "レポートを生成中...")
        
        if result["status"] == "success":
            self.show_progress(100, "処理完了")
            self.add_log(f"処理が正常に完了しました")
            self.add_log(f"出力ファイル: {result['output_file']}")
            self.add_log(f"処理レコード数: {result['records_processed']}")
            messagebox.showinfo("完了", "集計処理が完了しました")
        else:
            self.add_log(f"処理中にエラーが発生しました: {result['error_message']}", "error")
            messagebox.showerror("エラー", f"処理中にエラーが発生しました:\n{result['error_message']}")
    
    def _clear_log(self):
        """ログをクリア"""
        self.log_text.delete(1.0, tk.END)
        self.add_log("ログをクリアしました")
    
    def _show_about(self):
        """バージョン情報を表示"""
        about_text = """勤怠管理ツール v0.1.0

CSV形式の勤怠データを読み込み、
月次集計レポートを生成します。

© 2024 Attendance Tool Development Team"""
        messagebox.showinfo("バージョン情報", about_text)
    
    def run(self):
        """アプリケーションを実行"""
        self.add_log("勤怠管理ツールを開始しました")
        self.root.mainloop()