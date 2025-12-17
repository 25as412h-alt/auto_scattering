"""
GUI: メインウィンドウ
Tkinterを使用したUIの実装
"""
import logging
import tkinter as tk
from tkinter import ttk

from src.infrastructure.config import ConfigManager


class MainWindow:
    """メインウィンドウクラス"""
    
    def __init__(self, config: ConfigManager):
        self._config = config
        self._logger = logging.getLogger(__name__)
        
        # Tkinterルートウィンドウ作成
        self._root = tk.Tk()
        self._root.title(config.window_title)
        self._root.geometry(config.initial_geometry)
        
        self._setup_ui()
        
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
        
        # Phase 1: プレースホルダラベル
        placeholder = ttk.Label(
            plot_frame, 
            text="[グラフ描画エリア]\n\nPhase 3 で Matplotlib Canvas を配置",
            anchor=tk.CENTER,
            justify=tk.CENTER
        )
        placeholder.pack(expand=True, fill=tk.BOTH)
        
        self._plot_area = plot_frame
    
    def _create_control_panel(self, parent):
        """操作パネルの作成"""
        control_frame = ttk.LabelFrame(parent, text="操作パネル", padding="10")
        control_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5, pady=5)
        
        # Phase 1: 基本的なボタンのみ配置
        ttk.Label(control_frame, text="Phase 1: 基盤構築").pack(pady=10)
        
        # 更新ボタン（Phase 4で実装）
        self._update_btn = ttk.Button(
            control_frame, 
            text="更新",
            state=tk.DISABLED,
            command=self._on_update
        )
        self._update_btn.pack(pady=5, fill=tk.X)
        
        # 保存ボタン（Phase 5で実装）
        self._save_btn = ttk.Button(
            control_frame, 
            text="保存",
            state=tk.DISABLED,
            command=self._on_save
        )
        self._save_btn.pack(pady=5, fill=tk.X)
        
        # 情報表示エリア（Phase 3で使用）
        info_frame = ttk.LabelFrame(control_frame, text="分析結果", padding="5")
        info_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self._info_text = tk.Text(info_frame, height=10, width=30, state=tk.DISABLED)
        self._info_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(info_frame, command=self._info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._info_text.config(yscrollcommand=scrollbar.set)
    
    def _on_update(self):
        """更新ボタンのハンドラ（Phase 4で実装）"""
        self._logger.info("Update button clicked (not implemented yet)")
    
    def _on_save(self):
        """保存ボタンのハンドラ（Phase 5で実装）"""
        self._logger.info("Save button clicked (not implemented yet)")
    
    def run(self):
        """アプリケーションのメインループを開始"""
        self._logger.info("Starting main event loop...")
        self._root.mainloop()
        self._logger.info("Main event loop terminated")