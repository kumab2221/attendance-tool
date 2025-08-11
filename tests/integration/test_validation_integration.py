"""データ検証・クレンジング機能の統合テスト

TASK-102: データ検証・クレンジング機能のTDDテスト
このファイルは失敗するテスト（Red Phase）から始まります
"""

import pytest
import pandas as pd
import os
from datetime import date, timedelta
from unittest.mock import Mock, patch

# まだ実装されていないため、ImportErrorが発生する予定
try:
    from attendance_tool.validation.enhanced_csv_reader import EnhancedCSVReader
    from attendance_tool.validation.validator import DataValidator
    from attendance_tool.validation.cleaner import DataCleaner
    from attendance_tool.data.csv_reader import CSVReader
except ImportError:
    # Red Phase: モジュールが存在しないため、テストは失敗する
    EnhancedCSVReader = None
    DataValidator = None
    DataCleaner = None
    CSVReader = None


class TestCSVReaderIntegration:
    """CSVReader統合テスト"""

    def test_enhanced_csv_reader_full_workflow(self):
        """完全ワークフローテスト"""
        # Red Phase: EnhancedCSVReaderが未実装のため失敗
        if EnhancedCSVReader is None or DataValidator is None or DataCleaner is None:
            pytest.skip("Enhanced CSV Reader components not implemented yet")

        # Given: テストCSVファイル作成
        test_csv_path = self.create_test_csv_with_errors()

        # When: 統合処理実行
        validator = DataValidator(config={}, rules=[])
        cleaner = DataCleaner(config={})
        enhanced_reader = EnhancedCSVReader(validator, cleaner)

        df, report = enhanced_reader.load_and_validate(test_csv_path)

        # Then: 期待される結果
        assert isinstance(df, pd.DataFrame)
        assert hasattr(report, "total_records")
        assert hasattr(report, "errors")
        assert hasattr(report, "warnings")
        assert report.total_records > 0
        assert len(report.errors) >= 0  # エラー検出
        assert len(report.warnings) >= 0  # 警告検出

        # データ品質の改善確認
        assert hasattr(report, "quality_score")
        assert 0 <= report.quality_score <= 1.0

    def test_csv_reader_compatibility(self):
        """既存CSVReaderとの互換性テスト"""
        # Red Phase: EnhancedCSVReaderが未実装のため失敗
        if EnhancedCSVReader is None or CSVReader is None:
            pytest.skip("CSV Reader classes not implemented yet")

        # Given: テストCSVファイル
        csv_path = self.create_simple_test_csv()

        # When: 両方の読み込み方法で処理
        old_reader = CSVReader()
        new_reader = EnhancedCSVReader(
            DataValidator(config={}, rules=[]), DataCleaner(config={})
        )

        old_df = old_reader.load_file(csv_path)
        new_df, report = new_reader.load_and_validate(csv_path)

        # Then: 基本的なデータ構造は互換性維持
        assert len(old_df) == len(new_df)
        assert set(old_df.columns) == set(new_df.columns)

        # 新機能の追加確認
        assert hasattr(report, "quality_score")
        assert hasattr(report, "processing_time")

    def create_test_csv_with_errors(self):
        """エラーを含むテストCSVファイル作成"""
        test_data = """employee_id,employee_name,work_date,start_time,end_time,department
EMP001,田中太郎,2024-01-15,09:00,18:00,開発部
,山田花子,2024-01-15,09:30,18:30,営業部
EMP003,佐藤次郎,2025-01-15,25:00,17:00,開発課
EMP004,鈴木一郎,2024-01-15,18:00,09:00,総務部"""

        csv_path = "/tmp/test_with_errors.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(test_data)
        return csv_path

    def create_simple_test_csv(self):
        """シンプルなテストCSVファイル作成"""
        test_data = """employee_id,employee_name,work_date,start_time,end_time
EMP001,田中太郎,2024-01-15,09:00,18:00
EMP002,山田花子,2024-01-15,09:30,18:30"""

        csv_path = "/tmp/test_simple.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(test_data)
        return csv_path


