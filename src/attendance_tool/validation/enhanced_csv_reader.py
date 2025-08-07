"""拡張CSVリーダー

既存のCSVReaderにデータ検証・クレンジング機能を統合
"""

import pandas as pd
from typing import Tuple, Optional
from ..data.csv_reader import CSVReader
from .validator import DataValidator, ValidationReport
from .cleaner import DataCleaner, CleaningResult


class EnhancedCSVReader(CSVReader):
    """拡張CSVリーダー
    
    既存のCSVReaderにデータ検証・クレンジング機能を追加
    TASK-101との連携を維持しながら、TASK-102の新機能を提供
    """
    
    def __init__(self, validator: DataValidator, cleaner: DataCleaner, config_path: Optional[str] = None):
        """初期化
        
        Args:
            validator: データ検証エンジン
            cleaner: データクレンジングエンジン
            config_path: 設定ファイルパス（csv_format.yaml）
        """
        super().__init__(config_path)
        self.validator = validator
        self.cleaner = cleaner
    
    def load_and_validate(self, file_path: str, encoding: Optional[str] = None) -> Tuple[pd.DataFrame, ValidationReport]:
        """CSVファイル読み込みと検証
        
        Args:
            file_path: CSVファイルパス
            encoding: 文字エンコーディング
            
        Returns:
            Tuple[pd.DataFrame, ValidationReport]: 読み込み結果と検証レポート
        """
        try:
            # 既存のCSVReader機能でファイル読み込み
            df = super().load_file(file_path, encoding)
            
            # データ検証実行
            validation_report = self.validator.validate_dataframe(df)
            
            # 重大エラーがなければ処理を継続
            critical_errors = validation_report.get_critical_errors()
            if len(critical_errors) > 0:
                # 重大エラーがある場合は、データは返すが警告
                self.logger.warning(f"重大エラーが {len(critical_errors)} 件検出されました")
            
            return df, validation_report
            
        except Exception as e:
            # 既存のCSVReaderの例外をそのまま再発生
            raise e
    
    def load_validate_and_clean(self, file_path: str, encoding: Optional[str] = None) -> Tuple[pd.DataFrame, ValidationReport, CleaningResult]:
        """CSVファイル読み込み・検証・清洗の完全ワークフロー
        
        Args:
            file_path: CSVファイルパス  
            encoding: 文字エンコーディング
            
        Returns:
            Tuple[pd.DataFrame, ValidationReport, CleaningResult]: 
                清洗済みDataFrame、検証レポート、清洗結果
        """
        # 読み込み・検証
        df, validation_report = self.load_and_validate(file_path, encoding)
        
        # データ清洗実行
        cleaning_result = self.cleaner.clean_dataframe(df, validation_report)
        
        return cleaning_result.cleaned_dataframe, validation_report, cleaning_result
    
    def get_enhanced_validation_result(self, file_path: str, encoding: Optional[str] = None) -> dict:
        """拡張検証結果取得
        
        統合的な分析結果を辞書形式で返す
        
        Args:
            file_path: CSVファイルパス
            encoding: 文字エンコーディング
            
        Returns:
            dict: 拡張検証結果
        """
        try:
            # 完全ワークフロー実行
            cleaned_df, validation_report, cleaning_result = self.load_validate_and_clean(file_path, encoding)
            
            # 結果統合
            result = {
                'file_info': {
                    'path': file_path,
                    'encoding': encoding,
                    'original_records': validation_report.total_records,
                    'valid_records': validation_report.valid_records
                },
                'validation': {
                    'quality_score': validation_report.quality_score,
                    'error_count': len(validation_report.errors),
                    'warning_count': len(validation_report.warnings),
                    'error_summary': validation_report.get_error_summary(),
                    'processing_time': validation_report.processing_time
                },
                'cleaning': {
                    'corrections_applied': len(cleaning_result.corrections_applied),
                    'suggestions_count': len(cleaning_result.suggestions),
                    'correction_summary': cleaning_result.get_correction_summary()
                },
                'data': {
                    'original_dataframe': cleaning_result.original_dataframe,
                    'cleaned_dataframe': cleaned_df
                },
                'reports': {
                    'validation_report': validation_report,
                    'cleaning_result': cleaning_result
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'file_info': {'path': file_path, 'encoding': encoding}
            }
    
    def export_comprehensive_report(self, file_path: str, output_dir: str, encoding: Optional[str] = None) -> dict:
        """包括的レポート出力
        
        Args:
            file_path: 入力CSVファイルパス
            output_dir: 出力ディレクトリ
            encoding: 文字エンコーディング
            
        Returns:
            dict: 出力ファイル情報
        """
        import os
        from datetime import datetime
        
        # 拡張検証実行
        result = self.get_enhanced_validation_result(file_path, encoding)
        
        if 'error' in result:
            return {'error': result['error']}
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        
        output_files = {}
        
        try:
            # 1. 検証レポート出力
            validation_report_path = os.path.join(output_dir, f'{base_name}_validation_report_{timestamp}.csv')
            result['reports']['validation_report'].export_to_csv(validation_report_path)
            output_files['validation_report'] = validation_report_path
            
            # 2. 清洗ログ出力
            cleaning_log_path = os.path.join(output_dir, f'{base_name}_cleaning_log_{timestamp}.csv')
            result['reports']['cleaning_result'].export_corrections_log(cleaning_log_path)
            output_files['cleaning_log'] = cleaning_log_path
            
            # 3. 清洗済みデータ出力
            cleaned_data_path = os.path.join(output_dir, f'{base_name}_cleaned_{timestamp}.csv')
            result['data']['cleaned_dataframe'].to_csv(cleaned_data_path, index=False, encoding='utf-8-sig')
            output_files['cleaned_data'] = cleaned_data_path
            
            # 4. サマリーレポート作成
            summary_path = os.path.join(output_dir, f'{base_name}_summary_{timestamp}.txt')
            self._create_summary_report(result, summary_path)
            output_files['summary'] = summary_path
            
            return {
                'status': 'success',
                'output_files': output_files,
                'summary': {
                    'original_records': result['file_info']['original_records'],
                    'valid_records': result['file_info']['valid_records'],
                    'quality_score': result['validation']['quality_score'],
                    'corrections_applied': result['cleaning']['corrections_applied']
                }
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'partial_output_files': output_files
            }
    
    def _create_summary_report(self, result: dict, output_path: str) -> None:
        """サマリーレポート作成"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=== 勤怠データ検証・清洗レポート ===\n\n")
            
            # ファイル情報
            f.write("【ファイル情報】\n")
            f.write(f"ファイルパス: {result['file_info']['path']}\n")
            f.write(f"文字エンコーディング: {result['file_info'].get('encoding', '自動検出')}\n")
            f.write(f"総レコード数: {result['file_info']['original_records']}\n")
            f.write(f"有効レコード数: {result['file_info']['valid_records']}\n\n")
            
            # 検証結果
            f.write("【検証結果】\n")
            f.write(f"データ品質スコア: {result['validation']['quality_score']:.2%}\n")
            f.write(f"エラー数: {result['validation']['error_count']}\n")
            f.write(f"警告数: {result['validation']['warning_count']}\n")
            f.write(f"処理時間: {result['validation']['processing_time']:.2f}秒\n\n")
            
            # エラーサマリー
            if result['validation']['error_summary']:
                f.write("【エラー詳細】\n")
                for field, count in result['validation']['error_summary'].items():
                    f.write(f"  {field}: {count}件\n")
                f.write("\n")
            
            # 清洗結果
            f.write("【清洗結果】\n")
            f.write(f"自動修正件数: {result['cleaning']['corrections_applied']}\n")
            f.write(f"修正提案件数: {result['cleaning']['suggestions_count']}\n")
            
            # 修正サマリー
            if result['cleaning']['correction_summary']:
                f.write("【修正詳細】\n")
                for field, count in result['cleaning']['correction_summary'].items():
                    f.write(f"  {field}: {count}件\n")
            
            f.write("\n=== レポート終了 ===\n")