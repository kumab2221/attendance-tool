"""データ検証用モデル

AttendanceRecordモデルとカスタム例外クラスを定義
pydantic風のAPIを提供するが、内部実装は標準ライブラリベース
"""

from datetime import date, time, datetime, timedelta
from typing import Optional, Any, Dict
import re


# カスタム例外クラス
class ValidationError(Exception):
    """データ検証エラー基底クラス"""
    
    def __init__(self, message: str, field: str = None, value: Any = None, error_code: str = None):
        """
        Args:
            message: エラーメッセージ
            field: エラーが発生したフィールド名
            value: エラーが発生した値
            error_code: エラーコード
        """
        super().__init__(message)
        self.field = field
        self.value = value
        self.error_code = error_code
        self.message = message


class TimeLogicError(ValidationError):
    """時刻論理エラー (EDGE-201)"""
    
    def __init__(self, message: str, start_time: Any = None, end_time: Any = None):
        super().__init__(message, field='time_logic', error_code='EDGE-201')
        self.start_time = start_time
        self.end_time = end_time


class WorkHoursError(ValidationError):
    """勤務時間エラー (REQ-104)"""
    
    def __init__(self, message: str, work_hours: float = None):
        super().__init__(message, field='work_hours', error_code='REQ-104')
        self.work_hours = work_hours


class DateRangeError(ValidationError):
    """日付範囲エラー (EDGE-204)"""
    
    def __init__(self, message: str, date_value: Any = None):
        super().__init__(message, field='work_date', error_code='EDGE-204')
        self.date_value = date_value


class MissingDataError(ValidationError):
    """欠損データエラー"""
    
    def __init__(self, message: str, field: str = None):
        super().__init__(message, field=field, error_code='MISSING_DATA')
        self.missing_field = field


