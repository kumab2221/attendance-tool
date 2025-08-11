"""
リカバリー機能

エラー回復とリトライ機能を提供
"""

import gc
import time
from typing import Any, Callable, List

from .models import ErrorRecord, ProcessingResult, RecoveryResult


class RecoveryManager:
    """リカバリー機能管理"""

    def __init__(self):
        pass

    def retry_operation(
        self, operation: Callable, max_retries: int = 3, delay: float = 1.0
    ) -> Any:
        """操作のリトライ実行 (最小実装)"""
        last_exception = None

        for attempt in range(max_retries):
            try:
                return operation()
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(delay)

        # 最終的に失敗した場合は例外を再発生
        raise last_exception

    def handle_memory_error(self, operation: Callable) -> RecoveryResult:
        """メモリエラーハンドリング (最小実装)"""
        # ガベージコレクション実行
        before_gc = gc.get_count()[0]
        gc.collect()
        after_gc = gc.get_count()[0]

        memory_freed = max(0, before_gc - after_gc)

        # 回復試行
        recovery_success = None
        try:
            operation()
            recovery_success = True
        except Exception:
            recovery_success = False

        return RecoveryResult(
            success=recovery_success, gc_executed=True, memory_freed=memory_freed
        )

    def process_with_error_continuation(
        self, data: List[dict], processor: Callable
    ) -> ProcessingResult:
        """エラー継続処理 (最小実装)"""
        successful_results = []
        error_records = []

        for i, record in enumerate(data):
            try:
                result = processor(record)
                successful_results.append(result)
            except Exception as e:
                error_record = ErrorRecord(
                    record_id=record.get("employee_id", str(i)),
                    error=e,
                    timestamp=str(time.time()),
                )
                error_records.append(error_record)

        return ProcessingResult(
            successful_results=successful_results, error_records=error_records
        )
