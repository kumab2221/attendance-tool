"""CLIバリデーション機能"""

import click
import os
import re
from pathlib import Path
from datetime import datetime


class ValidationError(click.BadParameter):
    """バリデーションエラー"""
    pass


def validate_option_combinations(month, start_date, end_date, year, quiet, verbose):
    """オプション組み合わせのバリデーション
    
    Args:
        month: 月指定 (str or None)
        start_date: 開始日 (str or None)
        end_date: 終了日 (str or None)
        year: 年指定 (int or None)
        quiet: 静寂モード (bool)
        verbose: 詳細モード (int)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    # 期間指定オプションの排他制御
    if month and (start_date or end_date):
        raise ValidationError("--monthと--start-date/--end-dateは同時に指定できません")
    
    if year and (start_date or end_date or month):
        raise ValidationError("--yearは他の期間指定オプションと同時に指定できません")
    
    # start-date/end-dateの依存関係
    if start_date and not end_date:
        raise ValidationError("--start-dateを指定する場合は--end-dateも必須です")
    
    if end_date and not start_date:
        raise ValidationError("--end-dateを指定する場合は--start-dateも必須です")
    
    # quietとverboseの競合
    if quiet and verbose:
        raise ValidationError("--quietと--verboseは同時に指定できません")


def validate_input_file(input_file):
    """入力ファイルのバリデーション
    
    Args:
        input_file: 入力ファイルパス (Path)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    # ファイル拡張子チェック
    if not input_file.suffix.lower() == '.csv':
        raise ValidationError(f"入力ファイルはCSV形式である必要があります: {input_file}")
    
    # ファイルが読み込み可能かチェック
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            # 最初の行だけ読んで確認
            first_line = f.readline().strip()
            if not first_line:
                raise ValidationError(f"入力ファイルが空です: {input_file}")
    except PermissionError:
        raise ValidationError(f"入力ファイルの読み込み権限がありません: {input_file}")
    except UnicodeDecodeError:
        # UTF-8で読めない場合は別のエンコーディングを試す
        try:
            with open(input_file, 'r', encoding='shift_jis') as f:
                first_line = f.readline().strip()
                if not first_line:
                    raise ValidationError(f"入力ファイルが空です: {input_file}")
            click.echo("警告: ファイルのエンコーディングがShift_JISです。UTF-8を推奨します。")
        except Exception:
            raise ValidationError(f"入力ファイルのエンコーディングが不正です: {input_file}")
    except Exception as e:
        raise ValidationError(f"入力ファイルの読み込みに失敗しました: {input_file}, エラー: {e}")


def validate_month_format(month):
    """月形式のバリデーション
    
    Args:
        month: 月指定文字列 (str)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    # YYYY-MM形式のチェック
    if not re.match(r'^\d{4}-\d{2}$', month):
        raise ValidationError(f"月の形式はYYYY-MMである必要があります: {month}")
    
    try:
        year, month_num = month.split('-')
        year = int(year)
        month_num = int(month_num)
        
        # 年の範囲チェック
        if year < 2020 or year > 2030:
            raise ValidationError(f"年は2020-2030の範囲である必要があります: {year}")
        
        # 月の範囲チェック
        if month_num < 1 or month_num > 12:
            raise ValidationError(f"月は1-12の範囲である必要があります: {month_num}")
            
    except ValueError:
        raise ValidationError(f"月の形式が不正です: {month}")


def validate_date_range(start_date, end_date):
    """日付範囲のバリデーション
    
    Args:
        start_date: 開始日文字列 (str)
        end_date: 終了日文字列 (str)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    def parse_date(date_str, param_name):
        if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
            raise ValidationError(f"{param_name}の形式はYYYY-MM-DDである必要があります: {date_str}")
        
        try:
            return datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError(f"{param_name}の日付が不正です: {date_str}")
    
    start = parse_date(start_date, "開始日")
    end = parse_date(end_date, "終了日")
    
    # 開始日 <= 終了日のチェック
    if start > end:
        raise ValidationError(f"開始日は終了日以前である必要があります: {start_date} > {end_date}")
    
    # 日付範囲の妥当性チェック（過去5年〜未来1ヶ月）
    today = datetime.now().date()
    min_date = datetime(today.year - 5, 1, 1).date()
    max_date = datetime(today.year + 1, today.month, today.day).date() if today.month < 12 else datetime(today.year + 1, 12, 31).date()
    
    if start < min_date or end > max_date:
        raise ValidationError(f"日付は{min_date}から{max_date}の範囲である必要があります")


def validate_year_range(year):
    """年範囲のバリデーション
    
    Args:
        year: 年 (int)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    if year < 2020 or year > 2030:
        raise ValidationError(f"年は2020-2030の範囲である必要があります: {year}")


def validate_output_path(output_path):
    """出力パスのバリデーション
    
    Args:
        output_path: 出力パス (Path)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    # 親ディレクトリが存在し、書き込み可能かチェック
    if output_path.suffix:
        # ファイルパスが指定された場合
        parent_dir = output_path.parent
    else:
        # ディレクトリパスが指定された場合
        parent_dir = output_path
        if not parent_dir.exists():
            # ディレクトリが存在しない場合は作成を試みる
            try:
                parent_dir.mkdir(parents=True, exist_ok=True)
                click.echo(f"出力ディレクトリを作成しました: {parent_dir}")
            except PermissionError:
                raise ValidationError(f"出力ディレクトリの作成権限がありません: {parent_dir}")
            except OSError as e:
                raise ValidationError(f"出力ディレクトリの作成に失敗しました: {parent_dir}, エラー: {e}")
    
    # 書き込み権限チェック
    if parent_dir.exists() and not os.access(parent_dir, os.W_OK):
        raise ValidationError(f"出力先への書き込み権限がありません: {parent_dir}")


def validate_formats(formats):
    """出力形式のバリデーション
    
    Args:
        formats: 出力形式のタプル (tuple)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    valid_formats = {'csv', 'excel', 'both'}
    for fmt in formats:
        if fmt not in valid_formats:
            raise ValidationError(f"不正な出力形式です: {fmt}. 有効な形式: {', '.join(valid_formats)}")
    
    # 'both' が指定されている場合は他の形式と併用不可
    if 'both' in formats and len(formats) > 1:
        raise ValidationError("出力形式 'both' は他の形式と同時に指定できません")


def validate_report_types(report_types):
    """レポート種類のバリデーション
    
    Args:
        report_types: レポート種類のタプル (tuple)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    valid_types = {'employee', 'department', 'daily', 'all'}
    for rtype in report_types:
        if rtype not in valid_types:
            raise ValidationError(f"不正なレポート種類です: {rtype}. 有効な種類: {', '.join(valid_types)}")
    
    # 'all' が指定されている場合は他の種類と併用不可
    if 'all' in report_types and len(report_types) > 1:
        raise ValidationError("レポート種類 'all' は他の種類と同時に指定できません")


def validate_chunk_size(chunk_size):
    """チャンクサイズのバリデーション
    
    Args:
        chunk_size: チャンクサイズ (int)
        
    Raises:
        ValidationError: バリデーションエラー
    """
    
    if chunk_size < 1:
        raise ValidationError(f"チャンクサイズは1以上である必要があります: {chunk_size}")
    
    if chunk_size > 100000:
        raise ValidationError(f"チャンクサイズは100000以下である必要があります: {chunk_size}")
        
    # 推奨範囲外の場合は警告
    if chunk_size < 100 or chunk_size > 10000:
        click.echo(f"警告: チャンクサイズ{chunk_size}は推奨範囲（100-10000）外です")