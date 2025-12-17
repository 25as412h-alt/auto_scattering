"""
Repository実装のテスト
"""
import pytest
from pathlib import Path
import pandas as pd
import tempfile
import shutil

from src.infrastructure.repositories import ScatterRepository, CategoryRepository
from src.core.exceptions import DataLoadError


class TestScatterRepository:
    """ScatterRepositoryのテスト"""
    
    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_load_valid_data(self, temp_dir):
        """正常なデータの読み込み"""
        # テストデータ作成
        csv_path = temp_dir / "test.csv"
        df = pd.DataFrame({
            'label': ['A', 'B', 'C'],
            'x': [1.0, 2.0, 3.0],
            'y': [10.0, 20.0, 30.0]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        # Repository作成
        repo = ScatterRepository(csv_path, ['utf-8'])
        points = repo.load()
        
        # 検証
        assert len(points) == 3
        assert points[0].label == 'A'
        assert points[0].x == 1.0
        assert points[0].y == 10.0
    
    def test_load_with_invalid_rows(self, temp_dir):
        """不正な行を含むデータの読み込み"""
        csv_path = temp_dir / "test.csv"
        df = pd.DataFrame({
            'label': ['A', 'B', 'C'],
            'x': [1.0, 'invalid', 3.0],
            'y': [10.0, 20.0, 30.0]
        })
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        repo = ScatterRepository(csv_path, ['utf-8'])
        points = repo.load()
        
        # 不正な行は除外される
        assert len(points) == 2
        assert all(p.label in ['A', 'C'] for p in points)
    
    def test_load_missing_columns(self, temp_dir):
        """必須カラムが欠けている場合"""
        csv_path = temp_dir / "test.csv"
        df = pd.DataFrame({
            'label': ['A', 'B'],
            'x': [1.0, 2.0]
            # y カラムが欠けている
        })
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        repo = ScatterRepository(csv_path, ['utf-8'])
        
        with pytest.raises(DataLoadError, match="Required columns missing"):
            repo.load()
    
    def test_load_file_not_found(self, temp_dir):
        """ファイルが存在しない場合"""
        csv_path = temp_dir / "nonexistent.csv"
        repo = ScatterRepository(csv_path, ['utf-8'])
        
        with pytest.raises(DataLoadError, match="not found"):
            repo.load()
    
    def test_encoding_fallback(self, temp_dir):
        """エンコーディングフォールバックのテスト"""
        csv_path = temp_dir / "test.csv"
        df = pd.DataFrame({
            'label': ['あ', 'い', 'う'],
            'x': [1.0, 2.0, 3.0],
            'y': [10.0, 20.0, 30.0]
        })
        df.to_csv(csv_path, index=False, encoding='cp932')
        
        # UTF-8で失敗してCP932で成功するはず
        repo = ScatterRepository(csv_path, ['utf-8', 'cp932'])
        points = repo.load()
        
        assert len(points) == 3


class TestCategoryRepository:
    """CategoryRepositoryのテスト"""
    
    @pytest.fixture
    def temp_dir(self):
        """一時ディレクトリを作成"""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_load_valid_data(self, temp_dir):
        """正常なカテゴリデータの読み込み"""
        csv_path = temp_dir / "category.csv"
        df = pd.DataFrame({
            'label': ['A', 'B', 'C'],
            'category': ['Group1', 'Group2', 'Group1']
        })
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        repo = CategoryRepository(temp_dir, ['utf-8'])
        category_map = repo.load()
        
        assert len(category_map) == 3
        assert category_map['A'] == 'Group1'
        assert category_map['B'] == 'Group2'
    
    def test_load_with_missing_values(self, temp_dir):
        """欠損値を含むデータ"""
        csv_path = temp_dir / "category.csv"
        df = pd.DataFrame({
            'label': ['A', 'B', 'C', 'D'],
            'category': ['Group1', None, 'Group2', 'Group1']
        })
        df.to_csv(csv_path, index=False, encoding='utf-8')
        
        repo = CategoryRepository(temp_dir, ['utf-8'])
        category_map = repo.load()
        
        # 欠損値を含む行は除外される
        assert len(category_map) == 3
        assert 'B' not in category_map
    
    def test_load_no_csv_files(self, temp_dir):
        """CSVファイルが存在しない場合"""
        repo = CategoryRepository(temp_dir, ['utf-8'])
        category_map = repo.load()
        
        # 空の辞書を返す
        assert category_map == {}
    
    def test_load_multiple_csv_files(self, temp_dir):
        """複数のCSVファイルがある場合（最初のものを使用）"""
        for i in range(3):
            csv_path = temp_dir / f"category_{i}.csv"
            df = pd.DataFrame({
                'label': [f'Label_{i}'],
                'category': [f'Group_{i}']
            })
            df.to_csv(csv_path, index=False, encoding='utf-8')
        
        repo = CategoryRepository(temp_dir, ['utf-8'])
        category_map = repo.load()
        
        # いずれか1つのファイルが読み込まれる
        assert len(category_map) == 1