class AttendanceRecord:
    """勤怠レコードモデル
    
    pydantic風APIを持つデータモデル
    業務ルールに基づくバリデーションを含む
    """
    
    def __init__(self, **kwargs):
        """初期化とバリデーション"""
        # 必須フィールドのデフォルト値
        self.employee_id = kwargs.get('employee_id')
        self.employee_name = kwargs.get('employee_name')  
        self.work_date = kwargs.get('work_date')
        
        # オプショナルフィールド
        self.department = kwargs.get('department')
        self.start_time = kwargs.get('start_time')
        self.end_time = kwargs.get('end_time')
        self.break_minutes = kwargs.get('break_minutes')
        self.work_status = kwargs.get('work_status')
        
        # バリデーション実行
        self._validate_all(kwargs)
    
    def _validate_all(self, values: Dict[str, Any]) -> None:
        """全フィールドの検証"""
        # 社員ID検証
        self.employee_id = self._validate_employee_id(self.employee_id)
        
        # 社員名検証  
        self.employee_name = self._validate_employee_name(self.employee_name)
        
        # 勤務日検証
        self.work_date = self._validate_work_date(self.work_date)
        
        # 休憩時間検証
        self.break_minutes = self._validate_break_minutes(self.break_minutes)
        
        # 勤務状態検証
        self.work_status = self._validate_work_status(self.work_status)
        
        # 時刻論理検証
        self._validate_time_logic(values)
    
    def _validate_employee_id(self, v):
        """社員ID検証"""
        if not v or not str(v).strip():
            raise ValueError('社員IDは必須です')
        
        v_str = str(v).strip()
        
        # 基本的なフォーマットチェック（EMP + 数字）
        if not re.match(r'^[A-Z]{3}\d+$', v_str):
            # 最小限の実装：警告レベルではなくエラー
            # 後のリファクタリングで改善予定
            pass  # 現在は緩い検証
            
        return v_str
    
    def _validate_employee_name(self, v):
        """社員名検証"""
        if not v or not str(v).strip():
            raise ValueError('社員名は必須です')
        return str(v).strip()
    
    def _validate_work_date(self, v):
        """勤務日検証 (EDGE-204対応)"""
        if not v:
            raise ValueError('勤務日は必須です')
        
        if not isinstance(v, date):
            raise ValueError('勤務日は日付型である必要があります')
        
        today = date.today()
        
        # 未来日チェック（警告レベルとして例外発生）
        if v > today:
            raise ValueError('未来の日付です')
        
        # 過去5年を超えるチェック
        past_limit = today - timedelta(days=365 * 5)
        if v < past_limit:
            raise ValueError('過去の日付です（5年以上前）')
            
        return v
    
    def _validate_break_minutes(self, v):
        """休憩時間検証"""
        if v is None:
            return v
            
        if not isinstance(v, int):
            try:
                v = int(v)
            except (ValueError, TypeError):
                return v  # 変換できない場合はそのまま返す
                
        if v < 0:
            raise ValueError('休憩時間は0以上である必要があります')
        
        # 24時間を超える休憩時間（1440分以上）
        if v >= 1440:
            raise ValueError('休憩時間が長すぎます')
            
        return v
    
    def _validate_work_status(self, v):
        """勤務状態検証"""
        if v is None:
            return v
            
        valid_statuses = ["出勤", "欠勤", "有給", "特別休暇", "半休", "遅刻", "早退"]
        if v not in valid_statuses:
            raise ValueError('無効な勤務状態です')
            
        return v
    
    def _validate_time_logic(self, values):
        """時刻論理検証 (EDGE-201対応)"""
        start_time = self.start_time
        end_time = self.end_time
        
        # 両方の時刻が設定されている場合のみチェック
        if start_time is not None and end_time is not None:
            # 同じ時刻の場合（0時間勤務）
            if start_time == end_time:
                raise TimeLogicError(
                    '出勤時刻と退勤時刻が同じです。0時間勤務は無効です。',
                    start_time=start_time,
                    end_time=end_time
                )
            
            # 出勤時刻 > 退勤時刻の場合（日跨ぎの可能性）
            if start_time > end_time:
                # 日跨ぎ勤務の可能性をより詳細にチェック
                potential_work_hours = self._calculate_crossover_work_hours(start_time, end_time)
                
                if potential_work_hours > 24:  # 24時間超は異常
                    raise WorkHoursError(
                        f'計算された勤務時間が24時間を超えています: {potential_work_hours:.1f}時間',
                        work_hours=potential_work_hours
                    )
                elif potential_work_hours < 1:  # 1時間未満は入力ミスの可能性
                    raise TimeLogicError(
                        '出勤時刻が退勤時刻より遅く、勤務時間が短すぎます。入力ミスの可能性があります。',
                        start_time=start_time,
                        end_time=end_time
                    )
                # 1-24時間の範囲なら日跨ぎ勤務として許可（警告は別途）
    
    def _calculate_crossover_work_hours(self, start_time: time, end_time: time) -> float:
        """日跨ぎ勤務時間を計算"""
        next_day_end = datetime.combine(date.today() + timedelta(days=1), end_time)
        today_start = datetime.combine(date.today(), start_time)
        
        duration = next_day_end - today_start
        hours = duration.total_seconds() / 3600
        
        # 休憩時間を考慮
        if self.break_minutes and self.break_minutes > 0:
            hours -= self.break_minutes / 60
            
        return hours
    
    def is_24_hour_work(self) -> bool:
        """24時間勤務かどうか判定
        
        Returns:
            bool: 24時間以上の勤務の場合True
        """
        work_minutes = self.get_work_duration_minutes()
        if work_minutes is None:
            return False
            
        # 24時間 = 1440分
        return work_minutes >= 1440
    
    def is_over_time_work(self, standard_work_hours: float = 8.0) -> bool:
        """残業かどうか判定
        
        Args:
            standard_work_hours: 所定労働時間（時間単位）
            
        Returns:
            bool: 所定労働時間を超える場合True
        """
        work_minutes = self.get_work_duration_minutes()
        if work_minutes is None:
            return False
            
        standard_minutes = standard_work_hours * 60
        return work_minutes > standard_minutes
    
    def get_over_time_minutes(self, standard_work_hours: float = 8.0) -> int:
        """残業時間を分単位で取得
        
        Args:
            standard_work_hours: 所定労働時間（時間単位）
            
        Returns:
            int: 残業時間（分単位）
        """
        work_minutes = self.get_work_duration_minutes()
        if work_minutes is None:
            return 0
            
        standard_minutes = standard_work_hours * 60
        return max(0, work_minutes - int(standard_minutes))
    
    def get_work_duration_minutes(self) -> Optional[int]:
        """勤務時間を分単位で取得
        
        Returns:
            Optional[int]: 勤務時間（分単位）、計算できない場合はNone
        """
        if self.start_time is None or self.end_time is None:
            return None
            
        # 同日内の勤務時間計算
        if self.start_time <= self.end_time:
            duration = datetime.combine(date.today(), self.end_time) - \
                      datetime.combine(date.today(), self.start_time)
            total_minutes = int(duration.total_seconds() / 60)
            
            # 休憩時間を差し引き
            if self.break_minutes and self.break_minutes > 0:
                total_minutes -= self.break_minutes
                
            return max(0, total_minutes)  # 負の値は0に
        else:
            # 日跨ぎ勤務の場合（24:00を超える勤務）
            # 例: 22:00 - 06:00 = 8時間勤務
            next_day_end = datetime.combine(date.today() + timedelta(days=1), self.end_time)
            today_start = datetime.combine(date.today(), self.start_time)
            
            duration = next_day_end - today_start
            total_minutes = int(duration.total_seconds() / 60)
            
            # 休憩時間を差し引き
            if self.break_minutes and self.break_minutes > 0:
                total_minutes -= self.break_minutes
                
            # 24時間を超える勤務は異常として警告対象（REQ-104）
            if total_minutes > 1440:  # 24時間 = 1440分
                # 現在は計算結果を返すが、警告フラグを設定可能
                pass
                
            return max(0, total_minutes)
    
    def dict(self) -> dict:
        """辞書形式で返す"""
        return {
            'employee_id': self.employee_id,
            'employee_name': self.employee_name,
            'work_date': self.work_date,
            'department': self.department,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'break_minutes': self.break_minutes,
            'work_status': self.work_status
        }
    
    def dict_with_computed_fields(self) -> dict:
        """計算フィールドを含む辞書を返す"""
        result = self.dict()
        result['work_duration_minutes'] = self.get_work_duration_minutes()
        result['is_24_hour_work'] = self.is_24_hour_work()
        return result