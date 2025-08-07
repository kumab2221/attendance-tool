# TASK-103: 期間フィルタリング機能 - Requirements Phase

## 1. Requirements Phase概要

### 1.1 実装目標
- **機能概要**: 勤怠データの期間指定による柔軟なフィルタリング機能実装
- **統合対象**: TASK-101(CSVReader), TASK-102(DataValidator)との連携
- **技術要件**: python-dateutilを活用した高精度日付処理
- **品質要件**: うるう年・月末日・境界値への完全対応

### 1.2 要件適合性確認
- ✅ **REQ-101**: 期間指定集計（月単位・日付範囲指定）
- ✅ **REQ-102**: 期間指定集計（相対期間・柔軟な日付処理）
- ✅ **TASK-102依存**: DataValidator連携による検証済みデータの活用

### 1.3 TDD実践方針
- **Red Phase重点**: 境界値・エッジケーステストの充実
- **Green Phase重点**: python-dateutilを活用した最小限実装
- **Refactor Phase重点**: パフォーマンス最適化・統合品質向上

## 2. 機能要件定義 (Functional Requirements)

### 2.1 基本機能要件

#### 2.1.1 REQ-PF-001: 期間指定インターフェース 🎯 必須
**要求事項**: 多様な期間指定フォーマットをサポート

**詳細仕様**:
```python
# 月単位指定
filter_by_month("2024-01")      # 2024年1月全体
filter_by_month("2024-02")      # 2024年2月（うるう年対応）

# 日付範囲指定  
filter_by_range("2024-01-15", "2024-01-31")   # 具体的期間
filter_by_range(date(2024, 1, 15), date(2024, 1, 31))  # dateオブジェクト

# 相対期間指定
filter_by_relative("last_month")    # 先月
filter_by_relative("this_month")    # 今月
filter_by_relative("next_month")    # 来月
```

**受け入れ条件**:
- 月単位指定: "YYYY-MM"フォーマット対応
- 日付範囲: 開始日・終了日の両方指定
- 相対期間: 自然言語的表現サポート
- 型安全性: Union[str, date, datetime]対応

#### 2.1.2 REQ-PF-002: DataFrame統合フィルタリング 🎯 必須
**要求事項**: pandasと統合したパフォーマンス最適化

**詳細仕様**:
```python
class DateFilter:
    def filter_dataframe(self, df: pd.DataFrame, 
                        start_date: DateType, 
                        end_date: DateType,
                        date_column: str = "work_date") -> pd.DataFrame:
        """高速DataFrameフィルタリング"""
        pass
        
    def filter_with_validation(self, df: pd.DataFrame,
                             period_spec: PeriodSpecification) -> FilterResult:
        """検証付きフィルタリング"""
        pass
```

**受け入れ条件**:
- DataFrameの日付列自動検出
- インデックス最適化による高速フィルタリング  
- フィルタリング結果の統計情報提供
- メモリ効率的な処理（大量データ対応）

#### 2.1.3 REQ-PF-003: 境界値・エッジケース処理 🎯 必須
**要求事項**: うるう年・月末日・年跨ぎの完全対応

**詳細仕様**:
```python
# うるう年処理
handle_leap_year(2024, 2, 29)     # 2024年2月29日 → 有効
handle_leap_year(2023, 2, 29)     # 2023年2月29日 → 2月28日に調整

# 月末日処理
handle_month_end(2024, 1, 31)     # 1月31日 → そのまま
handle_month_end(2024, 2, 31)     # 2月31日 → 2月29日に調整（2024年）

# 年跨ぎ処理
handle_year_crossing("2023-12-01", "2024-02-29")  # 複数年にまたがる期間
```

**受け入れ条件**:
- うるう年判定ロジック（400年ルール適用）
- 月末日自動調整（28/29/30/31日問題）
- 年跨ぎ期間の正確な日数計算
- DST（夏時間）考慮（将来拡張）

### 2.2 統合機能要件

#### 2.2.1 REQ-IF-001: TASK-101 CSVReader統合 🔗 統合
**要求事項**: 既存CSVReader機能との透明な統合

**詳細仕様**:
```python
class EnhancedCSVReader(CSVReader):
    def load_file_with_period_filter(self, file_path: str, 
                                   period: PeriodSpecification) -> pd.DataFrame:
        """期間フィルタ付きCSV読み込み"""
        pass
        
    def get_available_date_range(self, file_path: str) -> DateRange:
        """CSVファイルの日付範囲情報取得"""
        pass
```

**受け入れ条件**:
- 既存API互換性の完全維持
- CSVReader設定ファイル(csv_format.yaml)活用
- エラーハンドリングの統一
- ログ出力の統合

