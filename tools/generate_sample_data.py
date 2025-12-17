"""
サンプルデータ生成スクリプト
テスト用のscatter.csvとcategory.csvを生成
"""
import sys
from pathlib import Path
import pandas as pd
import numpy as np

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def generate_scatter_data(n_points: int = 100) -> pd.DataFrame:
    """散布図データを生成"""
    np.random.seed(42)
    
    # ラベル生成
    labels = [f"Sample_{i:03d}" for i in range(1, n_points + 1)]
    
    # X値（0～100の範囲）
    x_values = np.random.uniform(0, 100, n_points)
    
    # Y値（X値と相関を持たせる + ノイズ）
    y_values = 2.5 * x_values + 10 + np.random.normal(0, 15, n_points)
    
    df = pd.DataFrame({
        'label': labels,
        'x': x_values,
        'y': y_values
    })
    
    return df


def generate_category_data(labels: list, categories: list = None) -> pd.DataFrame:
    """カテゴリデータを生成"""
    if categories is None:
        categories = ['Group_A', 'Group_B', 'Group_C']
    
    np.random.seed(42)
    
    # ランダムにカテゴリを割り当て
    assigned_categories = np.random.choice(categories, size=len(labels))
    
    # 一部のラベルにはカテゴリを割り当てない（欠損値のテスト）
    mask = np.random.random(len(labels)) > 0.9  # 10%欠損
    assigned_categories = [cat if not m else None for cat, m in zip(assigned_categories, mask)]
    
    df = pd.DataFrame({
        'label': labels,
        'category': assigned_categories
    })
    
    return df


def main():
    """サンプルデータを生成して保存"""
    print("Generating sample data...")
    
    # ディレクトリ作成
    scatter_dir = project_root / "data" / "scatter"
    category_dir = project_root / "data" / "category"
    
    scatter_dir.mkdir(parents=True, exist_ok=True)
    category_dir.mkdir(parents=True, exist_ok=True)
    
    # 散布図データ生成
    scatter_df = generate_scatter_data(n_points=100)
    scatter_path = scatter_dir / "scatter.csv"
    scatter_df.to_csv(scatter_path, index=False, encoding='utf-8')
    print(f"✓ Created: {scatter_path} ({len(scatter_df)} rows)")
    
    # カテゴリデータ生成
    category_df = generate_category_data(scatter_df['label'].tolist())
    category_path = category_dir / "category_A.csv"
    category_df.to_csv(category_path, index=False, encoding='utf-8')
    print(f"✓ Created: {category_path} ({len(category_df)} rows)")
    
    # 統計情報表示
    print("\n=== Data Statistics ===")
    print(f"Scatter data:")
    print(f"  X range: {scatter_df['x'].min():.2f} ~ {scatter_df['x'].max():.2f}")
    print(f"  Y range: {scatter_df['y'].min():.2f} ~ {scatter_df['y'].max():.2f}")
    
    print(f"\nCategory data:")
    category_counts = category_df['category'].value_counts()
    for cat, count in category_counts.items():
        print(f"  {cat}: {count}")
    null_count = category_df['category'].isna().sum()
    if null_count > 0:
        print(f"  (null): {null_count}")
    
    print("\n✓ Sample data generation completed!")


if __name__ == "__main__":
    main()