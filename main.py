"""
Auto Scattering Application - Entry Point
アプリケーションの起動エントリポイント
"""
import sys
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from bootstrap import Bootstrap


def main():
    """アプリケーションのメインエントリポイント"""
    try:
        # ブートストラップでDIコンテナを構成
        bootstrap = Bootstrap()
        
        # ロガー取得
        logger = logging.getLogger(__name__)
        logger.info("=" * 60)
        logger.info("Auto Scattering Application Starting...")
        logger.info("=" * 60)
        
        # アプリケーション起動
        app = bootstrap.create_application()
        app.run()
        
        logger.info("Application terminated successfully")
        
    except Exception as e:
        print(f"Fatal error during startup: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

import logging
import sys

def _configure_logging():
    # コンソールとファイルの両方に出力する設定
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("logs/app.log", encoding="utf-8")
        ]
    )

def _run_application():
    # 既存エントリポイントを呼び出す想定
    from src.usecases import __init__ as usecases
    if hasattr(usecases, "main"):
        return usecases.main()
    if hasattr(usecases, "main_entry"):
        return usecases.main_entry()
    raise RuntimeError("No entrypoint found in src.usecases.__init__")

if __name__ == "__main__":
    _configure_logging()
    try:
        _run_application()
    except KeyboardInterrupt:
        logging.info("Interrupted by user")
        sys.exit(0)
    except Exception:
        logging.exception("Unhandled exception in application")
        sys.exit(1)


if __name__ == "__main__":
    main()