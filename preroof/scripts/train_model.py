#!/usr/bin/env python3
"""
模型训练脚本
Model training script
"""

import os
import sys
import argparse
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.train import RoofDetectionTrainer
from src.data.download_dataset import download_and_setup

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🛰️ 卫星图像分割检测模型训练",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python scripts/train_model.py                    # 使用默认配置训练
  python scripts/train_model.py --epochs 100      # 训练100轮
  python scripts/train_model.py --batch 8         # 使用batch size 8
  python scripts/train_model.py --download        # 先下载数据再训练
        """
    )
    
    # 基础参数
    parser.add_argument("--config", default="config/model_config.yaml", 
                       help="模型配置文件路径")
    parser.add_argument("--data", default="config/data.yaml", 
                       help="数据配置文件路径")
    parser.add_argument("--project", default="runs/segment", 
                       help="训练结果保存路径")
    parser.add_argument("--name", default="train_improved", 
                       help="训练任务名称")
    
    # 训练参数
    parser.add_argument("--epochs", type=int, 
                       help="训练轮数 (覆盖配置文件)")
    parser.add_argument("--batch", type=int, 
                       help="批次大小 (覆盖配置文件)")
    parser.add_argument("--lr0", type=float, 
                       help="初始学习率 (覆盖配置文件)")
    parser.add_argument("--imgsz", type=int, 
                       help="图像尺寸 (覆盖配置文件)")
    
    # 数据参数
    parser.add_argument("--download", action="store_true", 
                       help="训练前先下载数据集")
    parser.add_argument("--data-config", default="config/data_config.yaml",
                       help="数据配置文件路径")
    
    # 其他选项
    parser.add_argument("--resume", type=str, 
                       help="从检查点恢复训练")
    parser.add_argument("--device", type=str, default="auto",
                       help="训练设备 (auto, cpu, 0, 1, 2, 3...)")
    parser.add_argument("--verbose", action="store_true", 
                       help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🛰️ 卫星图像分割检测模型训练")
    print("=" * 50)
    
    try:
        # 1. 下载数据集（如果需要）
        if args.download:
            logger.info("📥 开始下载数据集...")
            dataset_path = download_and_setup(args.data_config)
            if not dataset_path:
                logger.error("❌ 数据集下载失败")
                return 1
            logger.info(f"✅ 数据集下载完成: {dataset_path}")
        
        # 2. 检查数据配置文件
        if not os.path.exists(args.data):
            if args.download:
                logger.info("✅ 数据配置文件已通过下载过程创建")
            else:
                logger.error(f"❌ 数据配置文件不存在: {args.data}")
                logger.info("💡 提示: 使用 --download 参数自动下载和配置数据")
                return 1
        
        # 3. 创建训练器
        logger.info(f"🔧 加载模型配置: {args.config}")
        trainer = RoofDetectionTrainer(args.config)
        
        # 4. 验证训练设置
        logger.info("🔍 验证训练设置...")
        if not trainer.validate_training_setup(args.data):
            logger.error("❌ 训练设置验证失败")
            return 1
        logger.info("✅ 训练设置验证通过")
        
        # 5. 准备训练参数
        train_kwargs = {}
        if args.epochs:
            train_kwargs['epochs'] = args.epochs
        if args.batch:
            train_kwargs['batch'] = args.batch
        if args.lr0:
            train_kwargs['lr0'] = args.lr0
        if args.imgsz:
            train_kwargs['imgsz'] = args.imgsz
        if args.device != "auto":
            train_kwargs['device'] = args.device
        if args.resume:
            train_kwargs['resume'] = args.resume
        
        # 显示训练信息
        logger.info("🚀 开始训练...")
        logger.info(f"📊 数据配置: {args.data}")
        logger.info(f"🎯 项目路径: {args.project}")
        logger.info(f"📝 任务名称: {args.name}")
        if train_kwargs:
            logger.info(f"⚙️  自定义参数: {train_kwargs}")
        
        # 6. 开始训练
        results = trainer.train(
            data_yaml=args.data,
            project=args.project,
            name=args.name,
            **train_kwargs
        )
        
        # 7. 显示结果
        best_model_path = trainer.get_best_model_path(args.project, args.name)
        results_dir = os.path.join(args.project, args.name)
        
        print("\n" + "=" * 50)
        print("🎉 训练完成!")
        print(f"📁 最佳模型: {best_model_path}")
        print(f"📊 结果目录: {results_dir}")
        print(f"📈 查看训练曲线: {os.path.join(results_dir, 'results.png')}")
        print(f"🔍 查看混淆矩阵: {os.path.join(results_dir, 'confusion_matrix.png')}")
        print("\n💡 下一步:")
        print(f"   python src/models/evaluate.py --model {best_model_path}")
        print(f"   jupyter notebook notebooks/03_结果分析.ipynb")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️  训练被用户中断")
        return 1
    except Exception as e:
        logger.error(f"❌ 训练失败: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
