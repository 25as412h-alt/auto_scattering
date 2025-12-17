"""
Infrastructure: Repository実装
CSVファイルからデータを読み込むアダプタ
"""
import logging
from pathlib import Path
from typing import List, Dict
import pandas as pd

from src.core.interfaces import IScatterRepository, ICategoryRepository
from src.core.entities import ScatterPoint
from src.core.exceptions import DataLoadError


class ScatterRepository(IScatterRepository):
    """散布図データのRepository実装（Pandas使用）"""
    
    def __init__(self, file_path: Path, encodings: List[str]):
        """
        Args:
            file_path: CSVファイルのパス
            encodings: 試行するエンコーディングのリスト
        """
        self._file_path = file_path
        self._encodings = encodings
        self._logger = logging.getLogger(__name__)
    
    def load(self) -> List[ScatterPoint]:
        """
        CSVファイルから散布図データを読み込む
        
        Returns:
            ScatterPointのリスト
        Raises:
            DataLoadError: ファイルが存在しない、または読み込みに失敗
        """
        if not self._file_path.exists():
            raise DataLoadError(f"Scatter file not found: {self._file_path}")
        
        self._logger.info(f"Loading scatter data from: {self._file_path}")
        
        # エンコーディングを試行
        df = self._read_csv_with_fallback(self._file_path, self._encodings)
        
        # データ検証とクレンジング
        df = self._validate_and_clean(df)
        
        # ScatterPointエンティティに変換
        points = self._to_entities(df)
        
        self._logger.info(f"Successfully loaded {len(points)} scatter points")
        return points
    
    def _read_csv_with_fallback(self, path: Path, encodings: List[str]) -> pd.DataFrame:
        """エンコーディングをフォールバックしながらCSV読み込み"""
        last_error = None
        
        for encoding in encodings:
            try:
                self._logger.debug(f"Trying encoding: {encoding}")
                df = pd.read_csv(path, encoding=encoding)
                self._logger.info(f"Successfully read with encoding: {encoding}")
                return df
            except (UnicodeDecodeError, LookupError) as e:
                self._logger.warning(f"Encoding {encoding} failed: {e}")
                last_error = e
                continue
        
        raise DataLoadError(
            f"Failed to read CSV with any encoding: {encodings}"
        ) from last_error
    
    def _validate_and_clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """データの検証とクレンジング"""
        original_count = len(df)
        
        # 必須カラムの存在確認
        required_columns = ['label', 'x', 'y']
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            raise DataLoadError(
                f"Required columns missing: {missing}. "
                f"Available columns: {df.columns.tolist()}"
            )
        
        # ヘッダーの空白除去
        df.columns = df.columns.str.strip()
        
        # label列の文字列化
        df['label'] = df['label'].astype(str).str.strip()
        
        # x, y の数値変換
        df['x'] = pd.to_numeric(df['x'], errors='coerce')
        df['y'] = pd.to_numeric(df['y'], errors='coerce')
        
        # NaNを含む行を削除
        df_clean = df.dropna(subset=['x', 'y'])
        
        dropped_count = original_count - len(df_clean)
        if dropped_count > 0:
            self._logger.warning(
                f"Dropped {dropped_count} rows due to invalid numeric values"
            )
        
        if len(df_clean) == 0:
            raise DataLoadError("No valid data rows after cleaning")
        
        return df_clean
    
    def _to_entities(self, df: pd.DataFrame) -> List[ScatterPoint]:
        """DataFrameをScatterPointエンティティに変換"""
        points = []
        for _, row in df.iterrows():
            try:
                point = ScatterPoint(
                    label=row['label'],
                    x=float(row['x']),
                    y=float(row['y'])
                )
                points.append(point)
            except (ValueError, TypeError) as e:
                self._logger.warning(
                    f"Skipping invalid row (label={row.get('label')}): {e}"
                )
                continue
        
        return points


class CategoryRepository(ICategoryRepository):
    """カテゴリデータのRepository実装"""
    
    def __init__(self, category_dir: Path, encodings: List[str]):
        """
        Args:
            category_dir: カテゴリCSVが格納されたディレクトリ
            encodings: 試行するエンコーディングのリスト
        """
        self._category_dir = category_dir
        self._encodings = encodings
        self._logger = logging.getLogger(__name__)
    
    def load(self) -> Dict[str, str]:
        """
        カテゴリディレクトリからCSVを読み込む
        Ver 5.0: 最初に見つかった1ファイルを使用
        
        Returns:
            {label: category} のマッピング辞書
        """
        if not self._category_dir.exists():
            self._logger.warning(
                f"Category directory not found: {self._category_dir}. "
                "Returning empty category map."
            )
            return {}
        
        # ディレクトリ内のCSVファイルを検索
        csv_files = list(self._category_dir.glob("*.csv"))
        
        if not csv_files:
            self._logger.warning(
                f"No CSV files found in {self._category_dir}. "
                "Returning empty category map."
            )
            return {}
        
        # 最初のファイルを使用
        selected_file = csv_files[0]
        self._logger.info(f"Loading category data from: {selected_file}")
        
        if len(csv_files) > 1:
            self._logger.warning(
                f"Multiple CSV files found ({len(csv_files)}), "
                f"using: {selected_file.name}"
            )
        
        # CSV読み込み
        df = self._read_csv_with_fallback(selected_file, self._encodings)
        
        # カテゴリマッピングを作成
        category_map = self._build_category_map(df)
        
        self._logger.info(f"Loaded {len(category_map)} category mappings")
        return category_map
    
    def _read_csv_with_fallback(self, path: Path, encodings: List[str]) -> pd.DataFrame:
        """エンコーディングをフォールバックしながらCSV読み込み"""
        last_error = None
        
        for encoding in encodings:
            try:
                self._logger.debug(f"Trying encoding: {encoding}")
                df = pd.read_csv(path, encoding=encoding)
                self._logger.info(f"Successfully read with encoding: {encoding}")
                return df
            except (UnicodeDecodeError, LookupError) as e:
                self._logger.warning(f"Encoding {encoding} failed: {e}")
                last_error = e
                continue
        
        raise DataLoadError(
            f"Failed to read category CSV with any encoding: {encodings}"
        ) from last_error
    
    def _build_category_map(self, df: pd.DataFrame) -> Dict[str, str]:
        """DataFrameからカテゴリマッピングを構築"""
        # ヘッダーの空白除去
        df.columns = df.columns.str.strip()
        
        # 必須カラムの確認
        if 'label' not in df.columns or 'category' not in df.columns:
            self._logger.error(
                f"Category CSV must have 'label' and 'category' columns. "
                f"Found: {df.columns.tolist()}"
            )
            raise DataLoadError(
                "Category CSV missing required columns: 'label', 'category'"
            )
        
        # マッピング作成（欠損値を除外）
        df_clean = df.dropna(subset=['label', 'category'])
        df_clean['label'] = df_clean['label'].astype(str).str.strip()
        df_clean['category'] = df_clean['category'].astype(str).str.strip()
        
        # 辞書に変換（重複がある場合は最後の値を採用）
        category_map = dict(zip(df_clean['label'], df_clean['category']))
        
        # 欠損値の警告
        dropped = len(df) - len(df_clean)
        if dropped > 0:
            self._logger.warning(
                f"Dropped {dropped} category rows due to missing values"
            )
        
        return category_map