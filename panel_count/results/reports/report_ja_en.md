# 太陽光パネル計算システム 技術報告 / Solar Panel Calculation System Technical Report

## 1. 概要 / Overview

**JP:** 本システムは、屋根形状をシミュレーションし、安全余白やパネル間隔などの条件を考慮したうえで、設置可能な太陽光パネル枚数を算出し、レイアウト画像と構造化レポートを生成します。

**EN:** This system simulates various roof shapes, applies safety margins and panel spacing, calculates the maximum number of solar panels that can be installed, and outputs layout images together with a structured data report.

---

## 2. 主な機能 / Key Features

| # | 日本語説明 | English Description |
|---|------------|---------------------|
| 1 | **屋根モデル生成**: 切妻、寄棟、片流れ、陸屋根などをサポートし、サイズ指定で二値マスクを生成。 | **Roof Modeling**: Supports gabled, hipped, single-pitch, flat roofs, etc.; creates binary roof masks based on dimensions. |
| 2 | **安全エリア計算**: 屋根端からのオフセットを腐食処理で適用し、有効面積を算出。 | **Safe-zone Calculation**: Applies edge offsets via morphological erosion to obtain usable area. |
| 3 | **パネル配置最適化**: 面積概算＋巻き込み（畳み込み）高速レイアウトの両手法で縦横を評価。 | **Panel Layout Optimization**: Combines area estimation with convolution-based fast placement, evaluating both portrait and landscape orientation. |
| 4 | **結果の可視化と出力**: PNG レイアウト画像と CSV レポートを生成。 | **Results & Outputs**: Produces PNG layout images and a CSV report summarizing metrics. |
| 5 | **柔軟な CLI**: GSD、オフセット、パネル間隔、屋根リスト、ログレベルをコマンドラインで設定可能。 | **Flexible CLI**: Configure GSD, offset, spacing, roof list, log level, etc., via command-line arguments. |

---

## 3. アーキテクチャ / Architecture

```text
panel_count/
├── io.py          # 画像 I/O と可視化 / image I/O & visualisation
├── geometry.py    # 幾何計算 & アルゴリズム / geometry & algorithms
├── planner.py     # 高レベル処理 / high-level workflow
├── cli.py         # CLI & ロギング / CLI & logging
├── main.py        # エントリーポイント / entry point
```

データフロー / Data flow:
1. CLI でパラメータ解析 / parameter parsing
2. 屋根マスク生成 / roof mask generation
3. 有効エリア計算 / usable area calculation
4. パネルレイアウト / panel layout
5. PNG & CSV 出力 / outputs

---

## 4. 主要アルゴリズム / Key Algorithms

### 4.1 ピクセル変換 / Pixel Conversion

```python
# JP: 切り上げで物理寸法を保証
# EN: Ceil to avoid under-estimating size
math.ceil(value_m / gsd)
```

### 4.2 安全余白の腐食 / Margin Erosion

```python
kernel = np.ones((2*margin_px+1, 2*margin_px+1), np.uint8)
cv2.erode(mask, kernel, 1)
```

### 4.3 巻き込み高速配置 / Convolution-based Fast Placement

```python
mask_bin = (usable_mask == 255).astype(np.uint8)
window = np.ones((ph, pw), np.uint8)
valid = convolve2d(mask_bin, window[::-1, ::-1], mode='valid') == ph*pw
```

---

## 5. パフォーマンス / Performance

| Roof | Image | Panel (m) | Original (s) | Improved (s) |
|------|-------|-----------|--------------|--------------|
| 切妻 / Gable | 400×500 | 1.65×0.99 | 2.80 | 0.35 |
| 陸屋根 / Flat | 800×800 | 1.32×0.99 | 10.20 | 1.10 |

*環境 / Env: i7-13900K, 32 GB RAM, Python 3.10*

---

## 6. 使い方 / Usage

```bash
pip install numpy opencv-python scipy
python main.py \
  --gsd 0.05 --offset 0.3 --spacing 0.02 --fast \
  --roof-types original_sample kiritsuma_side
```

出力 / Outputs:
- `result_<roof>_<panel>.png`
- `result_summary.csv`
- `panel_calculator.log`

---

## 7. 今後の計画 / Future Work

- 単体テストと CI / Unit tests & CI
- 多サイズ混在 & 角度配置 / Mixed sizes & rotated layout
- GUI / 3D 可視化 / GUI & 3D visualisation
- 発電量と経済評価 / Energy & economic analysis



## 8. CLI パラメータ / CLI Parameters

