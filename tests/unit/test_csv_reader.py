"""CSV読み込み・検証機能の単体テスト

TASK-101のCSVファイル読み込み・検証機能に対する包括的なテスト。
TDDのRed Phaseとして、まずは失敗するテストを実装。
"""

import pytest
import pandas as pd
import tempfile
import os
from pathlib import Path

from attendance_tool.data.csv_reader import (
    CSVReader,
    ValidationResult,
    ValidationError,
    FileAccessError,
    EncodingError,
    CSVProcessingError,
)


class TestCSVReader:
    """CSVReaderクラスのテスト"""

    def setup_method(self):
        """テストセットアップ"""
        self.reader = CSVReader()
        self.fixtures_path = Path(__file__).parent.parent / "fixtures" / "csv"

    # ===== 正常系テスト (Happy Path) =====

    def test_load_standard_utf8_csv(self):
        """TC-101-001: 標準的なCSVファイル読み込み"""
        # Given: 標準的なUTF-8 CSVファイル
        csv_path = self.fixtures_path / "standard_utf8.csv"
        
        # When: ファイルを読み込む
        df = self.reader.load_file(str(csv_path))
        
        # Then: 正しく読み込まれる
        assert df is not None
        assert len(df) == 3  # 3行のデータ
        assert "社員ID" in df.columns or "employee_id" in df.columns
        assert "氏名" in df.columns or "employee_name" in df.columns
        
        # データの内容確認
        assert "E001" in df.iloc[0].values
        assert "田中太郎" in df.iloc[0].values

    def test_load_different_encodings(self):
        """TC-101-002: 異なるエンコーディングファイル読み込み"""
        # Given: UTF-8-sig エンコーディングファイル
        csv_path = self.fixtures_path / "standard_utf8.csv"
        
        # When: エンコーディングを指定して読み込む
        df = self.reader.load_file(str(csv_path), encoding="utf-8")
        
        # Then: 正しく読み込まれる
        assert df is not None
        assert len(df) > 0
        # 日本語文字が正しく読み込まれている
        assert any("田中太郎" in str(val) for val in df.iloc[0].values)

    def test_column_mapping_flexibility(self):
        """TC-101-005: カラム名の柔軟マッチング"""
        # Given: 様々なカラム名パターンのファイル
        csv_path = self.fixtures_path / "standard_utf8.csv"
        df = pd.read_csv(csv_path)
        
        # When: カラムマッピングを取得
        mapping = self.reader.get_column_mapping(df)
        
        # Then: 適切なマッピングが返される
        assert isinstance(mapping, dict)
        assert len(mapping) > 0

    def test_data_validation_success(self):
        """正常データの検証成功"""
        # Given: 正常なデータフレーム
        csv_path = self.fixtures_path / "standard_utf8.csv"
        df = pd.read_csv(csv_path)
        
        # When: データ検証を実行
        result = self.reader.validate_data(df)
        
        # Then: 検証成功
        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.processed_rows > 0

    # ===== 異常系テスト (Error Cases) =====

    def test_file_not_found_error(self):
        """TC-101-101: ファイル不存在エラー"""
        # Given: 存在しないファイルパス
        nonexistent_path = "/nonexistent/path/file.csv"
        
        # When & Then: FileNotFoundError例外が発生
        with pytest.raises(FileNotFoundError):
            self.reader.load_file(nonexistent_path)

    def test_permission_error(self):
        """TC-101-102: 権限不足エラー"""
        # Given: 一時的に権限を制限したファイル
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            f.write("test,data\n1,2\n")
            temp_path = f.name
        
        try:
            # ファイル権限を読み取り不可に設定
            os.chmod(temp_path, 0o000)
            
            # When & Then: PermissionError例外が発生
            with pytest.raises(PermissionError):
                self.reader.load_file(temp_path)
        
        finally:
            # クリーンアップ
            os.chmod(temp_path, 0o644)
            os.unlink(temp_path)

    def test_empty_file_error(self):
        """TC-101-103: 空ファイルエラー"""
        # Given: 空のCSVファイル
        csv_path = self.fixtures_path / "empty_file.csv"
        
        # When & Then: 適切なエラーが発生
        with pytest.raises(CSVProcessingError):
            self.reader.load_file(str(csv_path))

    def test_missing_required_columns_error(self):
        """TC-101-106: 必須カラム不足エラー"""
        # Given: 必須カラムが不足したファイル
        csv_path = self.fixtures_path / "missing_required_columns.csv"
        
        # When & Then: ValidationError例外が発生
        with pytest.raises(ValidationError):
            self.reader.load_file(str(csv_path))

    def test_invalid_data_type_error(self):
        """TC-101-107: データ型変換エラー"""
        # Given: データ型変換に失敗するファイル
        csv_path = self.fixtures_path / "invalid_date_format.csv"
        
        # When: ファイルを読み込む（エラーは検証段階で検出）
        df = pd.read_csv(csv_path)  # 読み込みは可能
        
        # Then: 検証でエラーが検出される
        result = self.reader.validate_data(df)
        assert result.is_valid is False
        assert len(result.errors) > 0

    # ===== 境界値テスト (Boundary Tests) =====

    def test_minimum_file_processing(self):
        """TC-101-202: 最小ファイルサイズ処理"""
        # Given: ヘッダー + 1行のみの最小ファイル
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("社員ID,氏名,日付\nE001,田中太郎,2024-01-15\n")
            temp_path = f.name
        
        try:
            # When: ファイルを読み込む
            df = self.reader.load_file(temp_path)
            
            # Then: 正常に処理される
            assert df is not None
            assert len(df) == 1
        finally:
            os.unlink(temp_path)

    def test_extreme_date_values(self):
        """TC-101-203: 極端な日付値処理"""
        # Given: 境界的な日付値を含むデータ
        data = {
            "社員ID": ["E001", "E002", "E003"],
            "氏名": ["田中太郎", "佐藤花子", "鈴木次郎"],
            "日付": ["2019-01-01", "2030-12-31", "2024-02-29"]  # 過去境界、未来、うるう年
        }
        df = pd.DataFrame(data)
        
        # When: データ検証を実行
        result = self.reader.validate_data(df)
        
        # Then: 境界値が適切に処理される
        assert isinstance(result, ValidationResult)
        # 未来日は警告される
        assert any("未来" in w.message for w in result.warnings)

    def test_extreme_time_values(self):
        """TC-101-204: 極端な時刻値処理"""
        # Given: 境界的な時刻値を含むデータ
        data = {
            "社員ID": ["E001", "E002", "E003"],
            "出勤時刻": ["00:00", "23:59", "25:00"],  # 深夜0時、深夜11:59、無効時刻
            "退勤時刻": ["09:00", "08:00", "10:00"]
        }
        df = pd.DataFrame(data)
        
        # When: データ検証を実行
        result = self.reader.validate_data(df)
        
        # Then: 無効時刻がエラーとして検出される
        assert not result.is_valid
        assert any("25:00" in str(e.value) for e in result.errors)

    def test_maximum_work_hours_detection(self):
        """TC-101-205: 最大勤務時間処理"""
        # Given: 24時間を超える勤務時間のデータ
        data = {
            "社員ID": ["E001"],
            "出勤時刻": ["09:00"],
            "退勤時刻": ["08:00"],  # 翌日8時（23時間勤務）
            "日付": ["2024-01-15"]
        }
        df = pd.DataFrame(data)
        
        # When: データ検証を実行
        result = self.reader.validate_data(df)
        
        # Then: 長時間勤務が警告される
        assert len(result.warnings) > 0
        assert any("勤務時間" in w.message for w in result.warnings)

    # ===== 統合テスト (Integration Tests) =====

    def test_config_file_integration(self):
        """TC-101-301: 設定ファイル統合テスト"""
        # Given: 設定ファイルパスを指定したCSVReader
        config_path = Path(__file__).parent.parent.parent / "config" / "csv_format.yaml"
        reader = CSVReader(str(config_path))
        
        # When: 設定が読み込まれる
        # Then: エラーなく初期化される
        assert reader.config_path == str(config_path)

    # ===== パフォーマンステスト =====

    @pytest.mark.slow
    def test_large_file_performance(self):
        """TC-101-401: 大容量ファイルの処理性能"""
        # Given: 大量データ（1000行）を含むファイル
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻\n")
            for i in range(1000):
                f.write(f"E{i:04d},社員{i},部署{i%5},2024-01-15,09:00,18:00\n")
            temp_path = f.name
        
        try:
            import time
            
            # When: 処理時間を測定
            start_time = time.time()
            df = self.reader.load_file(temp_path)
            end_time = time.time()
            
            # Then: 合理的な時間内で処理完了
            processing_time = end_time - start_time
            assert processing_time < 10.0  # 10秒以内
            assert len(df) == 1000
            
        finally:
            os.unlink(temp_path)

    # ===== セキュリティテスト =====

    def test_path_traversal_prevention(self):
        """TC-101-501: パストラバーサル攻撃防御"""
        # Given: 危険なファイルパス
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config",
            "/dev/null"
        ]
        
        for dangerous_path in dangerous_paths:
            # When & Then: 不正パスが検出される
            with pytest.raises((FileNotFoundError, OSError, ValueError)):
                self.reader.load_file(dangerous_path)


