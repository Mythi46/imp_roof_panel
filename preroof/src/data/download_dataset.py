"""
数据集下载模块
Dataset download module
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Optional

try:
    from roboflow import Roboflow
except ImportError:
    print("Warning: roboflow not installed. Please install with: pip install roboflow")
    Roboflow = None

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def download_roboflow_dataset(
    api_key: str,
    workspace: str,
    project: str,
    version: int = 1,
    format: str = "yolov8",
    download_path: str = "data/raw"
) -> Optional[str]:
    """
    从Roboflow下载数据集
    
    Args:
        api_key: Roboflow API密钥
        workspace: 工作空间名称
        project: 项目名称
        version: 数据集版本
        format: 数据格式
        download_path: 下载路径
        
    Returns:
        数据集路径或None（如果失败）
    """
    if Roboflow is None:
        logger.error("Roboflow not available. Please install: pip install roboflow")
        return None
    
    try:
        # 创建下载目录
        os.makedirs(download_path, exist_ok=True)
        
        # 初始化Roboflow
        rf = Roboflow(api_key=api_key)
        project_obj = rf.workspace(workspace).project(project)
        version_obj = project_obj.version(version)
        
        # 下载数据集
        logger.info(f"开始下载数据集: {workspace}/{project} v{version}")
        dataset = version_obj.download(format, location=download_path)
        
        logger.info(f"数据集下载完成: {dataset.location}")
        return dataset.location
        
    except Exception as e:
        logger.error(f"数据集下载失败: {e}")
        return None


def setup_data_yaml(
    dataset_path: str,
    class_weights: Optional[list] = None,
    output_path: str = "config/data.yaml"
) -> bool:
    """
    设置数据配置文件，添加类别权重
    
    Args:
        dataset_path: 数据集路径
        class_weights: 类别权重列表
        output_path: 输出配置文件路径
        
    Returns:
        是否成功
    """
    try:
        # 读取原始data.yaml
        original_yaml = os.path.join(dataset_path, "data.yaml")
        if not os.path.exists(original_yaml):
            logger.error(f"原始data.yaml不存在: {original_yaml}")
            return False
        
        with open(original_yaml, 'r') as f:
            config = yaml.safe_load(f)
        
        # 添加类别权重（关键改进）
        if class_weights:
            config['class_weights'] = class_weights
            logger.info(f"添加类别权重: {class_weights}")
        
        # 更新路径为绝对路径
        dataset_abs_path = os.path.abspath(dataset_path)
        config['train'] = os.path.join(dataset_abs_path, "train/images")
        config['val'] = os.path.join(dataset_abs_path, "valid/images")
        if 'test' in config:
            config['test'] = os.path.join(dataset_abs_path, "test/images")
        
        # 创建输出目录
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 保存修改后的配置
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"数据配置文件已保存: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"设置数据配置失败: {e}")
        return False


def download_and_setup(config_path: str = "config/data_config.yaml") -> Optional[str]:
    """
    根据配置文件下载并设置数据集
    
    Args:
        config_path: 数据配置文件路径
        
    Returns:
        数据集路径或None
    """
    try:
        # 读取配置
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        roboflow_config = config['roboflow']
        dataset_config = config['dataset']
        
        # 下载数据集
        dataset_path = download_roboflow_dataset(
            api_key=roboflow_config['api_key'],
            workspace=roboflow_config['workspace'],
            project=roboflow_config['project'],
            version=roboflow_config['version'],
            format=roboflow_config['format'],
            download_path=config['paths']['raw']
        )
        
        if dataset_path:
            # 设置数据配置
            success = setup_data_yaml(
                dataset_path=dataset_path,
                class_weights=dataset_config['class_weights'],
                output_path="config/data.yaml"
            )
            
            if success:
                return dataset_path
        
        return None
        
    except Exception as e:
        logger.error(f"下载和设置失败: {e}")
        return None


if __name__ == "__main__":
    # 示例用法
    dataset_path = download_and_setup()
    if dataset_path:
        print(f"✅ 数据集准备完成: {dataset_path}")
    else:
        print("❌ 数据集准备失败")
