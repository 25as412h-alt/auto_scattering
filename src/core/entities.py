"""
Core Entities - ドメインモデル
外部依存を一切持たない純粋なビジネスオブジェクト
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ScatterPoint:
    """散布図の1点を表現するエンティティ"""
    label: str
    x: float
    y: float
    category: Optional[str] = None
    
    def __post_init__(self):
        """バリデーション"""
        if not isinstance(self.x, (int, float)):
            raise ValueError(f"x must be numeric, got {type(self.x)}")
        if not isinstance(self.y, (int, float)):
            raise ValueError(f"y must be numeric, got {type(self.y)}")


@dataclass(frozen=True)
class RegressionLine:
    """回帰直線を表現するエンティティ"""
    slope: float      # 傾き a
    intercept: float  # 切片 b
    r_squared: float  # 決定係数 R²
    
    def predict(self, x: float) -> float:
        """x座標から予測値yを計算"""
        return self.slope * x + self.intercept
    
    def formula(self) -> str:
        """回帰式を文字列で返す"""
        return f"y = {self.slope:.4f}x + {self.intercept:.4f}"


@dataclass(frozen=True)
class AnalysisResult:
    """分析結果を格納するエンティティ"""
    regression_line: Optional[RegressionLine]
    point_count: int
    category_counts: dict[str, int]  # カテゴリ別のポイント数
    
    def __post_init__(self):
        if self.point_count < 0:
            raise ValueError("point_count must be non-negative")