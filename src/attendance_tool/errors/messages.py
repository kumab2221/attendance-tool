"""
メッセージフォーマッター

ユーザーフレンドリーなエラーメッセージを提供
"""

from typing import List

from attendance_tool.validation.models import ValidationError


class MessageFormatter:
    """メッセージフォーマッター"""

    def __init__(self, language: str = "ja"):
        self.language = language

        # 日本語メッセージマッピング (最小実装)
        self._message_templates = {
            FileNotFoundError: "ファイルが見つかりません\n詳細: {path}が存在しないか、アクセスできません\n解決方法: ファイルパスを確認し、ファイルが存在することを確認してください",
            PermissionError: "ファイルへのアクセス権限がありません\n詳細: ファイルまたはフォルダへの読み書き権限がない可能性があります\n解決方法: 管理者権限で実行するか、ファイルの権限設定を確認してください",
        }

        # 簡易化マッピング
        self._simplification_map = {
            ValidationError: "データの形式に問題があります",
            MemoryError: "メモリ不足により処理を継続できません",
            TimeoutError: "処理に時間がかかりすぎました",
        }

        # 解決方法マッピング
        self._solution_map = {
            "FileNotFoundError": [
                "ファイルパスを確認してください",
                "ファイルが存在することを確認してください",
                "ファイル名にタイプミスがないか確認してください",
            ],
            "PermissionError": [
                "管理者権限で実行してください",
                "ファイルの権限設定を確認してください",
                "他のプロセスがファイルを使用していないか確認してください",
            ],
        }

    def format_message(self, exception: Exception) -> str:
        """メッセージフォーマット (最小実装)"""
        exception_type = type(exception)

        if exception_type in self._message_templates:
            template = self._message_templates[exception_type]
            # 簡単な文字列置換（最小実装）
            if hasattr(exception, "filename") and exception.filename:
                return template.format(path=exception.filename)
            else:
                return template.format(path=str(exception))

        return f"エラーが発生しました: {str(exception)}"

    def simplify_message(self, exception: Exception) -> str:
        """技術用語の簡易化 (最小実装)"""
        exception_type = type(exception)

        if exception_type in self._simplification_map:
            return self._simplification_map[exception_type]

        return str(exception)

    def get_solution_suggestions(self, error_type: str) -> List[str]:
        """解決方法の提案 (最小実装)"""
        return self._solution_map.get(error_type, ["サポートに問い合わせてください"])
