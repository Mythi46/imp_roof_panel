# 太陽光パネル計算システム メンテナンスガイド / Solar Panel Calculation System Maintenance Guide

## 📋 概要 / Overview

このドキュメントは、太陽光パネル配置計算システムの継続的な運用とメンテナンスに関するガイドラインを提供します。

This document provides guidelines for the continuous operation and maintenance of the solar panel layout calculation system.

## 🗓️ メンテナンススケジュール / Maintenance Schedule

### 日次 / Daily
- [ ] システム稼働状況確認
- [ ] ログファイル確認
- [ ] API応答時間監視
- [ ] エラー率チェック

### 週次 / Weekly
- [ ] パフォーマンス指標レビュー
- [ ] ディスク使用量確認
- [ ] バックアップ検証
- [ ] セキュリティログ確認

### 月次 / Monthly
- [ ] 依存関係更新
- [ ] パフォーマンステスト実行
- [ ] ドキュメント更新
- [ ] 容量計画見直し

### 四半期 / Quarterly
- [ ] セキュリティ監査
- [ ] 災害復旧テスト
- [ ] アーキテクチャレビュー
- [ ] ユーザーフィードバック分析

## 🔍 監視項目 / Monitoring Items

### 1. システムヘルス / System Health

#### CPU使用率監視
```bash
#!/bin/bash
# cpu_monitor.sh
CPU_THRESHOLD=80
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)

if (( $(echo "$CPU_USAGE > $CPU_THRESHOLD" | bc -l) )); then
    echo "WARNING: High CPU usage: ${CPU_USAGE}%"
    # アラート送信
    curl -X POST "https://hooks.slack.com/..." \
         -d "{\"text\":\"High CPU usage: ${CPU_USAGE}%\"}"
fi
```

#### メモリ使用量監視
```bash
#!/bin/bash
# memory_monitor.sh
MEMORY_THRESHOLD=85
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')

if (( $(echo "$MEMORY_USAGE > $MEMORY_THRESHOLD" | bc -l) )); then
    echo "WARNING: High memory usage: ${MEMORY_USAGE}%"
    # メモリダンプの取得
    ps aux --sort=-%mem | head -10 > /tmp/memory_usage.log
fi
```

#### ディスク容量監視
```bash
#!/bin/bash
# disk_monitor.sh
DISK_THRESHOLD=90
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)

if [ "$DISK_USAGE" -gt "$DISK_THRESHOLD" ]; then
    echo "WARNING: High disk usage: ${DISK_USAGE}%"
    # 古いファイルの削除
    find /tmp -type f -mtime +7 -delete
    find results/logs -name "*.log" -mtime +30 -delete
fi
```

### 2. API監視 / API Monitoring

#### ヘルスチェック
```bash
#!/bin/bash
# health_check.sh
API_URL="http://localhost:8001/health"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL")

if [ "$RESPONSE" != "200" ]; then
    echo "ERROR: API health check failed. Status: $RESPONSE"
    # サービス再起動
    systemctl restart panel-calculator
fi
```

#### レスポンス時間測定
```bash
#!/bin/bash
# response_time_check.sh
API_URL="http://localhost:8001/health"
RESPONSE_TIME=$(curl -w "%{time_total}" -o /dev/null -s "$API_URL")
THRESHOLD=2.0

if (( $(echo "$RESPONSE_TIME > $THRESHOLD" | bc -l) )); then
    echo "WARNING: Slow API response: ${RESPONSE_TIME}s"
    # パフォーマンス調査の開始
    top -bn1 > /tmp/performance_snapshot.log
fi
```

### 3. ログ監視 / Log Monitoring

#### エラーログ監視
```bash
#!/bin/bash
# error_log_monitor.sh
LOG_FILE="panel_calculator.log"
ERROR_COUNT=$(grep -c "ERROR" "$LOG_FILE" | tail -1)
WARNING_COUNT=$(grep -c "WARNING" "$LOG_FILE" | tail -1)

echo "Errors: $ERROR_COUNT, Warnings: $WARNING_COUNT"

# 新しいエラーの検出
if [ "$ERROR_COUNT" -gt 0 ]; then
    echo "Recent errors found:"
    grep "ERROR" "$LOG_FILE" | tail -5
fi
```

## 🔧 定期メンテナンス作業 / Regular Maintenance Tasks

### 1. 依存関係管理 / Dependency Management

