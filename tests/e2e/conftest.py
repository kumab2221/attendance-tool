"""
E2Eテスト用設定とフィクスチャ
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Generator

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def test_data_directory() -> Path:
    """テストデータディレクトリを取得"""
    return Path(__file__).parent.parent / "fixtures" / "e2e"


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """テスト用の一時作業ディレクトリ"""
    temp_dir = tempfile.mkdtemp(prefix="attendance_e2e_")
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_employee_data() -> Dict[str, Any]:
    """サンプル従業員データ"""
    return {
        "従業員ID": "EMP001",
        "従業員名": "テスト太郎",
        "部門": "テスト部",
        "日付": "2024-01-15",
        "出勤時刻": "09:00",
        "退勤時刻": "18:00",
        "休憩時間": "01:00",
    }


@pytest.fixture
def performance_test_data(temp_workspace: Path) -> Path:
    """パフォーマンステスト用大容量データ"""
    csv_file = temp_workspace / "large_test_data.csv"

    # 100名×30日のデータを生成
    data = []
    for emp_id in range(1, 101):  # 100名
        for day in range(1, 31):  # 30日
            data.append(
                {
                    "従業員ID": f"EMP{emp_id:03d}",
                    "従業員名": f"テスト{emp_id}",
                    "部門": f"部門{(emp_id-1)//10 + 1}",
                    "日付": f"2024-01-{day:02d}",
                    "出勤時刻": "09:00",
                    "退勤時刻": "18:00",
                    "休憩時間": "01:00",
                }
            )

    df = pd.DataFrame(data)
    df.to_csv(csv_file, index=False, encoding="utf-8-sig")
    return csv_file


@pytest.fixture
def corrupted_csv_data(temp_workspace: Path) -> Path:
    """破損したCSVデータ（エラーハンドリングテスト用）"""
    csv_file = temp_workspace / "corrupted_test.csv"

    # 意図的に破損したCSVデータを作成
    with open(csv_file, "w", encoding="utf-8") as f:
        f.write("不正なヘッダー,データ\n")
        f.write("無効な日付,25:00\n")  # 不正な時刻
        f.write("欠損データ,\n")  # 欠損値

    return csv_file
