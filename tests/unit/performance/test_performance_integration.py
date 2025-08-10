import pytest
import pandas as pd
from attendance_tool.performance.optimized_calculator import PerformanceOptimizedCalculator


class TestPerformanceOptimizedCalculator:
    """最適化計算機統合テスト"""
    
    def test_calculate_batch_optimized_sequential(self):
        """順次バッチ計算テスト"""
        calculator = PerformanceOptimizedCalculator()
        
        # 小規模テストデータ（並列処理閾値以下）
        test_data = {
            "emp_001": ["record1", "record2"],
            "emp_002": ["record3", "record4"]
        }
        
        # 順次処理実行
        results = calculator.calculate_batch_optimized(test_data, parallel=False)
        
        # 結果確認
        assert len(results) == 2
        assert all("employee_id" in result for result in results)
    
    def test_calculate_batch_optimized_parallel(self):
        """並列バッチ計算テスト"""
        calculator = PerformanceOptimizedCalculator()
        
        # 並列処理閾値以上のデータ
        test_data = {f"emp_{i:03d}": [f"record_{j}" for j in range(5)] for i in range(10)}
        
        # 並列処理実行
        results = calculator.calculate_batch_optimized(test_data, parallel=True)
        
        # 結果確認
        assert len(results) == 10
        assert all(result["processed"] for result in results)
    
    def test_calculate_with_chunking(self):
        """チャンク処理計算テスト"""
        calculator = PerformanceOptimizedCalculator()
        
        # 大容量テストデータ
        large_df = pd.DataFrame({
            'id': range(1000),
            'value': [f"data_{i}" for i in range(1000)]
        })
        
        # チャンク処理実行
        results = calculator.calculate_with_chunking(large_df)
        
        # 結果確認
        assert len(results) > 0
        assert all("chunk_size" in result for result in results)
    
    def test_memory_limit_setting(self):
        """メモリ制限設定テスト"""
        calculator = PerformanceOptimizedCalculator()
        
        # メモリ制限設定
        calculator.set_memory_limit(2.0)  # 2GB
        
        # 設定確認
        assert calculator._memory_limit_gb == 2.0
        assert calculator.chunk_processor.memory_limit == 2 * 1024 * 1024 * 1024
    
    def test_cleanup(self):
        """クリーンアップテスト"""
        calculator = PerformanceOptimizedCalculator()
        
        # クリーンアップ実行（エラーが発生しないことを確認）
        calculator.cleanup()
        
        # 正常完了
        assert True