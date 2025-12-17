"""
UseCase: データ分析
散布図データの回帰分析を実行
"""
import logging
from typing import List

from src.core.interfaces import IAnalyzer
from src.core.entities import ScatterPoint, AnalysisResult
from src.core.exceptions import AnalysisError


class AnalyzeDataUseCase:
    """データ分析ユースケース"""
    
    def __init__(self, analyzer: IAnalyzer):
        self._analyzer = analyzer
        self._logger = logging.getLogger(__name__)
    
    def execute(self, points: List[ScatterPoint]) -> AnalysisResult:
        """
        データを分析
        
        Args:
            points: 分析対象のポイント
        Returns:
            分析結果
        Raises:
            AnalysisError: 分析失敗時
        """
        self._logger.info(f"Starting analysis on {len(points)} points")
        
        try:
            result = self._analyzer.analyze(points)
            
            self._logger.info(
                f"Analysis completed: {result.point_count} points, "
                f"{len(result.category_counts)} categories"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Analysis failed: {e}", exc_info=True)
            raise AnalysisError(f"Failed to analyze data: {e}") from e