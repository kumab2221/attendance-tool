"""
プログレス表示ウィンドウ

処理の進捗状況を視覚的に表示するウィンドウを提供します。
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional
import time


class ProgressWindow:
    """プログレス表示ウィンドウクラス"""

    def __init__(self, parent=None, title: str = "処理中..."):
        """プログレスウィンドウを初期化

        Args:
            parent: 親ウィンドウ
            title: ウィンドウタイトル
        """
        self.parent = parent
        self.window = tk.Toplevel(parent) if parent else tk.Tk()
        self.window.title(title)
        self.window.geometry("400x150")
        self.window.resizable(False, False)

        # ウィンドウを中央に配置
        self._center_window()

        # ウィンドウを最前面に
        self.window.transient(parent)
        self.window.grab_set()

        # GUI要素を作成
        self._create_widgets()

        # 初期状態
        self.current_progress = 0
        self.is_closed = False

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
        # メインフレーム
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # メッセージラベル
        self.message_label = ttk.Label(
            main_frame, text="処理を開始しています...", font=("", 10)
        )
        self.message_label.pack(pady=(0, 10))

        # プログレスバー
        self.progress_bar = ttk.Progressbar(
            main_frame, length=300, mode="determinate", maximum=100
        )
        self.progress_bar.pack(pady=(0, 10))

        # パーセンテージラベル
        self.percent_label = ttk.Label(main_frame, text="0%", font=("", 9))
        self.percent_label.pack()

        # キャンセルボタン（オプション）
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(10, 0))

        self.cancel_button = ttk.Button(
            button_frame,
            text="キャンセル",
            command=self._on_cancel,
            state="disabled",  # 初期は無効
        )
        self.cancel_button.pack()

        # キャンセルフラグ
        self.cancel_requested = False

    def update_progress(self, progress: int, message: str = ""):
        """プログレスを更新

        Args:
            progress: 進捗率（0-100）
            message: 表示メッセージ
        """
        if self.is_closed:
            return

        # 進捗率の範囲チェック
        progress = max(0, min(100, progress))
        self.current_progress = progress

        # プログレスバーを更新
        self.progress_bar["value"] = progress

        # パーセンテージラベルを更新
        self.percent_label.config(text=f"{progress}%")

        # メッセージを更新
        if message:
            self.message_label.config(text=message)

        # キャンセルボタンの状態を更新
        if progress > 0 and progress < 100:
            self.cancel_button.config(state="normal")
        else:
            self.cancel_button.config(state="disabled")

        # ウィンドウを更新
        self.window.update_idletasks()

        # 完了時の処理
        if progress >= 100:
            self.message_label.config(text="処理が完了しました")
            self.window.after(2000, self.close)  # 2秒後に自動的に閉じる

    def set_indeterminate(self, message: str = "処理中..."):
        """不確定プログレス（無限ループ）に設定

        Args:
            message: 表示メッセージ
        """
        if self.is_closed:
            return

        self.progress_bar.config(mode="indeterminate")
        self.progress_bar.start(10)  # アニメーション開始
        self.message_label.config(text=message)
        self.percent_label.config(text="")
        self.cancel_button.config(state="normal")

    def set_determinate(self):
        """確定プログレスに戻す"""
        if self.is_closed:
            return

        self.progress_bar.stop()  # アニメーション停止
        self.progress_bar.config(mode="determinate")
        self.progress_bar["value"] = self.current_progress
        self.percent_label.config(text=f"{self.current_progress}%")

    def _on_cancel(self):
        """キャンセルボタンが押された時の処理"""
        result = tk.messagebox.askyesno("確認", "処理をキャンセルしますか？")
        if result:
            self.cancel_requested = True
            self.message_label.config(text="キャンセル中...")
            self.cancel_button.config(state="disabled")

    def is_cancelled(self) -> bool:
        """キャンセルが要求されているかチェック

        Returns:
            キャンセル要求の有無
        """
        return self.cancel_requested

    def close(self):
        """ウィンドウを閉じる"""
        if not self.is_closed:
            self.is_closed = True
            try:
                self.window.grab_release()
                self.window.destroy()
            except tk.TclError:
                # ウィンドウが既に破棄されている場合
                pass

    def show(self):
        """ウィンドウを表示（モードレス）"""
        if not self.is_closed:
            self.window.deiconify()
            self.window.lift()

    def hide(self):
        """ウィンドウを非表示"""
        if not self.is_closed:
            self.window.withdraw()
