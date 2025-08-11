#!/usr/bin/env python3
"""
コード複雑度チェックスクリプト - lizardを使用

使用方法:
    python scripts/complexity_check.py [オプション]
    
オプション:
    --threshold <number>  : 循環的複雑度の閾値 (デフォルト: 10)
    --output <path>       : レポート出力ファイル
    --format <format>     : 出力形式 (html, xml, csv, json)
    --verbose            : 詳細出力
    --ci                 : CI用（閾値超過時に非ゼロ終了）
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import json


def run_lizard(source_dirs, threshold=10, output_file=None, output_format="text", verbose=False):
    """lizardを実行してコード複雑度を測定
    
    Args:
        source_dirs: ソースコードディレクトリのリスト
        threshold: 複雑度の閾値
        output_file: 出力ファイルパス
        output_format: 出力形式
        verbose: 詳細出力フラグ
        
    Returns:
        (return_code, stdout, stderr)
    """
    cmd = ["lizard", "--CCN", str(threshold)]
    
    # 出力形式設定
    if output_format == "html":
        cmd.extend(["--html"])
    elif output_format == "xml":
        cmd.extend(["--xml"])
    elif output_format == "csv":
        cmd.extend(["--csv"])
    elif output_format == "json":
        # lizardはjson直接サポートしていないので、後で変換
        pass
    
    # 詳細出力
    if verbose:
        cmd.extend(["-v"])
    
    # ソースディレクトリを追加
    cmd.extend(source_dirs)
    
    # 実行
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        # 出力ファイルに保存
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.stdout)
        
        return result.returncode, result.stdout, result.stderr
        
    except FileNotFoundError:
        print("エラー: lizardがインストールされていません。", file=sys.stderr)
        print("インストール: pip install lizard", file=sys.stderr)
        return 1, "", "lizard not found"


def generate_summary_report(stdout, output_dir):
    """サマリーレポートを生成
    
    Args:
        stdout: lizardの標準出力
        output_dir: 出力ディレクトリ
    """
    lines = stdout.split('\n')
    
    # 統計情報を抽出
    stats = {
        "timestamp": datetime.now().isoformat(),
        "total_lines": 0,
        "total_functions": 0,
        "high_complexity_functions": 0,
        "max_complexity": 0,
        "average_complexity": 0,
        "complexity_distribution": {"low": 0, "medium": 0, "high": 0, "very_high": 0}
    }
    
    complexity_values = []
    high_complexity_functions = []
    
    for line in lines:
        if "NLOC" in line and "CCN" in line and "token" in line:
            # 統計行をスキップ
            continue
        elif line.strip().startswith(("Total", "Average")):
            # 統計サマリー行を解析
            if "Total" in line:
                parts = line.split()
                if len(parts) >= 4:
                    try:
                        stats["total_lines"] = int(parts[1])
                        stats["total_functions"] = int(parts[3])
                    except (ValueError, IndexError):
                        pass
        elif line.strip() and not line.startswith("=") and not line.startswith("-"):
            # 関数の複雑度行を解析
            parts = line.split()
            if len(parts) >= 3:
                try:
                    complexity = int(parts[0])
                    complexity_values.append(complexity)
                    
                    if complexity > 10:
                        function_info = {
                            "complexity": complexity,
                            "function": " ".join(parts[3:]) if len(parts) > 3 else "unknown",
                            "file": parts[1] if len(parts) > 1 else "unknown"
                        }
                        high_complexity_functions.append(function_info)
                        stats["high_complexity_functions"] += 1
                    
                    # 複雑度分布
                    if complexity <= 5:
                        stats["complexity_distribution"]["low"] += 1
                    elif complexity <= 10:
                        stats["complexity_distribution"]["medium"] += 1
                    elif complexity <= 20:
                        stats["complexity_distribution"]["high"] += 1
                    else:
                        stats["complexity_distribution"]["very_high"] += 1
                        
                except ValueError:
                    pass
    
    # 統計計算
    if complexity_values:
        stats["max_complexity"] = max(complexity_values)
        stats["average_complexity"] = round(sum(complexity_values) / len(complexity_values), 2)
    
    # JSONサマリーを保存
    summary_file = Path(output_dir) / "complexity_summary.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "stats": stats,
            "high_complexity_functions": high_complexity_functions
        }, f, indent=2, ensure_ascii=False)
    
    print(f"✅ サマリーレポートを生成しました: {summary_file}")
    
    return stats


def main():
    parser = argparse.ArgumentParser(
        description="コード複雑度チェックツール (lizard使用)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
    python scripts/complexity_check.py
    python scripts/complexity_check.py --threshold 15 --output reports/complexity.html --format html
    python scripts/complexity_check.py --ci --threshold 10
        """
    )
    
    parser.add_argument(
        "--threshold", "-t",
        type=int,
        default=10,
        help="循環的複雑度の閾値 (デフォルト: 10)"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="レポート出力ファイル"
    )
    
    parser.add_argument(
        "--format", "-f",
        choices=["text", "html", "xml", "csv"],
        default="text",
        help="出力形式 (デフォルト: text)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="詳細出力"
    )
    
    parser.add_argument(
        "--ci",
        action="store_true",
        help="CI用モード（複雑度が閾値を超えると非ゼロで終了）"
    )
    
    args = parser.parse_args()
    
    # ソースディレクトリを設定
    source_dirs = ["src/attendance_tool"]
    
    # 出力ディレクトリを作成
    output_dir = Path("reports/complexity")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # デフォルト出力ファイル設定
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if args.format == "html":
            args.output = output_dir / f"complexity_{timestamp}.html"
        elif args.format == "xml":
            args.output = output_dir / f"complexity_{timestamp}.xml"
        elif args.format == "csv":
            args.output = output_dir / f"complexity_{timestamp}.csv"
        else:
            args.output = output_dir / f"complexity_{timestamp}.txt"
    
    print(f"🔍 コード複雑度チェックを開始...")
    print(f"   対象: {', '.join(source_dirs)}")
    print(f"   閾値: {args.threshold}")
    print(f"   出力: {args.output}")
    print(f"   形式: {args.format}")
    
    # lizardを実行
    return_code, stdout, stderr = run_lizard(
        source_dirs=source_dirs,
        threshold=args.threshold,
        output_file=args.output,
        output_format=args.format,
        verbose=args.verbose
    )
    
    if return_code != 0:
        print(f"❌ lizard実行でエラーが発生しました (終了コード: {return_code})")
        if stderr:
            print(f"エラー詳細: {stderr}")
        return return_code
    
    # サマリーレポート生成
    stats = generate_summary_report(stdout, output_dir)
    
    # 結果表示
    print(f"\n📊 複雑度分析結果:")
    print(f"   総関数数: {stats['total_functions']}")
    print(f"   高複雑度関数数: {stats['high_complexity_functions']}")
    print(f"   最大複雑度: {stats['max_complexity']}")
    print(f"   平均複雑度: {stats['average_complexity']}")
    
    # 複雑度分布
    dist = stats["complexity_distribution"]
    print(f"\n📈 複雑度分布:")
    print(f"   低 (≤5):    {dist['low']}")
    print(f"   中 (6-10):  {dist['medium']}")  
    print(f"   高 (11-20): {dist['high']}")
    print(f"   超高 (>20): {dist['very_high']}")
    
    # CI用チェック
    if args.ci:
        if stats['high_complexity_functions'] > 0:
            print(f"\n❌ CI失敗: {stats['high_complexity_functions']}個の関数が複雑度閾値({args.threshold})を超過")
            return 1
        else:
            print(f"\n✅ CI成功: すべての関数が複雑度閾値({args.threshold})以下")
    
    print(f"\n📄 詳細レポート: {args.output}")
    
    return return_code


if __name__ == "__main__":
    sys.exit(main())