#### 月次更新手順
```bash
#!/bin/bash
# monthly_update.sh

echo "=== Monthly Dependency Update ==="

# 1. 現在の依存関係をバックアップ
pip freeze > requirements_backup_$(date +%Y%m%d).txt

# 2. セキュリティ脆弱性チェック
pip audit

# 3. 更新可能なパッケージの確認
pip list --outdated

# 4. 重要なパッケージの更新
pip install --upgrade opencv-python numpy scipy flask requests

# 5. テストの実行
python -m pytest tests/ -v

# 6. 更新後の依存関係を記録
pip freeze > requirements_updated_$(date +%Y%m%d).txt

echo "Update completed. Please review test results."
```

#### 依存関係の脆弱性スキャン
```bash
#!/bin/bash
# security_scan.sh

echo "=== Security Vulnerability Scan ==="

# 1. pip audit実行
pip audit --format=json > security_audit_$(date +%Y%m%d).json

# 2. 結果の解析
VULNERABILITIES=$(pip audit --format=json | jq '.vulnerabilities | length')

if [ "$VULNERABILITIES" -gt 0 ]; then
    echo "WARNING: $VULNERABILITIES vulnerabilities found"
    pip audit
    
    # 緊急度の高い脆弱性の確認
    HIGH_SEVERITY=$(pip audit --format=json | jq '.vulnerabilities[] | select(.severity == "high") | length')
    if [ "$HIGH_SEVERITY" -gt 0 ]; then
        echo "CRITICAL: High severity vulnerabilities detected!"
        # 緊急アラート送信
    fi
fi
```

### 2. データベース・ファイル管理 / Database & File Management

#### ログローテーション
```bash
#!/bin/bash
# log_rotation.sh

LOG_DIR="results/logs"
ARCHIVE_DIR="$LOG_DIR/archive"
RETENTION_DAYS=90

# アーカイブディレクトリの作成
mkdir -p "$ARCHIVE_DIR"

# 30日以上古いログファイルをアーカイブ
find "$LOG_DIR" -name "*.log" -mtime +30 -not -path "$ARCHIVE_DIR/*" | while read logfile; do
    filename=$(basename "$logfile")
    gzip "$logfile"
    mv "${logfile}.gz" "$ARCHIVE_DIR/"
    echo "Archived: $filename"
done

# 90日以上古いアーカイブを削除
find "$ARCHIVE_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Log rotation completed"
```

#### 結果データのクリーンアップ
```bash
#!/bin/bash
# cleanup_results.sh

RESULTS_DIR="results"
TEMP_DIR="/tmp/panel_calc"
RETENTION_DAYS=30

echo "=== Results Data Cleanup ==="

# 1. 一時ファイルの削除
rm -rf "$TEMP_DIR"/*

# 2. 古い可視化画像の削除
find "$RESULTS_DIR/visualizations" -name "*.png" -mtime +$RETENTION_DAYS -delete

# 3. 古いCSVファイルのアーカイブ
find "$RESULTS_DIR/csv_data" -name "*.csv" -mtime +$RETENTION_DAYS | while read csvfile; do
    gzip "$csvfile"
    echo "Compressed: $(basename "$csvfile")"
done

# 4. ディスク使用量の確認
echo "Current disk usage:"
du -sh "$RESULTS_DIR"/*
```

### 3. パフォーマンス最適化 / Performance Optimization

#### データベース最適化（将来の拡張用）
```bash
#!/bin/bash
# db_optimization.sh

echo "=== Database Optimization ==="

# SQLiteデータベースがある場合の最適化例
if [ -f "panel_calc.db" ]; then
    echo "Optimizing SQLite database..."
    sqlite3 panel_calc.db "VACUUM;"
    sqlite3 panel_calc.db "ANALYZE;"
    echo "Database optimization completed"
fi

# インデックスの再構築
# sqlite3 panel_calc.db "REINDEX;"
```

#### キャッシュクリア
```bash
#!/bin/bash
# cache_cleanup.sh

echo "=== Cache Cleanup ==="

# 1. Pythonキャッシュの削除
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# 2. 一時ファイルの削除
rm -rf /tmp/panel_calc_*

# 3. システムキャッシュの確認（Linux）
if command -v sync >/dev/null 2>&1; then
    sync
    echo 3 > /proc/sys/vm/drop_caches 2>/dev/null || true
fi

echo "Cache cleanup completed"
```

