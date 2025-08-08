#!/usr/bin/env python3
"""
Architecture Refactor Phase 1: Clean Duplicate Systems
架构重构第一阶段：清理重复系统
"""
import os
import shutil
from pathlib import Path

def backup_important_files():
    """备份重要文件"""
    print("📦 Creating backup of important files...")
    
    backup_dir = Path("backup_before_refactor")
    backup_dir.mkdir(exist_ok=True)
    
    # 备份重要配置文件
    important_files = [
        "panel_count/roof_detect_segument/roof/README.md",
        "panel_count/roof_detect_segument/roof/requirements.txt",
        "panel_count/docker-compose.integration.yml"
    ]
    
    for file_path in important_files:
        if Path(file_path).exists():
            dest = backup_dir / Path(file_path).name
            shutil.copy2(file_path, dest)
            print(f"  ✅ Backed up {file_path}")

def remove_duplicate_roof_detection():
    """移除重复的屋顶检测系统"""
    print("🗑️  Removing duplicate roof detection system...")
    
    old_roof_system = Path("panel_count/roof_detect_segument")
    if old_roof_system.exists():
        print(f"  Removing {old_roof_system}")
        shutil.rmtree(old_roof_system)
        print("  ✅ Removed old roof detection system")
    else:
        print("  ℹ️  Old roof detection system not found")

def remove_duplicate_src():
    """移除重复的src目录"""
    print("🗑️  Removing duplicate src directory...")
    
    src_dir = Path("src")
    if src_dir.exists():
        print(f"  Removing {src_dir}")
        shutil.rmtree(src_dir)
        print("  ✅ Removed duplicate src directory")
    else:
        print("  ℹ️  src directory not found")

def clean_deprecated_api_endpoints():
    """清理废弃的API端点"""
    print("🧹 Cleaning deprecated API endpoints...")
    
    api_file = Path("panel_count/api_integration.py")
    if not api_file.exists():
        print("  ❌ api_integration.py not found")
        return
    
    content = api_file.read_text(encoding='utf-8')
    
    # 移除废弃的端点
    lines = content.split('\n')
    new_lines = []
    skip_section = False
    
    for line in lines:
        # 检测废弃端点的开始
        if "@app.route('/process_roof_segments'" in line or "@app.route('/segment_click'" in line:
            skip_section = True
            new_lines.append("# REMOVED: Deprecated endpoint - see ARCHITECTURE_REFACTOR_PLAN.md")
            continue
        
        # 检测函数结束
        if skip_section and line.strip() and not line.startswith(' ') and not line.startswith('\t'):
            if line.startswith('@app.route') or line.startswith('def ') or line.startswith('if __name__'):
                skip_section = False
        
        if not skip_section:
            new_lines.append(line)
    
    # 写回文件
    new_content = '\n'.join(new_lines)
    api_file.write_text(new_content, encoding='utf-8')
    print("  ✅ Cleaned deprecated API endpoints")

def update_roof_detection_client():
    """更新屋顶检测客户端"""
    print("🔄 Updating roof detection client...")
    
    client_file = Path("panel_count/roof_detection_client.py")
    if not client_file.exists():
        print("  ❌ roof_detection_client.py not found")
        return
    
    content = client_file.read_text(encoding='utf-8')
    
    # 更新API端点引用
    content = content.replace('/segment_click', '/segment')
    content = content.replace('/process_roof_segments', '/calculate_panels')
    
    # 更新注释
    content = content.replace(
        '屋根検出分割システムを呼び出し',
        '屋根検出システムを呼び出し (新API使用)'
    )
    
    client_file.write_text(content, encoding='utf-8')
    print("  ✅ Updated roof detection client")

def update_docker_compose():
    """更新Docker Compose配置"""
    print("🐳 Updating Docker Compose configuration...")
    
    # 移除旧的集成配置文件
    old_compose = Path("panel_count/docker-compose.integration.yml")
    if old_compose.exists():
        old_compose.unlink()
        print("  ✅ Removed old integration docker-compose.yml")
    
    # 更新主要的compose.yml
    compose_file = Path("compose.yml")
    if compose_file.exists():
        content = compose_file.read_text(encoding='utf-8')
        
        # 确保roof服务配置正确
        if 'roof:' in content and 'context: ./roof' in content:
            print("  ✅ Main compose.yml already correctly configured")
        else:
            print("  ⚠️  Main compose.yml may need manual review")

def update_documentation():
    """更新文档"""
    print("📚 Updating documentation...")
    
    # 更新主README
    readme_file = Path("panel_count/README.md")
    if readme_file.exists():
        content = readme_file.read_text(encoding='utf-8')
        
        # 添加架构更新说明
        if "架构重构" not in content:
            header = "# 太陽光パネル配置計算システム / Solar Panel Layout Calculation System\n\n"
            notice = """## ⚠️ 架构更新通知 / Architecture Update Notice

**重要**: 本系统已进行架构重构，移除了重复的屋顶检测系统。
**Important**: This system has undergone architectural refactoring, removing duplicate roof detection systems.

- 屋顶检测服务: `roof/` (端口 8000)
- 太阳能板计算服务: `panel_count/` (端口 8001)

详细信息请参考 `ARCHITECTURE_REFACTOR_PLAN.md`

---

"""
            new_content = header + notice + content[len(header):]
            readme_file.write_text(new_content, encoding='utf-8')
            print("  ✅ Updated README with architecture notice")

def create_migration_guide():
    """创建迁移指南"""
    print("📖 Creating migration guide...")
    
    guide_content = """# 迁移指南 / Migration Guide

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
"""
    
    with open("MIGRATION_GUIDE.md", "w", encoding="utf-8") as f:
        f.write(guide_content)
    
    print("  ✅ Created migration guide")

def main():
    """执行第一阶段重构"""
    print("🚀 Starting Architecture Refactor Phase 1")
    print("=" * 50)
    
    try:
        backup_important_files()
        remove_duplicate_roof_detection()
        remove_duplicate_src()
        clean_deprecated_api_endpoints()
        update_roof_detection_client()
        update_docker_compose()
        update_documentation()
        create_migration_guide()
        
        print("\n" + "=" * 50)
        print("✅ Phase 1 refactoring completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Review the changes in git")
        print("2. Test the remaining services")
        print("3. Update any external clients")
        print("4. Proceed to Phase 2 if everything works")
        print("\n📖 See MIGRATION_GUIDE.md for detailed migration instructions")
        
    except Exception as e:
        print(f"❌ Error during refactoring: {e}")
        print("Please check the backup_before_refactor/ directory for important files")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
