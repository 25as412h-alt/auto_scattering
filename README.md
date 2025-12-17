# Auto Scattering Ver 5.0

CSVデータから散布図を生成し、カテゴリ別の可視化および回帰分析をGUI操作で行うアプリケーション。

## アーキテクチャ

本プロジェクトは **クリーンアーキテクチャ** に基づいた設計を採用しています。

### レイヤー構成

```
Core (Entities, Interfaces) 
  ↑
UseCases
  ↑
Infrastructure / GUI (Adapters)
```

- **Core層**: 外部依存ゼロの純粋なビジネスロジック
- **UseCase層**: アプリケーションのユースケースを実装
- **Infrastructure層**: データソース、分析ライブラリ、描画ライブラリへのアダプタ
- **Interface層**: GUI（Tkinter）実装

## セットアップ

### 必要要件

- Python 3.10 以上
- pip

### インストール

```bash
# 依存パッケージのインストール
pip install -r requirements.txt

# ディレクトリ作成
mkdir -p data/scatter data/category png logs
```

### 設定ファイル

`config/settings.toml` でアプリケーションの動作をカスタマイズできます。

## 実行

```bash
python main.py
```

## 開発フェーズ

### Phase 1: 基盤構築 ✅（現在）

- ディレクトリ構成確定
- Core / UseCase / Infrastructure の骨格実装
- 設定ファイル読み込み
- Tkinter ウィンドウ起動

### Phase 2: データロード機能（次回）

- CSV読み込み実装
- Repository Pattern 実装
- データ検証とログ出力

### Phase 3: 描画・分析機能

- Analyzer実装（回帰分析）
- Visualizer実装（Matplotlib）
- 散布図描画

### Phase 4: UI操作機能

- カテゴリ選択
- 軸範囲・ラベル設定
- 更新ボタン機能

### Phase 5: 保存・品質向上

- PNG保存
- 例外ハンドリング
- テスト整備

## プロジェクト構造

```
AutoScattering/
├── main.py              # エントリポイント
├── bootstrap.py         # DIコンテナ
├── requirements.txt
├── README.md
├── config/
│   ├── settings.toml
│   └── logging_config.yaml
├── data/                # 入力データ（Git管理外）
├── png/                 # 出力画像（Git管理外）
├── logs/                # ログ（Git管理外）
└── src/
    ├── core/            # ドメインモデル
    ├── usecases/        # ユースケース
    ├── interfaces/      # GUI
    └── infrastructure/  # 外部依存
```

## ライセンス

MIT License