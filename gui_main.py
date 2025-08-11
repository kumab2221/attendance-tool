#!/usr/bin/env python3
"""
Attendance Tool GUI スタンドアロンエントリーポイント

PyInstallerビルド用のスタンドアロンエントリーポイント
"""

if __name__ == "__main__":
    try:
        from attendance_tool.gui.app import main
        main()
    except ImportError:
        import sys
        print("ERROR: attendance_tool package not found")
        print("Please ensure the package is properly installed.")
        sys.exit(1)