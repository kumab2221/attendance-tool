"""
カスタム例外クラス

アプリケーション固有の例外を定義
"""

from typing import Any, Optional


class AttendanceToolError(Exception):
    """勤怠管理ツール基底例外クラス"""

    def __init__(self, message: str, error_code: str = None, details: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}


class SystemError(AttendanceToolError):
    """システムエラー (SYS-XXX)"""

    pass


class DataError(AttendanceToolError):
    """データエラー (DATA-XXX)"""

    pass


class BusinessError(AttendanceToolError):
    """ビジネスロジックエラー (BIZ-XXX)"""

    pass


class UserError(AttendanceToolError):
    """ユーザーエラー (USER-XXX)"""

    pass
