# TASK-201: 勤怠集計エンジン - 詳細要件定義

## タスク概要

勤怠データから各種集計値を算出するコアエンジンの実装。出勤・欠勤日数、遅刻・早退回数、残業時間、有給・特別休暇日数を就業規則に基づいて正確に集計する。

## 要件リンク

- **REQ-002**: 出勤日数・出勤率の集計
- **REQ-003**: 欠勤日数の集計  
- **REQ-004**: 遅刻回数の集計
- **REQ-005**: 早退回数の集計
- **REQ-006**: 残業時間の算出（法定・所定）
- **REQ-007**: 有給休暇日数の集計
- **REQ-008**: 特別休暇日数の集計

## 依存関係

- **TASK-103**: 期間フィルタリング機能（完了済み）
- **ConfigManager**: 就業規則設定の読み込み
- **AttendanceRecord**: データモデル（検証済みレコード）

## 詳細要件

### 1. 基本集計機能

#### 1.1 出勤関連集計
- **出勤日数**: work_status="出勤"または勤務時間が最小労働時間(4時間)以上のレコード数
- **出勤率**: 出勤日数 ÷ (営業日数 - 有給等取得日数) × 100
- **平均勤務時間**: 総勤務時間 ÷ 出勤日数

#### 1.2 欠勤関連集計  
- **欠勤日数**: work_status="欠勤"のレコード数
- **欠勤率**: 欠勤日数 ÷ 営業日数 × 100

#### 1.3 遅刻・早退集計
- **遅刻回数**: 出勤時刻が標準開始時刻(09:00)より`late_threshold_minutes`(1分)以上遅いレコード数
- **早退回数**: 退勤時刻が標準終了時刻(18:00)より`early_leave_threshold_minutes`(1分)以上早いレコード数
- **遅刻時間**: 標準開始時刻を超過した時間の合計（`rounding.unit_minutes`=15分単位で切り上げ）
- **早退時間**: 標準終了時刻に満たない時間の合計（同上）

### 2. 残業時間集計

#### 2.1 残業時間の種類
- **所定残業時間**: 標準勤務時間(8時間)を超過した時間
- **法定残業時間**: 法定労働時間(8時間)を超過した時間  
- **深夜労働時間**: 22:00-5:00の勤務時間
- **休日労働時間**: 祝日・土日の勤務時間

#### 2.2 割増率適用
- **平日残業**: 1.25倍（`weekday_overtime: 1.25`）
- **法定残業**: 1.25倍（`legal_overtime: 1.25`）
- **深夜労働**: 1.25倍（`late_night: 1.25`）
- **休日労働**: 1.35倍（`holiday_work: 1.35`）
- **深夜かつ残業**: 1.50倍（`late_night_overtime: 1.50`）
- **休日かつ深夜**: 1.60倍（`holiday_late_night: 1.60`）

#### 2.3 残業時間上限チェック
- **月間残業上限**: 45時間（2700分）
- **特別条項適用**: 100時間（6000分）
- **年間残業上限**: 720時間（43200分）

### 3. 休暇集計

#### 3.1 有給休暇
- **有給取得日数**: work_status="有給"のレコード数
- **有給残日数**: 年間付与日数(20日) - 取得日数
- **有給取得率**: 取得日数 ÷ 付与日数 × 100
- **時間単位有給**: 勤務時間が標準時間未満で有給扱いの時間

#### 3.2 特別休暇
- **慶弔休暇**: work_status="特別休暇"のうち慶弔関連
- **産前産後休暇**: work_status="特別休暇"のうち産前産後関連  
- **育児休暇**: work_status="特別休暇"のうち育児関連

### 4. 集計結果データ構造

