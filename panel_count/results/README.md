# 太阳能板计算结果文件

## 文件夹结构

### csv_data/
包含所有CSV格式的计算数据：
- `all_samples_results.csv` - 所有sample图片的完整计算结果
- `sample_results.csv` - 完整屋顶图片的计算结果
- `segment_results.csv` - 分段屋顶图片的计算结果
- `result_summary.csv` - 几何形状屋顶的计算结果

### visualizations/
包含所有可视化图片：
- `result_*.png` - 太阳能板布局可视化图片
- 文件名格式：`result_[屋顶类型]_[面板型号].png`

### reports/
包含分析报告：
- `sample_analysis_report.md` - Sample图片分析报告
- `report.md` - 系统技术报告（中文）
- `report_ja_en.md` - 系统技术报告（日英双语）
- `technical_report_ja_en.md` - 完整技术报告（日英双语）
- `executive_summary_ja_en.md` - 执行摘要（日英双语）
- `bug_fix_report.md` - 重叠问题修复报告

### logs/
包含运行日志：
- `panel_calculator.log` - 系统运行日志

### scripts/
包含相关脚本：
- `calculate_all_samples.py` - 批量计算脚本

## 使用说明

### 快速开始
1. **执行摘要**: 查看 `reports/executive_summary_ja_en.md` 了解项目概况
2. **详细分析**: 查看 `reports/sample_analysis_report.md` 了解sample图片分析结果
3. **技术细节**: 查看 `reports/technical_report_ja_en.md` 了解完整技术实现
4. **数据查看**: 查看 `csv_data/all_samples_results.csv` 获取具体计算数据
5. **可视化**: 查看 `visualizations/` 中的图片了解面板布局

### 重要文件
- `reports/bug_fix_report.md` - 重叠问题修复详情
- `csv_data/all_samples_results.csv` - 修复后的正确计算结果
- `scripts/calculate_all_samples.py` - 批量处理脚本

### 项目成果
- ✅ 处理了9张sample图片
- ✅ 修复了重叠配置bug
- ✅ 生成了33个结果文件
- ✅ 提供了日英双语技术报告

生成时间: 2025-06-25
项目版本: v2.1.1