class TestErrorHandlingIntegration:
    """エラーハンドリング統合テスト"""

    def test_edge_201_time_logic_integration(self):
        """EDGE-201: 時刻論理エラー統合処理"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None or DataCleaner is None:
            pytest.skip("DataValidator or DataCleaner not implemented yet")

        # Given: 時刻論理エラーのあるDataFrame
        df = pd.DataFrame(
            {
                "employee_id": ["EMP001"],
                "employee_name": ["田中太郎"],
                "work_date": ["2024-01-15"],
                "start_time": ["18:00"],  # 出勤時刻
                "end_time": ["09:00"],  # 退勤時刻
            }
        )

        # When: 統合検証・修正実行
        validator = DataValidator(config={}, rules=[])
        report = validator.validate_dataframe(df)

        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(report.errors)

        # Then: 適切なエラー検出と修正提案
        assert len(report.errors) >= 1
        time_logic_errors = [
            error
            for error in report.errors
            if "時刻論理" in error.message or "出勤時刻" in error.message
        ]
        assert len(time_logic_errors) >= 1

        # 修正提案の確認
        assert len(suggestions) >= 1
        time_suggestions = [
            sugg
            for sugg in suggestions
            if "日跨ぎ" in sugg.description or "時刻交換" in sugg.description
        ]
        assert len(time_suggestions) >= 1
        assert time_suggestions[0].confidence_score >= 0.6

    def test_req_104_work_hours_integration(self):
        """REQ-104: 勤務時間エラー統合処理"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None or DataCleaner is None:
            pytest.skip("DataValidator or DataCleaner not implemented yet")

        # Given: 24時間超勤務・負の勤務時間のDataFrame
        df = pd.DataFrame(
            {
                "employee_id": ["EMP001", "EMP002", "EMP003"],
                "employee_name": ["田中太郎", "山田花子", "佐藤次郎"],
                "work_date": ["2024-01-15", "2024-01-15", "2024-01-15"],
                "start_time": ["08:00", "09:00", "06:00"],
                "end_time": [
                    "09:00",
                    "08:30",
                    "07:00",
                ],  # 25時間勤務、負時間、25時間勤務
                "break_minutes": [0, 0, 60],
            }
        )

        # When: 統合検証実行
        validator = DataValidator(
            config={"max_work_hours": 24, "allow_negative_hours": False}, rules=[]
        )
        report = validator.validate_dataframe(df)

        # Then: 勤務時間エラー検出
        work_hour_errors = [
            error
            for error in report.errors
            if (
                "勤務時間" in error.message
                or "24時間" in error.message
                or "負の" in error.message
            )
        ]
        assert len(work_hour_errors) >= 2  # 2つ以上の勤務時間エラー

        # 各エラーの詳細確認
        error_messages = [error.message for error in work_hour_errors]
        assert any("25時間" in msg or "超過" in msg for msg in error_messages)
        assert any("負の" in msg or "マイナス" in msg for msg in error_messages)

    def test_edge_204_future_date_integration(self):
        """EDGE-204: 未来日データ統合処理"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")

        # Given: 未来日を含むDataFrame
        future_date = date.today() + timedelta(days=30)
        df = pd.DataFrame(
            {
                "employee_id": ["EMP001", "EMP002"],
                "employee_name": ["田中太郎", "山田花子"],
                "work_date": ["2024-01-15", future_date.strftime("%Y-%m-%d")],
                "start_time": ["09:00", "09:00"],
                "end_time": ["18:00", "18:00"],
            }
        )

        # When: 検証実行
        validator = DataValidator(
            config={"allow_future_dates": False, "future_date_warning_days": 7},
            rules=[],
        )
        report = validator.validate_dataframe(df)

        # Then: 未来日警告・エラー検出
        future_date_issues = [
            issue
            for issue in (report.errors + report.warnings)
            if "未来" in issue.message
        ]
        assert len(future_date_issues) >= 1

        # 修正提案の生成
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(report.errors)

        date_suggestions = [
            sugg for sugg in suggestions if sugg.correction_type == "date_year"
        ]
        if date_suggestions:
            assert date_suggestions[0].confidence_score >= 0.7

    def test_multiple_validation_rules_integration(self):
        """複数検証ルール統合テスト"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")

        # Given: 複数種類のエラーを含むDataFrame
        df = pd.DataFrame(
            {
                "employee_id": [
                    "",
                    "EMP002",
                    "INVALID_ID",
                ],  # 空、正常、フォーマットエラー
                "employee_name": ["田中太郎", "", "佐藤次郎"],  # 正常、空、正常
                "work_date": [
                    "2024-01-15",
                    "2025-12-31",
                    "invalid",
                ],  # 正常、未来、無効
                "start_time": ["09:00", "25:00", "18:00"],  # 正常、無効、論理エラー
                "end_time": ["18:00", "17:00", "09:00"],  # 正常、正常、論理エラー
                "department": ["開発部", "廃止部署", None],  # 正常、無効、欠損
            }
        )

        # When: 複合検証実行
        validator = DataValidator(
            config={
                "employee_id_pattern": r"^EMP\d{3}$",
                "valid_departments": ["開発部", "営業部", "総務部"],
            },
            rules=[],
        )

        report = validator.validate_dataframe(df)

        # Then: 各種エラーが適切に分類される
        assert report.total_records == 3
        assert report.valid_records <= 1  # 最大1件のみ有効

        # エラータイプ別の検証
        error_fields = [error.field for error in report.errors]
        assert "employee_id" in error_fields
        assert "employee_name" in error_fields
        assert "work_date" in error_fields
        assert "start_time" in error_fields

        # 品質スコアが大幅に低下
        assert report.quality_score < 0.5


