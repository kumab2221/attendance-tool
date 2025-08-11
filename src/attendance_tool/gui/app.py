"""
勤怠管理ツール GUI アプリケーション

メインエントリーポイントです。
"""

import logging
import sys
from pathlib import Path

from .main_window import MainWindow


def setup_logging():
    """ログを設定"""
    log_dir = Path.home() / ".attendance_tool" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "gui.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def main():
    """GUIアプリケーションのメイン関数"""
    try:
        # ログ設定
        setup_logging()

        # メインウィンドウを作成・実行
        app = MainWindow()
        app.run()

    except ImportError as e:
        print(f"GUI環境が利用できません: {e}")
        print("GUI機能を使用するには、デスクトップ環境が必要です。")
        sys.exit(1)
    except Exception as e:
        print(f"アプリケーションの開始に失敗しました: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
