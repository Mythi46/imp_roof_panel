# 🏠 屋根検出プロジェクト (Roof Detection Project)

## 📋 プロジェクト概要

これはYOLOv8ベースの屋根セグメンテーション検出プロジェクトで、航空画像内の異なる種類の屋根を識別・分割することに特化しています。

### 🎯 検出クラス
- `Baren-Land`: 裸地
- `farm`: 農地
- `rice-fields`: 水田
- `roof`: 屋根

## 📁 プロジェクト構造

```
roof-detection/
├── data/                    # データディレクトリ
│   ├── raw/                # 生データ
│   └── processed/          # 処理済みデータ
├── models/                 # モデルディレクトリ
│   ├── pretrained/        # 事前訓練モデル
│   └── trained/           # 訓練済みモデル
├── results/               # 結果ディレクトリ
│   ├── training/         # 訓練結果
│   ├── evaluation/       # 評価結果
│   └── visualization/    # 可視化結果
├── scripts/              # スクリプトディレクトリ
├── config/               # 設定ファイル
├── notebooks/            # Jupyterノートブック
└── archive/              # アーカイブファイル
```

## 🚀 クイックスタート

### 1. 環境設定
```bash
pip install -r requirements.txt
```

### 2. データ準備
データセットは `data/raw/new-2-1/` ディレクトリに含まれています。

### 3. 訓練開始
```bash
python train_expert_correct_solution.py
```

### 4. 結果可視化
```bash
python generate_visualization_results.py
```

## 📊 訓練設定

現在使用中のエキスパート改良設定：
- **モデル**: YOLOv8m-seg (セグメンテーションモデル)
- **画像サイズ**: 768x768
- **バッチサイズ**: 16
- **学習率**: 0.005 (AdamWオプティマイザー)
- **損失重み**: cls=1.0, box=7.5, dfl=1.5
- **データ拡張**: copy_paste=0.5, mosaic=0.3, mixup=0.1

## 🔧 重要な注意事項

### YOLOv8クラス重み問題
⚠️ **重要な発見**: YOLOv8は`class_weights`パラメータをサポートしていません！

**解決策**:
1. 損失関数重みの調整 (cls, box, dfl)
2. データ拡張戦略によるクラスバランス調整
3. 訓練戦略の最適化 (学習率、エポック数など)

## 📈 性能最適化

- コサインアニーリング学習率スケジューリングの使用
- クラス不均衡改善のための分類損失重み増加
- 対象特化データ拡張戦略
- 過学習防止のための早期停止メカニズム

## 📝 更新履歴

- **2025-07-29**: プロジェクト再構築とクリーンアップ
- **2025-07-29**: YOLOv8クラス重み問題の修正
- **2025-07-29**: 訓練設定とデータ拡張戦略の最適化

## 🤝 貢献

このプロジェクトの改善のためのIssueやPull Requestを歓迎します！

## 📄 ライセンス

MIT License
