"""
GUI: メインウィンドウ
Tkinterを使用したUIの実装
"""
import logging
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from src.infrastructure.config import ConfigManager
from src.usecases.load_data import LoadDataUseCase
from src.usecases.analyze import AnalyzeDataUseCase
from src.usecases.save_image import SaveImageUseCase
from src.infrastructure.visualization import MatplotlibVisualizer
from src.core.exceptions import DataLoadError, AnalysisError


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(
        self, 
        config: ConfigManager, 
        load_data_usecase: LoadDataUseCase,
        analyze_usecase: AnalyzeDataUseCase,
        visualizer: MatplotlibVisualizer,
        save_image_usecase: SaveImageUseCase
    ):
        self._config = config
        self._load_data_usecase = load_data_usecase
        self._analyze_usecase = analyze_usecase
        self._visualizer = visualizer
        self._save_image_usecase = save_image_usecase
        self._logger = logging.getLogger(__name__)
        
        # データ保持
        self._current_points = []
        self._current_result = None
        
        # UI設定値
        self._show_regression = tk.BooleanVar(value=True)
        self._x_label = tk.StringVar(value="X")
        self._y_label = tk.StringVar(value="Y")
        self._selected_category = tk.StringVar(value="(すべて)")
        
        # Tkinterルートウィンドウ作成
        self._root = tk.Tk()
        self._root.title(config.window_title)
        self._root.geometry(config.initial_geometry)
        
        self._setup_ui()
        
        # 初期データロード
        self._initial_load()
        
        self._logger.info("MainWindow initialized")
    
    def _setup_ui(self):
        """UI要素の配置"""
        # メインフレーム
        main_frame = ttk.Frame(self._root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # ウィンドウのリサイズ設定
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=3)  # グラフエリア（可変）
        main_frame.columnconfigure(1, weight=1)  # 操作パネル（固定比率）
        main_frame.rowconfigure(0, weight=1)
        
        # 左ペイン: グラフ描画エリア（プレースホルダ）
        self._create_plot_area(main_frame)
        
        # 右ペイン: 操作パネル
        self._create_control_panel(main_frame)
        
        self._logger.info("UI setup completed")
    
    def _create_plot_area(self, parent):
        """グラフ描画エリアの作成"""
        plot_frame = ttk.LabelFrame(parent, text="散布図", padding="5")
        plot_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Matplotlib Canvas を埋め込み
        canvas = FigureCanvasTkAgg(self._visualizer.get_figure(), master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(expand=True, fill=tk.BOTH)
        
        self._canvas = canvas
        self._plot_area = plot_frame
        
        self._logger.info("Matplotlib canvas embedded in GUI")
    
    def _create_control_panel(self, parent):
        """操作パネルの作成"""
        control_frame = ttk.LabelFrame(parent, text="操作パネル", padding="10")
        control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # データ情報表示
        info_label = ttk.Label(control_frame, text="読み込み状況:")
        info_label.pack(pady=5)
        
        self._data_info_label = ttk.Label(
            control_frame, 
            text="データ未読み込み",
            foreground="gray"
        )
        self._data_info_label.pack(pady=5)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # カテゴリ選択
        category_frame = ttk.Frame(control_frame)
        category_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(category_frame, text="カテゴリ:").pack(side=tk.LEFT, padx=5)
        self._category_combo = ttk.Combobox(
            category_frame,
            textvariable=self._selected_category,
            state='readonly',
            width=15
        )
        self._category_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._category_combo['values'] = ["(すべて)"]
        
        # 軸ラベル設定
        label_frame = ttk.LabelFrame(control_frame, text="軸ラベル", padding="5")
        label_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(label_frame, text="X軸:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(label_frame, textvariable=self._x_label).grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(label_frame, text="Y軸:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(label_frame, textvariable=self._y_label).grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        label_frame.columnconfigure(1, weight=1)
        
        # 回帰線表示チェックボックス
        ttk.Checkbutton(
            control_frame,
            text="回帰線を表示",
            variable=self._show_regression
        ).pack(pady=5)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 更新ボタン
        self._update_btn = ttk.Button(
            control_frame, 
            text="グラフ更新",
            command=self._on_update
        )
        self._update_btn.pack(pady=5, fill=tk.X)
        
        # 保存ボタン
        self._save_btn = ttk.Button(
            control_frame, 
            text="画像保存",
            command=self._on_save
        )
        self._save_btn.pack(pady=5, fill=tk.X)
        
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)
        
        # 分析結果表示エリア
        info_frame = ttk.LabelFrame(control_frame, text="分析結果", padding="5")
        info_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self._info_text = tk.Text(info_frame, height=15, width=30, state=tk.DISABLED, wrap=tk.WORD)
        self._info_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(info_frame, command=self._info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._info_text.config(yscrollcommand=scrollbar.set)
    
    def _initial_load(self):
        """アプリケーション起動時の初期データロード"""
        self._logger.info("Performing initial data load...")
        self._load_data()
    
    def _load_data(self):
        """データをロードして表示を更新"""
        try:
            # データロード実行
            self._current_points = self._load_data_usecase.execute()
            
            # カテゴリリスト更新
            self._update_category_list()
            
            # 分析と描画
            self._analyze_and_visualize()
            
            # UI更新
            self._update_data_info()
            
            self._logger.info(f"Data loaded successfully: {len(self._current_points)} points")
            
        except DataLoadError as e:
            self._logger.error(f"Data load error: {e}", exc_info=True)
            messagebox.showerror(
                "データ読み込みエラー",
                f"データの読み込みに失敗しました:\n\n{str(e)}\n\n"
                f"ログファイルを確認してください。"
            )
            self._update_data_info(error=True)
            
        except Exception as e:
            self._logger.error(f"Unexpected error during data load: {e}", exc_info=True)
            messagebox.showerror(
                "エラー",
                f"予期しないエラーが発生しました:\n\n{str(e)}"
            )
            self._update_data_info(error=True)
    
    def _update_category_list(self):
        """カテゴリ選択コンボボックスを更新"""
        categories = set()
        for point in self._current_points:
            if point.category:
                categories.add(point.category)
        
        category_list = ["(すべて)"] + sorted(categories)
        self._category_combo['values'] = category_list
        self._selected_category.set("(すべて)")
    
    def _analyze_and_visualize(self):
        """分析と描画を実行"""
        try:
            # 分析実行
            self._current_result = self._analyze_usecase.execute(self._current_points)
            
            # 描画実行
            self._visualizer.visualize(
                self._current_points,
                self._current_result,
                x_label=self._x_label.get(),
                y_label=self._y_label.get(),
                show_regression=self._show_regression.get(),
                selected_category=self._selected_category.get()
            )
            
            # Canvas更新
            self._canvas.draw()
            
            # 分析結果表示
            self._display_analysis_result()
            
        except AnalysisError as e:
            self._logger.error(f"Analysis error: {e}", exc_info=True)
            messagebox.showerror(
                "分析エラー",
                f"データの分析に失敗しました:\n\n{str(e)}"
            )
        except Exception as e:
            self._logger.error(f"Visualization error: {e}", exc_info=True)
            messagebox.showerror(
                "描画エラー",
                f"グラフの描画に失敗しました:\n\n{str(e)}"
            )
    
    def _update_data_info(self, error: bool = False):
        """データ情報ラベルの更新"""
        if error:
            self._data_info_label.config(
                text="読み込み失敗",
                foreground="red"
            )
        else:
            self._data_info_label.config(
                text=f"{len(self._current_points)} 点読み込み済み",
                foreground="green"
            )
    
    def _display_data_summary(self):
        """データサマリーを情報エリアに表示"""
        self._info_text.config(state=tk.NORMAL)
        self._info_text.delete(1.0, tk.END)
        
        if not self._current_points:
            self._info_text.insert(tk.END, "データがありません")
        else:
            # 基本情報
            self._info_text.insert(tk.END, f"総データ数: {len(self._current_points)}\n\n")
            
            # カテゴリ別集計
            category_counts = {}
            no_category_count = 0
            
            for point in self._current_points:
                if point.category:
                    category_counts[point.category] = category_counts.get(point.category, 0) + 1
                else:
                    no_category_count += 1
            
            if category_counts:
                self._info_text.insert(tk.END, "カテゴリ別:\n")
                for category, count in sorted(category_counts.items()):
                    self._info_text.insert(tk.END, f"  {category}: {count}\n")
            
            if no_category_count > 0:
                self._info_text.insert(tk.END, f"  カテゴリなし: {no_category_count}\n")
            
            # 統計情報
            x_values = [p.x for p in self._current_points]
            y_values = [p.y for p in self._current_points]
            
            self._info_text.insert(tk.END, f"\nX範囲: {min(x_values):.2f} ~ {max(x_values):.2f}\n")
            self._info_text.insert(tk.END, f"Y範囲: {min(y_values):.2f} ~ {max(y_values):.2f}\n")
        
        self._info_text.config(state=tk.DISABLED)
    
    def _display_analysis_result(self):
        """分析結果を情報エリアに表示"""
        self._info_text.config(state=tk.NORMAL)
        self._info_text.delete(1.0, tk.END)
        
        if not self._current_result:
            self._info_text.insert(tk.END, "分析結果なし")
            self._info_text.config(state=tk.DISABLED)
            return
        
        # 基本情報
        self._info_text.insert(tk.END, f"総データ数: {self._current_result.point_count}\n\n")
        
        # カテゴリ別集計
        if self._current_result.category_counts:
            self._info_text.insert(tk.END, "カテゴリ別:\n")
            for category, count in sorted(self._current_result.category_counts.items()):
                self._info_text.insert(tk.END, f"  {category}: {count}\n")
            self._info_text.insert(tk.END, "\n")
        
        # 回帰分析結果
        if self._current_result.regression_line:
            reg = self._current_result.regression_line
            self._info_text.insert(tk.END, "=" * 30 + "\n")
            self._info_text.insert(tk.END, "回帰分析結果\n")
            self._info_text.insert(tk.END, "=" * 30 + "\n\n")
            
            # 回帰式
            self._info_text.insert(tk.END, f"回帰式:\n")
            self._info_text.insert(tk.END, f"  {reg.formula()}\n\n")
            
            # 決定係数
            self._info_text.insert(tk.END, f"決定係数 (R²):\n")
            self._info_text.insert(tk.END, f"  {reg.r_squared:.4f}\n\n")
            
            # 解釈
            if reg.r_squared >= 0.7:
                interpretation = "強い相関"
            elif reg.r_squared >= 0.4:
                interpretation = "中程度の相関"
            else:
                interpretation = "弱い相関"
            
            self._info_text.insert(tk.END, f"相関の強さ: {interpretation}\n")
        else:
            self._info_text.insert(tk.END, "\n回帰分析: 実行できません\n")
            self._info_text.insert(tk.END, "(データ点が不足しています)\n")
        
        self._info_text.config(state=tk.DISABLED)
    
    def _on_update(self):
        """更新ボタンのハンドラ"""
        self._logger.info("Update button clicked - reloading and re-analyzing")
        
        if self._current_points:
            # データ再ロードせず、設定変更のみ反映
            self._analyze_and_visualize()
        else:
            # データがない場合は再ロード
            self._load_data()
    
    def _on_save(self):
        """保存ボタンのハンドラ"""
        self._logger.info("Save button clicked")
        
        if not self._current_points:
            messagebox.showwarning(
                "保存エラー",
                "保存するデータがありません。\n先にデータを読み込んでください。"
            )
            return
        
        try:
            filepath = self._save_image_usecase.execute(
                x_label=self._x_label.get(),
                y_label=self._y_label.get(),
                category=self._selected_category.get()
            )
            
            messagebox.showinfo(
                "保存完了",
                f"画像を保存しました:\n\n{filepath}"
            )
            
        except Exception as e:
            self._logger.error(f"Save error: {e}", exc_info=True)
            messagebox.showerror(
                "保存エラー",
                f"画像の保存に失敗しました:\n\n{str(e)}"
            )
    
    def run(self):
        """アプリケーションのメインループを開始"""
        self._logger.info("Starting main event loop...")
        self._root.mainloop()
        self._logger.info("Main event loop terminated")