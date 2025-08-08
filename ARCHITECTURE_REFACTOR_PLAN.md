# 架构重构计划 / Architecture Refactor Plan

## 🎯 目标 / Objectives

### 中文
消除架构混乱，建立清晰的模块分离和API规范，提高系统的可维护性和可扩展性。

### English
Eliminate architectural confusion, establish clear module separation and API specifications, improve system maintainability and scalability.

## 📊 当前问题分析 / Current Issues Analysis

### 1. 重复的屋顶检测系统 / Duplicate Roof Detection Systems

#### 问题 / Problem:
- **新系统**: `roof/` (FastAPI, `/segment` 端点)
- **旧系统**: `panel_count/roof_detect_segument/roof/` (FastAPI, `/segment_click` 端点)

#### 解决方案 / Solution:
保留新系统 `roof/`，移除旧系统，更新所有引用。

### 2. API端点混乱 / API Endpoint Confusion

#### 问题 / Problem:
- 主要API: `/calculate_panels`
- 废弃API: `/process_roof_segments`, `/segment_click`
- 客户端仍在使用旧端点

#### 解决方案 / Solution:
完全移除废弃端点，更新客户端代码。

### 3. 模块重复 / Module Duplication

#### 问题 / Problem:
- `panel_count/roof_io.py`
- `src/panel_count/roof_io.py`

#### 解决方案 / Solution:
统一到 `panel_count/` 目录，移除 `src/` 中的重复。

## 🏗️ 新架构设计 / New Architecture Design

```
iot-ai/
├── services/                    # 微服务目录
│   ├── roof-detection/         # 屋顶检测服务
│   │   ├── app/
│   │   ├── models/
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── panel-calculation/      # 太阳能板计算服务
│   │   ├── core/              # 核心计算逻辑
│   │   ├── api/               # API层
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   │
│   ├── classification/         # 分类服务 (保持不变)
│   └── prediction/            # 预测服务 (保持不变)
│
├── shared/                     # 共享库
│   ├── utils/
│   ├── models/
│   └── config/
│
├── tests/                      # 测试
├── docs/                       # 文档
├── docker-compose.yml          # 统一Docker配置
└── README.md
```

## 📋 重构步骤 / Refactoring Steps

### Phase 1: 清理重复系统 / Clean Duplicate Systems

1. **移除旧屋顶检测系统**
   ```bash
   rm -rf panel_count/roof_detect_segument/
   ```

2. **移除重复模块**
   ```bash
   rm -rf src/
   ```

3. **移除废弃API端点**
   - 从 `panel_count/api_integration.py` 移除 `/process_roof_segments` 和 `/segment_click`

### Phase 2: 重组服务结构 / Reorganize Service Structure

1. **创建services目录结构**
2. **移动屋顶检测服务**
3. **重组太阳能板计算服务**
4. **更新Docker配置**

### Phase 3: 统一API规范 / Standardize API Specification

1. **定义统一的API规范**
2. **更新客户端代码**
3. **更新文档**

### Phase 4: 测试和验证 / Testing and Validation

1. **更新测试用例**
2. **验证服务间通信**
3. **性能测试**

## 🔧 实施细节 / Implementation Details

### 新的服务端口分配 / New Service Port Allocation
- 屋顶检测服务: 8000
- 太阳能板计算服务: 8001
- 分类服务: 8002
- 预测服务: 8003

### API规范 / API Specification

#### 屋顶检测服务 / Roof Detection Service
```
POST /api/v1/segment
Content-Type: multipart/form-data
```

#### 太阳能板计算服务 / Panel Calculation Service
```
POST /api/v1/calculate
Content-Type: application/json
```

### 配置管理 / Configuration Management
- 使用环境变量进行配置
- 统一的配置文件格式
- 开发/测试/生产环境分离

## ⚠️ 风险和注意事项 / Risks and Considerations

### 风险 / Risks:
1. 现有客户端可能需要更新
2. 数据迁移可能需要时间
3. 服务间依赖关系需要重新验证

### 缓解措施 / Mitigation:
1. 分阶段实施，保持向后兼容
2. 充分测试每个阶段
3. 准备回滚计划

## 📅 时间计划 / Timeline

### Week 1: Phase 1 - 清理
- 移除重复系统
- 更新引用

### Week 2: Phase 2 - 重组
- 创建新目录结构
- 移动服务

### Week 3: Phase 3 - 标准化
- 统一API
- 更新文档

### Week 4: Phase 4 - 测试
- 全面测试
- 性能验证

## ✅ 成功标准 / Success Criteria

1. ✅ 消除所有重复代码
2. ✅ 清晰的服务边界
3. ✅ 统一的API规范
4. ✅ 完整的文档
5. ✅ 所有测试通过
6. ✅ 性能不降低

## 📞 联系人 / Contact

如有问题，请联系项目负责人。
For questions, please contact the project lead.
