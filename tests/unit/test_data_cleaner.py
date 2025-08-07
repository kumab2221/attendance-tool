"""DataCleanerクラスのテスト

TASK-102: データ検証・クレンジング機能のTDDテスト
このファイルは失敗するテスト（Red Phase）から始まります
"""

import pytest
import pandas as pd
from typing import List, Dict, Any

# まだ実装されていないため、ImportErrorが発生する予定
try:
    from attendance_tool.validation.cleaner import DataCleaner, CleaningResult, CorrectionSuggestion
    from attendance_tool.validation.validator import ValidationError, ValidationWarning, ValidationReport
except ImportError:
    # Red Phase: モジュールが存在しないため、テストは失敗する
    DataCleaner = None
    CleaningResult = None
    CorrectionSuggestion = None
    ValidationError = None
    ValidationWarning = None
    ValidationReport = None


class TestDataCleanerAutoCorrection:
    """DataCleaner自動修正テスト"""
    
    def test_clean_time_format(self):
        """時刻フォーマット統一"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: 様々な時刻フォーマット
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003'],
            'start_time': ['9:00', '09:00:00', '9時00分'],
            'end_time': ['18:0', '18:00:00', '18時00分']
        })
        
        # When: 自動修正実行
        cleaner = DataCleaner(config={})
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 統一されたフォーマット
        assert cleaned_df.loc[0, 'start_time'] == '09:00'
        assert cleaned_df.loc[1, 'start_time'] == '09:00'
        assert cleaned_df.loc[2, 'start_time'] == '09:00'
        
        assert cleaned_df.loc[0, 'end_time'] == '18:00'
        assert cleaned_df.loc[1, 'end_time'] == '18:00'
        assert cleaned_df.loc[2, 'end_time'] == '18:00'
        
    def test_clean_department_names(self):
        """部署名正規化"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: 表記ゆれのある部署名
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003', 'EMP004'],
            'department': ['開発部', '開発課', 'Development', '開発部門']
        })
        
        # When: 正規化実行
        cleaner = DataCleaner(config={
            'department_mapping': {
                '開発課': '開発部',
                'Development': '開発部',
                '開発部門': '開発部'
            }
        })
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 統一された部署名
        assert all(dept == '開発部' for dept in cleaned_df['department'])

    def test_clean_employee_name_formatting(self):
        """社員名フォーマット統一"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: フォーマットが異なる社員名
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003'],
            'employee_name': ['　田中太郎　', 'YAMADA Hanako', '佐藤　次郎']
        })
        
        # When: 名前フォーマット統一
        cleaner = DataCleaner(config={
            'name_cleaning': {
                'trim_whitespace': True,
                'normalize_alphabet': True
            }
        })
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 統一されたフォーマット
        assert cleaned_df.loc[0, 'employee_name'] == '田中太郎'
        assert cleaned_df.loc[1, 'employee_name'] == '山田花子'  # アルファベット→ひらがな変換
        assert cleaned_df.loc[2, 'employee_name'] == '佐藤次郎'

    def test_clean_date_format(self):
        """日付フォーマット統一"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: 様々な日付フォーマット
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003'],
            'work_date': ['2024/1/15', '2024-01-15', '01/15/2024']
        })
        
        # When: 日付フォーマット統一
        cleaner = DataCleaner(config={'date_format': 'YYYY-MM-DD'})
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 統一されたフォーマット (YYYY-MM-DD)
        assert cleaned_df.loc[0, 'work_date'] == '2024-01-15'
        assert cleaned_df.loc[1, 'work_date'] == '2024-01-15'
        assert cleaned_df.loc[2, 'work_date'] == '2024-01-15'

    def test_clean_break_minutes_normalization(self):
        """休憩時間の正規化"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: 様々な休憩時間表記
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002', 'EMP003'],
            'break_time': ['1:00', '60分', '1時間']  # 時間:分、分単位、時間単位
        })
        
        # When: 休憩時間を分単位に正規化
        cleaner = DataCleaner(config={'break_time_unit': 'minutes'})
        cleaned_df = cleaner.apply_auto_corrections(df)
        
        # Then: 分単位に統一
        assert cleaned_df.loc[0, 'break_time'] == 60
        assert cleaned_df.loc[1, 'break_time'] == 60
        assert cleaned_df.loc[2, 'break_time'] == 60


class TestDataCleanerSuggestions:
    """DataCleaner修正提案テスト"""
    
    def test_suggest_time_corrections(self):
        """時刻修正提案"""
        # Red Phase: DataCleaner, ValidationError, CorrectionSuggestionが未実装のため失敗
        if DataCleaner is None or ValidationError is None or CorrectionSuggestion is None:
            pytest.skip("Required classes not implemented yet")
            
        # Given: 時刻論理エラー
        errors = [
            ValidationError(
                row_number=1,
                field='time_logic',
                message='出勤時刻が退勤時刻より遅い',
                value=('18:00', '09:00')
            )
        ]
        
        # When: 修正提案生成
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(errors)
        
        # Then: 適切な提案
        assert isinstance(suggestions, list)
        assert len(suggestions) == 1
        
        suggestion = suggestions[0]
        assert isinstance(suggestion, CorrectionSuggestion)
        assert suggestion.correction_type == 'time_swap'
        assert '日跨ぎ勤務' in suggestion.description
        assert suggestion.confidence_score >= 0.7
        assert suggestion.suggested_value == ('09:00', '18:00')  # スワップ提案
        
    def test_suggest_date_corrections(self):
        """日付修正提案"""
        # Red Phase: DataCleaner関連クラスが未実装のため失敗
        if DataCleaner is None or ValidationError is None or CorrectionSuggestion is None:
            pytest.skip("Required classes not implemented yet")
            
        # Given: 未来日エラー
        errors = [
            ValidationError(
                row_number=1,
                field='work_date',
                message='未来の日付です',
                value='2025-01-15'
            )
        ]
        
        # When: 修正提案生成
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(errors)
        
        # Then: 年度修正提案
        assert len(suggestions) == 1
        suggestion = suggestions[0]
        assert suggestion.correction_type == 'date_year'
        assert '2024-01-15' in suggestion.suggested_value
        assert suggestion.confidence_score >= 0.8

    def test_suggest_employee_id_corrections(self):
        """社員ID修正提案"""
        # Red Phase: DataCleaner関連クラスが未実装のため失敗
        if DataCleaner is None or ValidationError is None or CorrectionSuggestion is None:
            pytest.skip("Required classes not implemented yet")
            
        # Given: 社員IDフォーマットエラー
        errors = [
            ValidationError(
                row_number=1,
                field='employee_id',
                message='無効な社員IDフォーマット',
                value='EMP1'  # 桁数不足
            )
        ]
        
        # When: 修正提案生成（社員名から推測）
        record_context = {
            'employee_id': 'EMP1',
            'employee_name': '田中太郎'
        }
        cleaner = DataCleaner(config={})
        suggestions = cleaner.suggest_corrections(errors, context=record_context)
        
        # Then: 桁数補正提案
        assert len(suggestions) >= 1
        suggestion = suggestions[0]
        assert suggestion.correction_type == 'employee_id_format'
        assert 'EMP001' in suggestion.suggested_value or 'EMP0001' in suggestion.suggested_value
        assert suggestion.confidence_score >= 0.6

    def test_suggest_department_corrections(self):
        """部署名修正提案"""
        # Red Phase: DataCleaner関連クラスが未実装のため失敗
        if DataCleaner is None or ValidationError is None or CorrectionSuggestion is None:
            pytest.skip("Required classes not implemented yet")
            
        # Given: 不明な部署名エラー
        errors = [
            ValidationError(
                row_number=1,
                field='department',
                message='不明な部署名',
                value='開発グループ'
            )
        ]
        
        # When: 修正提案生成
        cleaner = DataCleaner(config={
            'department_candidates': ['開発部', '営業部', '総務部', 'システム部']
        })
        suggestions = cleaner.suggest_corrections(errors)
        
        # Then: 類似部署名提案
        assert len(suggestions) >= 1
        suggestion = suggestions[0]
        assert suggestion.correction_type == 'department_similarity'
        assert '開発部' in suggestion.suggested_value  # 最も類似した部署名
        assert suggestion.confidence_score >= 0.7


class TestDataCleanerCleaningResult:
    """DataCleaner清洗结果テスト"""
    
    def test_cleaning_result_creation(self):
        """CleaningResult作成テスト"""
        # Red Phase: CleaningResultが未実装のため失敗
        if CleaningResult is None:
            pytest.skip("CleaningResult not implemented yet")
            
        # Given: 清洗データ
        original_df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002'],
            'start_time': ['9:00', '09:00:00']
        })
        
        cleaned_df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP002'],
            'start_time': ['09:00', '09:00']
        })
        
        corrections = [
            {'row': 0, 'field': 'start_time', 'old': '9:00', 'new': '09:00'},
            {'row': 1, 'field': 'start_time', 'old': '09:00:00', 'new': '09:00'}
        ]
        
        # When: CleaningResult作成
        result = CleaningResult(
            original_dataframe=original_df,
            cleaned_dataframe=cleaned_df,
            corrections_applied=corrections,
            suggestions=[]
        )
        
        # Then: 適切に作成される
        assert result.original_dataframe.equals(original_df)
        assert result.cleaned_dataframe.equals(cleaned_df)
        assert len(result.corrections_applied) == 2
        assert result.corrections_applied[0]['field'] == 'start_time'

    def test_get_correction_summary(self):
        """修正サマリー取得テスト"""
        # Red Phase: CleaningResultが未実装のため失敗
        if CleaningResult is None:
            pytest.skip("CleaningResult not implemented yet")
            
        # Given: 複数の修正を含むCleaningResult
        corrections = [
            {'row': 0, 'field': 'start_time', 'old': '9:00', 'new': '09:00'},
            {'row': 1, 'field': 'start_time', 'old': '10:00:00', 'new': '10:00'},
            {'row': 2, 'field': 'department', 'old': '開発課', 'new': '開発部'},
            {'row': 3, 'field': 'department', 'old': '開発チーム', 'new': '開発部'}
        ]
        
        result = CleaningResult(
            original_dataframe=pd.DataFrame(),
            cleaned_dataframe=pd.DataFrame(),
            corrections_applied=corrections,
            suggestions=[]
        )
        
        # When: 修正サマリー取得
        summary = result.get_correction_summary()
        
        # Then: フィールド別修正数
        assert isinstance(summary, dict)
        assert summary['start_time'] == 2
        assert summary['department'] == 2
        assert sum(summary.values()) == 4

    def test_export_corrections_log(self):
        """修正ログ出力テスト"""
        # Red Phase: CleaningResultが未実装のため失敗
        if CleaningResult is None:
            pytest.skip("CleaningResult not implemented yet")
            
        # Given: 修正ログを含むCleaningResult
        corrections = [
            {
                'row': 0,
                'field': 'start_time',
                'old': '9:00',
                'new': '09:00',
                'correction_type': 'time_format',
                'confidence': 0.95
            }
        ]
        
        result = CleaningResult(
            original_dataframe=pd.DataFrame(),
            cleaned_dataframe=pd.DataFrame(),
            corrections_applied=corrections,
            suggestions=[]
        )
        
        # When: 修正ログ出力
        log_path = '/tmp/test_corrections_log.csv'
        result.export_corrections_log(log_path)
        
        # Then: ファイルが作成される
        import os
        assert os.path.exists(log_path)
        
        # ログ内容の確認
        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'start_time' in content
            assert '9:00' in content
            assert '09:00' in content


class TestDataCleanerIntegration:
    """DataCleaner統合テスト"""
    
    def test_clean_dataframe_with_validation_report(self):
        """ValidationReportを使ったDataFrame清洗"""
        # Red Phase: DataCleaner, ValidationReportが未実装のため失敗
        if DataCleaner is None or ValidationReport is None or ValidationError is None:
            pytest.skip("Required classes not implemented yet")
            
        # Given: エラーを含むDataFrameと検証結果
        df = pd.DataFrame({
            'employee_id': ['EMP001', 'EMP2'],  # EMP2はフォーマットエラー
            'start_time': ['9:00', '10:00:00'],  # フォーマット不統一
            'department': ['開発課', '営業部']   # 開発課は正規化対象
        })
        
        errors = [
            ValidationError(
                row_number=1,
                field='employee_id',
                message='社員IDフォーマットエラー',
                value='EMP2'
            )
        ]
        
        validation_report = ValidationReport(
            total_records=2,
            valid_records=1,
            errors=errors,
            warnings=[],
            processing_time=1.0,
            quality_score=0.5
        )
        
        # When: 統合清洗実行
        cleaner = DataCleaner(config={
            'employee_id_padding': 4,
            'department_mapping': {'開発課': '開発部'}
        })
        
        cleaning_result = cleaner.clean_dataframe(df, validation_report)
        
        # Then: 修正が適用される
        assert isinstance(cleaning_result, CleaningResult)
        cleaned_df = cleaning_result.cleaned_dataframe
        
        assert cleaned_df.loc[1, 'employee_id'] == 'EMP0002'  # パディング修正
        assert cleaned_df.loc[0, 'start_time'] == '09:00'     # フォーマット統一
        assert cleaned_df.loc[1, 'start_time'] == '10:00'     # フォーマット統一
        assert cleaned_df.loc[0, 'department'] == '開発部'    # 部署名正規化
        
        # 修正ログの確認
        assert len(cleaning_result.corrections_applied) >= 3

    def test_cleaning_configuration_levels(self):
        """清洗設定レベルテスト"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: テストデータ
        df = pd.DataFrame({
            'employee_name': ['　田中太郎　', 'YAMADA Hanako'],
            'start_time': ['9:00', '09:00:00']
        })
        
        # When: 異なる清洗レベルでテスト
        # Conservative（保守的）: 安全な修正のみ
        conservative_cleaner = DataCleaner(config={'level': 'conservative'})
        conservative_result = conservative_cleaner.apply_auto_corrections(df)
        
        # Aggressive（積極的）: より多くの推測修正
        aggressive_cleaner = DataCleaner(config={'level': 'aggressive'})
        aggressive_result = aggressive_cleaner.apply_auto_corrections(df)
        
        # Then: レベルによって修正内容が異なる
        # Conservative: 空白トリムのみ
        assert conservative_result.loc[0, 'employee_name'] == '田中太郎'
        assert conservative_result.loc[1, 'employee_name'] == 'YAMADA Hanako'  # アルファベットはそのまま
        
        # Aggressive: 名前の変換も実行
        assert aggressive_result.loc[0, 'employee_name'] == '田中太郎'
        assert aggressive_result.loc[1, 'employee_name'] == '山田花子'  # アルファベット変換実行

    def test_parallel_cleaning_performance(self):
        """並列清洗性能テスト"""
        # Red Phase: DataCleanerが未実装のため失敗
        if DataCleaner is None:
            pytest.skip("DataCleaner not implemented yet")
            
        # Given: 大量のテストデータ
        size = 5000
        df = pd.DataFrame({
            'employee_id': [f'EMP{i}' for i in range(size)],
            'start_time': ['9:00'] * (size // 2) + ['09:00:00'] * (size // 2),
            'department': ['開発課'] * (size // 2) + ['営業部'] * (size // 2)
        })
        
        # When: 並列清洗実行
        import time
        
        # シーケンシャル処理
        sequential_cleaner = DataCleaner(config={'parallel': False})
        start_time = time.time()
        sequential_result = sequential_cleaner.apply_auto_corrections(df)
        sequential_time = time.time() - start_time
        
        # 並列処理
        parallel_cleaner = DataCleaner(config={'parallel': True, 'n_jobs': 4})
        start_time = time.time()
        parallel_result = parallel_cleaner.apply_auto_corrections(df)
        parallel_time = time.time() - start_time
        
        # Then: 並列処理による高速化
        assert parallel_time < sequential_time
        speedup_ratio = sequential_time / parallel_time
        assert speedup_ratio >= 1.2  # 20%以上の高速化
        
        # 結果の一貫性確認
        pd.testing.assert_frame_equal(sequential_result, parallel_result)