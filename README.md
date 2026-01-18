# Auto Scattering Ver 6.0 - セットアップガイド

## 📁 ディレクトリ構成

プロジェクトを以下の構成で作成してください：

```
AutoScattering/
├── main.py                 # 起動ファイル
├── requirements.txt        # 依存ライブラリ
├── README.md              # このファイル
│
├── gui/
│   ├── __init__.py        # 空ファイル
│   └── main_window.py     # メインウィンドウ
│
├── logic/
│   ├── __init__.py        # 空ファイル
│   ├── data_loader.py     # データ読み込み
│   ├── analyzer.py        # 回帰分析
│   └── plotter.py         # 散布図描画
│
├── data/
│   ├── category.csv       # カテゴリデータ
│   └── scatter.csv        # サンプルデータ
│
└── output/                # 画像出力先（自動作成）
```

## 🚀 インストール手順

### 1. Python環境の確認
```bash
python --version  # Python 3.8以上が必要
```

### 2. 依存ライブラリのインストール(必要な場合)
※python main.pyで仮想環境を作成
```bash
pip install -r requirements.txt
```

### 3. `__init__.py` の作成
```bash
# Windows (PowerShell)
New-Item gui/__init__.py
New-Item logic/__init__.py

# Mac/Linux
touch gui/__init__.py
touch logic/__init__.py
```

### 4. サンプルデータの配置
`data/scatter.csv` を配置してください。

## ▶️ 起動方法

```bash
python main.py
```

## 📊 使い方

### 基本操作
1. **起動時**: `data/scatter.csv` を自動読み込み
2. **更新ボタン**: 設定を反映して再描画
3. **保存ボタン**: `output/` に画像を保存

### データファイル選択
- 「📂 散布図データを選択」: メインデータ（X, Y列が必須）
- 「📂 カテゴリデータを選択」: カテゴリ情報（オプション）

### 軸範囲設定
- X軸/Y軸の最小値・最大値を入力
- 空欄にすると自動スケール

### 表示設定
- **回帰線を表示**: チェックで回帰線のON/OFF
- **カテゴリ**: ドロップダウンでカテゴリ列を選択

## 📋 CSVフォーマット

### scatter.csv（必須）
```csv
Label,X,Y
Sample1,10.5,20.3
Sample2,15.2,25.8
```

- `X`, `Y` 列は必須（数値）
- `Label` 列は任意の名前でOK

### category.csv（オプション）
```csv
Label,Category1,Category2,...
Sample1,GroupA,Group1,...
Sample2,GroupB,Group2,..
```

- `Label` 列でscatter.csvと結合

## 🔧 トラブルシューティング

### エラー: モジュールが見つからない
```bash
pip install pandas matplotlib scipy
```

### エラー: `__init__.py` がない
```bash
# gui/ と logic/ の下に空の __init__.py を作成
touch gui/__init__.py logic/__init__.py
```

### 日本語が文字化け
- Windows: システムのフォント設定を確認
- Mac: 自動で Hiragino Sans を使用
- Linux: 日本語フォントをインストール

### データが読み込めない
- CSVファイルに `X`, `Y` 列があるか確認
- エンコーディングは UTF-8 または CP932
- `app.log` でエラー内容を確認

## 📝 ログ確認

`app.log` ファイルに詳細なログが出力されます。

```bash
# ログの確認
cat app.log
# または
notepad app.log  # Windows
```

## 🎨 カスタマイズ

### 配色変更
`logic/plotter.py` の `_draw_simple()` で色を変更：
```python
ax.scatter(..., color='#FF5722')  # オレンジ色
```

### フォントサイズ変更
`logic/plotter.py` の `draw()` で調整：
```python
ax.set_xlabel(x_col, fontsize=14)  # 12 → 14
```

## 🆘 サポート

問題が発生した場合：
1. `app.log` を確認
2. エラーメッセージをコピー
3. 開発者に問い合わせ

---

**開発**: Auto Scattering Ver 6.0  
**ライセンス**: MIT