```python
@dataclass
class AttendanceSummary:
    """勤怠集計結果"""
    
    # 基本情報
    employee_id: str
    period_start: date
    period_end: date
    total_days: int
    business_days: int
    
    # 出勤関連
    attendance_days: int
    attendance_rate: float
    average_work_hours: float
    total_work_minutes: int
    
    # 欠勤関連
    absence_days: int
    absence_rate: float
    
    # 遅刻・早退
    tardiness_count: int
    early_leave_count: int
    tardiness_minutes: int
    early_leave_minutes: int
    
    # 残業時間
    scheduled_overtime_minutes: int    # 所定残業
    legal_overtime_minutes: int        # 法定残業
    late_night_work_minutes: int       # 深夜労働
    holiday_work_minutes: int          # 休日労働
    
    # 割増残業時間（支給対象）
    overtime_pay_minutes: int
    late_night_pay_minutes: int
    holiday_pay_minutes: int
    
    # 休暇
    paid_leave_days: int
    paid_leave_hours: float
    remaining_paid_leave: int
    special_leave_days: int
    
    # 警告・注意事項
    warnings: List[str]
    violations: List[str]
```

### 5. パフォーマンス要件

- **処理速度**: 100名分×1か月データを5分以内で処理
- **メモリ使用量**: 1GB以下で動作
- **バッチ処理**: 大容量データ対応（チャンク処理）

### 6. エラーハンドリング

#### 6.1 データ不整合検出
- 勤務時間が負の値
- 24時間を超える勤務（警告）
- 出勤日なのに勤務時間0（警告）

#### 6.2 就業規則違反検出
- 月間残業時間上限超過
- 連続勤務日数上限超過
- 休憩時間不足

### 7. アクセプタンスクライテリア

#### 7.1 正常フロー
- [ ] 期間内の全勤怠レコードが正確に集計される
- [ ] 出勤日数・出勤率が就業規則に基づき算出される
- [ ] 残業時間が種類別に正確に計算される
- [ ] 割増率が正しく適用される
- [ ] 有給・特別休暇日数が正確に集計される

#### 7.2 境界値・異常フロー  
- [ ] 勤務時間0分のレコードが適切に処理される
- [ ] 24時間勤務データで警告が発生する
- [ ] 月末・月初の日跨ぎ勤務が正確に計算される
- [ ] うるう年2月29日の勤怠データが処理される
- [ ] 残業時間上限超過で警告が発生する

#### 7.3 パフォーマンス
- [ ] 100名×1か月データが5分以内で処理される
- [ ] メモリ使用量が1GB以下に収まる
- [ ] 処理進捗が適切に表示される

#### 7.4 統合性
- [ ] 期間フィルタリング結果が正しく入力される
- [ ] 就業規則設定が正しく適用される
- [ ] 計算結果がCSV出力可能な形式で提供される

## 実装アーキテクチャ

### クラス構成
- `AttendanceCalculator`: メイン集計クラス
- `AttendanceSummary`: 集計結果格納クラス  
- `WorkRulesEngine`: 就業規則適用ロジック
- `OvertimeCalculator`: 残業時間計算専用クラス
- `VacationTracker`: 休暇管理クラス

### ディレクトリ構成
```
src/attendance_tool/calculation/
├── __init__.py
├── calculator.py          # AttendanceCalculator
├── summary.py            # AttendanceSummary
├── work_rules_engine.py  # WorkRulesEngine  
├── overtime.py           # OvertimeCalculator
├── vacation.py           # VacationTracker
└── exceptions.py         # 集計関連例外
```

## 実装制約

- 既存のAttendanceRecordモデルをそのまま使用
- ConfigManagerの設定読み込み機能を活用
- 期間フィルタリング結果(FilterResult)を入力とする
- ログ出力は既存のlogging設定を使用
- 個人情報はマスクして記録

## テスト戦略

- **単体テスト**: 各計算ロジックの詳細テスト
- **統合テスト**: 期間フィルタ→集計の連携テスト  
- **境界値テスト**: うるう年、月末、24時間勤務等
- **パフォーマンステスト**: 大容量データでの動作確認