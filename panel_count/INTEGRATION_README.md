# 屋顶检测分割系统集成 / Roof Detection Segmentation System Integration

## 🎯 集成目标 / Integration Goal

将屋顶检测分割系统与太阳能板配置计算系统进行集成，实现从卫星图像到太阳能板布局的完整工作流程。

Integrate the roof detection segmentation system with the solar panel layout calculation system to achieve a complete workflow from satellite images to solar panel layouts.

## 📋 集成内容 / Integration Contents

### 🔧 新增文件 / New Files

1. **`api_integration.py`** - 主要API服务器
   - Flask-based REST API
   - Base64图像解码功能
   - 太阳能板计算集成

2. **`test_integration.py`** - 测试脚本
   - API功能测试
   - 示例数据生成
   - 结果验证

3. **`integration_guide.md`** - 详细集成指南
   - API规格说明
   - 使用示例
   - 错误处理

4. **`start_integration.py`** - 快速启动脚本
   - 依赖检查和安装
   - 服务器启动
   - 测试执行

## 🚀 快速开始 / Quick Start

### 1. 启动集成系统 / Start Integration System

```bash
python start_integration.py
```

### 2. 选择操作 / Select Operation

```
1. APIサーバーを起動 (Start API Server)
2. テストを実行 (Run Tests)  
3. 統合ガイドを表示 (Show Integration Guide)
4. 終了 (Exit)
```

### 3. API使用 / API Usage

```bash
# 服务器启动后
curl -X POST http://localhost:8000/segment_click \
  -H "Content-Type: application/json" \
  -d '{
    "mask": "data:image/png;base64,iVBORw0KGgo...",
    "centers": [{"x":123,"y":456}],
    "center_latitude": 35.6895,
    "map_scale": 0.05,
    "spacing_interval": 0.3
  }'
```

## 📊 数据流程 / Data Flow

```
[屋顶检测系统:8000] → [POST /segment_click] → [太阳能板计算:8001] → [结果返回]
     ↓                         ↓                         ↓              ↓
Form Data (x,y,image)    Roof Segments JSON      Panel Layout    JSON Response
YOLO Detection           Base64 Masks            Calculation     Visualization
Segmentation             Centers Data            Optimization    Results Data
```

### 🔄 **完整工作流程 / Complete Workflow**

1. **屋顶检测** (roof_detect_segument:8000)
   - 输入: 卫星图像 + 点击坐标 (x, y)
   - 输出: 屋顶分割结果 (segments with masks)

2. **太阳能板计算** (panel_count:8001)
   - 输入: 屋顶分割结果 + 地图参数
   - 输出: 太阳能板布局 + 可视化图像

3. **统一客户端** (roof_detection_client.py)
   - 协调两个系统的调用
   - 提供完整的端到端解决方案

## 🔌 API规格 / API Specification

### 🏠 屋顶检测系统 (Port 8000)
**端点**: `POST /segment_click`
- **输入**: Form Data
  - `x`: 点击X坐标
  - `y`: 点击Y坐标
  - `image`: 卫星图像文件
- **输出**: JSON
  - `segments`: 分割结果数组
  - `bbox`: 边界框坐标
  - `label`: 标签信息

### ☀️ 太阳能板计算系统 (Port 8001)

#### 端点1: `POST /process_roof_segments`
- **输入**: JSON
  - `segments`: 屋顶分割结果
  - `center_latitude`: 中心纬度
  - `map_scale`: 地图比例 (m/pixel)
  - `spacing_interval`: 间距 (meters)
- **输出**: JSON
  - `total_segments`: 总分割数
  - `total_panels`: 总面板数
  - `best_segment`: 最优分割结果
  - `visualization_b64`: 可视化图像

#### 端点2: `POST /segment_click` (兼容性)
- **输入**: JSON (单一掩膜格式)
- **输出**: JSON (单一结果格式)

## 🧪 测试验证 / Testing & Validation

### 自动测试 / Automated Tests
```bash
python test_integration.py
```

### 手动测试 / Manual Tests
1. 启动API服务器
2. 发送测试请求
3. 验证返回结果
4. 检查可视化图像

## 📁 文件结构 / File Structure

```
panel_count/
├── api_integration.py          # 主API服务器
├── test_integration.py         # 测试脚本
├── integration_guide.md        # 详细指南
├── start_integration.py        # 启动脚本
├── INTEGRATION_README.md       # 本文件
├── requirements.txt            # 更新的依赖
└── 0630/                      # 合作方提供的文件
    ├── Analysis of Solar Panels from Satellite Imagery_EN.pptx
    └── スクリーンショット*.png
```

## 🔧 技术实现 / Technical Implementation

### Base64处理 / Base64 Processing
```python
def b64_to_cv2(b64str, flags=cv2.IMREAD_UNCHANGED):
    img_bytes = base64.b64decode(b64str.split(",")[-1])
    img_np = np.frombuffer(img_bytes, dtype=np.uint8)
    return cv2.imdecode(img_np, flags)
```

### 太阳能板计算集成 / Solar Panel Calculation Integration
- 使用现有的高速算法
- 支持多种面板规格
- 自动选择最优配置方向
- 生成可视化结果

## 🌟 主要特性 / Key Features

✅ **完全兼容**: 支持合作方的数据格式
✅ **高性能**: 使用优化的计算算法  
✅ **易于集成**: RESTful API设计
✅ **详细文档**: 完整的使用指南
✅ **错误处理**: 完善的错误处理机制
✅ **可视化**: 自动生成布局图像

## 🔄 工作流程 / Workflow

1. **接收数据**: 从屋顶检测系统接收Base64掩膜和元数据
2. **图像处理**: 解码Base64并进行预处理
3. **计算布局**: 使用太阳能板算法计算最优布局
4. **生成结果**: 创建可视化图像和详细数据
5. **返回响应**: 以JSON格式返回完整结果

## 📞 支持 / Support

如有技术问题或需要帮助，请参考：
- `integration_guide.md` - 详细技术文档
- `test_integration.py` - 测试示例
- API日志输出 - 调试信息

---

**开发日期 / Development Date**: 2025-06-27
**版本 / Version**: v1.0
**状态 / Status**: Ready for Integration ✅
