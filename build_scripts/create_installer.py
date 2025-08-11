"""
NSIS インストーラー作成スクリプト

PyInstallerで作成した実行ファイルからWindowsインストーラーを作成します。
"""

import os
import sys
import subprocess
from pathlib import Path


def check_nsis_installed():
    """NSISがインストールされているかを確認"""
    try:
        result = subprocess.run(["makensis", "/VERSION"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"NSIS が見つかりました: {result.stdout.strip()}")
            return True
        else:
            return False
    except FileNotFoundError:
        return False


def create_installer():
    """NSISインストーラーを作成"""
    
    print("=== NSIS インストーラー作成開始 ===")
    
    # 1. NSISの確認
    if not check_nsis_installed():
        print("エラー: NSISがインストールされていません。")
        print("https://nsis.sourceforge.io/ からNSISをダウンロード・インストールしてください。")
        return False
    
    # 2. 必要ファイルの確認
    required_files = [
        Path("dist/attendance-tool-cli.exe"),
        Path("dist/attendance-tool-gui.exe"),
        Path("LICENSE"),
        Path("build_scripts/create_installer.nsi")
    ]
    
    for file_path in required_files:
        if not file_path.exists():
            print(f"エラー: 必要ファイルが見つかりません: {file_path}")
            return False
    
    print("必要ファイルの確認完了")
    
    # 3. NSISスクリプトの実行
    nsi_script = Path("build_scripts/create_installer.nsi")
    
    try:
        print("NSISインストーラーをコンパイル中...")
        result = subprocess.run([
            "makensis",
            "/V3",  # 詳細出力
            str(nsi_script)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("インストーラーの作成に成功しました！")
            print(f"出力ファイル: dist/AttendanceTool-0.1.0-Setup.exe")
            
            # ファイルサイズを表示
            installer_path = Path("dist/AttendanceTool-0.1.0-Setup.exe")
            if installer_path.exists():
                size_mb = installer_path.stat().st_size / (1024 * 1024)
                print(f"インストーラーサイズ: {size_mb:.2f} MB")
            
            return True
        else:
            print("インストーラーの作成に失敗しました:")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
    
    except Exception as e:
        print(f"NSISの実行中にエラーが発生しました: {e}")
        return False


def main():
    """メインプロセス"""
    
    # プロジェクトルートディレクトリに移動
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    success = create_installer()
    
    if success:
        print("\n=== インストーラー作成完了 ===")
        
        # distディレクトリの内容を表示
        dist_dir = Path("dist")
        if dist_dir.exists():
            print("\n作成されたファイル:")
            for file in dist_dir.iterdir():
                if file.is_file():
                    size_mb = file.stat().st_size / (1024 * 1024)
                    print(f"  {file.name}: {size_mb:.2f} MB")
    else:
        print("インストーラー作成に失敗しました。")
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)