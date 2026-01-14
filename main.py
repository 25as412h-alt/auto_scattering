"""
Auto Scattering Ver 6.0 - メインエントリポイント
"""
import tkinter as tk
from gui.main_window import MainWindow
import logging
from pathlib import Path
import os
import sys
import subprocess
import platform

def setup_virtualenv():
    venv_dir = "venv"
    
    # 仮想環境が存在しない場合に作成
    if not os.path.exists(venv_dir):
        logging.info("仮想環境を作成しています...")
        subprocess.check_call([sys.executable, '-m', 'venv', venv_dir])
    
    # 仮想環境をアクティベート
    if platform.system() == "Windows":
        activate_script = os.path.join(venv_dir, "Scripts", "activate.bat")
        subprocess.call(f'cmd /c "{activate_script}" && pip install -r requirements.txt', shell=True)
    else:
        activate_script = os.path.join(venv_dir, "bin", "activate")
        subprocess.call(f'source {activate_script} && pip install -r requirements.txt', shell=True)
    logging.info("仮想環境のセットアップが完了しました。")

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
    setup_logging()  # 最初にロギングを設定
    setup_virtualenv()
    setup_directories()
    
    logging.info("Auto Scattering Ver 6.0 起動")
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()
    
    logging.info("アプリケーション終了")

if __name__ == "__main__":
    main()