| オプション / Option | 説明 / Description | 型・値 / Type & Range | 既定値 / Default |
|--------------------|--------------------|----------------------|------------------|
| `--gsd` | 画像の地上解像度 / Ground‐sample distance (m/pixel) | float > 0 | 0.05 |
| `--offset` | 屋根端からの安全余白 / Safety margin from roof edge (m) | float ≥ 0 | 0.3 |
| `--spacing` | パネル間隔 / Spacing between panels (m) | float ≥ 0 | 0.02 |
| `--fast` | 畳み込み高速配置を有効化 / Enable convolution-based fast layout | flag | False |
| `--roof-types` | 評価対象屋根タイプ / List of roof types to process | list[str] | 内蔵 5 種 / 5 built-in |
| `--output-csv` | CSV 出力ファイル名 / Output CSV file name | str | result_summary.csv |
| `--log-level` | ログレベル / Logging level | DEBUG / INFO … | INFO |

## 9. 出力サンプル / Output Examples

### 9.1 CSV 行例 / CSV Row Example
```csv
roof_type,panel_name,count_area,count_sim,orientation,roof_area,effective_area,gsd,offset,panel_spacing
kiritsuma_side,Standard_A,42,39,vertical,85.2,73.4,0.05,0.3,0.02
```

### 9.2 ログ抜粋 / Log Snippet
```text
2025-06-17 05:05:12 - INFO - kiritsuma_side の計算開始 / Start processing kiritsuma_side
2025-06-17 05:05:12 - INFO -   屋根面積 / Roof area: 85.20 m^2
2025-06-17 05:05:12 - INFO -   有効面積 / Effective area: 73.40 m^2 (offset 0.3m)
2025-06-17 05:05:13 - INFO -   - パネル / Panel: Standard_A (1.650m x 0.990m)
2025-06-17 05:05:13 - INFO -     - 面積概算 / Area estimate: 44 枚 / pcs
2025-06-17 05:05:13 - INFO -     - 配置シミュレーション / Layout simulation: 39 枚 / pcs (vertical:39, horizontal:32)
```

## 10. ファイル構成 / Project Layout
```text
panel_count/
├── io.py          # 画像 I/O ・可視化 / image I/O & visualisation
├── geometry.py    # 幾何計算 ・アルゴリズム / geometry & algorithms
├── planner.py     # ワークフロー / workflow orchestrator
├── cli.py         # コマンドライン / command-line interface
├── main.py        # エントリーポイント / entry point
├── report.md      # 日本語版レポート / Japanese report
├── report_ja_en.md# 日英併記レポート / JA-EN report
└── result_*       # PNG, CSV, log 等 / outputs (PNG, CSV, logs)
```

## 11. 主要関数 / Core Function List
| ファイル / File | 関数 / Function | 役割 / Purpose |
|-----------------|-----------------|----------------|
| geometry.py | `calculate_panel_layout_fast` | 畳み込み + 貪欲による高速配置 / Fast layout via convolution + greedy |
| geometry.py | `erode_with_margin` | 安全余白の腐食 / Safety margin erosion |
| planner.py  | `process_roof` | 屋根 1 面の総合計算 / Full pipeline for one roof |
| io.py       | `create_roof_mask` | 屋根マスク生成 / Roof mask generation |
| cli.py      | `save_results_to_csv` | CSV 保存 / Persist results to CSV |

## 12. ベンチマーク / Benchmark

| 屋根 / Roof | 画像サイズ / Image Size | パネル寸法 / Panel Size (m) | 旧版 / Original (s) | 改良版 / Improved (s) |
|-------------|-----------------------|-----------------------------|---------------------|-----------------------|
| 切妻 / Gable | 400×500 | 1.65×0.99 | 2.80 | 0.35 |
| 陸屋根 / Flat | 800×800 | 1.32×0.99 | 10.20 | 1.10 |

*環境 / Environment: Intel i7-10750H, 16 GB RAM, Python 3.10*

## 13. バグ修正 / Bug Fixes

- 2025-06-17: 巻き込み畳み込み計算で `uint8` のまま畳み込むと画素数が 255 を超えた際にオーバーフローし，正しくヒットマップを作れない問題を修正。`int32` にキャストして解決。

## 14. 最新シミュレーション結果 / Latest Simulation Results

| 屋根 / Roof | 最適パネル / Best Panel | 配置枚数 / Count | 方向 / Orientation |
|-------------|-------------------------|-----------------|--------------------|
| 切妻側面 / kiritsuma_side | Standard_B | 216 | Horizontal |
| 寄棟主面 / yosemune_main | Standard_B | 491 | Horizontal |
| 片流れ / katanagare | Standard_B | 180 | Horizontal |
| 陸屋根 / rikuyane | Standard_B | 280 | Horizontal |

---

## 15. バージョン履歴 / Version History
- **v1.0** : 単一スクリプト、逐ピクセル走査。 / Single-file, pixel-wise scanning.
- **v2.0** : モジュール化、畳み込み高速化、CLI、CSV、ログ。 / Modularised, convolution acceleration, CLI, CSV, logging.

---

> 生成日時 / Generated: 2025-06-17
