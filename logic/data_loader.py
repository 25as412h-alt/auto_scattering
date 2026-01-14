"""
データローダー - CSV読み込み処理
"""
import pandas as pd
from pathlib import Path
import logging

class DataLoader:
    """CSVファイルを読み込んでDataFrameを返す"""
    
    def load(self, scatter_path: str, category_path: str = None) -> pd.DataFrame:
        """
        散布図データとカテゴリデータを読み込む
        
        Args:
            scatter_path: 散布図データのパス
            category_path: カテゴリデータのパス（オプション）
        
        Returns:
            pd.DataFrame: 結合されたデータ
        """
        # 1. 散布図データ読み込み
        df = self._read_csv(scatter_path)
        # 列名を大文字に統一して X/Y の検出をケースに依らず行えるようにする
        if df.columns is not None:
            df.columns = [str(col).upper() for col in df.columns]
        logging.info(f"散布図データ読み込み: {len(df)}行")
        
        # 2. X, Y列の検証とクレンジング
        if 'X' not in df.columns or 'Y' not in df.columns:
            raise ValueError("CSVに'X'列または'Y'列がありません")
        
        df = self._clean_numeric_columns(df, ['X', 'Y'])
        logging.info(f"数値クレンジング後: {len(df)}行")
        
        # 3. カテゴリデータの結合
        if category_path and Path(category_path).exists():
            try:
                cat_df = self._read_csv(category_path)
                
                # 結合キーを自動検出（共通列名）を安定させるため、カテゴリデータの列名も大文字化
                cat_df.columns = [str(col).upper() for col in cat_df.columns]

                common_cols = set(df.columns) & set(cat_df.columns)
                if common_cols:
                    # 優先キーを ID があればそれを、なければ共通列のうち1つを選択
                    if 'ID' in common_cols:
                        join_key = 'ID'
                    else:
                        join_key = sorted(list(common_cols))[0]
                    df = df.merge(cat_df, on=join_key, how='left')
                    logging.info(f"カテゴリデータ結合: キー={join_key}")
                else:
                    logging.warning("共通の結合キーが見つかりません")
            except Exception as e:
                logging.warning(f"カテゴリデータ読み込み失敗: {e}")
        
        return df
    
    def _read_csv(self, path: str) -> pd.DataFrame:
        """
        CSVファイルを読み込む（エンコーディング自動判定）
        
        Args:
            path: CSVファイルのパス
        
        Returns:
            pd.DataFrame: 読み込んだデータ
        """
        encodings = ['utf-8', 'cp932', 'shift_jis']
        
        for encoding in encodings:
            try:
                df = pd.read_csv(path, encoding=encoding)
                logging.info(f"CSV読み込み成功: {path} (encoding={encoding})")
                return df
            except (UnicodeDecodeError, FileNotFoundError) as e:
                if encoding == encodings[-1]:
                    # 最後のエンコーディングでも失敗
                    raise ValueError(f"CSVファイル読み込み失敗: {path}") from e
                continue
        
        raise ValueError(f"CSVファイル読み込み失敗: {path}")
    
    def _clean_numeric_columns(self, df: pd.DataFrame, cols: list) -> pd.DataFrame:
        """
        数値列のクレンジング（数値変換できない行を削除）
        
        Args:
            df: データフレーム
            cols: 数値列のリスト
        
        Returns:
            pd.DataFrame: クレンジング後のデータ
        """
        original_len = len(df)
        
        for col in cols:
            if col in df.columns:
                # 数値変換（変換できない値はNaNに）
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # NaNを含む行を削除
        df = df.dropna(subset=cols)
        
        dropped = original_len - len(df)
        if dropped > 0:
            logging.warning(f"{dropped}行をドロップしました（数値変換不可）")
        
        return df