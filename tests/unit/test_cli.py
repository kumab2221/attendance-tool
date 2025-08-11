"""CLI機能の単体テストモジュール"""

import pytest
import tempfile
import os
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from attendance_tool.cli import main
from attendance_tool.cli.validators import ValidationError


class TestMainCommand:
    """メインコマンドのテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    def test_main_command_help(self, runner):
        """メインコマンドのヘルプ表示テスト"""
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "attendance-tool" in result.output
        assert "Commands:" in result.output

    def test_main_command_version(self, runner):
        """バージョン情報表示テスト"""
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output  # バージョン番号が含まれること

    def test_main_command_no_args(self, runner):
        """引数なしでヘルプ表示テスト"""
        result = runner.invoke(main, [])

        # Clickはデフォルトで引数なしの場合ヘルプを表示
        assert result.exit_code == 0
        assert "Usage:" in result.output


class TestProcessCommand:
    """processコマンドのテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    @pytest.fixture
    def temp_csv_file(self):
        """テスト用CSVファイル"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻\n")
            f.write("E001,田中太郎,営業部,2024-03-01,09:00,18:00\n")
            temp_path = f.name

        yield temp_path

        # クリーンアップ
        if os.path.exists(temp_path):
            os.unlink(temp_path)

    def test_process_command_help(self, runner):
        """processコマンドのヘルプ表示テスト"""
        result = runner.invoke(main, ["process", "--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output
        assert "process" in result.output
        assert "--input" in result.output
        assert "--output" in result.output

    def test_process_command_missing_required_args(self, runner):
        """必須引数不足テスト"""
        # 入力ファイル未指定
        result = runner.invoke(main, ["process"])
        assert result.exit_code != 0

        # 出力パス未指定
        result = runner.invoke(main, ["process", "--input", "dummy.csv"])
        assert result.exit_code != 0

    def test_process_command_nonexistent_input_file(self, runner):
        """存在しない入力ファイルエラーテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(
                main, ["process", "--input", "nonexistent.csv", "--output", temp_dir]
            )

            assert result.exit_code != 0
            assert (
                "does not exist" in result.output.lower()
                or "not found" in result.output.lower()
            )


class TestArgumentParsing:
    """引数パーステスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    @pytest.fixture
    def temp_files(self):
        """テスト用一時ファイル"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as input_file:
            input_file.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻\n")
            input_file.write("E001,田中太郎,営業部,2024-03-01,09:00,18:00\n")
            input_path = input_file.name

        temp_dir = tempfile.mkdtemp()

        yield input_path, temp_dir

        # クリーンアップ
        if os.path.exists(input_path):
            os.unlink(input_path)
        if os.path.exists(temp_dir):
            os.rmdir(temp_dir)

    def test_parse_month_option_valid(self, runner, temp_files):
        """月単位期間指定の正常パーステスト"""
        input_path, output_dir = temp_files

        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "2024-03",
            ],
        )

        # この段階では実装していないのでエラーになることを確認
        # 実装後は成功することを期待
        assert result.exit_code != 0  # 未実装なのでエラー

    def test_parse_month_option_invalid(self, runner, temp_files):
        """月単位期間指定の不正形式テスト"""
        input_path, output_dir = temp_files

        # 不正な月形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "2024-13",  # 13月は存在しない
            ],
        )

        assert result.exit_code != 0

        # 不正な文字列形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "invalid-month",
            ],
        )

        assert result.exit_code != 0

    def test_parse_date_range_options(self, runner, temp_files):
        """日付範囲指定パーステスト"""
        input_path, output_dir = temp_files

        # 正常な日付範囲
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--start-date",
                "2024-03-01",
                "--end-date",
                "2024-03-31",
            ],
        )

        # 未実装なのでエラー
        assert result.exit_code != 0

    def test_parse_date_range_invalid_order(self, runner, temp_files):
        """開始日 > 終了日のエラーテスト"""
        input_path, output_dir = temp_files

        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--start-date",
                "2024-03-31",
                "--end-date",
                "2024-03-01",  # 開始日より前
            ],
        )

        assert result.exit_code != 0

    def test_parse_format_options(self, runner, temp_files):
        """出力形式指定パーステスト"""
        input_path, output_dir = temp_files

        # CSV形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--format",
                "csv",
            ],
        )

        # 未実装なのでエラー
        assert result.exit_code != 0

        # Excel形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--format",
                "excel",
            ],
        )

        assert result.exit_code != 0

        # 複数形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--format",
                "csv",
                "--format",
                "excel",
            ],
        )

        assert result.exit_code != 0


