"""
Infrastructure: 分析エンジン実装
Scipyを使用した回帰分析
"""
import logging
from typing import List
import numpy as np
from scipy import stats

from src.core.interfaces import IAnalyzer
from src.core.entities import ScatterPoint, AnalysisResult, RegressionLine
from src.core.exceptions import AnalysisError


class ScipyAnalyzer(IAnalyzer):
    """Scipyを使用した線形回帰分析"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    def analyze(self, points: List[ScatterPoint]) -> AnalysisResult:
        """
        散布図データを線形回帰分析
        
        Args:
            points: 分析対象のポイントリスト
        Returns:
            分析結果（回帰線、統計情報）
        Raises:
            AnalysisError: 分析に失敗した場合
        """
        if not points:
            self._logger.warning("No points provided for analysis")
            return AnalysisResult(
                regression_line=None,
                point_count=0,
                category_counts={}
            )
        
        try:
            self._logger.info(f"Analyzing {len(points)} points...")
            
            # カテゴリ別集計
            category_counts = self._count_categories(points)
            
            # 回帰分析実行
            regression_line = self._compute_regression(points)
            
            result = AnalysisResult(
                regression_line=regression_line,
                point_count=len(points),
                category_counts=category_counts
            )
            
            if regression_line:
                self._logger.info(
                    f"Regression analysis completed: "
                    f"y = {regression_line.slope:.4f}x + {regression_line.intercept:.4f}, "
                    f"R² = {regression_line.r_squared:.4f}"
                )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Analysis failed: {e}", exc_info=True)
            raise AnalysisError(f"Failed to analyze data: {e}") from e
    
    def _count_categories(self, points: List[ScatterPoint]) -> dict[str, int]:
        """カテゴリ別のポイント数を集計"""
        counts = {}
        for point in points:
            category = point.category if point.category else "(カテゴリなし)"
            counts[category] = counts.get(category, 0) + 1
        return counts
    
    def _compute_regression(self, points: List[ScatterPoint]) -> RegressionLine | None:
        """線形回帰を計算"""
        # データが2点未満の場合は回帰できない
        if len(points) < 2:
            self._logger.warning("Need at least 2 points for regression")
            return None
        
        # X, Y配列を抽出
        x_values = np.array([p.x for p in points])
        y_values = np.array([p.y for p in points])
        
        # 分散がゼロの場合（全て同じ値）は回帰できない
        if np.var(x_values) == 0 or np.var(y_values) == 0:
            self._logger.warning("Zero variance detected, cannot compute regression")
            return None
        
        # 線形回帰実行
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)
        
        # R²（決定係数）を計算
        r_squared = r_value ** 2
        
        self._logger.debug(
            f"Regression computed: slope={slope:.4f}, intercept={intercept:.4f}, "
            f"R²={r_squared:.4f}, p-value={p_value:.4e}"
        )
        
        return RegressionLine(
            slope=slope,
            intercept=intercept,
            r_squared=r_squared
        )


class RobustAnalyzer(IAnalyzer):
    """ロバスト回帰分析（将来の拡張用）"""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
    
    def analyze(self, points: List[ScatterPoint]) -> AnalysisResult:
        """
        外れ値に強いロバスト回帰
        
        Note: Phase 3では未実装、将来の拡張ポイント
        """
        self._logger.warning("RobustAnalyzer not implemented, using basic analysis")
        
        # フォールバック: 基本的な分析のみ実行
        basic_analyzer = ScipyAnalyzer()
        return basic_analyzer.analyze(points)