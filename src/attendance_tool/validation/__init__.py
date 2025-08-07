"""データ検証・クレンジング機能

TASK-102: データ検証・クレンジング機能の実装
pydantic風のデータモデル定義と業務ルールに基づくデータ検証・クレンジング機能を提供
"""

# モデルは常にインポート可能
from .models import AttendanceRecord, TimeLogicError, WorkHoursError, DateRangeError, MissingDataError
from .rules import ValidationRule

__all__ = [
    'AttendanceRecord',
    'TimeLogicError', 
    'WorkHoursError',
    'DateRangeError',
    'MissingDataError',
    'ValidationRule'
]

# pandas依存のモジュールは条件付きインポート
try:
    from .validator import DataValidator, ValidationReport, ValidationError, ValidationWarning
    from .cleaner import DataCleaner, CleaningResult, CorrectionSuggestion
    
    __all__.extend([
        'DataValidator',
        'ValidationReport',
        'ValidationError',
        'ValidationWarning',
        'DataCleaner',
        'CleaningResult',
        'CorrectionSuggestion'
    ])
    
except ImportError as e:
    # pandas等が利用できない場合のフォールバック
    print(f"Warning: Some validation modules not available due to missing dependencies: {e}")
    DataValidator = None
    DataCleaner = None