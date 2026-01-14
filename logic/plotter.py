"""
プロッター - 散布図描画処理
"""
import matplotlib.pyplot as plt
from matplotlib import rcParams
import pandas as pd
import logging
from scipy import stats

class ScatterPlotter:
    """散布図を描画"""
    
    def __init__(self):
        """日本語フォント設定"""
        try:
            # 日本語フォント設定（環境に応じて自動選択）
            rcParams['font.family'] = 'sans-serif'
            # Windows
            if 'Meiryo' in plt.matplotlib.font_manager.findSystemFonts():
                rcParams['font.sans-serif'] = ['Meiryo']
            # Mac
            elif 'Hiragino Sans' in plt.matplotlib.font_manager.findSystemFonts():
                rcParams['font.sans-serif'] = ['Hiragino Sans']
            # その他
            else:
                rcParams['font.sans-serif'] = ['DejaVu Sans']
            
            logging.info("フォント設定完了")
        except Exception as e:
            logging.warning(f"フォント設定失敗: {e}")
    
    def draw(self, ax, df: pd.DataFrame, x_col: str = 'X', y_col: str = 'Y',
            category_col: str = None, show_regression: bool = True,
            xlim: tuple = None, ylim: tuple = None, show_labels: bool = True,
            label_col: str = None):

        # plotter.pyのdrawメソッドの先頭に追加
        print("利用可能なカラム:", df.columns.tolist())
        print(f"指定されたラベル列 '{label_col}' は存在するか:", label_col in df.columns)
        print("先頭5行のラベルデータ:", df[label_col].head().tolist() if label_col in df.columns else "ラベル列が存在しません")
        """
        散布図を描画
    
        Args:
        ax: Matplotlibの軸オブジェクト
        df: データフレーム
        x_col: X列の列名
        y_col: Y列の列名
        category_col: カテゴリ列の列名（オプション）
        show_regression: 回帰線を表示するか
        xlim: X軸の範囲 (min, max)
        ylim: Y軸の範囲 (min, max)
        show_labels: 各点にラベルを表示するか
        label_col: ラベルとして使用する列名（指定しない場合はインデックスを使用）
        """
        try:
            # 軸をクリア
            ax.clear()
        
            # カテゴリ別に描画
            if category_col and category_col in df.columns:
                self._draw_with_category(ax, df, x_col, y_col, category_col)
            else:
                self._draw_simple(ax, df, x_col, y_col)
            
            # 回帰直線
            if show_regression:
                self._draw_regression_line(ax, df, x_col, y_col)
            
            # 軸ラベル
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
        
            # 軸範囲の設定
            if xlim:
                ax.set_xlim(xlim)
            if ylim:
                ax.set_ylim(ylim)

            # 各点にラベルを表示
            if show_labels:
                labels = df[label_col] if label_col and label_col in df.columns else df.index.astype(str)
                for x, y, label in zip(df[x_col], df[y_col], labels):
                    ax.text(x, y, str(label), 
                            fontsize=8, 
                            ha='center', 
                            va='bottom',
                            bbox=dict(facecolor='white', alpha=0.7, 
                                     edgecolor='none', pad=1),
                            transform=ax.transData)
        
            # レイアウト調整
            ax.figure.tight_layout()
        
            logging.info("散布図描画完了")
        
        except Exception as e:
            logging.error(f"散布図描画エラー: {e}", exc_info=True)
            raise
    
    def _draw_simple(self, ax, df: pd.DataFrame, x_col: str, y_col: str):
        """シンプルな散布図（カテゴリなし）"""
        ax.scatter(df[x_col], df[y_col], 
                  alpha=0.7, s=50, color='#2196F3', edgecolors='white', linewidths=0.5)
    
    def _draw_with_category(self, ax, df: pd.DataFrame, x_col: str, y_col: str, category_col: str):
        """カテゴリ別散布図"""
        categories = df[category_col].unique()
        colors = plt.cm.tab10(range(len(categories)))
        
        for i, cat in enumerate(categories):
            subset = df[df[category_col] == cat]
            ax.scatter(subset[x_col], subset[y_col],
                      alpha=0.7, s=50, label=str(cat), 
                      color=colors[i], edgecolors='white', linewidths=0.5)
        
        ax.legend(loc='best', framealpha=0.9)
    
    def _draw_regression_line(self, ax, df: pd.DataFrame, x_col: str, y_col: str):
        """回帰線を描画"""
        try:
            x = df[x_col].values
            y = df[y_col].values
            
            # 回帰直線の計算
            slope, intercept, _, _, _ = stats.linregress(x, y)
            
            # 描画範囲
            x_min, x_max = x.min(), x.max()
            x_line = [x_min, x_max]
            y_line = [slope * xi + intercept for xi in x_line]
            
            # 回帰線描画
            ax.plot(x_line, y_line, 'r-', alpha=0.6, linewidth=2.5, label='回帰線')
            
        except Exception as e:
            logging.warning(f"回帰線描画失敗: {e}")