class TestValidationResult:
    """ValidationResultクラスのテスト"""

    def test_has_critical_errors_method(self):
        """重大エラーの有無判定テスト"""
        # Given: エラーを含む検証結果
        result = ValidationResult(
            is_valid=False,
            errors=[],
            warnings=[],
            processed_rows=0,
            valid_rows=0,
            column_mapping={}
        )
        
        # When: 重大エラーの有無を確認
        has_errors = result.has_critical_errors()
        
        # Then: 結果が返される
        assert isinstance(has_errors, bool)
        assert has_errors is False  # エラーがないのでFalse

    def test_get_summary_method(self):
        """検証結果サマリー取得テスト"""
        # Given: 検証結果
        result = ValidationResult(
            is_valid=True,
            errors=[],
            warnings=[],
            processed_rows=5,
            valid_rows=5,
            column_mapping={}
        )
        
        # When: サマリー取得
        summary = result.get_summary()
        
        # Then: サマリー文字列が返される
        assert isinstance(summary, str)
        assert "検証結果" in summary
        assert "処理行数" in summary


class TestCustomExceptions:
    """カスタム例外クラスのテスト"""

    def test_csv_processing_error(self):
        """CSVProcessingError例外テスト"""
        # Given & When: 基底例外を発生
        with pytest.raises(CSVProcessingError):
            raise CSVProcessingError("テストエラー")

    def test_file_access_error(self):
        """FileAccessError例外テスト"""
        # Given & When: ファイルアクセスエラーを発生
        with pytest.raises(FileAccessError):
            raise FileAccessError("ファイルアクセスエラー")

    def test_validation_error(self):
        """ValidationError例外テスト"""
        # Given & When: 検証エラーを発生
        with pytest.raises(ValidationError):
            raise ValidationError("データ検証エラー")

    def test_encoding_error(self):
        """EncodingError例外テスト"""
        # Given & When: エンコーディングエラーを発生
        with pytest.raises(EncodingError):
            raise EncodingError("エンコーディングエラー")

    def test_exception_inheritance(self):
        """例外の継承関係テスト"""
        # Given: カスタム例外インスタンス
        file_error = FileAccessError("ファイルエラー")
        validation_error = ValidationError("検証エラー")
        encoding_error = EncodingError("エンコーディングエラー")
        
        # Then: 適切な継承関係
        assert isinstance(file_error, CSVProcessingError)
        assert isinstance(validation_error, CSVProcessingError)
        assert isinstance(encoding_error, CSVProcessingError)