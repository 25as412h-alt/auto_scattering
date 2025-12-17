"""
Core Interfaces - 抽象インターフェース
依存性逆転の原則（DIP）に基づく抽象定義
"""
from abc import ABC, abstractmethod
from typing import List
from pathlib import Path

from .entities import ScatterPoint, AnalysisResult


class IScatterRepository(ABC):
    """散布図データを取得するリポジトリ"""
    
    @abstractmethod
    def load(self) -> List[ScatterPoint]:
        """メインデータを読み込む"""
        pass


class ICategoryRepository(ABC):
    """カテゴリデータを取得するリポジトリ"""
    
    @abstractmethod
    def load(self) -> dict[str, str]:
        """
        カテゴリマッピングを読み込む
        Returns: {label: category}
        """
        pass


class IAnalyzer(ABC):
    """散布図データを分析する"""
    
    @abstractmethod
    def analyze(self, points: List[ScatterPoint]) -> AnalysisResult:
        """
        データを分析し結果を返す
        Args:
            points: 分析対象のポイントリスト
        Returns:
            分析結果
        """
        pass


class IVisualizer(ABC):
    """散布図を描画する"""
    
    @abstractmethod
    def visualize(
        self, 
        points: List[ScatterPoint], 
        result: AnalysisResult,
        **options
    ):
        """
        散布図を描画する
        Args:
            points: 描画するポイント
            result: 分析結果
            options: 描画オプション（軸ラベル、範囲など）
        """
        pass
    
    @abstractmethod
    def save(self, filepath: Path):
        """描画した図を保存"""
        pass