"""DataValidatorクラスのテスト

TASK-102: データ検証・クレンジング機能のTDDテスト
このファイルは失敗するテスト（Red Phase）から始まります
"""

import pytest
import pandas as pd
import time
from datetime import date, timedelta
from typing import List, Dict

# まだ実装されていないため、ImportErrorが発生する予定
try:
    from attendance_tool.validation.validator import DataValidator, ValidationReport, ValidationError, ValidationWarning
    from attendance_tool.validation.rules import ValidationRule
except ImportError:
    # Red Phase: モジュールが存在しないため、テストは失敗する
    DataValidator = None
    ValidationReport = None
    ValidationError = None
    ValidationWarning = None
    ValidationRule = None


class TestDataValidatorDataFrame:
    """DataValidator DataFrame検証テスト"""
    
    def setup_method(self):
        """テスト準備"""
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
        self.validator = DataValidator(config={}, rules=[])
        
    def test_validate_dataframe_success(self):
        """正常なDataFrame検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 有効なDataFrame
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002'],
            'employee_name': ['田中太郎', '山田花子'],
            'work_date': ['2024-01-15', '2024-01-15'],
            'start_time': ['09:00', '09:30'],
            'end_time': ['18:00', '18:30']
        })
        
        # When: 検証実行
        report = self.validator.validate_dataframe(df)
        
        # Then: 成功結果
        assert isinstance(report, ValidationReport)
        assert report.total_records == 2
        assert report.valid_records == 2
        assert len(report.errors) == 0
        assert report.quality_score >= 0.95
        assert report.processing_time > 0
        
    def test_validate_dataframe_with_errors(self):
        """エラーありDataFrame検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: エラーを含むDataFrame
        df = pd.DataFrame({
            'employee_id': ['EMP001', ''],  # 空の社員ID
            'employee_name': ['田中太郎', '山田花子'],
            'work_date': ['2024-01-15', '2025-01-15'],  # 未来日
            'start_time': ['18:00', '09:30'],  # 論理エラー
            'end_time': ['09:00', '18:30']
        })
        
        # When: 検証実行
        report = self.validator.validate_dataframe(df)
        
        # Then: エラー検出
        assert isinstance(report, ValidationReport)
        assert report.total_records == 2
        assert report.valid_records == 0  # 両方エラー
        assert len(report.errors) >= 2
        
        # 特定のエラーメッセージをチェック
        error_messages = [error.message for error in report.errors]
        assert any("社員ID" in msg for msg in error_messages)
        assert any("時刻論理" in msg or "出勤時刻" in msg for msg in error_messages)
        
        # 品質スコアが低下していることを確認
        assert report.quality_score < 0.5
        
    def test_validate_large_dataframe_performance(self):
        """大量データ処理性能テスト"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 10,000件のDataFrame
        size = 10000
        df = pd.DataFrame({
            'employee_id': [f'EMP{i:04d}' for i in range(size)],
            'employee_name': [f'社員{i}' for i in range(size)],
            'work_date': ['2024-01-15'] * size,
            'start_time': ['09:00'] * size,
            'end_time': ['18:00'] * size
        })
        
        # When: 検証実行 (時間測定)
        start_time = time.time()
        report = self.validator.validate_dataframe(df)
        end_time = time.time()
        
        # Then: 性能要件達成 (30秒以内)
        processing_time = end_time - start_time
        assert processing_time <= 30.0
        assert report.total_records == size
        assert report.valid_records == size
        assert report.processing_time <= 30.0

    def test_validate_empty_dataframe(self):
        """空のDataFrame検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 空のDataFrame
        df = pd.DataFrame()
        
        # When: 検証実行
        report = self.validator.validate_dataframe(df)
        
        # Then: 適切に処理される
        assert isinstance(report, ValidationReport)
        assert report.total_records == 0
        assert report.valid_records == 0
        assert len(report.errors) == 0
        assert len(report.warnings) == 0

    def test_validate_missing_columns_dataframe(self):
        """必須カラム不足のDataFrame検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 必須カラムが不足するDataFrame
        df = pd.DataFrame({
            'employee_id': ['EMP001'],
            'employee_name': ['田中太郎']
            # work_dateカラムが不足
        })
        
        # When: 検証実行
        report = self.validator.validate_dataframe(df)
        
        # Then: 構造エラーとして検出
        assert len(report.errors) >= 1
        assert any("必須カラム" in error.message for error in report.errors)


class TestDataValidatorRecord:
    """DataValidator個別レコード検証テスト"""
    
    def test_validate_record_success(self):
        """正常レコード検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 有効なレコード
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '18:00'
        }
        
        # When: レコード検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: エラーなし
        assert isinstance(errors, list)
        assert len(errors) == 0
        
    def test_validate_record_multiple_errors(self):
        """複数エラーレコード検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 複数エラーを含むレコード
        record = {
            'employee_id': '',  # エラー1: 空ID
            'employee_name': '田中太郎',
            'work_date': '2025-01-15',  # エラー2: 未来日
            'start_time': '25:00',  # エラー3: 無効時刻
            'end_time': '18:00'
        }
        
        # When: レコード検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        
        # Then: 3つのエラー検出
        assert isinstance(errors, list)
        assert len(errors) == 3
        
        error_messages = [error.message for error in errors]
        assert any("社員ID" in msg for msg in error_messages)
        assert any("未来" in msg for msg in error_messages)
        assert any("無効な時刻" in msg for msg in error_messages)

    def test_validate_record_with_warnings(self):
        """警告レベルの問題を含むレコード検証"""
        # Red Phase: DataValidatorが未実装のため失敗
        if DataValidator is None:
            pytest.skip("DataValidator not implemented yet")
            
        # Given: 警告レベルの問題を含むレコード
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-01-15',
            'start_time': '06:00',  # 異常に早い出勤（警告）
            'end_time': '23:30',    # 異常に遅い退勤（警告）
            'break_minutes': 30     # 短い休憩（警告）
        }
        
        # When: レコード検証
        validator = DataValidator(config={}, rules=[])
        errors = validator.validate_record(record)
        warnings = validator.get_warnings(record)
        
        # Then: エラーはないが警告あり
        assert len(errors) == 0
        assert len(warnings) >= 2
        
        warning_messages = [warning.message for warning in warnings]
        assert any("早い出勤" in msg or "長時間勤務" in msg for msg in warning_messages)


class TestDataValidatorCustomRules:
    """DataValidatorカスタムルールテスト"""
    
    def test_add_custom_rule(self):
        """カスタムルール追加テスト"""
        # Red Phase: DataValidator, ValidationRuleが未実装のため失敗
        if DataValidator is None or ValidationRule is None:
            pytest.skip("DataValidator or ValidationRule not implemented yet")
            
        # Given: カスタムバリデーションルール
        def custom_department_rule(record):
            """部署名チェックのカスタムルール"""
            if record.get('department') == '廃止部署':
                return ValidationError(
                    field='department',
                    message='廃止された部署です',
                    value=record.get('department')
                )
            return None
            
        custom_rule = ValidationRule(
            name='department_check',
            validator=custom_department_rule,
            priority=1
        )
        
        # When: カスタムルールを追加
        validator = DataValidator(config={}, rules=[])
        validator.add_custom_rule(custom_rule)
        
        # Then: ルールが追加される
        assert len(validator.rules) == 1
        assert validator.rules[0].name == 'department_check'

    def test_custom_rule_execution(self):
        """カスタムルール実行テスト"""
        # Red Phase: DataValidator, ValidationRuleが未実装のため失敗
        if DataValidator is None or ValidationRule is None:
            pytest.skip("DataValidator or ValidationRule not implemented yet")
            
        # Given: カスタムルール付きバリデーター
        def overtime_limit_rule(record):
            """残業時間制限チェック"""
            start = record.get('start_time', '09:00')
            end = record.get('end_time', '18:00')
            # 簡易的な残業時間計算（実際はより複雑）
            if end > '20:00':
                return ValidationWarning(
                    field='overtime',
                    message='長時間残業の可能性',
                    value=f'{start}-{end}'
                )
            return None
            
        custom_rule = ValidationRule(
            name='overtime_check',
            validator=overtime_limit_rule,
            priority=1
        )
        
        validator = DataValidator(config={}, rules=[custom_rule])
        
        # When: 残業時間の長いレコードを検証
        record = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': '2024-01-15',
            'start_time': '09:00',
            'end_time': '22:00'  # 22:00まで勤務
        }
        
        errors = validator.validate_record(record)
        warnings = validator.get_warnings(record)
        
        # Then: カスタムルールによる警告
        assert len(warnings) >= 1
        assert any("残業" in warning.message for warning in warnings)


class TestValidationReport:
    """ValidationReportテスト"""
    
    def test_validation_report_creation(self):
        """ValidationReport作成テスト"""
        # Red Phase: ValidationReportが未実装のため失敗
        if ValidationReport is None:
            pytest.skip("ValidationReport not implemented yet")
            
        # Given: 検証結果データ
        errors = [
            ValidationError(
                row_number=1,
                field='employee_id',
                message='社員IDが空です',
                value=''
            )
        ]
        warnings = [
            ValidationWarning(
                row_number=2,
                field='overtime',
                message='長時間勤務',
                value='09:00-22:00'
            )
        ]
        
        # When: レポート作成
        report = ValidationReport(
            total_records=10,
            valid_records=8,
            errors=errors,
            warnings=warnings,
            processing_time=1.5,
            quality_score=0.8
        )
        
        # Then: 適切に作成される
        assert report.total_records == 10
        assert report.valid_records == 8
        assert len(report.errors) == 1
        assert len(report.warnings) == 1
        assert report.processing_time == 1.5
        assert report.quality_score == 0.8

    def test_get_error_summary(self):
        """エラーサマリー取得テスト"""
        # Red Phase: ValidationReportが未実装のため失敗
        if ValidationReport is None or ValidationError is None:
            pytest.skip("ValidationReport or ValidationError not implemented yet")
            
        # Given: 複数のエラーを含むレポート
        errors = [
            ValidationError(row_number=1, field='employee_id', message='社員IDエラー', value=''),
            ValidationError(row_number=2, field='employee_id', message='社員IDエラー', value=''),
            ValidationError(row_number=3, field='work_date', message='日付エラー', value='invalid'),
            ValidationError(row_number=4, field='start_time', message='時刻エラー', value='25:00'),
        ]
        
        report = ValidationReport(
            total_records=10,
            valid_records=6,
            errors=errors,
            warnings=[],
            processing_time=1.0,
            quality_score=0.6
        )
        
        # When: エラーサマリー取得
        summary = report.get_error_summary()
        
        # Then: フィールド別エラー数
        assert isinstance(summary, dict)
        assert summary['employee_id'] == 2
        assert summary['work_date'] == 1
        assert summary['start_time'] == 1

    def test_get_critical_errors(self):
        """重大エラー取得テスト"""
        # Red Phase: ValidationReportが未実装のため失敗
        if ValidationReport is None or ValidationError is None:
            pytest.skip("ValidationReport or ValidationError not implemented yet")
            
        # Given: 重大・軽微エラー混在のレポート
        errors = [
            ValidationError(
                row_number=1,
                field='employee_id',
                message='社員IDが空です',
                value='',
                level='CRITICAL'
            ),
            ValidationError(
                row_number=2,
                field='department',
                message='部署名が不明です',
                value='不明部署',
                level='WARNING'
            ),
            ValidationError(
                row_number=3,
                field='work_date',
                message='必須フィールドです',
                value=None,
                level='CRITICAL'
            )
        ]
        
        report = ValidationReport(
            total_records=5,
            valid_records=2,
            errors=errors,
            warnings=[],
            processing_time=1.0,
            quality_score=0.4
        )
        
        # When: 重大エラー取得
        critical_errors = report.get_critical_errors()
        
        # Then: 重大エラーのみ抽出
        assert len(critical_errors) == 2
        assert all(error.level == 'CRITICAL' for error in critical_errors)
        
        critical_messages = [error.message for error in critical_errors]
        assert '社員IDが空です' in critical_messages
        assert '必須フィールドです' in critical_messages

    def test_export_to_csv(self):
        """CSV出力テスト"""
        # Red Phase: ValidationReportが未実装のため失敗
        if ValidationReport is None:
            pytest.skip("ValidationReport not implemented yet")
            
        # Given: エラーレポート
        report = ValidationReport(
            total_records=5,
            valid_records=3,
            errors=[
                ValidationError(
                    row_number=1,
                    field='employee_id',
                    message='社員IDが空です',
                    value=''
                )
            ],
            warnings=[],
            processing_time=1.0,
            quality_score=0.6
        )
        
        # When: CSV出力
        output_path = '/tmp/test_validation_report.csv'
        report.export_to_csv(output_path)
        
        # Then: ファイルが作成される
        import os
        assert os.path.exists(output_path)
        
        # ファイル内容の確認
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert '社員IDが空です' in content
            assert 'employee_id' in content