"""
分析エンジンのテスト
"""
import pytest
import numpy as np

from src.infrastructure.analysis import ScipyAnalyzer
from src.core.entities import ScatterPoint


class TestScipyAnalyzer:
    """ScipyAnalyzerのテスト"""
    
    @pytest.fixture
    def analyzer(self):
        return ScipyAnalyzer()
    
    def test_analyze_linear_data(self, analyzer):
        """完全な線形データの分析"""
        # y = 2x + 1 の直線上の点
        points = [
            ScatterPoint('A', 0, 1),
            ScatterPoint('B', 1, 3),
            ScatterPoint('C', 2, 5),
            ScatterPoint('D', 3, 7),
            ScatterPoint('E', 4, 9)
        ]
        
        result = analyzer.analyze(points)
        
        assert result.point_count == 5
        assert result.regression_line is not None
        
        # 傾きと切片を検証
        assert abs(result.regression_line.slope - 2.0) < 0.001
        assert abs(result.regression_line.intercept - 1.0) < 0.001
        
        # R²は1に近いはず
        assert result.regression_line.r_squared > 0.99
    
    def test_analyze_with_noise(self, analyzer):
        """ノイズを含むデータの分析"""
        np.random.seed(42)
        
        # y = 2x + 1 + ノイズ
        points = []
        for i in range(50):
            x = i
            y = 2 * x + 1 + np.random.normal(0, 5)
            points.append(ScatterPoint(f'P{i}', x, y))
        
        result = analyzer.analyze(points)
        
        assert result.point_count == 50
        assert result.regression_line is not None
        
        # 傾きは2に近いはず
        assert abs(result.regression_line.slope - 2.0) < 0.5
        
        # R²は0.5以上あるはず
        assert result.regression_line.r_squared > 0.5
    
    def test_analyze_with_categories(self, analyzer):
        """カテゴリ付きデータの分析"""
        points = [
            ScatterPoint('A', 1, 2, 'Group1'),
            ScatterPoint('B', 2, 4, 'Group1'),
            ScatterPoint('C', 3, 6, 'Group2'),
            ScatterPoint('D', 4, 8, 'Group2'),
            ScatterPoint('E', 5, 10, None)
        ]
        
        result = analyzer.analyze(points)
        
        assert result.point_count == 5
        assert len(result.category_counts) == 3
        assert result.category_counts['Group1'] == 2
        assert result.category_counts['Group2'] == 2
        assert result.category_counts['(カテゴリなし)'] == 1
    
    def test_analyze_insufficient_points(self, analyzer):
        """データ点が不足している場合"""
        points = [ScatterPoint('A', 1, 2)]
        
        result = analyzer.analyze(points)
        
        assert result.point_count == 1
        assert result.regression_line is None  # 回帰できない
    
    def test_analyze_empty_data(self, analyzer):
        """空のデータ"""
        points = []
        
        result = analyzer.analyze(points)
        
        assert result.point_count == 0
        assert result.regression_line is None
        assert result.category_counts == {}
    
    def test_analyze_zero_variance(self, analyzer):
        """分散がゼロのデータ"""
        # 全てのX座標が同じ
        points = [
            ScatterPoint('A', 5, 1),
            ScatterPoint('B', 5, 2),
            ScatterPoint('C', 5, 3)
        ]
        
        result = analyzer.analyze(points)
        
        assert result.point_count == 3
        assert result.regression_line is None  # 回帰できない
    
    def test_regression_line_predict(self):
        """回帰線の予測機能"""
        from src.core.entities import RegressionLine
        
        reg = RegressionLine(slope=2.0, intercept=1.0, r_squared=0.95)
        
        # y = 2x + 1
        assert abs(reg.predict(0) - 1.0) < 0.001
        assert abs(reg.predict(5) - 11.0) < 0.001
        assert abs(reg.predict(-2) - (-3.0)) < 0.001
    
    def test_regression_line_formula(self):
        """回帰式の文字列表現"""
        from src.core.entities import RegressionLine
        
        reg = RegressionLine(slope=2.5, intercept=10.0, r_squared=0.85)
        formula = reg.formula()
        
        assert 'y =' in formula
        assert '2.5' in formula
        assert '10.0' in formula or '10.' in formula