# 🚀 屋顶检测与太阳能板计算系统集成部署指南

## 📋 系统架构概览

```
┌─────────────────────────────────────────────────────────────┐
│                    集成系统架构                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │  屋顶检测系统    │    │ 太阳能板计算系统 │                │
│  │   (Port 8000)   │◄──►│   (Port 8001)   │                │
│  │                 │    │                 │                │
│  │ • YOLO分割      │    │ • 面板布局计算   │                │
│  │ • Base64输出    │    │ • 可视化生成     │                │
│  │ • FastAPI       │    │ • Flask API     │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           └───────────┬───────────┘                        │
│                       │                                    │
│              ┌─────────────────┐                           │
│              │   统一客户端     │                           │
│              │ roof_detection_ │                           │
│              │    client.py    │                           │
│              └─────────────────┘                           │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ 部署方式

### 方式1: Docker Compose (推荐)

#### 1. 准备工作
```bash
# 确保对方的代码在正确位置
ls roof_detect_segument/roof/
# 应该看到: app/, models/, Dockerfile, requirements.txt

# 确保我们的代码文件存在
ls *.py
# 应该看到: api_integration.py, roof_detection_client.py, 等
```

#### 2. 构建和启动
```bash
# 启动屋顶检测和太阳能板计算系统
docker-compose -f docker-compose.integration.yml up -d

# 查看服务状态
docker-compose -f docker-compose.integration.yml ps

# 查看日志
docker-compose -f docker-compose.integration.yml logs -f
```

#### 3. 验证部署
```bash
# 检查屋顶检测系统
curl http://localhost:8000/docs

# 检查太阳能板计算系统
curl http://localhost:8001/health
```

#### 4. 使用统一客户端
```bash
# 启动客户端容器
docker-compose -f docker-compose.integration.yml --profile client up integration-client
```

### 方式2: 本地开发环境

#### 1. 安装依赖
```bash
# 安装我们系统的依赖
pip install -r requirements.txt

# 安装对方系统的依赖
cd roof_detect_segument/roof
pip install -r requirements.txt
cd ../..
```

#### 2. 启动屋顶检测系统
```bash
# 在第一个终端
cd roof_detect_segument/roof
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

#### 3. 启动太阳能板计算系统
```bash
# 在第二个终端
python api_integration.py
# 或者
python start_integration.py
```

#### 4. 运行测试
```bash
# 在第三个终端
python test_integration.py
```

## 🧪 测试和验证

### 1. 基本功能测试
```bash
# 运行完整测试套件
python test_integration.py

# 选择测试项目:
# 1. ヘルスチェック
# 2. 基本API統合テスト  
# 3. 屋根セグメント処理テスト
# 4. サンプルリクエストファイル作成
# 5. 統合クライアントテスト
```

### 2. 端到端工作流测试
```bash
# 使用统一客户端
python roof_detection_client.py

# 选择 "1. 完全ワークフローを実行"
# 提供测试图像和坐标
```

### 3. API直接测试
```bash
# 测试屋顶检测 (需要图像文件)
curl -X POST http://localhost:8000/segment_click \
  -F "x=250" \
  -F "y=200" \
  -F "image=@test_image.jpg"

# 测试太阳能板计算
curl -X POST http://localhost:8001/process_roof_segments \
  -H "Content-Type: application/json" \
  -d @sample_request.json
```

## 📊 监控和日志

### 1. 服务健康检查
```bash
# 屋顶检测系统
curl http://localhost:8000/docs

# 太阳能板计算系统  
curl http://localhost:8001/health
```

### 2. 日志查看
```bash
# Docker环境
docker-compose -f docker-compose.integration.yml logs roof-detection
docker-compose -f docker-compose.integration.yml logs solar-panel-calc

# 本地环境
# 查看各服务的控制台输出
```

### 3. 性能监控
```bash
# 容器资源使用情况
docker stats

# 系统资源监控
htop
```

## 🔧 配置参数

### 环境变量
```bash
# 太阳能板计算系统
FLASK_RUN_PORT=8001          # API端口
LOG_LEVEL=INFO               # 日志级别

# 统一客户端
ROOF_API_URL=http://localhost:8000      # 屋顶检测API
PANEL_API_URL=http://localhost:8001     # 太阳能板计算API
```

### 计算参数
```json
{
  "center_latitude": 35.6895,    // 中心纬度
  "map_scale": 0.05,             // 地图比例 (m/pixel)
  "spacing_interval": 0.3        // 面板间距 (meters)
}
```

## 🚨 故障排除

### 常见问题

#### 1. 端口冲突
```bash
# 检查端口占用
netstat -tulpn | grep :8000
netstat -tulpn | grep :8001

# 修改端口配置
export FLASK_RUN_PORT=8002
```

#### 2. 依赖问题
```bash
# 重新安装依赖
pip install --upgrade -r requirements.txt

# 检查OpenCV安装
python -c "import cv2; print(cv2.__version__)"
```

#### 3. 内存不足
```bash
# 监控内存使用
free -h

# 调整Docker内存限制
docker-compose -f docker-compose.integration.yml up -d --memory=2g
```

#### 4. 模型文件缺失
```bash
# 检查模型文件
ls roof_detect_segument/roof/models/
# 应该包含: best_v2.pt, roof_yolov8m-seg.pt, yolo_multi_detect.pt
```

### 日志分析
```bash
# 查看错误日志
docker-compose -f docker-compose.integration.yml logs | grep ERROR

# 查看API调用日志
docker-compose -f docker-compose.integration.yml logs | grep "POST"
```

## 📈 性能优化

### 1. 系统优化
- 使用GPU加速 (如果可用)
- 调整图像处理分辨率
- 优化内存使用

### 2. API优化
- 启用请求缓存
- 使用连接池
- 异步处理长时间任务

### 3. 部署优化
- 使用生产级WSGI服务器 (Gunicorn)
- 配置负载均衡
- 启用API网关

## 🔒 安全考虑

### 1. API安全
- 添加认证机制
- 限制请求频率
- 验证输入数据

### 2. 网络安全
- 使用HTTPS
- 配置防火墙
- 限制网络访问

### 3. 数据安全
- 加密敏感数据
- 定期备份
- 访问日志记录

## 📞 支持和维护

### 联系信息
- 技术支持: 开发团队
- 文档更新: 定期维护
- 问题报告: GitHub Issues

### 维护计划
- 定期更新依赖
- 性能监控和优化
- 安全补丁应用

---

**最后更新**: 2025-06-27  
**版本**: v1.0  
**状态**: 生产就绪 ✅