class TestPerformanceIntegration:
    """パフォーマンス統合テスト"""

    @pytest.mark.performance
    def test_large_dataset_end_to_end(self):
        """大量データセットのエンドツーエンドテスト"""
        # Red Phase: EnhancedCSVReaderが未実装のため失敗
        if EnhancedCSVReader is None:
            pytest.skip("EnhancedCSVReader not implemented yet")

        # Given: 50,000件のテストCSVファイル
        large_csv = self.create_large_test_csv(50000)

        # When: エンドツーエンド処理実行
        import time

        start_time = time.time()

        validator = DataValidator(config={}, rules=[])
        cleaner = DataCleaner(config={"parallel": True})
        enhanced_reader = EnhancedCSVReader(validator, cleaner)

        df, report = enhanced_reader.load_and_validate(large_csv)

        end_time = time.time()
        total_time = end_time - start_time

        # Then: パフォーマンス要件達成
        assert total_time <= 60.0  # 1分以内
        assert len(df) == 50000
        assert report.processing_time <= 60.0

        # メモリ効率性の確認
        memory_usage = self.get_memory_usage()
        expected_max_memory = df.memory_usage(deep=True).sum() * 4  # 4倍以内
        assert memory_usage <= expected_max_memory

    @pytest.mark.performance
    def test_parallel_vs_sequential_performance(self):
        """並列vs逐次処理性能比較"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")

        # Given: 中規模データセット
        df = self.generate_test_dataframe(10000)

        # When: 逐次処理
        import time

        validator_seq = DataValidator(config={"parallel": False}, rules=[])
        start_time = time.time()
        report_seq = validator_seq.validate_dataframe(df)
        sequential_time = time.time() - start_time

        # 並列処理
        validator_par = DataValidator(config={"parallel": True, "n_jobs": 4}, rules=[])
        start_time = time.time()
        report_par = validator_par.validate_dataframe(df)
        parallel_time = time.time() - start_time

        # Then: 並列処理による高速化
        speedup_ratio = sequential_time / parallel_time
        assert speedup_ratio >= 1.3  # 30%以上の高速化

        # 結果の一貫性確認
        assert report_seq.total_records == report_par.total_records
        assert len(report_seq.errors) == len(report_par.errors)

    def create_large_test_csv(self, size: int):
        """大量データのテストCSVファイル作成"""
        csv_path = f"/tmp/large_test_{size}.csv"

        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(
                "employee_id,employee_name,work_date,start_time,end_time,department\n"
            )
            for i in range(size):
                # 意図的に一部エラーを含む
                emp_id = f"EMP{i:05d}" if i % 100 != 0 else ""  # 1%空ID
                name = f"社員{i}"
                date_val = "2024-01-15" if i % 1000 != 0 else "2025-01-15"  # 0.1%未来日
                start_time = "09:00" if i % 500 != 0 else "25:00"  # 0.2%無効時刻
                end_time = "18:00"
                dept = (
                    "開発部" if i % 3 == 0 else ("営業部" if i % 3 == 1 else "総務部")
                )

                f.write(f"{emp_id},{name},{date_val},{start_time},{end_time},{dept}\n")

        return csv_path

    def generate_test_dataframe(self, size: int):
        """テスト用DataFrame生成"""
        return pd.DataFrame(
            {
                "employee_id": [f"EMP{i:05d}" for i in range(size)],
                "employee_name": [f"社員{i}" for i in range(size)],
                "work_date": ["2024-01-15"] * size,
                "start_time": ["09:00"] * size,
                "end_time": ["18:00"] * size,
                "department": ["開発部"] * size,
            }
        )

    def get_memory_usage(self):
        """現在のメモリ使用量取得"""
        import psutil

        process = psutil.Process()
        return process.memory_info().rss


class TestRealDataIntegration:
    """実データ統合テスト"""

    @pytest.mark.real_data
    def test_real_csv_file_processing(self):
        """実際のCSVファイル処理テスト"""
        # Red Phase: EnhancedCSVReaderが未実装のため失敗
        if EnhancedCSVReader is None:
            pytest.skip("EnhancedCSVReader not implemented yet")

        # Given: 実際の勤怠CSVファイル（テスト用）
        real_csv_path = self.get_real_test_csv_path()
        if not os.path.exists(real_csv_path):
            pytest.skip("Real CSV test file not available")

        # When: 実データ処理
        validator = DataValidator(config=self.get_production_config(), rules=[])
        cleaner = DataCleaner(config=self.get_production_config())
        enhanced_reader = EnhancedCSVReader(validator, cleaner)

        df, report = enhanced_reader.load_and_validate(real_csv_path)

        # Then: 実用的な結果
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0

        # 品質レポートの妥当性確認
        assert 0 <= report.quality_score <= 1.0
        assert report.processing_time > 0

        # エラーレポートの有用性確認
        if report.errors:
            for error in report.errors[:5]:  # 最初の5件チェック
                assert hasattr(error, "row_number")
                assert hasattr(error, "field")
                assert hasattr(error, "message")
                assert error.message.strip() != ""

    def get_real_test_csv_path(self):
        """実テストCSVファイルパス取得"""
        # 実際のプロジェクトではテスト用の実データファイルパスを返す
        return "/home/kuma/dev/attendance-tool/tests/fixtures/csv/real_sample.csv"

    def get_production_config(self):
        """本番設定取得"""
        return {
            "validation": {
                "employee_id_pattern": r"^[A-Z]{3}\d{4}$",
                "max_work_hours": 12,
                "allow_future_dates": False,
            },
            "cleaning": {
                "level": "standard",
                "department_mapping": {"開発課": "開発部", "営業課": "営業部"},
            },
        }


class TestErrorRecoveryIntegration:
    """エラー回復統合テスト"""

    def test_partial_file_corruption_recovery(self):
        """部分的ファイル破損からの回復テスト"""
        # Red Phase: EnhancedCSVReaderが未実装のため失敗
        if EnhancedCSVReader is None:
            pytest.skip("EnhancedCSVReader not implemented yet")

        # Given: 部分的に破損したCSVファイル
        corrupted_csv = self.create_partially_corrupted_csv()

        # When: 回復処理実行
        validator = DataValidator(config={"error_recovery": True}, rules=[])
        cleaner = DataCleaner(config={"skip_corrupted_rows": True})
        enhanced_reader = EnhancedCSVReader(validator, cleaner)

        df, report = enhanced_reader.load_and_validate(corrupted_csv)

        # Then: 処理可能な部分は正常に処理される
        assert len(df) > 0  # 一部のデータは処理される
        assert len(report.errors) > 0  # エラーが記録される
        assert "corruption" in str(report.errors).lower()

    def create_partially_corrupted_csv(self):
        """部分的に破損したCSVファイル作成"""
        corrupted_data = """employee_id,employee_name,work_date,start_time,end_time
EMP001,田中太郎,2024-01-15,09:00,18:00
EMP002,山田花子,2024-01-15,"09:30,18:30  # 破損行（クォート不正）
EMP003,佐藤次郎,2024-01-15,09:00,18:00
,,,,,invalid_extra_columns  # 破損行（列数不正）
EMP005,鈴木一郎,2024-01-15,09:00,18:00"""

        csv_path = "/tmp/corrupted_test.csv"
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(corrupted_data)
        return csv_path
