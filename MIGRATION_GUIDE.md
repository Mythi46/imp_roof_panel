# 迁移指南 / Migration Guide

## API端点变更 / API Endpoint Changes

### 屋顶检测 / Roof Detection
- **旧端点**: `/segment_click` (已移除)
- **新端点**: `/segment`
- **服务地址**: `http://localhost:8000`

### 太阳能板计算 / Panel Calculation
- **旧端点**: `/process_roof_segments` (已移除)
- **新端点**: `/calculate_panels`
- **服务地址**: `http://localhost:8001`

## 客户端更新 / Client Updates

### JavaScript示例 / JavaScript Example
```javascript
// 旧代码 (已废弃)
// const response = await fetch('/segment_click', {...});

// 新代码
const response = await fetch('http://localhost:8000/segment', {
  method: 'POST',
  body: formData
});
```

### Python示例 / Python Example
```python
# 旧代码 (已废弃)
# response = requests.post(f"{api_url}/segment_click", ...)

# 新代码
response = requests.post(f"{api_url}/segment", files=files)
```

## 服务启动 / Service Startup

```bash
# 启动所有服务
docker-compose up

# 或分别启动
docker-compose up roof        # 屋顶检测服务
docker-compose up panel-calc  # 太阳能板计算服务 (需要添加到compose.yml)
```

## 测试验证 / Testing Verification

```bash
# 测试屋顶检测服务
curl -X POST http://localhost:8000/segment -F "image=@test.jpg"

# 测试太阳能板计算服务
curl -X POST http://localhost:8001/calculate_panels -H "Content-Type: application/json" -d '{...}'
```
