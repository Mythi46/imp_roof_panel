# 太陽光パネル計算システム トラブルシューティング / Solar Panel Calculation System Troubleshooting

## 🚨 概要 / Overview

このドキュメントは、太陽光パネル配置計算システムでよく発生する問題とその解決方法を説明します。

This document explains common issues that occur in the solar panel layout calculation system and their solutions.

## 📋 目次 / Table of Contents

1. [インストール問題 / Installation Issues](#installation-issues)
2. [実行時エラー / Runtime Errors](#runtime-errors)
3. [API関連問題 / API Related Issues](#api-related-issues)
4. [パフォーマンス問題 / Performance Issues](#performance-issues)
5. [統合問題 / Integration Issues](#integration-issues)
6. [ログ分析 / Log Analysis](#log-analysis)
7. [メンテナンス / Maintenance](#maintenance)

## 🔧 インストール問題 / Installation Issues

### 1. 依存関係エラー / Dependency Errors

#### 問題: OpenCV インストールエラー
```bash
ERROR: Could not install opencv-python
```

**解決方法**:
```bash
# システムの更新
pip install --upgrade pip setuptools wheel

# OpenCVの個別インストール
pip install opencv-python-headless

# または conda使用
conda install opencv
```

#### 問題: SciPy インストールエラー
```bash
ERROR: Failed building wheel for scipy
```

**解決方法**:
```bash
# 必要なシステムライブラリのインストール (Ubuntu/Debian)
sudo apt-get install python3-dev build-essential

# または conda使用
conda install scipy

# または pre-compiled wheel使用
pip install --only-binary=all scipy
```

#### 問題: Flask インストール後の起動エラー
```bash
ModuleNotFoundError: No module named 'flask'
```

**解決方法**:
```bash
# 仮想環境の確認
which python
which pip

# 正しい環境でのインストール
pip install flask requests

# 環境変数の確認
echo $PYTHONPATH
```

### 2. Python バージョン問題

#### 問題: Python 3.7以下での実行エラー
```bash
SyntaxError: invalid syntax
```

**解決方法**:
```bash
# Pythonバージョン確認
python --version

# Python 3.8+ のインストール
# Ubuntu/Debian:
sudo apt-get install python3.9

# macOS (Homebrew):
brew install python@3.9

# Windows: 公式サイトからダウンロード
```

## ⚠️ 実行時エラー / Runtime Errors

### 1. メモリ関連エラー

#### 問題: メモリ不足エラー
```bash
MemoryError: Unable to allocate array
```

**解決方法**:
```bash
# 画像サイズの縮小
python main.py --dimensions 200 300

# バッチサイズの調整
python main.py --roof-types kiritsuma_side  # 一度に1つずつ処理

# システムメモリの確認
free -h  # Linux
vm_stat  # macOS
```

#### 問題: 大画像処理でのクラッシュ
```python
cv2.error: OpenCV(4.5.0) error
```

**解決方法**:
```python
# 画像サイズ制限の追加
def load_roof_mask_from_image(image_path, target_dimensions=None):
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    
    # 最大サイズ制限
    max_size = 2000
    if img.shape[0] > max_size or img.shape[1] > max_size:
        scale = max_size / max(img.shape)
        new_size = (int(img.shape[1] * scale), int(img.shape[0] * scale))
        img = cv2.resize(img, new_size)
```

### 2. 計算エラー

#### 問題: GSD値エラー
```bash
ValueError: GSD must be positive, got: 0
```

**解決方法**:
```bash
# 正しいGSD値の指定
python main.py --gsd 0.05  # 5cm/pixel

# 有効範囲: 0.01 - 0.5
python main.py --gsd 0.03  # 3cm/pixel (高解像度)
python main.py --gsd 0.1   # 10cm/pixel (低解像度)
```

#### 問題: パネルサイズエラー
```bash
ValueError: Panel dimensions must be positive
```

**解決方法**:
```python
# パネル仕様の確認
panel_options = {
    "Sharp_NQ-256AF": (1.318, 0.990),  # 正: (長さ, 幅)
    "Invalid_Panel": (0, 1.0),         # 誤: 0サイズ
}

# 修正版
panel_options = {
    "Sharp_NQ-256AF": (1.318, 0.990),
    "Custom_Panel": (1.5, 1.0),       # 正: 正の値
}
```

### 3. ファイル関連エラー

#### 問題: 画像ファイル読み込みエラー
```bash
FileNotFoundError: Image file not found
```

**解決方法**:
```bash
# ファイルパスの確認
ls -la sample/
ls -la *.png

# 相対パスの使用
python main.py --roof-types sample/roof_image.png

# 絶対パスの使用
python main.py --roof-types /full/path/to/image.png
```

#### 問題: 権限エラー
```bash
PermissionError: [Errno 13] Permission denied
```

**解決方法**:
```bash
# ファイル権限の確認
ls -la result_summary.csv

# 権限の修正
chmod 644 result_summary.csv
chmod 755 .

# 別の出力ディレクトリの指定
python main.py --output-csv /tmp/results.csv
```

## 🌐 API関連問題 / API Related Issues

### 1. サーバー起動問題

#### 問題: ポート競合エラー
```bash
OSError: [Errno 98] Address already in use
```

**解決方法**:
```bash
# ポート使用状況の確認
netstat -tulpn | grep :8001
lsof -i :8001

# プロセスの終了
kill -9 <PID>

# 別ポートの使用
export FLASK_RUN_PORT=8002
python api_integration.py
```

#### 問題: Flask起動エラー
```bash
ImportError: No module named 'flask'
```

**解決方法**:
```bash
# Flask環境の確認
pip list | grep -i flask

# Flaskの再インストール
pip uninstall flask
pip install flask==2.0.3

# 開発サーバーの起動確認
python -c "from flask import Flask; print('Flask OK')"
```

### 2. API通信問題

#### 問題: 接続タイムアウト
```bash
requests.exceptions.ConnectTimeout
```

**解決方法**:
```python
# タイムアウト値の調整
response = requests.post(url, json=data, timeout=60)

# リトライ機構の追加
import time
for attempt in range(3):
    try:
        response = requests.post(url, json=data, timeout=30)
        break
    except requests.exceptions.Timeout:
        if attempt < 2:
            time.sleep(5)
            continue
        raise
```

#### 問題: Base64デコードエラー
```bash
binascii.Error: Invalid base64-encoded string
```

**解決方法**:
```python
# Base64データの検証
def validate_base64_image(b64_string):
    try:
        # data URI prefixの除去
        if ',' in b64_string:
            b64_string = b64_string.split(',')[1]
        
        # パディングの修正
        missing_padding = len(b64_string) % 4
        if missing_padding:
            b64_string += '=' * (4 - missing_padding)
        
        # デコードテスト
        base64.b64decode(b64_string)
        return True
    except Exception:
        return False
```

### 3. JSON関連エラー

#### 問題: JSON解析エラー
```bash
json.decoder.JSONDecodeError: Expecting value
```

**解決方法**:
```python
# レスポンス内容の確認
print(f"Status Code: {response.status_code}")
print(f"Response Text: {response.text}")

# Content-Typeの確認
print(f"Content-Type: {response.headers.get('content-type')}")

# 安全なJSON解析
try:
    result = response.json()
except json.JSONDecodeError as e:
    print(f"JSON decode error: {e}")
    print(f"Raw response: {response.text}")
```

## 🚀 パフォーマンス問題 / Performance Issues

### 1. 処理速度の改善

#### 問題: 計算が遅い
```bash
# 大画像での処理時間: 30秒以上
```

**解決方法**:
```bash
# 高速アルゴリズムの使用
python main.py --fast

# 画像サイズの最適化
python main.py --dimensions 400 500

# 並列処理の活用
python main.py --roof-types type1 &
python main.py --roof-types type2 &
wait
```

#### 問題: メモリ使用量が多い
```bash
# メモリ使用量: 1GB以上
```

**解決方法**:
```python
# メモリ効率的な処理
def process_large_image(image_path):
    # 画像を分割して処理
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    # 512x512のタイルに分割
    tile_size = 512
    results = []
    
    for y in range(0, h, tile_size):
        for x in range(0, w, tile_size):
            tile = img[y:y+tile_size, x:x+tile_size]
            result = process_tile(tile)
            results.append(result)
    
    return combine_results(results)
```

### 2. API応答時間の改善

#### 問題: API応答が遅い
```bash
# 応答時間: 10秒以上
```

**解決方法**:
```python
# 非同期処理の実装
from concurrent.futures import ThreadPoolExecutor

def process_segments_async(segments):
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = []
        for segment in segments:
            future = executor.submit(process_single_segment, segment)
            futures.append(future)
        
        results = []
        for future in futures:
            results.append(future.result())
    
    return results
```

## 🔗 統合問題 / Integration Issues

### 1. 屋根検出システムとの連携

#### 問題: 屋根検出APIへの接続失敗
```bash
ConnectionError: Failed to establish connection
```

**解決方法**:
```bash
# サービス状態の確認
curl http://localhost:8000/docs
curl http://localhost:8000/health

# Docker環境の確認
docker-compose ps
docker-compose logs roof-detection

# ネットワーク設定の確認
docker network ls
docker network inspect <network_name>
```

#### 問題: データ形式の不一致
```bash
KeyError: 'segments'
```

**解決方法**:
```python
# データ形式の検証
def validate_roof_segments(data):
    required_fields = ['segments']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    for i, segment in enumerate(data['segments']):
        if 'mask_base64' not in segment:
            raise ValueError(f"Segment {i} missing mask_base64")
    
    return True

# 使用例
try:
    validate_roof_segments(request_data)
    result = process_roof_segments(request_data)
except ValueError as e:
    return {"error": str(e)}, 400
```

### 2. Docker環境での問題

#### 問題: コンテナ間通信エラー
```bash
requests.exceptions.ConnectionError: ('Connection aborted.')
```

**解決方法**:
```yaml
# docker-compose.yml の修正
version: '3.8'
services:
  roof-detection:
    ports:
      - "8000:8000"
    networks:
      - panel-network
  
  panel-calculation:
    ports:
      - "8001:8001"
    networks:
      - panel-network
    environment:
      - ROOF_API_URL=http://roof-detection:8000

networks:
  panel-network:
    driver: bridge
```

## 📊 ログ分析 / Log Analysis

### 1. ログレベルの設定

```bash
# デバッグログの有効化
python main.py --log-level DEBUG

# ログファイルの確認
tail -f panel_calculator.log

# エラーログの抽出
grep ERROR panel_calculator.log
grep -A 5 -B 5 "Exception" panel_calculator.log
```

### 2. 一般的なログパターン

#### 正常処理:
```
2025-07-02 10:30:00 - INFO - --- kiritsuma_side の計算開始 ---
2025-07-02 10:30:01 - INFO - 屋根面積: 60.00 m^2
2025-07-02 10:30:01 - INFO - 有効面積: 55.20 m^2
2025-07-02 10:30:02 - INFO - 配置シミュレーション: 42 枚
```

#### エラー処理:
```
2025-07-02 10:30:00 - ERROR - Failed to load image: sample/missing.png
2025-07-02 10:30:00 - WARNING - 'invalid_roof' は空のマスクのためスキップします
2025-07-02 10:30:00 - ERROR - GSD must be positive, got: -0.05
```

## 🔧 メンテナンス / Maintenance

### 1. 定期メンテナンス

#### 依存関係の更新:
```bash
# 月次更新
pip list --outdated
pip install --upgrade opencv-python numpy scipy flask

# セキュリティ更新の確認
pip audit
```

#### ログファイルの管理:
```bash
# ログローテーション
logrotate /etc/logrotate.d/panel-calculator

# 古いログの削除
find logs/ -name "*.log" -mtime +30 -delete
```

### 2. パフォーマンス監視

#### システムリソース:
```bash
# CPU/メモリ使用量
top -p $(pgrep -f "python.*api_integration")
htop

# ディスク使用量
df -h
du -sh results/
```

#### API監視:
```bash
# レスポンス時間の測定
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8001/health

# 同時接続数の監視
netstat -an | grep :8001 | wc -l
```

### 3. バックアップとリストア

#### 設定ファイル:
```bash
# 設定のバックアップ
tar -czf config-backup-$(date +%Y%m%d).tar.gz \
    requirements.txt \
    docker-compose.integration.yml \
    *.py

# 結果データのバックアップ
tar -czf results-backup-$(date +%Y%m%d).tar.gz results/
```

## 📞 サポート / Support

### 問題報告時の情報収集:

1. **システム情報**:
   ```bash
   python --version
   pip list
   uname -a  # Linux/macOS
   ```

2. **エラーログ**:
   ```bash
   tail -100 panel_calculator.log
   ```

3. **再現手順**:
   - 実行したコマンド
   - 入力データ
   - 期待される結果
   - 実際の結果

### 連絡先:
- **GitHub Issues**: [プロジェクトリポジトリ]
- **技術サポート**: [開発チーム]
- **ドキュメント**: [README.md](README.md)

---

**最終更新 / Last Updated**: 2025-07-02  
**バージョン / Version**: 1.2.0
