"""データ検証設定管理

validation_rules.yamlファイルの読み込みと設定管理機能
"""

import os
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging


class ValidationConfig:
    """データ検証設定管理クラス"""
    
    def __init__(self, config_path: Optional[str] = None):
        """設定初期化
        
        Args:
            config_path: 設定ファイルパス（validation_rules.yaml）
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if not self.config_path:
            # デフォルト設定パス
            default_config = Path(__file__).parent.parent.parent.parent / "config" / "validation_rules.yaml"
            if default_config.exists():
                self.config_path = str(default_config)
            else:
                # 設定ファイルが見つからない場合のデフォルト設定
                return self._get_default_config()
                
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.logger.warning(f"設定ファイル読み込みエラー: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """デフォルト設定を返す"""
        return {
            "validation": {
                "employee_id": {
                    "pattern": r"^[A-Z]{3}\d{3,4}$",
                    "required": True,
                    "max_length": 10
                },
                "employee_name": {
                    "required": True,
                    "max_length": 50,
                    "min_length": 1
                }
            },
            "date_validation": {
                "work_date": {
                    "past_years": 5,
                    "future_days": 0
                }
            },
            "time_validation": {
                "work_hours": {
                    "max_daily_hours": 24.0,
                    "min_daily_hours": 0.5,
                    "standard_hours": 8.0,
                    "overtime_warning_hours": 10.0
                }
            }
        }
    
    def get_employee_id_config(self) -> Dict[str, Any]:
        """社員ID検証設定を取得"""
        return self.config.get("validation", {}).get("employee_id", {})
    
    def get_employee_name_config(self) -> Dict[str, Any]:
        """社員名検証設定を取得"""
        return self.config.get("validation", {}).get("employee_name", {})
    
    def get_department_config(self) -> Dict[str, Any]:
        """部署検証設定を取得"""
        return self.config.get("validation", {}).get("department", {})
    
    def get_date_validation_config(self) -> Dict[str, Any]:
        """日付検証設定を取得"""
        return self.config.get("date_validation", {}).get("work_date", {})
    
    def get_time_validation_config(self) -> Dict[str, Any]:
        """時刻検証設定を取得"""
        return self.config.get("time_validation", {})
    
    def get_work_hours_config(self) -> Dict[str, Any]:
        """勤務時間検証設定を取得"""
        return self.config.get("time_validation", {}).get("work_hours", {})
    
    def get_break_time_config(self) -> Dict[str, Any]:
        """休憩時間検証設定を取得"""
        return self.config.get("break_time_validation", {})
    
    def get_work_status_config(self) -> Dict[str, Any]:
        """勤務状態検証設定を取得"""
        return self.config.get("work_status_validation", {})
    
    def get_data_quality_config(self) -> Dict[str, Any]:
        """データ品質設定を取得"""
        return self.config.get("data_quality", {})
    
    def get_performance_config(self) -> Dict[str, Any]:
        """パフォーマンス設定を取得"""
        return self.config.get("performance", {})
    
    def get_valid_departments(self) -> List[str]:
        """有効な部署リストを取得"""
        dept_config = self.get_department_config()
        return dept_config.get("valid_departments", [])
    
    def get_department_mapping(self) -> Dict[str, str]:
        """部署名マッピングを取得"""
        dept_config = self.get_department_config()
        return dept_config.get("department_mapping", {})
    
    def get_valid_work_statuses(self) -> List[str]:
        """有効な勤務状態リストを取得"""
        status_config = self.get_work_status_config()
        return status_config.get("valid_statuses", [
            "出勤", "欠勤", "有給", "特別休暇", "半休", "遅刻", "早退"
        ])
    
    def get_max_work_hours(self) -> float:
        """最大勤務時間を取得"""
        work_hours_config = self.get_work_hours_config()
        return work_hours_config.get("max_daily_hours", 24.0)
    
    def get_min_work_hours(self) -> float:
        """最小勤務時間を取得"""
        work_hours_config = self.get_work_hours_config()
        return work_hours_config.get("min_daily_hours", 0.5)
    
    def get_standard_work_hours(self) -> float:
        """標準勤務時間を取得"""
        work_hours_config = self.get_work_hours_config()
        return work_hours_config.get("standard_hours", 8.0)
    
    def get_overtime_warning_hours(self) -> float:
        """残業警告しきい値を取得"""
        work_hours_config = self.get_work_hours_config()
        return work_hours_config.get("overtime_warning_hours", 10.0)
    
    def get_past_years_limit(self) -> int:
        """過去年数制限を取得"""
        date_config = self.get_date_validation_config()
        return date_config.get("past_years", 5)
    
    def get_future_days_limit(self) -> int:
        """未来日制限を取得"""
        date_config = self.get_date_validation_config()
        return date_config.get("future_days", 0)
    
    def get_quality_thresholds(self) -> Dict[str, float]:
        """品質しきい値を取得"""
        quality_config = self.get_data_quality_config()
        return quality_config.get("quality_thresholds", {
            "excellent": 0.95,
            "good": 0.85,
            "acceptable": 0.70,
            "poor": 0.50
        })
    
    def get_quality_weights(self) -> Dict[str, float]:
        """品質スコア重みを取得"""
        quality_config = self.get_data_quality_config()
        return quality_config.get("quality_weights", {
            "required_fields": 0.4,
            "valid_formats": 0.3,
            "logical_consistency": 0.2,
            "data_completeness": 0.1
        })
    
    def is_parallel_enabled(self) -> bool:
        """並列処理が有効かチェック"""
        perf_config = self.get_performance_config()
        return perf_config.get("enable_parallel", True)
    
    def get_max_workers(self) -> int:
        """最大ワーカー数を取得"""
        perf_config = self.get_performance_config()
        return perf_config.get("max_workers", 4)
    
    def get_batch_size(self) -> int:
        """バッチサイズを取得"""
        perf_config = self.get_performance_config()
        return perf_config.get("batch_size", 1000)
    
    def validate_config(self) -> List[str]:
        """設定の妥当性をチェック
        
        Returns:
            List[str]: 検証エラーメッセージのリスト
        """
        errors = []
        
        # 必須設定項目チェック
        required_sections = ["validation", "date_validation", "time_validation"]
        for section in required_sections:
            if section not in self.config:
                errors.append(f"必須設定セクションが不足: {section}")
        
        # 数値範囲チェック
        work_hours_config = self.get_work_hours_config()
        max_hours = work_hours_config.get("max_daily_hours", 0)
        min_hours = work_hours_config.get("min_daily_hours", 0)
        
        if max_hours <= min_hours:
            errors.append("最大勤務時間は最小勤務時間より大きい必要があります")
        
        if max_hours > 48:
            errors.append("最大勤務時間が48時間を超えています（労働基準法違反の可能性）")
        
        # 品質しきい値チェック
        thresholds = self.get_quality_thresholds()
        if not all(0 <= v <= 1 for v in thresholds.values()):
            errors.append("品質しきい値は0-1の範囲である必要があります")
        
        return errors
    
    def reload_config(self) -> bool:
        """設定を再読み込み
        
        Returns:
            bool: 再読み込み成功時True
        """
        try:
            self.config = self._load_config()
            validation_errors = self.validate_config()
            
            if validation_errors:
                self.logger.warning(f"設定検証エラー: {validation_errors}")
                return False
            
            self.logger.info("設定を再読み込みしました")
            return True
            
        except Exception as e:
            self.logger.error(f"設定再読み込みエラー: {e}")
            return False
    
    def export_config(self, output_path: str) -> bool:
        """現在の設定をファイルに出力
        
        Args:
            output_path: 出力ファイルパス
            
        Returns:
            bool: 出力成功時True
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, ensure_ascii=False, default_flow_style=False, indent=2)
            
            self.logger.info(f"設定をファイルに出力しました: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"設定出力エラー: {e}")
            return False