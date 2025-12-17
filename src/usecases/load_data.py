"""
UseCase: データロード
散布図データとカテゴリデータを結合して取得
"""
import logging
from typing import List

from src.core.interfaces import IScatterRepository, ICategoryRepository
from src.core.entities import ScatterPoint
from src.core.exceptions import DataLoadError


class LoadDataUseCase:
    """データロードユースケース"""
    
    def __init__(
        self,
        scatter_repo: IScatterRepository,
        category_repo: ICategoryRepository
    ):
        self._scatter_repo = scatter_repo
        self._category_repo = category_repo
        self._logger = logging.getLogger(__name__)
    
    def execute(self) -> List[ScatterPoint]:
        """
        散布図データとカテゴリデータを結合して返す
        
        Returns:
            ScatterPointのリスト
        Raises:
            DataLoadError: データロードに失敗した場合
        """
        try:
            self._logger.info("Loading scatter data...")
            scatter_points = self._scatter_repo.load()
            self._logger.info(f"Loaded {len(scatter_points)} scatter points")
            
            self._logger.info("Loading category data...")
            category_map = self._category_repo.load()
            self._logger.info(f"Loaded {len(category_map)} category mappings")
            
            # カテゴリ情報を結合（Left Join）
            enriched_points = self._merge_categories(scatter_points, category_map)
            
            self._logger.info(f"Data loading completed: {len(enriched_points)} points")
            return enriched_points
            
        except Exception as e:
            self._logger.error(f"Failed to load data: {e}", exc_info=True)
            raise DataLoadError(f"Data loading failed: {e}") from e
    
    def _merge_categories(
        self, 
        points: List[ScatterPoint], 
        category_map: dict[str, str]
    ) -> List[ScatterPoint]:
        """
        散布図ポイントにカテゴリ情報を付与
        
        Args:
            points: 元の散布図ポイント
            category_map: ラベル→カテゴリのマッピング
        Returns:
            カテゴリ付きポイントリスト
        """
        result = []
        for point in points:
            category = category_map.get(point.label)
            # 新しいインスタンスを作成（immutable）
            enriched = ScatterPoint(
                label=point.label,
                x=point.x,
                y=point.y,
                category=category
            )
            result.append(enriched)
        
        # カテゴリなしのポイント数をログ
        no_category = sum(1 for p in result if p.category is None)
        if no_category > 0:
            self._logger.warning(
                f"{no_category} points have no category assigned"
            )
        
        return result