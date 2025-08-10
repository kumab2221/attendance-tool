"""
E2Eワークフローコーディネーター

統合テスト用のワークフロー実行を管理する。
"""

import time
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
import pandas as pd
from click.testing import CliRunner

from attendance_tool.cli.main import main
from attendance_tool.data.csv_reader import CSVReader


class E2EWorkflowCoordinator:
    """E2E統合テスト用のワークフローコーディネーター"""
    
    def __init__(self):
        self.csv_reader = CSVReader()
    
    def execute_complete_workflow(self, input_file: Path, output_dir: Path, 
                                 month: str) -> Dict[str, Any]:
        """完全なワークフローを実行"""
        try:
            # 1. CSVファイル読み込み
            raw_data = self._load_csv_data(input_file)
            
            # 2. データ検証
            validation_result = self._validate_data(raw_data)
            
            # 3. 基本的な集計処理
            summary_data = self._calculate_summary(raw_data)
            
            # 4. レポート出力
            output_file = self._export_report(summary_data, output_dir, month)
            
            return self._create_success_result(
                len(raw_data), output_file, validation_result
            )
            
        except Exception as e:
            return self._create_error_result(e)
    
    def _load_csv_data(self, input_file: Path) -> pd.DataFrame:
        """CSVデータを読み込み"""
        return self.csv_reader.load_file(str(input_file))
    
    def _validate_data(self, raw_data: pd.DataFrame) -> Any:
        """データ検証を実行"""
        return self.csv_reader.validate_data(raw_data)
    
    def _get_column_mapping(self, raw_data: pd.DataFrame) -> Dict[str, Optional[str]]:
        """カラムマッピングを取得"""
        mapping = {
            'emp_id': None,
            'emp_name': None,
            'dept': None
        }
        
        column_patterns = {
            'emp_id': ['社員ID', 'employee_id', '従業員ID'],
            'emp_name': ['氏名', 'employee_name', '従業員名'],
            'dept': ['部署', 'department', '部門']
        }
        
        for col in raw_data.columns:
            for key, patterns in column_patterns.items():
                if col in patterns:
                    mapping[key] = col
                    break
        
        return mapping
    
    def _calculate_summary(self, raw_data: pd.DataFrame) -> List[Dict[str, Any]]:
        """集計処理を実行"""
        summary_data = []
        if raw_data.empty:
            return summary_data
        
        column_mapping = self._get_column_mapping(raw_data)
        emp_id_col = column_mapping['emp_id']
        
        if not emp_id_col:
            return summary_data
        
        for emp_id in raw_data[emp_id_col].unique():
            emp_data = raw_data[raw_data[emp_id_col] == emp_id]
            summary_data.append(self._create_employee_summary(emp_data, column_mapping))
        
        return summary_data
    
    def _create_employee_summary(self, emp_data: pd.DataFrame, 
                                column_mapping: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """従業員サマリーを作成"""
        return {
            '社員ID': emp_data.iloc[0][column_mapping['emp_id']],
            '氏名': emp_data.iloc[0][column_mapping['emp_name']] if column_mapping['emp_name'] else 'N/A',
            '部署': emp_data.iloc[0][column_mapping['dept']] if column_mapping['dept'] else 'N/A',
            '出勤日数': len(emp_data),
            '総労働時間': len(emp_data) * 8  # 簡易計算
        }
    
    def _export_report(self, summary_data: List[Dict[str, Any]], 
                      output_dir: Path, month: str) -> Path:
        """レポートを出力"""
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"attendance_report_{month.replace('-', '_')}.csv"
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        else:
            # 空のファイルを作成
            pd.DataFrame().to_csv(output_file, index=False, encoding='utf-8-sig')
        
        return output_file
    
    def _create_success_result(self, records_count: int, output_file: Path, 
                              validation_result: Any) -> Dict[str, Any]:
        """成功結果を作成"""
        return {
            "status": "success",
            "records_processed": records_count,
            "output_file": str(output_file),
            "validation_errors": len(validation_result.errors) if hasattr(validation_result, 'errors') else 0,
            "warnings": len(validation_result.warnings) if hasattr(validation_result, 'warnings') else 0
        }
    
    def _create_error_result(self, exception: Exception) -> Dict[str, Any]:
        """エラー結果を作成"""
        return {
            "status": "error",
            "error_message": str(exception),
            "error_type": type(exception).__name__
        }
    
    def execute_cli_workflow(self, input_file: Path, output_dir: Path, 
                           month: str) -> Dict[str, Any]:
        """CLI経由でのワークフローを実行"""
        runner = CliRunner()
        
        result = runner.invoke(main, [
            '--input', str(input_file),
            '--output', str(output_dir), 
            '--month', month
        ])
        
        return {
            "exit_code": result.exit_code,
            "output": result.output,
            "exception": result.exception
        }
    
    def measure_performance(self, input_file: Path, output_dir: Path,
                          month: str) -> Dict[str, Any]:
        """パフォーマンス測定付きでワークフローを実行"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        start_time = time.time()
        result = self.execute_complete_workflow(input_file, output_dir, month)
        end_time = time.time()
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        
        result.update({
            "execution_time_seconds": end_time - start_time,
            "memory_usage_mb": memory_after - memory_before,
            "peak_memory_mb": memory_after
        })
        
        return result
    
    def check_security_compliance(self, input_file: Path, output_dir: Path,
                                month: str) -> Dict[str, Any]:
        """セキュリティコンプライアンスを確認"""
        # 一時ファイルのトラッキング
        temp_files_before = set(Path(tempfile.gettempdir()).iterdir())
        
        result = self.execute_complete_workflow(input_file, output_dir, month)
        
        temp_files_after = set(Path(tempfile.gettempdir()).iterdir())
        
        # ログファイルの個人情報確認（簡易版）
        log_files = list(Path("logs").glob("*.log")) if Path("logs").exists() else []
        personal_info_found = False
        
        for log_file in log_files:
            try:
                content = log_file.read_text(encoding='utf-8')
                # 簡易的な個人情報検出
                if any(word in content for word in ["山田", "佐藤", "田中", "EMP001"]):
                    personal_info_found = True
                    break
            except Exception:
                continue
        
        result.update({
            "temp_files_cleaned": len(temp_files_after - temp_files_before) == 0,
            "personal_info_in_logs": personal_info_found,
            "security_compliant": not personal_info_found
        })
        
        return result