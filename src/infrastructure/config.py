"""
Infrastructure: 設定管理
settings.toml を読み込み、アプリケーション設定を提供
"""
import logging
from pathlib import Path
from typing import Any, Dict
try:
    import tomllib as tomli
except ModuleNotFoundError:
    import tomli

from src.core.exceptions import ConfigurationError


class ConfigManager:
    """設定ファイルの読み込みと管理"""
    
    DEFAULT_CONFIG = {
        "paths": {
            "input_dir": "./data",
            "output_dir": "./png",
            "font_path": ""
        },
        "data": {
            "encodings": ["utf-8", "cp932"]
        },
        "plot": {
            "default_color": "blue",
            "font_size": 12,
            "alpha": 0.7,
            "figure_size": [10, 8]
        },
        "ui": {
            "window_title": "Auto Scattering Ver 5.0",
            "initial_geometry": "1200x800"
        }
    }
    
    def __init__(self, config_path: str = "config/settings.toml"):
        self._config_path = Path(config_path)
        self._config = self._load_config()
        self._logger = logging.getLogger(__name__)
        self._logger.info(f"Configuration loaded from {self._config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む"""
        if not self._config_path.exists():
            logging.warning(
                f"Config file not found: {self._config_path}, using defaults"
            )
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self._config_path, 'rb') as f:
                config = tomli.load(f)
            
            # デフォルト値とマージ
            merged = self.DEFAULT_CONFIG.copy()
            self._deep_update(merged, config)
            return merged
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load config from {self._config_path}: {e}"
            ) from e
    
    def _deep_update(self, base: dict, update: dict):
        """辞書を再帰的にマージ"""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        ドット記法で設定値を取得
        例: get("paths.input_dir")
        """
        keys = key_path.split(".")
        value = self._config
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @property
    def input_dir(self) -> Path:
        """入力ディレクトリパス"""
        return Path(self.get("paths.input_dir", "./data"))
    
    @property
    def output_dir(self) -> Path:
        """出力ディレクトリパス"""
        return Path(self.get("paths.output_dir", "./png"))
    
    @property
    def window_title(self) -> str:
        """ウィンドウタイトル"""
        return self.get("ui.window_title", "Auto Scattering")
    
    @property
    def initial_geometry(self) -> str:
        """初期ウィンドウサイズ"""
        return self.get("ui.initial_geometry", "1200x800")