# 自動散布図生成アプリケーション（Auto Scattering）要件定義書 Ver 5.0

---

## 1. 概要

### 1.1 システム名称

**自動散布図生成アプリケーション（Auto Scattering）**

### 1.2 目的

CSVデータから散布図を描画し、カテゴリ別の可視化および回帰分析を **GUI操作のみ** で行う。

### 1.3 設計思想

* **クリーンアーキテクチャの徹底**
  GUI・データソース・分析ライブラリへの依存を排除し、ビジネスロジック（Core / UseCase）の純粋性を保つ。
* **Open / Closed Principle（OCP）**
  分析アルゴリズムやデータソース形式の追加に対し、既存コードを修正せず「拡張」で対応可能とする。

---

## 2. アーキテクチャ設計方針

本システムは **責務と依存方向** に基づくレイヤードアーキテクチャを採用する。

### 2.1 ディレクトリ構成

```text
AutoScattering/
│
├── main.py                    # アプリ起動エントリポイント
├── bootstrap.py               # DIコンテナ構成・依存解決・インスタンス生成
├── requirements.txt           # 依存ライブラリ
├── README.md
│
├── config/
│   ├── settings.toml          # アプリ設定
│   └── logging_config.yaml    # ログ設定
│
├── data/                      # 入力データ（Git管理外）
│   ├── scatter/
│   │   └── scatter_A.csv      # 複数CSV配置を想定
│   │   └── ...        
│   └── category/              # 複数CSV配置を想定
│       └── category_A.csv
│       └── ...        
│
├── png/                       # 画像出力先（Git管理外）
├── logs/                      # ログ出力先（Git管理外）
│
├── src/
│   ├── core/                  # Core層（依存なし）
│   │   ├── entities.py        # ScatterPoint, AnalysisResult, RegressionLine
│   │   ├── exceptions.py      # DataLoadError, AnalysisError
│   │   └── interfaces.py      # IRepository, IAnalyzer, IVisualizer
│   │
│   ├── usecases/              # UseCase層
│   │   ├── load_data.py
│   │   ├── analyze.py
│   │   └── save_image.py
│   │
│   ├── interfaces/            # Interface層（Adapter）
│   │   └── gui/
│   │       ├── windows.py     # MainView (Tkinter)
│   │       ├── components.py  # Widget部品
│   │       └── view_models.py # ViewModel
│   │
│   └── infrastructure/        # Infrastructure層
│       ├── config.py
│       ├── repositories.py    # CSV読み込み（Pandas）
│       ├── analysis.py        # 分析（Scipy）
│       ├── visualization.py   # 描画（Matplotlib）
│       └── file_system.py
│
└── tests/                     # テストコード
```

### 2.2 依存関係のルール

* **Dependency Rule**
  `Infrastructure → Interfaces → UseCases → Core`
* **抽象依存**
  UseCase層は `IAnalyzer` 等の抽象にのみ依存する。
* **DI（Dependency Injection）**
  `bootstrap.py` にて具象クラスを生成し、UseCaseへ注入する。

---

## 3. 入力データ仕様とアクセス（Repository Pattern）

### 3.1 データソース

* **Main Data**: `data/scatter/*.csv`（ラベル, X, Y）
* **Category Data**: `data/category/*.csv`（ラベル, , , , ,）

**Ver 5.0 仕様**

* `data/category/` 配下の CSV を走査して読み込む
* 当面は以下のいずれかを使用

  * 最初に見つかった 1 ファイル
  * 設定ファイルで指定されたファイル

### 3.2 結合・処理ルール（Infrastructure責務）

* Repository 実装: `ICategoryRepository`
* 結合方法: scatter を主とした **Left Join**
* エンコーディング: `utf-8 → cp932` フォールバック
* クレンジング:

  * 数値変換不可行はドロップ
  * WARNING ログを出力

---

## 4. 機能要件（Use Cases）

### 4.1 UC-01: データのロード

* **トリガー**: 起動時 / 再読込ボタン
* **処理**:

  * `IScatterRepository`, `ICategoryRepository` 経由で取得
  * `List[ScatterPoint]` に変換

### 4.2 UC-02: 散布図の更新と分析

#### 分析の抽象化（IAnalyzer）

```python
analyze(points: List[ScatterPoint]) -> AnalysisResult
```

* 実装: `ScipyAnalyzer`（線形回帰）
* 将来拡張:

  * RobustAnalyzer
  * NonLinearAnalyzer

#### カテゴリ選択

* 「なし」またはカテゴリ列を選択

#### 描画（IVisualizer）

* 日本語フォント自動解決
* 透過度・配色は設定ファイル準拠

### 4.3 UC-03: 画像の保存

* 出力形式: PNG
* 命名規則: `XLabel_YLabel_Category.png`
* ファイル名はサニタイズ処理を行う

---

## 5. UI / 画面仕様（Interface Layer）

### 5.1 アーキテクチャ（MVVM / MVP）

**ViewModel**

* 許可:

  * UseCase 呼び出し
  * Entity → 表示用データ変換
* 禁止:

  * 数値計算
  * ファイルI/O
  * Matplotlib API の直接操作

**View**

* Tkinter Widget の配置とイベント定義のみ

### 5.2 エラーハンドリング

| レベル     | 内容             | UI挙動         |
| ------- | -------------- | ------------ |
| ERROR   | 必須ファイル欠落・致命的例外 | ダイアログ表示 + ログ |
| WARNING | 一部欠損・代替処理      | ログのみ         |

### 5.3 画面レイアウト

* 左ペイン（可変）: グラフ描画エリア
* 右ペイン（固定）: 操作パネル・情報表示
*グラフ描写詳細

* 情報表示:

  * 回帰式 `y = ax + b`
  * 決定係数 `R²`

---

## 6. 非機能要件・設定

### 6.1 設定ファイル（settings.toml）

```toml
[paths]
input_dir = "./data"
output_dir = "./png"
font_path = ""

[data]
encodings = ["utf-8", "cp932"]

[plot]
default_color = "blue"
font_size = 12
alpha = 0.7
figure_size = [10, 8]

[ui]
window_title = "Auto Scattering Ver 5.0"
initial_geometry = "1200x800"
```

### 6.2 ログ設計

* INFO: 操作履歴、ロード件数
* WARNING: データドロップ、フォールバック
* ERROR: 例外・スタックトレース

### 6.3 品質特性

* **Testability**: Core / UseCase は GUI・FS 非依存でテスト可能
* **Robustness**: 異常データ混入時も可能な限り描画を継続
