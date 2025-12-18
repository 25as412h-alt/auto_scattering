"""
アナライザー - 回帰分析処理
"""
from scipy import stats
import pandas as pd
import logging

class Analyzer:
    """線形回帰分析を実行"""
    
    def analyze(self, df: pd.DataFrame, x_col: str = 'X', y_col: str = 'Y') -> dict:
        """
        線形回帰分析を実行
        
        Args:
            df: データフレーム
            x_col: X列の列名
            y_col: Y列の列名
        
        Returns:
            dict: 分析結果
                - slope: 傾き
                - intercept: 切片
                - r_squared: 決定係数
                - equation: 回帰式の文字列
                - n_samples: データ数
        """
        try:
            # データ抽出
            x = df[x_col].values
            y = df[y_col].values
            
            # 線形回帰
            slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
            
            result = {
                'slope': slope,
                'intercept': intercept,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'std_err': std_err,
                'equation': self._format_equation(slope, intercept),
                'n_samples': len(df)
            }
            
            logging.info(f"回帰分析完了: {result['equation']}, R²={result['r_squared']:.4f}")
            return result
            
        except Exception as e:
            logging.error(f"回帰分析エラー: {e}", exc_info=True)
            raise
    
    def _format_equation(self, slope: float, intercept: float) -> str:
        """
        回帰式を文字列にフォーマット
        
        Args:
            slope: 傾き
            intercept: 切片
        
        Returns:
            str: 回帰式（例: "y = 1.23x + 4.56"）
        """
        sign = '+' if intercept >= 0 else '-'
        return f"y = {slope:.4f}x {sign} {abs(intercept):.4f}"