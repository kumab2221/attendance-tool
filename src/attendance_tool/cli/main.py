"""メインCLIエントリーポイント"""

from pathlib import Path

import click

try:
    from attendance_tool import __version__
    from attendance_tool.utils.config import get_environment, setup_logging

    from .progress import ProcessingSteps, ProgressBar, show_processing_summary
    from .validators import (
        ValidationError,
        validate_chunk_size,
        validate_date_range,
        validate_formats,
        validate_input_file,
        validate_month_format,
        validate_option_combinations,
        validate_output_path,
        validate_report_types,
        validate_year_range,
    )
except ImportError:
    # PyInstallerでの実行時のフォールバック
    import os
    import sys

    sys.path.append(os.path.dirname(__file__))
    __version__ = "0.1.0"

    def setup_logging():
        pass

    def get_environment():
        return "production"

    from progress import ProcessingSteps, ProgressBar, show_processing_summary
    from validators import (
        ValidationError,
        validate_chunk_size,
        validate_date_range,
        validate_formats,
        validate_input_file,
        validate_month_format,
        validate_option_combinations,
        validate_output_path,
        validate_report_types,
        validate_year_range,
    )


@click.group(invoke_without_command=True)
@click.option("--version", is_flag=True, help="Show version information")
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="設定ディレクトリパス",
)
@click.pass_context
def main(ctx, version, config_dir):
    """勤怠管理自動集計ツール

    CSVファイルから勤怠データを読み込み、集計・レポート生成を行います。

    Examples:
        # 基本的な使用方法
        attendance-tool process --input data.csv --output report.csv

        # 月単位での集計
        attendance-tool process -i data.csv -o report.csv --month 2024-03

        # Excel形式で出力
        attendance-tool process -i data.csv -o report.xlsx --format excel
    """

    # 設定の初期化
    try:
        setup_logging()
    except Exception:
        # ログ設定に失敗した場合は基本設定を使用
        pass

    if version:
        click.echo(f"attendance-tool version {__version__}")
        if config_dir:
            click.echo(f"設定ディレクトリ: {config_dir}")
        click.echo(f"実行環境: {get_environment()}")
        return

    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="入力CSVファイルパス",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    required=True,
    type=click.Path(path_type=Path),
    help="出力パス（ファイル/ディレクトリ）",
)
@click.option("--month", "-m", help="月単位指定 (YYYY-MM)")
@click.option("--start-date", "-s", help="開始日 (YYYY-MM-DD)")
@click.option("--end-date", "-e", help="終了日 (YYYY-MM-DD)")
@click.option("--year", "-y", type=int, help="年単位指定")
@click.option(
    "--format",
    "-f",
    "formats",
    multiple=True,
    type=click.Choice(["csv", "excel", "both"]),
    default=["csv"],
    help="出力形式",
)
@click.option(
    "--report-type",
    "-r",
    "report_types",
    multiple=True,
    type=click.Choice(["employee", "department", "daily", "all"]),
    default=["employee"],
    help="レポート種類",
)
@click.option(
    "--config-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="設定ディレクトリパス",
)
@click.option("--verbose", "-v", count=True, help="詳細ログ出力")
@click.option("--quiet", "-q", is_flag=True, help="静寂モード")
@click.option("--dry-run", is_flag=True, help="ドライラン")
@click.option("--chunk-size", type=int, default=1000, help="チャンク処理サイズ")
@click.option("--parallel", is_flag=True, help="並列処理")
def process(
    input_file,
    output_path,
    month,
    start_date,
    end_date,
    year,
    formats,
    report_types,
    config_dir,
    verbose,
    quiet,
    dry_run,
    chunk_size,
    parallel,
):
    """勤怠データの処理・集計

    指定されたCSVファイルから勤怠データを読み込み、
    期間指定に基づいて集計・レポート生成を行います。
    """

    # プログレスバー初期化
    progress = ProgressBar(quiet=quiet, verbose=verbose)

    try:
        # バリデーション実行
        progress.echo("🔍 入力データの検証を開始します...", level=1)

        validate_option_combinations(month, start_date, end_date, year, quiet, verbose)
        validate_input_file(input_file)
        validate_formats(formats)
        validate_report_types(report_types)
        validate_chunk_size(chunk_size)

        if month:
            validate_month_format(month)

        if start_date or end_date:
            validate_date_range(start_date, end_date)

        if year:
            validate_year_range(year)

        validate_output_path(output_path)

        progress.echo_success("入力データの検証が完了しました")

        # 処理設定の表示
        if verbose > 0:
            progress.echo("📋 処理設定:", level=1)
            progress.echo(f"  入力ファイル: {input_file}", level=1)
            progress.echo(f"  出力パス: {output_path}", level=1)
            if month:
                progress.echo(f"  対象月: {month}", level=1)
            elif start_date and end_date:
                progress.echo(f"  対象期間: {start_date} ～ {end_date}", level=1)
            elif year:
                progress.echo(f"  対象年: {year}", level=1)
            progress.echo(f"  出力形式: {', '.join(formats)}", level=1)
            progress.echo(f"  レポート種類: {', '.join(report_types)}", level=1)
            progress.echo(f"  チャンクサイズ: {chunk_size}", level=1)

        if dry_run:
            progress.echo_success("ドライランモード: 検証のみ完了しました")
            return

        # まだ実際の処理は未実装
        progress.echo("⚠️  実際の処理機能は未実装です。今後のバージョンで対応予定です。")

        # サンプル統計の表示
        sample_stats = {
            "input_records": 0,
            "processed_records": 0,
            "error_records": 0,
            "processing_time": 0.0,
            "output_files": [],
        }
        show_processing_summary(progress, sample_stats)

        raise click.Abort()

    except ValidationError as e:
        progress.echo_error(f"検証エラー: {e}")
        raise click.Abort()
    except Exception as e:
        progress.echo_error(f"予期しないエラー: {e}")
        raise click.Abort()


@main.group()
def config():
    """設定管理"""
    pass


@config.command()
@click.argument("section", required=False)
def show(section):
    """設定表示"""
    click.echo("設定表示機能は未実装です。")
    raise click.Abort()


@config.command()
def validate():
    """設定検証"""
    click.echo("設定検証機能は未実装です。")
    raise click.Abort()


@main.command()
@click.option(
    "--input",
    "-i",
    "input_file",
    required=True,
    type=click.Path(exists=True, path_type=Path),
    help="入力CSVファイルパス",
)
def validate(input_file):
    """データ検証"""
    click.echo("データ検証機能は未実装です。")
    raise click.Abort()


@main.command()
@click.option("--detailed", is_flag=True, help="詳細情報表示")
def version(detailed):
    """バージョン情報表示"""
    click.echo(f"attendance-tool version {__version__}")
    if detailed:
        click.echo("詳細バージョン情報は未実装です。")


if __name__ == "__main__":
    main()
