"""プログレスバー表示機能"""

import click
from typing import Optional, Any
import sys


class ProgressBar:
    """プログレスバー管理クラス"""

    def __init__(self, quiet: bool = False, verbose: int = 0):
        """初期化

        Args:
            quiet: 静寂モード
            verbose: 詳細レベル (0=通常, 1=詳細, 2以上=デバッグ)
        """
        self.quiet = quiet
        self.verbose = verbose
        self._current_bar: Optional[Any] = None

    def create_bar(self, iterable=None, length=None, label=None, **kwargs):
        """プログレスバー作成

        Args:
            iterable: 反復可能オブジェクト
            length: 総数
            label: ラベル
            **kwargs: その他のclick.progressbarオプション

        Returns:
            プログレスバーオブジェクト
        """
        if self.quiet:
            # 静寂モードでは何も表示しない
            return NoOpProgressBar(iterable, length)

        # 詳細モードに応じてラベルを調整
        if self.verbose > 0 and label:
            label = f"[{self._get_timestamp()}] {label}"

        self._current_bar = click.progressbar(
            iterable=iterable,
            length=length,
            label=label,
            file=sys.stderr,  # 標準エラー出力に表示
            **kwargs,
        )

        return self._current_bar

    def echo(self, message: str, level: int = 0):
        """メッセージ表示

        Args:
            message: メッセージ
            level: メッセージレベル (0=通常, 1=詳細, 2=デバッグ)
        """
        if self.quiet and level == 0:
            # 静寂モードでは通常メッセージは表示しない
            return

        if level <= self.verbose:
            prefix = ""
            if self.verbose > 0:
                timestamp = self._get_timestamp()
                if level == 0:
                    prefix = f"[{timestamp}] "
                elif level == 1:
                    prefix = f"[{timestamp}] [INFO] "
                else:
                    prefix = f"[{timestamp}] [DEBUG] "

            click.echo(f"{prefix}{message}", err=True)

    def echo_success(self, message: str):
        """成功メッセージ表示"""
        if not self.quiet:
            click.echo(click.style(f"✅ {message}", fg="green"), err=True)

    def echo_warning(self, message: str):
        """警告メッセージ表示"""
        if not self.quiet:
            click.echo(click.style(f"⚠️  {message}", fg="yellow"), err=True)

    def echo_error(self, message: str):
        """エラーメッセージ表示"""
        # エラーは静寂モードでも表示
        click.echo(click.style(f"❌ {message}", fg="red"), err=True)

    def _get_timestamp(self) -> str:
        """タイムスタンプ取得"""
        from datetime import datetime

        return datetime.now().strftime("%H:%M:%S")


class NoOpProgressBar:
    """何も行わないプログレスバー（静寂モード用）"""

    def __init__(self, iterable=None, length=None):
        self.iterable = iterable
        self.length = length
        self._iter = None

    def __enter__(self):
        if self.iterable is not None:
            self._iter = iter(self.iterable)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def __iter__(self):
        if self._iter is not None:
            return self._iter
        return self

    def __next__(self):
        if self._iter is not None:
            return next(self._iter)
        raise StopIteration

    def update(self, n_steps=1):
        """進捗更新（何もしない）"""
        pass

    def finish(self):
        """完了処理（何もしない）"""
        pass


class ProcessingSteps:
    """処理ステップ定義"""

    VALIDATE_INPUT = "入力ファイル検証"
    LOAD_DATA = "データ読み込み"
    VALIDATE_DATA = "データ検証"
    FILTER_PERIOD = "期間フィルタリング"
    CALCULATE_ATTENDANCE = "勤怠集計"
    GENERATE_REPORTS = "レポート生成"
    SAVE_OUTPUT = "出力保存"

    ALL_STEPS = [
        VALIDATE_INPUT,
        LOAD_DATA,
        VALIDATE_DATA,
        FILTER_PERIOD,
        CALCULATE_ATTENDANCE,
        GENERATE_REPORTS,
        SAVE_OUTPUT,
    ]


def create_step_progress_bar(progress: ProgressBar, step_name: str, total: int):
    """ステップ用プログレスバー作成

    Args:
        progress: ProgressBarインスタンス
        step_name: ステップ名
        total: 総数

    Returns:
        プログレスバーオブジェクト
    """
    return progress.create_bar(
        length=total,
        label=step_name,
        show_eta=True,
        show_percent=True,
        item_show_func=lambda x: x if x else "",
    )


def show_processing_summary(progress: ProgressBar, stats: dict):
    """処理サマリー表示

    Args:
        progress: ProgressBarインスタンス
        stats: 処理統計情報
    """
    if progress.quiet:
        return

    progress.echo("\n📊 処理結果サマリー:")

    if "input_records" in stats:
        progress.echo(f"   入力レコード数: {stats['input_records']:,}件")

    if "processed_records" in stats:
        progress.echo(f"   処理レコード数: {stats['processed_records']:,}件")

    if "error_records" in stats:
        if stats["error_records"] > 0:
            progress.echo_warning(f"エラーレコード数: {stats['error_records']:,}件")
        else:
            progress.echo_success(f"エラーレコード数: {stats['error_records']:,}件")

    if "processing_time" in stats:
        progress.echo(f"   処理時間: {stats['processing_time']:.2f}秒")

    if "output_files" in stats:
        progress.echo(f"   出力ファイル数: {len(stats['output_files'])}件")
        if progress.verbose > 0:
            for output_file in stats["output_files"]:
                progress.echo(f"     - {output_file}", level=1)
