"""
UseCase: 画像保存
散布図を画像ファイルとして保存
"""
import logging
from pathlib import Path
import re

from src.core.interfaces import IVisualizer
from src.core.exceptions import AutoScatteringError


class SaveImageUseCase:
    """画像保存ユースケース"""
    
    def __init__(self, visualizer: IVisualizer, output_dir: Path):
        self._visualizer = visualizer
        self._output_dir = output_dir
        self._logger = logging.getLogger(__name__)
    
    def execute(self, x_label: str, y_label: str, category: str = None) -> Path:
        """
        現在の描画を画像として保存
        
        Args:
            x_label: X軸ラベル
            y_label: Y軸ラベル
            category: カテゴリ名（省略可）
        Returns:
            保存されたファイルのパス
        Raises:
            AutoScatteringError: 保存失敗時
        """
        try:
            # ファイル名生成
            filename = self._generate_filename(x_label, y_label, category)
            filepath = self._output_dir / filename
            
            self._logger.info(f"Saving image to: {filepath}")
            
            # 保存実行
            self._visualizer.save(filepath)
            
            self._logger.info(f"Image saved successfully: {filepath}")
            return filepath
            
        except Exception as e:
            self._logger.error(f"Failed to save image: {e}", exc_info=True)
            raise AutoScatteringError(f"Image save failed: {e}") from e
    
    def _generate_filename(self, x_label: str, y_label: str, category: str = None) -> str:
        """
        ファイル名を生成（サニタイズ処理付き）
        
        形式: XLabel_YLabel_Category.png
        """
        # ファイル名として使えない文字を除去
        def sanitize(text: str) -> str:
            # 空白・スラッシュ・バックスラッシュ等を削除
            text = re.sub(r'[\\/:*?"<>|]', '', text)
            # 前後の空白を除去
            text = text.strip()
            # 空の場合はデフォルト値
            return text if text else 'unnamed'
        
        parts = [
            sanitize(x_label),
            sanitize(y_label)
        ]
        
        if category and category != "(すべて)":
            parts.append(sanitize(category))
        
        filename = "_".join(parts) + ".png"
        
        # ファイル名が既に存在する場合は連番を付与
        if (self._output_dir / filename).exists():
            filename = self._generate_unique_filename(filename)
        
        return filename
    
    def _generate_unique_filename(self, base_filename: str) -> str:
        """重複しないファイル名を生成"""
        name, ext = base_filename.rsplit('.', 1)
        counter = 1
        
        while True:
            new_filename = f"{name}_{counter}.{ext}"
            if not (self._output_dir / new_filename).exists():
                return new_filename
            counter += 1
            
            # 無限ループ防止
            if counter > 9999:
                raise AutoScatteringError("Too many files with same name")