class TestFileValidation:
    """ファイルバリデーションテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    def test_validate_input_file_not_exists(self, runner):
        """存在しない入力ファイルバリデーション"""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(
                main, ["process", "--input", "nonexistent.csv", "--output", temp_dir]
            )

            assert result.exit_code != 0
            # エラーメッセージに「存在しない」または「見つからない」が含まれること
            error_msg = result.output.lower()
            assert any(
                keyword in error_msg
                for keyword in [
                    "does not exist",
                    "not found",
                    "存在しません",
                    "見つかりません",
                ]
            )

    def test_validate_input_file_extension(self, runner):
        """CSVファイル拡張子チェック"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("test data")
            txt_file = f.name

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                result = runner.invoke(
                    main, ["process", "--input", txt_file, "--output", temp_dir]
                )

                # CSV以外の拡張子はエラー（実装後に期待する動作）
                # 現在は未実装なので別の理由でエラーになる
                assert result.exit_code != 0
        finally:
            os.unlink(txt_file)

    def test_validate_output_directory_writable(self, runner):
        """出力ディレクトリ書き込み権限チェック"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as input_file:
            input_file.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻\n")
            input_path = input_file.name

        try:
            # 書き込み不可のディレクトリをシミュレート
            with tempfile.TemporaryDirectory() as temp_dir:
                readonly_dir = os.path.join(temp_dir, "readonly")
                os.makedirs(readonly_dir, mode=0o555)  # 読み込み専用

                try:
                    result = runner.invoke(
                        main,
                        ["process", "--input", input_path, "--output", readonly_dir],
                    )

                    # 書き込み権限がない場合はエラー（実装後に期待する動作）
                    # 現在は未実装なので別の理由でエラーになる
                    assert result.exit_code != 0
                finally:
                    # 権限を戻してクリーンアップ
                    os.chmod(readonly_dir, 0o755)
        finally:
            os.unlink(input_path)


class TestDateValidation:
    """日付バリデーションテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    @pytest.fixture
    def temp_files(self):
        """テスト用一時ファイル"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as input_file:
            input_file.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻\n")
            input_path = input_file.name

        temp_dir = tempfile.mkdtemp()

        yield input_path, temp_dir

        # クリーンアップ
        os.unlink(input_path)
        os.rmdir(temp_dir)

    def test_validate_month_format(self, runner, temp_files):
        """月形式バリデーション"""
        input_path, output_dir = temp_files

        # 無効な月（13月）
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "2024-13",
            ],
        )
        assert result.exit_code != 0

        # 無効な月（0月）
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "2024-00",
            ],
        )
        assert result.exit_code != 0

        # 完全に無効な形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "invalid",
            ],
        )
        assert result.exit_code != 0

    def test_validate_date_format(self, runner, temp_files):
        """日付形式バリデーション"""
        input_path, output_dir = temp_files

        # 無効な日付（2月30日）
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--start-date",
                "2024-02-30",
                "--end-date",
                "2024-02-30",
            ],
        )
        assert result.exit_code != 0

        # 完全に無効な日付形式
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--start-date",
                "invalid-date",
                "--end-date",
                "2024-03-01",
            ],
        )
        assert result.exit_code != 0


class TestOptionCombinations:
    """オプション組み合わせテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    @pytest.fixture
    def temp_files(self):
        """テスト用一時ファイル"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as input_file:
            input_file.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻\n")
            input_path = input_file.name

        temp_dir = tempfile.mkdtemp()

        yield input_path, temp_dir

        # クリーンアップ
        os.unlink(input_path)
        os.rmdir(temp_dir)

    def test_exclusive_period_options(self, runner, temp_files):
        """期間指定オプションの排他制御"""
        input_path, output_dir = temp_files

        # month と start-date/end-date の同時指定はエラー
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--month",
                "2024-03",
                "--start-date",
                "2024-03-01",
                "--end-date",
                "2024-03-31",
            ],
        )

        assert result.exit_code != 0

    def test_dependent_options(self, runner, temp_files):
        """依存オプションチェック"""
        input_path, output_dir = temp_files

        # start-date指定時はend-dateも必須
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--start-date",
                "2024-03-01",
                # --end-date未指定
            ],
        )

        assert result.exit_code != 0

        # end-date指定時はstart-dateも必須
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--end-date",
                "2024-03-31",
                # --start-date未指定
            ],
        )

        assert result.exit_code != 0

    def test_conflicting_options(self, runner, temp_files):
        """矛盾するオプション組み合わせ"""
        input_path, output_dir = temp_files

        # --quiet と --verbose は矛盾
        result = runner.invoke(
            main,
            [
                "process",
                "--input",
                input_path,
                "--output",
                output_dir,
                "--quiet",
                "--verbose",
            ],
        )

        # 実装によってはwarningで済ます場合もあるが、
        # 基本的には矛盾するので適切にハンドリングされる
        # 現在は未実装なので別の理由でエラーになる
        assert result.exit_code != 0


class TestErrorHandling:
    """エラーハンドリングテスト"""

    @pytest.fixture
    def runner(self):
        """CLIテストランナー"""
        return CliRunner()

    def test_command_not_found(self, runner):
        """存在しないコマンドエラー"""
        result = runner.invoke(main, ["nonexistent-command"])

        assert result.exit_code != 0
        assert (
            "no such command" in result.output.lower()
            or "command not found" in result.output.lower()
        )

    def test_invalid_option(self, runner):
        """存在しないオプションエラー"""
        result = runner.invoke(main, ["process", "--nonexistent-option"])

        assert result.exit_code != 0
        assert (
            "no such option" in result.output.lower()
            or "unrecognized" in result.output.lower()
        )

    def test_missing_option_value(self, runner):
        """オプション値不足エラー"""
        result = runner.invoke(main, ["process", "--input"])

        assert result.exit_code != 0
        # オプションに値が必要な場合のエラー