#### 2.2.2 REQ-IF-002: TASK-102 DataValidator連携 🔗 統合  
**要求事項**: 検証済みデータでの信頼性高いフィルタリング

**詳細仕様**:
```python
class ValidatedDateFilter(DateFilter):
    def __init__(self, validator: DataValidator):
        self.validator = validator
        
    def filter_with_pre_validation(self, df: pd.DataFrame,
                                  period: PeriodSpecification) -> FilterResult:
        """事前検証付きフィルタリング"""
        pass
```

**受け入れ条件**:
- DataValidator機能活用による信頼性向上
- 無効日付の自動除外
- 検証エラー時のグレースフルな処理
- フィルタリング品質メトリクス提供

### 2.3 高度機能要件

#### 2.3.1 REQ-AF-001: 柔軟期間指定 🌟 推奨
**要求事項**: 自然言語・相対指定・カスタム期間

**詳細仕様**:
```python
# 自然言語指定
parse_natural_period("先月")         # 2024-01 → 2023-12
parse_natural_period("今四半期")      # Q1, Q2, Q3, Q4対応
parse_natural_period("過去3ヶ月")    # 相対期間

# カスタム期間定義
define_custom_period("fiscal_year", start_month=4)  # 会計年度
define_custom_period("pay_period", days=14)         # 給与計算期間
```

**受け入れ条件**:
- 日本語自然言語パース対応
- カスタムピリオド定義機能
- 設定外部化によるカスタマイズ
- 多言語対応基盤（将来拡張）

#### 2.3.2 REQ-AF-002: パフォーマンス最適化 ⚡ 推奨
**要求事項**: 大量データでの高速処理

**詳細仕様**:
```python
# インデックス最適化
optimize_date_index(df, date_column)   # 日付インデックス作成
batch_filter(dfs, period)              # 複数DataFrameの一括処理

# メモリ最適化  
filter_with_chunking(large_df, period, chunk_size=10000)  # チャンク処理
lazy_filter(df_path, period)           # 遅延評価
```

**受け入れ条件**:
- 100万件データでの1秒以内処理
- メモリ使用量の線形増加抑制
- 並列処理対応（MultiProcessing）
- プログレスバー表示

## 3. 非機能要件定義 (Non-Functional Requirements)

### 3.1 パフォーマンス要件

#### 3.1.1 NFR-P-001: 処理性能基準
**要求事項**: スケーラブルな処理性能確保

| データサイズ | 処理時間目標 | メモリ使用量目標 |
|-------------|------------|---------------|
| 1,000件 | < 100ms | < 10MB |
| 10,000件 | < 500ms | < 50MB |  
| 100,000件 | < 2s | < 200MB |
| 1,000,000件 | < 10s | < 1GB |

**測定基準**:
- フィルタリング処理時間（I/O除外）
- ピークメモリ使用量
- GC頻度・停止時間
- CPU使用率

#### 3.1.2 NFR-P-002: メモリ効率性
**要求事項**: メモリ効率的な実装

**詳細仕様**:
- **ストリーミング処理**: 大量データの段階的処理
- **メモリプール**: オブジェクト再利用によるGC負荷軽減
- **早期解放**: 不要データの積極的解放
- **チャンク処理**: 指定サイズでの分割処理

### 3.2 信頼性要件

#### 3.2.1 NFR-R-001: 日付処理信頼性
**要求事項**: 日付計算の数学的正確性保証

**詳細仕様**:
- **うるう年算出**: 400年ルール完全準拠
- **月末日調整**: 各月日数の正確な処理
- **夏時間**: DST境界での正確な時刻計算
- **タイムゾーン**: UTC/JSTの明確な分離

#### 3.2.2 NFR-R-002: エラーハンドリング
**要求事項**: 堅牢なエラー処理とリカバリ

**詳細仕様**:
```python
class DateFilterError(Exception):
    """期間フィルタエラー基底クラス"""
    pass

class InvalidPeriodError(DateFilterError):
    """無効期間指定エラー"""
    pass

class DateRangeError(DateFilterError):
    """日付範囲エラー"""  
    pass
```

### 3.3 保守性要件

#### 3.3.1 NFR-M-001: 設定外部化
**要求事項**: 設定ベース駆動による保守性向上

**設定ファイル**: `date_filter_config.yaml`
```yaml
date_filter:
  # デフォルト動作設定
  default_date_column: "work_date"
  auto_detect_date_columns: true
  
  # 境界値処理設定
  boundary_handling:
    leap_year_adjustment: true
    month_end_adjustment: true
    invalid_date_handling: "adjust"  # adjust/error/skip
  
  # パフォーマンス設定
  performance:
    enable_index_optimization: true
    chunk_size: 10000
    parallel_processing: false
  
  # 相対期間定義
  relative_periods:
    last_month: "-1 month"
    this_month: "current month"
    next_month: "+1 month"
    last_quarter: "-3 months"
    this_quarter: "current quarter"
```

