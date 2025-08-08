"""
数据处理工具模块
Data processing utilities module
"""

import os
import yaml
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from collections import Counter

logger = logging.getLogger(__name__)


class DatasetAnalyzer:
    """数据集分析器"""
    
    def __init__(self, data_yaml_path: str):
        """
        初始化数据集分析器
        
        Args:
            data_yaml_path: 数据配置文件路径
        """
        self.data_yaml_path = data_yaml_path
        self.data_config = self._load_config()
        
    def _load_config(self) -> Dict:
        """加载数据配置"""
        try:
            with open(self.data_yaml_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"加载数据配置失败: {e}")
            return {}
    
    def analyze_class_distribution(self) -> Dict[int, int]:
        """
        分析类别分布
        
        Returns:
            类别ID到实例数的映射
        """
        if not self.data_config:
            return {}
        
        train_path = self.data_config.get('train', '')
        if not train_path:
            return {}
        
        # 获取标签目录
        if os.path.isfile(train_path):
            train_dir = os.path.dirname(train_path)
        else:
            train_dir = train_path
        
        label_dir = os.path.join(os.path.dirname(train_dir), 'labels') if 'images' in train_dir else os.path.join(train_dir, 'labels')
        
        if not os.path.exists(label_dir):
            logger.warning(f"标签目录不存在: {label_dir}")
            return {}
        
        # 统计类别分布
        counter = Counter()
        label_files = [f for f in os.listdir(label_dir) if f.endswith('.txt')]
        
        for label_file in label_files:
            label_path = os.path.join(label_dir, label_file)
            try:
                with open(label_path, 'r') as f:
                    for line in f:
                        if line.strip():
                            cls_id = int(line.split()[0])
                            counter[cls_id] += 1
            except Exception as e:
                logger.warning(f"读取标签文件失败 {label_file}: {e}")
        
        return dict(counter)
    
    def get_class_names(self) -> List[str]:
        """获取类别名称"""
        return self.data_config.get('names', [])
    
    def get_num_classes(self) -> int:
        """获取类别数量"""
        return self.data_config.get('nc', 0)


def create_data_splits(
    source_dir: str,
    output_dir: str,
    train_ratio: float = 0.7,
    val_ratio: float = 0.2,
    test_ratio: float = 0.1
) -> bool:
    """
    创建数据集分割
    
    Args:
        source_dir: 源数据目录
        output_dir: 输出目录
        train_ratio: 训练集比例
        val_ratio: 验证集比例
        test_ratio: 测试集比例
        
    Returns:
        是否成功
    """
    try:
        # 验证比例
        if abs(train_ratio + val_ratio + test_ratio - 1.0) > 1e-6:
            logger.error("数据分割比例之和必须等于1")
            return False
        
        # 创建输出目录
        for split in ['train', 'val', 'test']:
            for subdir in ['images', 'labels']:
                os.makedirs(os.path.join(output_dir, split, subdir), exist_ok=True)
        
        # 获取所有图像文件
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(Path(source_dir).glob(f'**/*{ext}'))
        
        if not image_files:
            logger.error(f"在 {source_dir} 中未找到图像文件")
            return False
        
        # 随机分割
        import random
        random.shuffle(image_files)
        
        total_files = len(image_files)
        train_count = int(total_files * train_ratio)
        val_count = int(total_files * val_ratio)
        
        splits = {
            'train': image_files[:train_count],
            'val': image_files[train_count:train_count + val_count],
            'test': image_files[train_count + val_count:]
        }
        
        # 复制文件
        for split_name, files in splits.items():
            for image_file in files:
                # 复制图像
                dst_image = os.path.join(output_dir, split_name, 'images', image_file.name)
                shutil.copy2(image_file, dst_image)
                
                # 复制对应的标签文件
                label_file = image_file.with_suffix('.txt')
                if label_file.exists():
                    dst_label = os.path.join(output_dir, split_name, 'labels', label_file.name)
                    shutil.copy2(label_file, dst_label)
        
        logger.info(f"数据分割完成: 训练集{len(splits['train'])}, 验证集{len(splits['val'])}, 测试集{len(splits['test'])}")
        return True
        
    except Exception as e:
        logger.error(f"数据分割失败: {e}")
        return False


def validate_dataset(data_yaml_path: str) -> bool:
    """
    验证数据集
    
    Args:
        data_yaml_path: 数据配置文件路径
        
    Returns:
        是否有效
    """
    try:
        # 检查配置文件
        if not os.path.exists(data_yaml_path):
            logger.error(f"数据配置文件不存在: {data_yaml_path}")
            return False
        
        with open(data_yaml_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # 检查必要字段
        required_fields = ['train', 'val', 'nc', 'names']
        for field in required_fields:
            if field not in config:
                logger.error(f"配置文件缺少必要字段: {field}")
                return False
        
        # 检查路径
        for split in ['train', 'val']:
            path = config[split]
            if not os.path.exists(path):
                logger.error(f"{split} 路径不存在: {path}")
                return False
        
        # 检查类别数量
        if config['nc'] != len(config['names']):
            logger.error("类别数量与类别名称数量不匹配")
            return False
        
        logger.info("数据集验证通过")
        return True
        
    except Exception as e:
        logger.error(f"数据集验证失败: {e}")
        return False


def calculate_class_weights(data_yaml_path: str, beta: float = 0.999) -> Optional[List[float]]:
    """
    计算类别权重 - 专家改进版
    使用有效样本数方法 (Cui et al., 2019)
    
    Args:
        data_yaml_path: 数据配置文件路径
        beta: 重采样参数
        
    Returns:
        类别权重列表
    """
    try:
        analyzer = DatasetAnalyzer(data_yaml_path)
        class_distribution = analyzer.analyze_class_distribution()
        num_classes = analyzer.get_num_classes()
        
        if not class_distribution:
            logger.warning("无法获取类别分布，使用默认权重")
            return [1.0] * num_classes
        
        # 有效样本数方法
        freq = [class_distribution.get(i, 0) for i in range(num_classes)]
        freq = [max(f, 1) for f in freq]  # 避免除零
        
        eff_num = [1 - (beta ** f) for f in freq]
        weights = [(1 - beta) / en for en in eff_num]
        
        # 归一化
        mean_weight = sum(weights) / len(weights)
        weights = [w / mean_weight for w in weights]
        
        return weights
        
    except Exception as e:
        logger.error(f"计算类别权重失败: {e}")
        return None
