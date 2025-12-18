"""
Auto Scattering Ver 6.0 - メインエントリポイント
"""
import tkinter as tk
from gui.main_window import MainWindow
import logging
from pathlib import Path

def setup_directories():
    """必要なディレクトリを作成"""
    Path("data").mkdir(exist_ok=True)
    Path("output").mkdir(exist_ok=True)

def setup_logging():
    """ログ設定"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def main():
    setup_directories()
    setup_logging()
    
    logging.info("Auto Scattering Ver 6.0 起動")
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    
    logging.info("アプリケーション終了")

if __name__ == "__main__":
    main()