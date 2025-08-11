"""
テストデータマネージャー

E2Eテスト用のデータ生成と管理を行う。
"""

from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
import random
from datetime import datetime, timedelta


class TestDataManager:
    """テストデータの生成と管理"""

    def __init__(self):
        self.departments = ["営業部", "開発部", "総務部", "人事部", "経理部"]
        self.employee_names = [
            "山田太郎",
            "佐藤花子",
            "田中一郎",
            "鈴木美咲",
            "高橋健太",
            "松本理恵",
            "中村友香",
            "小林大輔",
            "加藤優子",
            "吉田直樹",
        ]

    def generate_standard_csv_data(
        self, output_file: Path, num_employees: int = 3, num_days: int = 3
    ) -> None:
        """標準的なCSVテストデータを生成"""
        data = []

        for emp_id in range(1, num_employees + 1):
            emp_name = (
                self.employee_names[emp_id - 1]
                if emp_id <= len(self.employee_names)
                else f"従業員{emp_id}"
            )
            dept = self.departments[(emp_id - 1) % len(self.departments)]

            for day in range(1, num_days + 1):
                # 基本的な勤務パターン
                start_time = "09:00"
                if random.random() < 0.3:  # 30%の確率で遅刻
                    start_minute = random.randint(15, 45)
                    start_time = f"09:{start_minute:02d}"

                end_time = "18:00"
                if random.random() < 0.2:  # 20%の確率で残業
                    end_hour = random.randint(19, 21)
                    end_time = f"{end_hour}:00"

                data.append(
                    {
                        "社員ID": f"EMP{emp_id:03d}",
                        "氏名": emp_name,
                        "部署": dept,
                        "日付": f"2024-01-{day:02d}",
                        "出勤時刻": start_time,
                        "退勤時刻": end_time,
                        "休憩時間": "01:00",
                    }
                )

        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

    def generate_large_dataset(
        self, output_file: Path, num_employees: int = 100, num_days: int = 30
    ) -> None:
        """大容量データセット生成（パフォーマンステスト用）"""
        data = []

        for emp_id in range(1, num_employees + 1):
            emp_name = f"テスト従業員{emp_id}"
            dept = f"部門{(emp_id - 1) // 10 + 1}"

            for day in range(1, num_days + 1):
                data.append(
                    {
                        "社員ID": f"EMP{emp_id:03d}",
                        "氏名": emp_name,
                        "部署": dept,
                        "日付": f"2024-01-{day:02d}",
                        "出勤時刻": "09:00",
                        "退勤時刻": "18:00",
                        "休憩時間": "01:00",
                    }
                )

        df = pd.DataFrame(data)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")

    def generate_corrupted_csv(self, output_file: Path) -> None:
        """破損したCSVデータ生成（エラーハンドリングテスト用）"""
        with open(output_file, "w", encoding="utf-8") as f:
            f.write("社員ID,氏名,部署,日付,出勤時刻,退勤時刻,休憩時間\n")
            f.write(
                "EMP001,テスト太郎,テスト部,2024-02-30,25:00,26:00,01:00\n"
            )  # 不正な日付と時刻
            f.write(
                "EMP002,,テスト部,2024-01-01,09:00,18:00,\n"
            )  # 名前と休憩時間が欠損
            f.write(
                "EMP003,テスト花子,,2024-01-01,09:00,07:00,01:00\n"
            )  # 部門欠損、退勤＜出勤

    def create_expected_output(
        self, input_data: List[Dict[str, Any]], output_file: Path
    ) -> None:
        """期待する出力ファイルを生成"""
        # 簡易的な集計処理をシミュレート
        summary_data = []

        employees = {}
        for record in input_data:
            emp_id = record["従業員ID"]
            if emp_id not in employees:
                employees[emp_id] = {
                    "従業員ID": emp_id,
                    "従業員名": record["従業員名"],
                    "部門": record["部門"],
                    "出勤日数": 0,
                    "総労働時間": 0.0,
                    "遅刻回数": 0,
                    "残業時間": 0.0,
                }

            # 出勤日数カウント
            employees[emp_id]["出勤日数"] += 1

            # 労働時間計算（簡易版）
            start_hour = int(record["出勤時刻"].split(":")[0])
            end_hour = int(record["退勤時刻"].split(":")[0])
            work_hours = end_hour - start_hour - 1  # 休憩1時間を引く
            employees[emp_id]["総労働時間"] += work_hours

            # 遅刻チェック
            if record["出勤時刻"] > "09:00":
                employees[emp_id]["遅刻回数"] += 1

            # 残業チェック
            if end_hour > 18:
                employees[emp_id]["残業時間"] += end_hour - 18

        summary_data = list(employees.values())
        df = pd.DataFrame(summary_data)
        df.to_csv(output_file, index=False, encoding="utf-8-sig")
