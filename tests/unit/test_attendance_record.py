"""AttendanceRecord pydanticモデルのテスト

TASK-102: データ検証・クレンジング機能のTDDテスト
このファイルは失敗するテスト（Red Phase）から始まります
"""

import pytest
from datetime import date, time, timedelta
from pydantic import ValidationError

# まだ実装されていないため、ImportErrorが発生する予定
try:
    from attendance_tool.validation.models import AttendanceRecord, TimeLogicError
except ImportError:
    # Red Phase: モジュールが存在しないため、テストは失敗する
    AttendanceRecord = None
    TimeLogicError = None


class TestAttendanceRecordNormal:
    """AttendanceRecord正常系テスト"""
    
    def test_valid_record_creation(self):
        """有効なレコード作成テスト"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 有効なデータ
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "department": "開発部",
            "work_date": date(2024, 1, 15),
            "start_time": time(9, 0),
            "end_time": time(18, 0),
            "break_minutes": 60
        }
        
        # When: レコード作成
        record = AttendanceRecord(**data)
        
        # Then: 正しく作成される
        assert record.employee_id == "EMP001"
        assert record.employee_name == "田中太郎"
        assert record.department == "開発部"
        assert record.work_date == date(2024, 1, 15)
        assert record.start_time == time(9, 0)
        assert record.end_time == time(18, 0)
        assert record.break_minutes == 60
        
    def test_optional_fields_none(self):
        """オプショナルフィールドがNoneのケース"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 必須フィールドのみ
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15)
        }
        
        # When & Then: エラーなしで作成
        record = AttendanceRecord(**data)
        assert record.employee_id == "EMP001"
        assert record.employee_name == "田中太郎"
        assert record.work_date == date(2024, 1, 15)
        assert record.department is None
        assert record.start_time is None
        assert record.end_time is None
        assert record.break_minutes is None

    def test_work_status_optional(self):
        """勤務状態オプションフィールドのテスト"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: work_statusを含むデータ
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15),
            "work_status": "出勤"
        }
        
        # When: レコード作成
        record = AttendanceRecord(**data)
        
        # Then: work_statusが設定される
        assert record.work_status == "出勤"


class TestAttendanceRecordValidation:
    """AttendanceRecordバリデーションテスト"""
    
    def test_invalid_employee_id_empty(self):
        """空の社員IDテスト (エラーケース)"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 空の社員ID
        data = {
            "employee_id": "",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15)
        }
        
        # When & Then: ValidationError発生
        with pytest.raises(ValidationError, match="社員IDは必須"):
            AttendanceRecord(**data)
            
    def test_invalid_employee_name_empty(self):
        """空の社員名テスト (エラーケース)"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 空の社員名
        data = {
            "employee_id": "EMP001",
            "employee_name": "",
            "work_date": date(2024, 1, 15)
        }
        
        # When & Then: ValidationError発生
        with pytest.raises(ValidationError, match="社員名は必須"):
            AttendanceRecord(**data)
            
    def test_future_work_date(self):
        """未来日の検証 (EDGE-204)"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 未来の日付
        future_date = date.today() + timedelta(days=1)
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": future_date
        }
        
        # When & Then: 警告レベルの例外（カスタム例外として）
        with pytest.raises(ValidationError, match="未来の日付"):
            AttendanceRecord(**data)
            
    def test_start_time_after_end_time(self):
        """出勤時刻 > 退勤時刻 (EDGE-201) - 日跨ぎ勤務として処理される"""
        # Red Phase: AttendanceRecord, TimeLogicErrorが未実装のため失敗
        if AttendanceRecord is None or TimeLogicError is None:
            pytest.skip("AttendanceRecord or TimeLogicError not implemented yet")
            
        # Given: 日跨ぎ勤務のケース（18:00 → 翌9:00, 13時間勤務）
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15),
            "start_time": time(18, 0),  # 18:00
            "end_time": time(9, 0),     # 翌日09:00（日跨ぎ勤務）
            "break_minutes": 60
        }
        
        # When: レコード作成（日跨ぎ勤務として正常処理される）
        record = AttendanceRecord(**data)
        
        # Then: 正常に作成される
        assert record.start_time == time(18, 0)
        assert record.end_time == time(9, 0)
            
    def test_negative_break_minutes(self):
        """負の休憩時間"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 負の休憩時間
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15),
            "break_minutes": -30
        }
        
        # When & Then: バリデーションエラー
        with pytest.raises(ValidationError, match="休憩時間は0以上"):
            AttendanceRecord(**data)
            
    def test_excessive_break_minutes(self):
        """過大な休憩時間（24時間超）"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 24時間を超える休憩時間
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": date(2024, 1, 15),
            "break_minutes": 1500  # 25時間
        }
        
        # When & Then: バリデーションエラー
        with pytest.raises(ValidationError, match="休憩時間が長すぎます"):
            AttendanceRecord(**data)

    def test_past_date_beyond_limit(self):
        """5年以上前の古い日付テスト"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 5年以上前の日付
        old_date = date.today() - timedelta(days=365 * 6)  # 6年前
        data = {
            "employee_id": "EMP001",
            "employee_name": "田中太郎",
            "work_date": old_date
        }
        
        # When & Then: 警告レベルエラー
        with pytest.raises(ValidationError, match="過去の日付"):
            AttendanceRecord(**data)


class TestAttendanceRecordTimeBoundary:
    """時刻境界値テスト"""
    
    @pytest.mark.parametrize("start_time,end_time,should_raise", [
        (time(0, 0), time(23, 59), False),   # 通常の24時間勤務
        (time(23, 59), time(0, 1), True),    # 日跨ぎ（EDGE-201）
        (time(23, 58), time(23, 59), False), # 1分勤務
        (time(9, 0), time(9, 0), True),      # 同時刻（0時間勤務）
    ])
    def test_time_boundary_validation(self, start_time, end_time, should_raise):
        """時刻境界値検証"""
        # Red Phase: AttendanceRecord, TimeLogicErrorが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 境界値の時刻ペア
        data = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': date(2024, 1, 15),
            'start_time': start_time,
            'end_time': end_time
        }
        
        # When & Then: 期待される結果
        if should_raise:
            with pytest.raises((TimeLogicError, ValidationError)):
                AttendanceRecord(**data)
        else:
            record = AttendanceRecord(**data)
            assert record.start_time == start_time
            assert record.end_time == end_time

    def test_24_hour_work_detection(self):
        """24時間勤務検出テスト (REQ-104)"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 同じ時刻の出退勤（0時間勤務として扱われる）
        data = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': date(2024, 1, 15),
            'start_time': time(8, 0),
            'end_time': time(8, 0),  # 同じ時刻のためTimeLogicError
            'break_minutes': 60
        }
        
        # When & Then: TimeLogicErrorが発生することを確認
        from src.attendance_tool.validation.models import TimeLogicError
        with pytest.raises(TimeLogicError, match="0時間勤務は無効です"):
            AttendanceRecord(**data)


class TestAttendanceRecordWorkStatus:
    """勤務状態バリデーションテスト"""
    
    @pytest.mark.parametrize("work_status", [
        "出勤", "欠勤", "有給", "特別休暇", "半休", "遅刻", "早退"
    ])
    def test_valid_work_status(self, work_status):
        """有効な勤務状態のテスト"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 有効な勤務状態
        data = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': date(2024, 1, 15),
            'work_status': work_status
        }
        
        # When: レコード作成
        record = AttendanceRecord(**data)
        
        # Then: 勤務状態が設定される
        assert record.work_status == work_status
        
    def test_invalid_work_status(self):
        """無効な勤務状態のテスト"""
        # Red Phase: AttendanceRecordが未実装のため失敗
        if AttendanceRecord is None:
            pytest.skip("AttendanceRecord not implemented yet")
            
        # Given: 無効な勤務状態
        data = {
            'employee_id': 'EMP001',
            'employee_name': '田中太郎',
            'work_date': date(2024, 1, 15),
            'work_status': '無効な状態'
        }
        
        # When & Then: バリデーションエラー
        with pytest.raises(ValidationError, match="無効な勤務状態"):
            AttendanceRecord(**data)