## 📊 パフォーマンス監視 / Performance Monitoring

### 1. ベンチマークテスト
```python
#!/usr/bin/env python3
# benchmark_test.py

import time
import psutil
import requests
import numpy as np
from datetime import datetime

def benchmark_api_performance():
    """API パフォーマンステスト"""
    url = "http://localhost:8001/health"
    response_times = []
    
    print("=== API Performance Benchmark ===")
    
    for i in range(10):
        start_time = time.time()
        response = requests.get(url)
        end_time = time.time()
        
        response_time = end_time - start_time
        response_times.append(response_time)
        
        print(f"Request {i+1}: {response_time:.3f}s (Status: {response.status_code})")
    
    avg_time = np.mean(response_times)
    max_time = np.max(response_times)
    min_time = np.min(response_times)
    
    print(f"\nResults:")
    print(f"Average: {avg_time:.3f}s")
    print(f"Min: {min_time:.3f}s")
    print(f"Max: {max_time:.3f}s")
    
    # パフォーマンス基準のチェック
    if avg_time > 1.0:
        print("WARNING: Average response time exceeds 1 second")
    
    return {
        'timestamp': datetime.now().isoformat(),
        'avg_response_time': avg_time,
        'max_response_time': max_time,
        'min_response_time': min_time
    }

def benchmark_calculation_performance():
    """計算パフォーマンステスト"""
    from geometry import calculate_panel_layout_fast
    
    print("=== Calculation Performance Benchmark ===")
    
    # テストデータの生成
    mask_sizes = [(400, 500), (800, 1000), (1200, 1500)]
    panel_size = (50, 80)
    
    results = []
    
    for size in mask_sizes:
        mask = np.ones(size, dtype=np.uint8) * 255
        
        start_time = time.time()
        count, positions = calculate_panel_layout_fast(mask, panel_size[0], panel_size[1])
        end_time = time.time()
        
        calc_time = end_time - start_time
        
        print(f"Size {size}: {calc_time:.3f}s ({count} panels)")
        
        results.append({
            'size': size,
            'calculation_time': calc_time,
            'panel_count': count
        })
    
    return results

if __name__ == "__main__":
    # システムリソース情報
    print(f"CPU Count: {psutil.cpu_count()}")
    print(f"Memory: {psutil.virtual_memory().total / (1024**3):.1f} GB")
    print(f"Python Version: {sys.version}")
    print()
    
    # ベンチマーク実行
    api_results = benchmark_api_performance()
    calc_results = benchmark_calculation_performance()
    
    # 結果の保存
    with open(f"benchmark_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 'w') as f:
        json.dump({
            'api_performance': api_results,
            'calculation_performance': calc_results
        }, f, indent=2)
```

### 2. リソース使用量監視
```bash
#!/bin/bash
# resource_monitor.sh

MONITOR_DURATION=300  # 5分間
INTERVAL=10          # 10秒間隔

echo "=== Resource Monitoring (${MONITOR_DURATION}s) ==="

# ヘッダー出力
echo "Timestamp,CPU%,Memory%,DiskIO,NetworkIO" > resource_usage.csv

for ((i=0; i<$((MONITOR_DURATION/INTERVAL)); i++)); do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.1f", $3/$2 * 100.0)}')
    
    # ディスクI/O（簡易版）
    DISK_IO=$(iostat -d 1 1 | tail -n +4 | awk '{sum+=$4} END {print sum}')
    
    # ネットワークI/O（簡易版）
    NETWORK_IO=$(cat /proc/net/dev | grep eth0 | awk '{print $2+$10}')
    
    echo "$TIMESTAMP,$CPU_USAGE,$MEMORY_USAGE,$DISK_IO,$NETWORK_IO" >> resource_usage.csv
    
    sleep $INTERVAL
done

echo "Resource monitoring completed. Results saved to resource_usage.csv"
```

## 🔒 セキュリティメンテナンス / Security Maintenance

### 1. セキュリティ監査
```bash
#!/bin/bash
# security_audit.sh

echo "=== Security Audit ==="

# 1. ファイル権限チェック
echo "Checking file permissions..."
find . -type f -name "*.py" -not -perm 644 -ls
find . -type d -not -perm 755 -ls

# 2. 設定ファイルのセキュリティチェック
echo "Checking configuration security..."
grep -r "password\|secret\|key" *.py *.yml *.json 2>/dev/null | grep -v "example"

# 3. ネットワークポートチェック
echo "Checking open ports..."
netstat -tulpn | grep LISTEN

# 4. プロセスチェック
echo "Checking running processes..."
ps aux | grep python

echo "Security audit completed"
```

