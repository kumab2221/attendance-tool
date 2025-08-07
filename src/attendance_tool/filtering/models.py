"""
期間フィルタリング機能 - データモデル定義
TASK-103 Green Phase実装
"""

from dataclasses import dataclass
from typing import Union, Optional, Tuple, Dict, Any
from datetime import date, datetime
from enum import Enum
import pandas as pd


class PeriodType(Enum):
    """期間指定種別"""
    MONTH = "month"           # 月単位
    DATE_RANGE = "date_range" # 日付範囲
    RELATIVE = "relative"     # 相対期間
    CUSTOM = "custom"         # カスタム期間


@dataclass
class PeriodSpecification:
    """期間指定仕様"""
    
    period_type: PeriodType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    month_string: Optional[str] = None      # "2024-01"
    relative_string: Optional[str] = None   # "last_month"
    custom_config: Optional[dict] = None    # カスタム設定
    
    def to_date_range(self) -> Tuple[date, date]:
        """期間仕様を日付範囲に変換"""
        if self.period_type == PeriodType.DATE_RANGE:
            if self.start_date and self.end_date:
                return (self.start_date, self.end_date)
            else:
                raise InvalidPeriodError("日付範囲指定には開始日・終了日が必要です")
        
        elif self.period_type == PeriodType.MONTH:
            if self.month_string:
                return self._month_string_to_range(self.month_string)
            else:
                raise InvalidPeriodError("月指定にはmonth_stringが必要です")
        
        elif self.period_type == PeriodType.RELATIVE:
            if self.relative_string:
                return self._relative_to_range(self.relative_string)
            else:
                raise InvalidPeriodError("相対指定にはrelative_stringが必要です")
        
        else:
            raise InvalidPeriodError(f"未サポートの期間タイプ: {self.period_type}")
    
    def _month_string_to_range(self, month_string: str) -> Tuple[date, date]:
        """月文字列を日付範囲に変換"""
        try:
            year, month = map(int, month_string.split('-'))
            
            # 月初日
            start_date = date(year, month, 1)
            
            # 月末日の計算（うるう年対応）
            if month == 12:
                next_month_start = date(year + 1, 1, 1)
            else:
                next_month_start = date(year, month + 1, 1)
            
            from datetime import timedelta
            end_date = next_month_start - timedelta(days=1)
            
            return (start_date, end_date)
            
        except (ValueError, IndexError) as e:
            raise InvalidPeriodError(f"無効な月指定フォーマット: {month_string}")
    
    def _relative_to_range(self, relative_string: str) -> Tuple[date, date]:
        """相対指定を日付範囲に変換"""
        from dateutil.relativedelta import relativedelta
        
        today = date.today()
        
        if relative_string == "last_month":
            # 先月の範囲
            last_month_start = today.replace(day=1) - relativedelta(months=1)
            last_month_end = today.replace(day=1) - relativedelta(days=1)
            return (last_month_start, last_month_end)
        
        elif relative_string == "this_month":
            # 今月の範囲
            this_month_start = today.replace(day=1)
            next_month_start = this_month_start + relativedelta(months=1)
            this_month_end = next_month_start - relativedelta(days=1)
            return (this_month_start, this_month_end)
        
        elif relative_string == "next_month":
            # 来月の範囲
            next_month_start = today.replace(day=1) + relativedelta(months=1)
            next_next_month_start = next_month_start + relativedelta(months=1)
            next_month_end = next_next_month_start - relativedelta(days=1)
            return (next_month_start, next_month_end)
        
        else:
            raise InvalidPeriodError(f"未サポートの相対期間: {relative_string}")
    
    def validate(self) -> bool:
        """期間仕様の妥当性検証"""
        if self.period_type == PeriodType.MONTH:
            return self.month_string is not None
        elif self.period_type == PeriodType.DATE_RANGE:
            return self.start_date is not None and self.end_date is not None
        elif self.period_type == PeriodType.RELATIVE:
            return self.relative_string is not None
        else:
            return False


@dataclass  
class FilterResult:
    """フィルタリング結果"""
    
    filtered_data: pd.DataFrame
    original_count: int
    filtered_count: int
    date_range: Tuple[date, date]
    processing_time: float
    
    # 統計情報
    earliest_date: Optional[date] = None
    latest_date: Optional[date] = None
    excluded_records: int = 0
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー情報取得"""
        filtered_ratio = self.filtered_count / self.original_count if self.original_count > 0 else 0.0
        date_span_days = (self.date_range[1] - self.date_range[0]).days
        
        return {
            "original_count": self.original_count,
            "filtered_count": self.filtered_count,
            "excluded_records": self.excluded_records,
            "filtered_ratio": filtered_ratio,
            "processing_time": self.processing_time,
            "date_range": self.date_range,
            "date_span_days": date_span_days,
            "earliest_date": self.earliest_date,
            "latest_date": self.latest_date
        }


@dataclass
class DateFilterConfig:
    """期間フィルタ設定"""
    
    # 基本設定
    default_date_column: str = "work_date"
    auto_detect_columns: bool = True
    
    # 境界値処理
    leap_year_adjustment: bool = True
    month_end_adjustment: bool = True
    invalid_date_handling: str = "adjust"  # adjust/error/skip
    
    # パフォーマンス設定
    enable_optimization: bool = True
    chunk_size: int = 10000
    parallel_processing: bool = False
    
    # カスタム期間定義
    custom_periods: Optional[Dict[str, str]] = None
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "DateFilterConfig":
        """YAML設定読み込み"""
        import yaml
        
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
                
            date_filter_config = config_data.get('date_filter', {})
            
            return cls(
                default_date_column=date_filter_config.get('default_date_column', 'work_date'),
                auto_detect_columns=date_filter_config.get('auto_detect_columns', True),
                leap_year_adjustment=date_filter_config.get('leap_year_adjustment', True),
                month_end_adjustment=date_filter_config.get('month_end_adjustment', True),
                invalid_date_handling=date_filter_config.get('invalid_date_handling', 'adjust'),
                enable_optimization=date_filter_config.get('enable_optimization', True),
                chunk_size=date_filter_config.get('chunk_size', 10000),
                parallel_processing=date_filter_config.get('parallel_processing', False),
                custom_periods=date_filter_config.get('custom_periods', None)
            )
        except FileNotFoundError:
            # 設定ファイルがない場合はデフォルト設定を返す
            return cls()
        except Exception as e:
            raise InvalidPeriodError(f"設定ファイル読み込みエラー: {e}")


# 例外クラス定義

class DateFilterError(Exception):
    """期間フィルタエラー基底クラス"""
    pass


class InvalidPeriodError(DateFilterError):
    """無効期間指定エラー"""
    pass


class DateRangeError(DateFilterError):
    """日付範囲エラー"""  
    pass