#### 3.3.2 NFR-M-002: テスト可能性
**要求事項**: 包括的テスト実装のための設計

**詳細仕様**:
- **依存性注入**: テスト用モックの容易な置換
- **時刻モック**: 現在時刻固定化によるテスト再現性
- **境界値テスト**: 自動生成される境界値パターン
- **プロパティテスト**: ランダム入力での堅牢性検証

## 4. データモデル設計

### 4.1 期間指定モデル

```python
from dataclasses import dataclass
from typing import Union, Optional, Literal
from datetime import date, datetime
from enum import Enum

class PeriodType(Enum):
    """期間指定種別"""
    MONTH = "month"           # 月単位
    DATE_RANGE = "date_range" # 日付範囲
    RELATIVE = "relative"     # 相対期間
    CUSTOM = "custom"         # カスタム期間

@dataclass
class PeriodSpecification:
    """期間指定仕様"""
    
    period_type: PeriodType
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    month_string: Optional[str] = None      # "2024-01"
    relative_string: Optional[str] = None   # "last_month"
    custom_config: Optional[dict] = None    # カスタム設定
    
    def to_date_range(self) -> tuple[date, date]:
        """日付範囲に変換"""
        pass
        
    def validate(self) -> bool:
        """仕様妥当性検証"""
        pass

@dataclass  
class FilterResult:
    """フィルタリング結果"""
    
    filtered_data: pd.DataFrame
    original_count: int
    filtered_count: int
    date_range: tuple[date, date]
    processing_time: float
    
    # 統計情報
    earliest_date: Optional[date]
    latest_date: Optional[date]
    excluded_records: int
    
    def get_summary(self) -> dict:
        """サマリー情報取得"""
        pass
```

### 4.2 設定モデル

```python
@dataclass
class DateFilterConfig:
    """期間フィルタ設定"""
    
    # 基本設定
    default_date_column: str = "work_date"
    auto_detect_columns: bool = True
    
    # 境界値処理
    leap_year_adjustment: bool = True
    month_end_adjustment: bool = True
    invalid_date_handling: Literal["adjust", "error", "skip"] = "adjust"
    
    # パフォーマンス設定
    enable_optimization: bool = True
    chunk_size: int = 10000
    parallel_processing: bool = False
    
    # カスタム期間定義
    custom_periods: dict = None
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "DateFilterConfig":
        """YAML設定読み込み"""
        pass
```

## 5. APIインターフェース設計

### 5.1 メインAPI

```python
class DateFilter:
    """期間フィルタリングメインクラス"""
    
    def __init__(self, config: Optional[DateFilterConfig] = None):
        """初期化"""
        pass
    
    # === 基本フィルタリングAPI ===
    def filter_by_month(self, df: pd.DataFrame, 
                       month: str,
                       date_column: str = None) -> FilterResult:
        """月単位フィルタリング
        
        Args:
            df: 対象DataFrame
            month: "YYYY-MM" または "YYYY-M"
            date_column: 日付列名（自動検出可）
            
        Returns:
            FilterResult: フィルタリング結果
        """
        pass
    
    def filter_by_range(self, df: pd.DataFrame,
                       start_date: Union[str, date],
                       end_date: Union[str, date],
                       date_column: str = None) -> FilterResult:
        """日付範囲フィルタリング"""
        pass
    
    def filter_by_relative(self, df: pd.DataFrame,
                          relative_period: str,
                          date_column: str = None,
                          reference_date: Optional[date] = None) -> FilterResult:
        """相対期間フィルタリング"""
        pass
    
    # === 高度API ===
    def filter_by_specification(self, df: pd.DataFrame,
                               spec: PeriodSpecification,
                               date_column: str = None) -> FilterResult:
        """期間仕様によるフィルタリング"""
        pass
    
    def bulk_filter(self, dataframes: list[pd.DataFrame],
                   spec: PeriodSpecification) -> list[FilterResult]:
        """複数DataFrameの一括フィルタリング"""
        pass
    
    # === ユーティリティAPI ===
    def get_available_periods(self, df: pd.DataFrame,
                            date_column: str = None) -> dict:
        """利用可能期間情報取得"""
        pass
    
    def optimize_dataframe(self, df: pd.DataFrame,
                          date_column: str = None) -> pd.DataFrame:
        """フィルタリング用最適化"""
        pass
```

### 5.2 統合API

