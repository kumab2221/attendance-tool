"""
ビルド機能テストスクリプト

PyInstallerやビルドプロセスが正常に実行できるかテストします。
"""

import os
import sys
import subprocess
from pathlib import Path


def test_python_environment():
    """Python環境の確認"""
    print("=== Python環境テスト ===")
    print(f"Python バージョン: {sys.version}")
    print(f"プラットフォーム: {sys.platform}")
    print(f"実行パス: {sys.executable}")
    
    # パッケージの確認
    try:
        sys.path.insert(0, "src")
        from attendance_tool import __version__
        print(f"パッケージバージョン: {__version__}")
        return True
    except ImportError as e:
        print(f"パッケージインポートエラー: {e}")
        return False


def test_dependencies():
    """依存関係の確認"""
    print("\n=== 依存関係テスト ===")
    
    required_packages = [
        "pandas", "openpyxl", "click", "pydantic", 
        "python-dateutil", "pyyaml", "tqdm"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (未インストール)")
            missing_packages.append(package)
    
    return len(missing_packages) == 0


def test_gui_imports():
    """GUI関連のインポートテスト"""
    print("\n=== GUIインポートテスト ===")
    
    try:
        sys.path.insert(0, "src")
        from attendance_tool.gui.app import main
        from attendance_tool.gui.main_window import MainWindow
        from attendance_tool.gui.file_dialogs import FileDialogs
        print("✓ GUI関連モジュール正常")
        return True
    except ImportError as e:
        print(f"✗ GUIインポートエラー: {e}")
        return False


def test_cli_imports():
    """CLI関連のインポートテスト"""
    print("\n=== CLIインポートテスト ===")
    
    try:
        sys.path.insert(0, "src")
        from attendance_tool.cli import main
        print("✓ CLI関連モジュール正常")
        return True
    except ImportError as e:
        print(f"✗ CLIインポートエラー: {e}")
        return False


def test_pyinstaller_available():
    """PyInstallerの確認"""
    print("\n=== PyInstallerテスト ===")
    
    try:
        result = subprocess.run(
            ["pyinstaller", "--version"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ PyInstaller: {result.stdout.strip()}")
            return True
        else:
            print("✗ PyInstaller実行エラー")
            return False
    except subprocess.TimeoutExpired:
        print("✗ PyInstaller実行タイムアウト")
        return False
    except FileNotFoundError:
        print("✗ PyInstallerが見つかりません")
        print("  pip install pyinstaller でインストールしてください")
        return False


def test_build_script():
    """ビルドスクリプトの構文確認"""
    print("\n=== ビルドスクリプトテスト ===")
    
    build_script = Path("build_scripts/build_exe.py")
    if not build_script.exists():
        print("✗ build_exe.pyが見つかりません")
        return False
    
    try:
        # 構文チェックのみ（実行はしない）
        with open(build_script, 'r', encoding='utf-8') as f:
            compile(f.read(), str(build_script), 'exec')
        print("✓ build_exe.py 構文正常")
        return True
    except SyntaxError as e:
        print(f"✗ build_exe.py 構文エラー: {e}")
        return False


def test_nsis_script():
    """NSISスクリプトの確認"""
    print("\n=== NSISスクリプトテスト ===")
    
    nsis_script = Path("build_scripts/create_installer.nsi")
    if not nsis_script.exists():
        print("✗ create_installer.nsiが見つかりません")
        return False
    
    print("✓ create_installer.nsi 存在確認")
    
    # NSIS がインストールされているかチェック
    try:
        result = subprocess.run(
            ["makensis", "/VERSION"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(f"✓ NSIS: {result.stdout.strip()}")
            return True
        else:
            print("⚠ NSISはインストールされていますが、実行に問題があります")
            return True  # スクリプト自体は存在するので True
    except FileNotFoundError:
        print("⚠ NSISがインストールされていません（インストーラー作成時に必要）")
        return True  # NSISなしでもビルドは可能


def main():
    """メインテスト実行"""
    print("Attendance Tool ビルド環境テスト")
    print("=" * 50)
    
    tests = [
        ("Python環境", test_python_environment),
        ("依存関係", test_dependencies),
        ("GUIインポート", test_gui_imports),
        ("CLIインポート", test_cli_imports),
        ("PyInstaller", test_pyinstaller_available),
        ("ビルドスクリプト", test_build_script),
        ("NSISスクリプト", test_nsis_script),
    ]
    
    results = {}
    for name, test_func in tests:
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"✗ {name}テストで予期しないエラー: {e}")
            results[name] = False
    
    # 結果サマリー
    print("\n" + "=" * 50)
    print("テスト結果サマリー")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for name, result in results.items():
        status = "✓ 合格" if result else "✗ 失敗"
        print(f"{name:15}: {status}")
        if result:
            passed += 1
    
    print(f"\n合格: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 すべてのテストに合格しました！")
        print("ビルドプロセスを実行できます。")
        return True
    else:
        print(f"\n⚠ {total - passed}個のテストが失敗しました。")
        print("失敗した項目を修正してからビルドを実行してください。")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)