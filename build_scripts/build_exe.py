"""
PyInstaller用ビルドスクリプト

スタンドアロン実行ファイルを作成します。
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def clean_build_dirs():
    """ビルド用一時ディレクトリをクリーンアップ"""
    dirs_to_clean = ['build', 'dist']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            print(f"クリーンアップ中: {dir_name}")
            shutil.rmtree(dir_name)


def build_cli_executable():
    """CLI版の実行ファイルを作成"""
    spec_file = "attendance_tool_cli.spec"
    
    # PyInstallerコマンドを構築
    cmd = [
        "pyinstaller",
        "--name=attendance-tool-cli",
        "--onefile",
        "--console",
        "--add-data=config;attendance_tool/config",
        "--add-data=templates;attendance_tool/templates",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=yaml",
        "--hidden-import=click",
        "--hidden-import=pydantic",
        "--hidden-import=dateutil",
        "--hidden-import=tqdm",
        "cli_main.py"
    ]
    
    print("CLI版実行ファイルをビルド中...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("CLI版ビルド完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"CLI版ビルドエラー: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def build_gui_executable():
    """GUI版の実行ファイルを作成"""
    
    # PyInstallerコマンドを構築
    cmd = [
        "pyinstaller",
        "--name=attendance-tool-gui",
        "--onefile",
        "--windowed",
        "--add-data=config;attendance_tool/config",
        "--add-data=templates;attendance_tool/templates",
        "--hidden-import=pandas",
        "--hidden-import=openpyxl",
        "--hidden-import=yaml",
        "--hidden-import=click",
        "--hidden-import=pydantic",
        "--hidden-import=dateutil",
        "--hidden-import=tqdm",
        "--hidden-import=tkinter",
        "--hidden-import=PIL",
        "gui_main.py"
    ]
    
    print("GUI版実行ファイルをビルド中...")
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("GUI版ビルド完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"GUI版ビルドエラー: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


def copy_additional_files():
    """実行ファイルと一緒に配布するファイルをコピー"""
    dist_dir = Path("dist")
    
    # README、ライセンス等をコピー
    files_to_copy = [
        "README.md",
        "LICENSE",
        "CHANGELOG.md",
    ]
    
    for file_name in files_to_copy:
        src_file = Path(file_name)
        if src_file.exists():
            dst_file = dist_dir / file_name
            print(f"コピー中: {file_name}")
            shutil.copy2(src_file, dst_file)
    
    # 設定ファイルサンプルをコピー
    config_dir = dist_dir / "config_samples"
    config_dir.mkdir(exist_ok=True)
    
    src_config_dir = Path("config")
    if src_config_dir.exists():
        for config_file in src_config_dir.glob("*.yaml"):
            dst_file = config_dir / config_file.name
            print(f"設定サンプルコピー中: {config_file.name}")
            shutil.copy2(config_file, dst_file)


def create_version_info():
    """バージョン情報ファイルを作成"""
    version = "0.1.0"  # pyproject.tomlから取得
    
    version_info = f"""# Attendance Tool v{version}

## ビルド情報
- Python バージョン: {sys.version}
- ビルド日時: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- プラットフォーム: {sys.platform}

## 実行ファイル
- attendance-tool-cli.exe: コマンドライン版
- attendance-tool-gui.exe: GUI版

## 使用方法
詳細な使用方法は README.md をご確認ください。
"""
    
    with open("dist/VERSION.txt", "w", encoding="utf-8") as f:
        f.write(version_info)


def main():
    """メインビルドプロセス"""
    print("=== Attendance Tool ビルドプロセス開始 ===")
    
    # 1. クリーンアップ
    clean_build_dirs()
    
    # 2. PyInstallerが利用可能か確認
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        print("PyInstaller が見つかりました")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("エラー: PyInstallerがインストールされていません。")
        print("pip install pyinstaller を実行してください。")
        return False
    
    # 3. CLI版ビルド
    cli_success = build_cli_executable()
    
    # 4. GUI版ビルド
    gui_success = build_gui_executable()
    
    # 5. 追加ファイルのコピー
    if cli_success or gui_success:
        copy_additional_files()
        create_version_info()
        
        print("=== ビルド完了 ===")
        print("実行ファイルは dist/ ディレクトリに作成されました。")
        
        # ファイルサイズ確認
        dist_dir = Path("dist")
        if dist_dir.exists():
            print("\n作成されたファイル:")
            for file in dist_dir.iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  {file.name}: {size_mb:.2f} MB")
    else:
        print("ビルドに失敗しました。")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)