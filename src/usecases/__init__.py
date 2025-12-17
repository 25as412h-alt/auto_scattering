"""
Use Cases Layer
アプリケーション固有のビジネスルールを実装
"""
from .load_data import LoadDataUseCase
from .analyze import AnalyzeDataUseCase
from .save_image import SaveImageUseCase

__all__ = [
    'LoadDataUseCase',
    'AnalyzeDataUseCase',
    'SaveImageUseCase',
    'main',
]

def main():
    """アプリケーションのエントリーポイント"""
    from src.interfaces.gui.windows import MainWindow
    from src.infrastructure.config import ConfigManager
    
    config = ConfigManager()
    main_window = MainWindow(config=config)
    main_window.run()

if __name__ == "__main__":
    main()