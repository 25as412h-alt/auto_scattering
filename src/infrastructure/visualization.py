"""
Infrastructure: 可視化エンジン実装
Matplotlibを使用した散布図描画
"""
import logging
from pathlib import Path
from typing import List, Optional
import matplotlib
matplotlib.use('TkAgg')  # Tkinter統合用バックエンド
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm
import numpy as np

from src.core.interfaces import IVisualizer
from src.core.entities import ScatterPoint, AnalysisResult


class MatplotlibVisualizer(IVisualizer):
    """Matplotlibを使用した散布図可視化"""
    
    # カテゴリ別のデフォルト色
    DEFAULT_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    def __init__(self, config: dict):
        """
        Args:
            config: 描画設定（figure_size, alpha, font_sizeなど）
        """
        self._config = config
        self._logger = logging.getLogger(__name__)
        
        # 日本語フォント設定
        self._setup_japanese_font()
        
        # Figure作成
        figsize = config.get('figure_size', [10, 8])
        self._fig = Figure(figsize=figsize, facecolor='white')
        self._ax = self._fig.add_subplot(111)
        
        self._logger.info("MatplotlibVisualizer initialized")
    
    def _setup_japanese_font(self):
        """日本語フォントの設定"""
        # システムで利用可能な日本語フォントを検索
        japanese_fonts = [
            'Yu Gothic',      # Windows
            'Meiryo',         # Windows
            'MS Gothic',      # Windows
            'Hiragino Sans',  # macOS
            'AppleGothic',    # macOS
            'Noto Sans CJK JP',  # Linux
            'IPAGothic',      # Linux
        ]
        
        available_fonts = [f.name for f in fm.fontManager.ttflist]
        
        selected_font = None
        for font in japanese_fonts:
            if font in available_fonts:
                selected_font = font
                break
        
        if selected_font:
            plt.rcParams['font.family'] = selected_font
            self._logger.info(f"Japanese font set to: {selected_font}")
        else:
            self._logger.warning(
                "No Japanese font found, text may not display correctly"
            )
            # フォールバック: DejaVu Sans (英数字のみ対応)
            plt.rcParams['font.family'] = 'DejaVu Sans'
        
        # マイナス記号の文字化け対策
        plt.rcParams['axes.unicode_minus'] = False
    
    def visualize(
        self, 
        points: List[ScatterPoint], 
        result: AnalysisResult,
        **options
    ):
        """
        散布図を描画
        
        Args:
            points: 描画するポイント
            result: 分析結果
            options: 描画オプション
                - x_label: X軸ラベル
                - y_label: Y軸ラベル
                - x_min, x_max: X軸範囲
                - y_min, y_max: Y軸範囲
                - show_regression: 回帰線表示フラグ
                - selected_category: 選択されたカテゴリ（Noneで全表示）
        """
        self._logger.info(f"Visualizing {len(points)} points...")
        
        # 軸をクリア
        self._ax.clear()
        
        # カテゴリフィルタリング
        selected_category = options.get('selected_category')
        if selected_category and selected_category != "(すべて)":
            points = [p for p in points if p.category == selected_category]
            self._logger.info(f"Filtered to category '{selected_category}': {len(points)} points")
        
        if not points:
            self._ax.text(
                0.5, 0.5, 'データがありません',
                ha='center', va='center',
                transform=self._ax.transAxes,
                fontsize=16, color='gray'
            )
            return
        
        # カテゴリ別に色分けして描画
        self._plot_by_category(points)
        
        # 回帰線描画
        if options.get('show_regression', True) and result.regression_line:
            self._plot_regression_line(result.regression_line, points)
        
        # 軸設定
        self._configure_axes(points, options)
        
        # グリッド表示
        self._ax.grid(
            True, 
            alpha=self._config.get('grid_alpha', 0.3),
            linestyle=self._config.get('grid_style', 'dotted')
        )
        
        # レイアウト調整
        self._fig.tight_layout()
        
        self._logger.info("Visualization completed")
    
    def _plot_by_category(self, points: List[ScatterPoint]):
        """カテゴリ別に散布図を描画"""
        # カテゴリごとにグループ化
        category_groups = {}
        for point in points:
            category = point.category if point.category else "(カテゴリなし)"
            if category not in category_groups:
                category_groups[category] = {'x': [], 'y': []}
            category_groups[category]['x'].append(point.x)
            category_groups[category]['y'].append(point.y)
        
        # カテゴリごとにプロット
        alpha = self._config.get('alpha', 0.7)
        
        for i, (category, data) in enumerate(sorted(category_groups.items())):
            color = self.DEFAULT_COLORS[i % len(self.DEFAULT_COLORS)]
            self._ax.scatter(
                data['x'], data['y'],
                label=category,
                alpha=alpha,
                color=color,
                s=50,  # マーカーサイズ
                edgecolors='white',
                linewidths=0.5
            )
        
        # 凡例表示（カテゴリが2つ以上ある場合）
        if len(category_groups) > 1:
            self._ax.legend(loc='best', framealpha=0.9)
    
    def _plot_regression_line(self, regression: 'RegressionLine', points: List[ScatterPoint]):
        """回帰線を描画"""
        x_values = np.array([p.x for p in points])
        x_min, x_max = x_values.min(), x_values.max()
        
        # 回帰線のX座標（範囲を少し広げる）
        x_range = x_max - x_min
        x_line = np.array([x_min - 0.05 * x_range, x_max + 0.05 * x_range])
        
        # 回帰線のY座標を計算
        y_line = regression.predict(x_line[0]), regression.predict(x_line[1])
        
        # 描画
        self._ax.plot(
            x_line, y_line,
            color='red',
            linewidth=2,
            linestyle='--',
            label=f'回帰線 (R²={regression.r_squared:.3f})',
            alpha=0.8
        )
        
        # 凡例更新
        self._ax.legend(loc='best', framealpha=0.9)
    
    def _configure_axes(self, points: List[ScatterPoint], options: dict):
        """軸の設定"""
        # 軸ラベル
        x_label = options.get('x_label', 'X')
        y_label = options.get('y_label', 'Y')
        
        self._ax.set_xlabel(x_label, fontsize=self._config.get('font_size', 12))
        self._ax.set_ylabel(y_label, fontsize=self._config.get('font_size', 12))
        
        # 軸範囲
        x_min = options.get('x_min')
        x_max = options.get('x_max')
        y_min = options.get('y_min')
        y_max = options.get('y_max')
        
        if x_min is not None and x_max is not None:
            self._ax.set_xlim(x_min, x_max)
        else:
            # 自動スケール（余白を持たせる）
            x_values = [p.x for p in points]
            x_range = max(x_values) - min(x_values)
            self._ax.set_xlim(
                min(x_values) - 0.05 * x_range,
                max(x_values) + 0.05 * x_range
            )
        
        if y_min is not None and y_max is not None:
            self._ax.set_ylim(y_min, y_max)
        else:
            # 自動スケール
            y_values = [p.y for p in points]
            y_range = max(y_values) - min(y_values)
            self._ax.set_ylim(
                min(y_values) - 0.05 * y_range,
                max(y_values) + 0.05 * y_range
            )
    
    def get_figure(self) -> Figure:
        """Figureオブジェクトを取得（GUI統合用）"""
        return self._fig
    
    def save(self, filepath: Path):
        """図を画像ファイルとして保存"""
        self._logger.info(f"Saving figure to: {filepath}")
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        self._fig.savefig(
            filepath,
            dpi=150,
            bbox_inches='tight',
            facecolor='white'
        )
        
        self._logger.info(f"Figure saved successfully: {filepath}")