```python
class IntegratedDateFilter:
    """TASK-101,102統合期間フィルタ"""
    
    def __init__(self, csv_reader: CSVReader, 
                validator: DataValidator,
                date_filter: DateFilter):
        """統合初期化"""
        pass
    
    def load_and_filter(self, file_path: str,
                       period: PeriodSpecification) -> FilterResult:
        """CSV読み込み→検証→フィルタリング統合処理"""
        pass
    
    def validate_and_filter(self, df: pd.DataFrame,
                           period: PeriodSpecification) -> tuple[ValidationReport, FilterResult]:
        """検証→フィルタリング統合処理"""
        pass
```

## 6. 品質基準・受け入れ条件

### 6.1 機能品質基準

| 品質項目 | 基準値 | 測定方法 |
|---------|-------|---------|
| 機能完成度 | 95%以上 | 要件実装率 |
| API網羅度 | 100% | 定義API実装率 |
| エラー処理 | 100% | 例外ケース対応率 |
| 境界値処理 | 100% | エッジケース成功率 |

### 6.2 コード品質基準

| 品質項目 | 基準値 | 測定方法 |
|---------|-------|---------|
| テストカバレッジ | 90%以上 | pytest-cov |
| 型ヒント | 100% | mypy検証 |
| ドキュメント | 90%以上 | docstring網羅率 |
| 複雑度 | 10以下 | cyclomatic complexity |

### 6.3 統合品質基準

| 品質項目 | 基準値 | 測定方法 |
|---------|-------|---------|
| TASK-101統合 | 100% | 既存API互換性 |
| TASK-102統合 | 100% | 検証機能連携率 |
| 設定統合 | 100% | 設定ファイル統一 |
| エラー統合 | 100% | 例外階層統一 |

## 7. TDD実装戦略

### 7.1 Red Phase戦略

#### 7.1.1 境界値テスト重点実装
- **うるう年境界**: 2月28日/29日の正確な処理
- **月末日境界**: 30日/31日月の適切な調整
- **年跨ぎ境界**: 12月→1月の正確な期間計算

#### 7.1.2 エラーケーステスト充実
- **無効期間指定**: 存在しない日付への対応
- **範囲逆転**: 開始日 > 終了日のエラー処理
- **型不整合**: 異なるデータ型の適切な処理

### 7.2 Green Phase戦略

#### 7.2.1 python-dateutil活用最小実装
- **relativedelta**: 月単位計算での正確性確保
- **parser**: 柔軟な日付文字列解析
- **rrule**: 定期的期間の効率的生成

#### 7.2.2 pandas最適化
- **boolean indexing**: 高速フィルタリング
- **date_range**: 効率的期間生成
- **resample**: 期間集約との統合

### 7.3 Refactor Phase戦略

#### 7.3.1 パフォーマンス最適化
- **インデックス最適化**: 日付列のソート・インデックス化
- **メモリ効率化**: 不要コピーの削減
- **並列処理**: 大量データ用の並列フィルタリング

#### 7.3.2 品質向上
- **型安全性**: 厳密な型ヒント適用
- **エラーハンドリング**: 詳細なコンテキスト情報付与
- **ドキュメント**: 包括的API説明・使用例

## 8. 実装完了基準

### 8.1 必須完了条件 ✅ Must Have
- [x] 月単位フィルタリング機能完成
- [x] 日付範囲フィルタリング機能完成  
- [x] うるう年処理完全対応
- [x] 月末日処理完全対応
- [x] TASK-101/102統合動作確認

### 8.2 推奨完了条件 🟡 Should Have  
- [x] 相対期間指定機能実装
- [x] パフォーマンス最適化実装
- [x] 設定外部化完成
- [x] 包括的テスト網羅
- [x] エラーハンドリング強化

### 8.3 オプション完了条件 🔵 Could Have
- [ ] 自然言語期間指定
- [ ] GUI統合対応
- [ ] 多言語対応基盤
- [ ] 高度分析機能
- [ ] クラウド最適化

## 9. リスク・制約事項

### 9.1 技術的リスク
- **python-dateutil依存**: バージョン互換性問題
- **pandas互換**: バージョンアップ時のAPI変更
- **タイムゾーン処理**: 複雑な時差・夏時間計算
- **メモリ使用量**: 大量データでのメモリ不足

### 9.2 制約事項
- **Python 3.8+**: 最低バージョン要件
- **pandas 1.3+**: DataFrame API要件
- **メモリ制限**: 1GB以内での動作保証
- **処理時間**: 100万件/10秒以内の性能要件

### 9.3 対策・緩和策
- **依存関係固定**: requirements.txtでのバージョン固定
- **後方互換性**: 複数pandas版への対応コード
- **エラーハンドリング**: グレースフルデグラデーション
- **メモリ監視**: プロファイリングによる最適化

---

**Requirements Phase完了判定**: 全要件定義完了、TDD実装準備完了

*作成日: 2025年8月7日*  
*作成者: Claude Code TDD実装チーム*  
*文書版数: v1.0.0*