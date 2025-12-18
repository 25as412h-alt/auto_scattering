"""
メインウィンドウ - GUI制御
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from datetime import datetime
import logging

from logic.data_loader import DataLoader
from logic.analyzer import Analyzer
from logic.plotter import ScatterPlotter

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Auto Scattering Ver 6.0")
        self.root.geometry("1200x800")
        
        # ビジネスロジック初期化
        self.loader = DataLoader()
        self.analyzer = Analyzer()
        self.plotter = ScatterPlotter()
        
        # データ保持
        self.df = None
        self.scatter_path = "data/scatter.csv"
        self.category_path = None
        
        # GUI構築
        self._create_layout()
        self._load_initial_data()
    
    def _create_layout(self):
        """レイアウト構築"""
        # ========== 左ペイン: Canvas ==========
        left_frame = tk.Frame(self.root, bg='white')
        left_frame.pack(side='left', fill='both', expand=True)
        
        # Matplotlibキャンバス
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, left_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True, padx=5, pady=5)
        
        # ========== 右ペイン: 操作パネル ==========
        right_frame = tk.Frame(self.root, width=350, bg='#f0f0f0')
        right_frame.pack(side='right', fill='y', padx=10, pady=10)
        right_frame.pack_propagate(False)  # サイズ固定
        
        # --- データ読み込みセクション ---
        section1 = tk.LabelFrame(right_frame, text="データ読み込み", padx=10, pady=10)
        section1.pack(fill='x', pady=5)
        
        tk.Button(section1, text="📂 散布図データを選択", 
                  command=self._select_scatter_file, width=25).pack(pady=3)
        self.scatter_label = tk.Label(section1, text="未選択", fg='gray')
        self.scatter_label.pack()
        
        tk.Button(section1, text="📂 カテゴリデータを選択", 
                  command=self._select_category_file, width=25).pack(pady=3)
        self.category_label = tk.Label(section1, text="未選択", fg='gray')
        self.category_label.pack()
        
        # --- 軸設定セクション ---
        section2 = tk.LabelFrame(right_frame, text="軸設定", padx=10, pady=10)
        section2.pack(fill='x', pady=5)
        
        # X軸
        x_frame = tk.Frame(section2)
        x_frame.pack(fill='x', pady=3)
        tk.Label(x_frame, text="X軸:", width=5).pack(side='left')
        self.x_min_entry = tk.Entry(x_frame, width=8)
        self.x_min_entry.pack(side='left', padx=2)
        tk.Label(x_frame, text="～").pack(side='left')
        self.x_max_entry = tk.Entry(x_frame, width=8)
        self.x_max_entry.pack(side='left', padx=2)
        
        # Y軸
        y_frame = tk.Frame(section2)
        y_frame.pack(fill='x', pady=3)
        tk.Label(y_frame, text="Y軸:", width=5).pack(side='left')
        self.y_min_entry = tk.Entry(y_frame, width=8)
        self.y_min_entry.pack(side='left', padx=2)
        tk.Label(y_frame, text="～").pack(side='left')
        self.y_max_entry = tk.Entry(y_frame, width=8)
        self.y_max_entry.pack(side='left', padx=2)
        
        # --- 表示設定セクション ---
        section3 = tk.LabelFrame(right_frame, text="表示設定", padx=10, pady=10)
        section3.pack(fill='x', pady=5)
        
        # 回帰線ON/OFF
        self.show_regression = tk.BooleanVar(value=True)
        tk.Checkbutton(section3, text="回帰線を表示", 
                       variable=self.show_regression).pack(anchor='w')
        
        # カテゴリ選択
        cat_frame = tk.Frame(section3)
        cat_frame.pack(fill='x', pady=5)
        tk.Label(cat_frame, text="カテゴリ:").pack(side='left')
        self.category_var = tk.StringVar(value="なし")
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var, 
                                            state='readonly', width=15)
        self.category_combo['values'] = ["なし"]
        self.category_combo.pack(side='left', padx=5)
        
        # --- アクションボタン ---
        btn_frame = tk.Frame(right_frame)
        btn_frame.pack(fill='x', pady=10)
        
        tk.Button(btn_frame, text="🔄 更新", command=self._update_plot, 
                  bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                  width=15, height=2).pack(pady=3)
        tk.Button(btn_frame, text="💾 保存", command=self._save_image,
                  bg='#2196F3', fg='white', font=('Arial', 10, 'bold'),
                  width=15, height=2).pack(pady=3)
        
        # --- 分析結果表示 ---
        section4 = tk.LabelFrame(right_frame, text="分析結果", padx=10, pady=10)
        section4.pack(fill='both', expand=True, pady=5)
        
        # スクロール可能なテキスト
        text_frame = tk.Frame(section4)
        text_frame.pack(fill='both', expand=True)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side='right', fill='y')
        
        self.result_text = tk.Text(text_frame, height=10, width=30, 
                                     yscrollcommand=scrollbar.set,
                                     font=('Courier', 9))
        self.result_text.pack(side='left', fill='both', expand=True)
        scrollbar.config(command=self.result_text.yview)
    
    def _load_initial_data(self):
        """起動時のデータ読み込み"""
        try:
            from pathlib import Path
            if Path(self.scatter_path).exists():
                self.df = self.loader.load(self.scatter_path, self.category_path)
                self.scatter_label.config(text=Path(self.scatter_path).name, fg='green')
                self._update_category_combo()
                self._update_plot()
                logging.info(f"初期データ読み込み成功: {len(self.df)}件")
            else:
                self._show_result("データファイルが見つかりません。\n'data/scatter.csv' を配置してください。")
                logging.warning("初期データファイルが存在しません")
        except Exception as e:
            messagebox.showerror("エラー", f"初期データ読み込み失敗:\n{e}")
            logging.error(f"初期データ読み込みエラー: {e}", exc_info=True)
    
    def _select_scatter_file(self):
        """散布図データファイル選択"""
        path = filedialog.askopenfilename(
            title="散布図データを選択",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir="data"
        )
        if path:
            self.scatter_path = path
            self.scatter_label.config(text=Path(path).name, fg='green')
            logging.info(f"散布図データ選択: {path}")
    
    def _select_category_file(self):
        """カテゴリデータファイル選択"""
        path = filedialog.askopenfilename(
            title="カテゴリデータを選択",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            initialdir="data"
        )
        if path:
            self.category_path = path
            self.category_label.config(text=Path(path).name, fg='green')
            logging.info(f"カテゴリデータ選択: {path}")
        else:
            self.category_path = None
            self.category_label.config(text="未選択", fg='gray')
    
    def _update_category_combo(self):
        """カテゴリコンボボックスを更新"""
        if self.df is None:
            return
        
        # カテゴリ列を検出（X, Y以外の列）
        category_cols = [col for col in self.df.columns if col not in ['X', 'Y']]
        self.category_combo['values'] = ["なし"] + category_cols
        
        if category_cols:
            self.category_var.set(category_cols[0])
        else:
            self.category_var.set("なし")
    
    def _update_plot(self):
        """散布図を更新"""
        try:
            # データ再読み込み
            self.df = self.loader.load(self.scatter_path, self.category_path)
            self._update_category_combo()
            
            # 軸範囲取得
            xlim = self._get_axis_range(self.x_min_entry, self.x_max_entry)
            ylim = self._get_axis_range(self.y_min_entry, self.y_max_entry)
            
            # カテゴリ取得
            category_col = None if self.category_var.get() == "なし" else self.category_var.get()
            
            # 描画
            self.plotter.draw(
                self.ax, 
                self.df, 
                x_col='X', 
                y_col='Y',
                category_col=category_col,
                show_regression=self.show_regression.get(),
                xlim=xlim,
                ylim=ylim
            )
            self.canvas.draw()
            
            # 分析結果表示
            result = self.analyzer.analyze(self.df, 'X', 'Y')
            self._show_result(self._format_result(result))
            
            logging.info("散布図更新完了")
            
        except Exception as e:
            messagebox.showerror("エラー", f"散布図更新失敗:\n{e}")
            logging.error(f"散布図更新エラー: {e}", exc_info=True)
    
    def _get_axis_range(self, min_entry, max_entry):
        """軸範囲を取得（空欄ならNone）"""
        try:
            min_val = float(min_entry.get()) if min_entry.get().strip() else None
            max_val = float(max_entry.get()) if max_entry.get().strip() else None
            if min_val is not None and max_val is not None:
                return (min_val, max_val)
            return None
        except ValueError:
            return None
    
    def _format_result(self, result):
        """分析結果をフォーマット"""
        return f"""
━━━━━━━━━━━━━━━━━━
  回帰分析結果
━━━━━━━━━━━━━━━━━━

回帰式:
  {result['equation']}

決定係数:
  R² = {result['r_squared']:.4f}

データ数:
  n = {result['n_samples']}

━━━━━━━━━━━━━━━━━━
        """
    
    def _show_result(self, text):
        """分析結果を表示"""
        self.result_text.delete('1.0', 'end')
        self.result_text.insert('1.0', text)
    
    def _save_image(self):
        """画像を保存"""
        try:
            if self.df is None:
                messagebox.showwarning("警告", "データが読み込まれていません")
                return
            
            # ファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            category = self.category_var.get() if self.category_var.get() != "なし" else "all"
            filename = f"X_Y_{category}_{timestamp}.png"
            filepath = f"output/{filename}"
            
            # 保存
            self.fig.savefig(filepath, dpi=300, bbox_inches='tight')
            messagebox.showinfo("保存完了", f"画像を保存しました:\n{filepath}")
            logging.info(f"画像保存: {filepath}")
            
        except Exception as e:
            messagebox.showerror("エラー", f"画像保存失敗:\n{e}")
            logging.error(f"画像保存エラー: {e}", exc_info=True)