### 2. バックアップとリストア
```bash
#!/bin/bash
# backup_system.sh

BACKUP_DIR="/backup/panel_calc"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="panel_calc_backup_$DATE"

echo "=== System Backup ==="

# バックアップディレクトリの作成
mkdir -p "$BACKUP_DIR"

# 1. アプリケーションファイルのバックアップ
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_app.tar.gz" \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude="results/logs" \
    --exclude="results/visualizations" \
    *.py requirements.txt *.yml *.md

# 2. 設定ファイルのバックアップ
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_config.tar.gz" \
    docker-compose*.yml \
    requirements.txt \
    *.env 2>/dev/null || true

# 3. 重要な結果データのバックアップ
tar -czf "$BACKUP_DIR/${BACKUP_NAME}_data.tar.gz" \
    results/csv_data \
    results/reports

# 4. バックアップの検証
echo "Verifying backups..."
for backup_file in "$BACKUP_DIR"/${BACKUP_NAME}_*.tar.gz; do
    if tar -tzf "$backup_file" >/dev/null 2>&1; then
        echo "✓ $(basename "$backup_file") - OK"
    else
        echo "✗ $(basename "$backup_file") - FAILED"
    fi
done

# 5. 古いバックアップの削除（30日以上）
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_NAME"
```

## 📈 容量計画 / Capacity Planning

### ディスク使用量予測
```python
#!/usr/bin/env python3
# capacity_planning.py

import os
import json
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

def analyze_disk_usage():
    """ディスク使用量の分析と予測"""
    
    # 過去のデータ収集（例）
    usage_data = []
    
    # 現在の使用量
    total, used, free = shutil.disk_usage(".")
    current_usage = used / total * 100
    
    print(f"Current disk usage: {current_usage:.1f}%")
    print(f"Free space: {free / (1024**3):.1f} GB")
    
    # 成長率の計算（簡易版）
    # 実際の実装では過去のデータを使用
    daily_growth_gb = 0.1  # 1日あたり100MBの成長と仮定
    
    # 30日後の予測
    days_ahead = 30
    predicted_usage = current_usage + (daily_growth_gb * days_ahead * 1024**3 / total * 100)
    
    print(f"Predicted usage in {days_ahead} days: {predicted_usage:.1f}%")
    
    if predicted_usage > 80:
        print("WARNING: Disk usage will exceed 80% in 30 days")
        print("Consider implementing data archival or increasing storage")
    
    return {
        'current_usage_percent': current_usage,
        'free_space_gb': free / (1024**3),
        'predicted_usage_percent': predicted_usage,
        'days_until_80_percent': max(0, (80 - current_usage) / (daily_growth_gb * 1024**3 / total * 100))
    }

if __name__ == "__main__":
    results = analyze_disk_usage()
    
    # 結果の保存
    with open(f"capacity_analysis_{datetime.now().strftime('%Y%m%d')}.json", 'w') as f:
        json.dump(results, f, indent=2)
```

## 📞 緊急時対応 / Emergency Response

### システム復旧手順
```bash
#!/bin/bash
# emergency_recovery.sh

echo "=== Emergency Recovery Procedure ==="

# 1. サービス状態の確認
echo "Checking service status..."
systemctl status panel-calculator || echo "Service not running"

# 2. ログの確認
echo "Checking recent errors..."
tail -50 panel_calculator.log | grep -E "(ERROR|CRITICAL)"

# 3. リソース状況の確認
echo "Checking system resources..."
df -h
free -h
top -bn1 | head -20

# 4. 自動復旧の試行
echo "Attempting automatic recovery..."

# プロセスの再起動
pkill -f "python.*api_integration"
sleep 5
python api_integration.py &

# 5. 復旧確認
sleep 10
if curl -s http://localhost:8001/health >/dev/null; then
    echo "✓ Service recovered successfully"
else
    echo "✗ Manual intervention required"
    echo "Please check logs and contact support"
fi
```

---

**最終更新 / Last Updated**: 2025-07-02  
**バージョン / Version**: 1.2.0  
**次回レビュー / Next Review**: 2025-10-02
