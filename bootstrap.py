"""
Bootstrap - Dependency Injection Container
依存関係の解決とインスタンス生成を担当
"""
import logging
import logging.config
from pathlib import Path
import yaml

from src.infrastructure.config import ConfigManager
from src.interfaces.gui.windows import MainWindow


class Bootstrap:
    """DIコンテナとアプリケーション構成を管理"""
    
    def __init__(self):
        self._setup_logging()
        self._config = ConfigManager()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Bootstrap initialized")
    
    def _setup_logging(self):
        """ログ設定の初期化 with safe fallback"""
        log_config_path = Path("config/logging_config.yaml")
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        if log_config_path.exists():
            try:
                import yaml  # 既に import に含まれている場合は不要
                with open(log_config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                logging.config.dictConfig(config)
            except Exception as e:
                # 設定読み込み失敗時のフォールバック
                logging.basicConfig(
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler('logs/app.log', encoding='utf-8'),
                        logging.StreamHandler()
                    ]
                )
                logging.getLogger(__name__).warning(
                    f"Failed to load logging config ({log_config_path}): {e}. Using default config."
                )
        else:
            # 既定のフォールバックは既存のブランクを埋める形で維持
            logging.basicConfig(
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s',
                handlers=[
                    logging.FileHandler('logs/app.log', encoding='utf-8'),
                    logging.StreamHandler()
                ]
            )
            logging.getLogger(__name__).warning(
                f"Logging config not found: {log_config_path}, using default config."
            )
    
    def create_application(self):
        """アプリケーションインスタンスを生成"""
        self.logger.info("Creating application instance...")
        
        # Phase 1: 空のMainWindowを生成
        # 後のフェーズでUseCaseやRepositoryを注入
        app = MainWindow(self._config)
        
        self.logger.info("Application instance created successfully")
        return app