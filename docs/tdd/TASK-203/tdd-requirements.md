# TASK-203: 部門別集計機能 - 要件定義

## 概要

勤怠データを部門ごとに集計・分析し、部門別レポートを生成する機能を実装する。
組織の階層構造に対応し、部門間の比較分析を可能にする。

## 機能要件

### REQ-203-001: 部門マスターデータ管理
- **目的**: 部門情報の一元管理
- **内容**:
  - 部門コード、部門名、上位部門の管理
  - 階層構造の表現（親子関係）
  - 部門の有効/無効状態管理
  - 部門責任者情報（オプション）

### REQ-203-002: 部門別統計算出
- **目的**: 各部門の勤怠統計を算出
- **内容**:
  - 部門別勤務時間集計（総労働時間、残業時間）
  - 部門別出勤率・欠勤率
  - 部門別平均勤務時間
  - 部門別違反件数統計
  - 期間指定による集計

### REQ-203-003: 階層集計機能
- **目的**: 組織階層に沿った集計
- **内容**:
  - 親部門への子部門統計の集約
  - 階層レベル指定での集計
  - 部門ツリー構造の表現
  - 階層別サマリーデータ

### REQ-203-004: 部門間比較分析
- **目的**: 部門パフォーマンスの比較
- **内容**:
  - 同階層部門間の比較
  - ランキング表示（労働時間、出勤率等）
  - 平均値との比較
  - 異常値検出（極端な値の部門特定）

### REQ-203-005: 部門別レポート生成
- **目的**: 部門管理者向けレポート作成
- **内容**:
  - 部門単位のサマリーレポート
  - CSV/Excel形式での出力
  - 期間比較レポート
  - グラフ・チャート用データ（将来対応）

## 技術要件

### TECH-203-001: データ構造
```python
@dataclass
class Department:
    code: str                    # 部門コード (例: "DEPT001")
    name: str                    # 部門名 (例: "営業部")
    parent_code: Optional[str]   # 親部門コード
    level: int                   # 階層レベル (0=トップ, 1=第1階層...)
    is_active: bool             # 有効フラグ
    manager_id: Optional[str]    # 部門責任者ID（オプション）

@dataclass 
class DepartmentSummary:
    department_code: str         # 部門コード
    department_name: str         # 部門名
    period_start: date          # 集計期間開始
    period_end: date            # 集計期間終了
    employee_count: int         # 対象従業員数
    total_work_minutes: int     # 総労働時間（分）
    total_overtime_minutes: int # 総残業時間（分）
    attendance_rate: float      # 出勤率
    average_work_minutes: float # 平均労働時間
    violation_count: int        # 違反件数
    compliance_score: float     # コンプライアンススコア
```

### TECH-203-002: メインクラス
```python
class DepartmentAggregator:
    def __init__(self, departments: List[Department])
    def load_department_master(self, file_path: str) -> List[Department]
    def aggregate_by_department(self, records: List[AttendanceRecord], 
                               period_start: date, period_end: date) -> List[DepartmentSummary]
    def aggregate_by_hierarchy(self, summaries: List[DepartmentSummary], 
                              level: int) -> List[DepartmentSummary]
    def compare_departments(self, summaries: List[DepartmentSummary]) -> DepartmentComparison
    def generate_department_report(self, summary: DepartmentSummary) -> DepartmentReport
```

### TECH-203-003: パフォーマンス要件
- 100部門 × 100名 × 1ヶ月データの処理を5分以内
- メモリ使用量: 500MB以内
- 階層の深さ: 10階層まで対応

## 業務ルール

### RULE-203-001: 部門コード規則
- 形式: `DEPT` + 3桁数字 (例: DEPT001, DEPT002)
- 一意性: 同一コードの重複不可
- 削除: 物理削除ではなく無効化で対応

### RULE-203-002: 階層構造規則
- 最大階層: 10階層まで
- 循環参照: 禁止（親子関係の循環検出）
- 親部門削除: 子部門が存在する場合は削除不可

### RULE-203-003: 集計対象規則
- 対象期間: 指定された期間内の勤怠レコード
- 無効部門: 集計対象外
- 退職者: 退職日以降は集計対象外
- 異動者: 異動日を境に部門を分けて集計

### RULE-203-004: 統計計算規則
- 出勤率 = 出勤日数 / 営業日数 × 100
- 平均労働時間 = 総労働時間 / 出勤日数  
- コンプライアンススコア = 部門内全員の平均値

## エラーハンドリング

### ERROR-203-001: 部門マスターエラー
- 部門コード重複
- 循環参照検出
- 必須項目不足

### ERROR-203-002: 集計エラー
- 部門に所属する従業員が0人
- 無効な期間指定
- データ不整合

### ERROR-203-003: 階層エラー
- 階層の深さ上限超過
- 親部門の存在しない参照
- 階層レベル不整合

## アクセプタンスクライテリア

### AC-203-001: 基本機能
- [x] 部門マスターデータの読み込みができる
- [x] 部門別に勤怠データを集計できる
- [x] 階層構造を考慮した集計ができる
- [x] 部門間比較データを生成できる

### AC-203-002: データ品質
- [x] 集計結果の数値が正確である
- [x] 階層集計で親部門の値が子部門の合計と一致する
- [x] 期間指定が正確に反映される
- [x] エラーデータが適切に除外される

### AC-203-003: パフォーマンス
- [x] 大量データでも処理時間が要件内
- [x] メモリ使用量が上限内
- [x] 同時実行時のパフォーマンス劣化が最小限

### AC-203-004: エラー処理
- [x] 不正なデータでも処理が続行される  
- [x] エラー内容が適切にログ出力される
- [x] 部分的なエラーが全体に影響しない

## テストデータ仕様

### 部門構造例
```
本社 (DEPT001)
├─ 営業部 (DEPT002)  
│  ├─ 東京営業課 (DEPT003)
│  └─ 大阪営業課 (DEPT004)
├─ 技術部 (DEPT005)
│  ├─ 開発課 (DEPT006)
│  └─ 品質管理課 (DEPT007)
└─ 管理部 (DEPT008)
   ├─ 人事課 (DEPT009)
   └─ 経理課 (DEPT010)
```

### テスト従業員配置
- 各課3-5名、部長1名の配置
- 総計30-40名程度
- 異なる勤務パターンを持つ従業員配置

## 実装優先順位

### Phase 1: 基本機能 (High Priority)
1. 部門マスターデータ管理
2. 基本的な部門別集計
3. 簡単な階層集計

### Phase 2: 拡張機能 (Medium Priority)  
1. 部門間比較機能
2. 詳細レポート生成
3. パフォーマンス最適化

### Phase 3: 高度機能 (Low Priority)
1. 動的階層変更対応
2. グラフデータ生成
3. 予測・分析機能

## 参考資料

- 組織図・部門構成表
- 既存の勤怠集計仕様
- 部門別レポートサンプル
- 労務管理システム連携仕様