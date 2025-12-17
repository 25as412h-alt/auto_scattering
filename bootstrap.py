"""
Bootstrap - Dependency Injection Container
依存関係の解決とインスタンス生成を担当
"""
import logging
import logging.config
from pathlib import Path
import yaml

from src.infrastructure.config import ConfigManager
from src.infrastructure.repositories import ScatterRepository, CategoryRepository
from src.infrastructure.analysis import ScipyAnalyzer
from src.infrastructure.visualization.matplotlib_visualizer import MatplotlibVisualizer
from src.usecases.load_data import LoadDataUseCase
from src.usecases.analyze import AnalyzeDataUseCase
from src.usecases.save_image import SaveImageUseCase
from src.interfaces.gui.windows import MainWindow


class Bootstrap:
    """DIコンテナとアプリケーション構成を管理"""
    
    def __init__(self):
        self._setup_logging()
        self._config = ConfigManager()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Bootstrap initialized")
        
        # 必要なディレクトリを作成
        self._ensure_directories()
    
    def _setup_logging(self):
        """ログ設定の初期化"""
        log_config_path = Path("config/logging_config.yaml")
        
        # ログディレクトリ作成
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        if log_config_path.exists():
            with open(log_config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                logging.config.dictConfig(config)
        else:
            # デフォルトログ設定
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/app.log', encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            logging.warning(f"Logging config not found: {log_config_path}, using default")
    
    def _ensure_directories(self):
        """必要なディレクトリが存在することを確認"""
        directories = [
            self._config.input_dir / "scatter",
            self._config.input_dir / "category",
            self._config.output_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured directory exists: {directory}")
    
    def create_application(self):
        """アプリケーションインスタンスを生成"""
        self.logger.info("Creating application instance...")
        
        # Repository の生成
        scatter_repo = self._create_scatter_repository()
        category_repo = self._create_category_repository()
        
        # Analyzer の生成
        analyzer = ScipyAnalyzer()
        
        # Visualizer の生成
        visualizer = self._create_visualizer()
        
        # UseCase の生成
        load_data_usecase = LoadDataUseCase(scatter_repo, category_repo)
        analyze_usecase = AnalyzeDataUseCase(analyzer)
        save_image_usecase = SaveImageUseCase(visualizer, self._config.output_dir)
        
        # MainWindow に UseCase を注入
        app = MainWindow(
            self._config, 
            load_data_usecase,
            analyze_usecase,
            visualizer,
            save_image_usecase
        )
        
        self.logger.info("Application instance created successfully")
        return app
    
    def _create_scatter_repository(self) -> ScatterRepository:
        """ScatterRepository を生成"""
        scatter_file = self._config.input_dir / self._config.get(
            "data.scatter_file", "scatter/scatter.csv"
        )
        encodings = self._config.get("data.encodings", ["utf-8", "cp932"])
        
        return ScatterRepository(scatter_file, encodings)
    
    def _create_category_repository(self) -> CategoryRepository:
        """CategoryRepository を生成"""
        category_dir = self._config.input_dir / self._config.get(
            "data.category_dir", "category"
        )
        encodings = self._config.get("data.encodings", ["utf-8", "cp932"])
        
        return CategoryRepository(category_dir, encodings)
    
    def _create_visualizer(self) -> MatplotlibVisualizer:
        """MatplotlibVisualizer を生成"""
        plot_config = {
            'figure_size': self._config.get('plot.figure_size', [10, 8]),
            'alpha': self._config.get('plot.alpha', 0.7),
            'font_size': self._config.get('plot.font_size', 12),
            'grid_alpha': self._config.get('plot.grid_alpha', 0.3),
            'grid_style': self._config.get('plot.grid_style', 'dotted')
        }
        
        return MatplotlibVisualizer(plot_config)