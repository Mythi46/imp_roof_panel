#!/usr/bin/env python3
"""
本地专家改进版训练脚本
Local expert improved training script

针对conda环境roof (Python 3.10.18)优化
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


def check_environment():
    """检查运行环境"""
    import platform
    
    print("🔍 环境检查...")
    print(f"   Python版本: {sys.version}")
    print(f"   平台: {platform.system()} {platform.release()}")
    
    # 检查conda环境
    conda_env = os.environ.get('CONDA_DEFAULT_ENV', 'base')
    if conda_env == 'roof':
        print(f"   ✅ Conda环境: {conda_env}")
    else:
        print(f"   ⚠️ Conda环境: {conda_env} (推荐使用roof)")
    
    # 检查GPU
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"   ✅ GPU: {gpu_name}")
        else:
            print(f"   ⚠️ GPU: 不可用，将使用CPU")
    except ImportError:
        print(f"   ❌ PyTorch未安装")
    
    # 检查关键依赖
    try:
        from ultralytics import YOLO
        import ultralytics
        print(f"   ✅ Ultralytics: {ultralytics.__version__}")
    except ImportError:
        print(f"   ❌ Ultralytics未安装")
        return False
    
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="🛰️ 本地专家改进版 - 卫星图像分割检测训练",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
专家改进功能:
  🎯 自动类别权重计算 - 基于有效样本数方法
  📐 统一解像度768 - 训练验证推理一致
  🔄 余弦退火+AdamW - 现代学习率策略
  🎨 分割友好增强 - 低Mosaic+Copy-Paste
  🚀 TTA+瓦片推理 - 高解像度支持

示例用法:
  python scripts/train_expert_local.py                    # 使用专家改进
  python scripts/train_expert_local.py --no-expert       # 使用原始配置
  python scripts/train_expert_local.py --epochs 100      # 长时间训练
  python scripts/train_expert_local.py --download        # 先下载数据
        """
    )
    
    # 基础参数
    parser.add_argument("--config", default="config/model_config.yaml", 
                       help="模型配置文件路径")
    parser.add_argument("--data", default="config/data.yaml", 
                       help="数据配置文件路径")
    parser.add_argument("--project", default="runs/segment", 
                       help="训练结果保存路径")
    parser.add_argument("--name", default="expert_local", 
                       help="训练任务名称")
    
    # 专家改进控制
    parser.add_argument("--no-expert", action="store_true",
                       help="禁用专家改进，使用原始配置")
    
    # 训练参数
    parser.add_argument("--epochs", type=int, default=60,
                       help="训练轮数")
    parser.add_argument("--batch", type=int, default=16,
                       help="批次大小")
    parser.add_argument("--lr0", type=float,
                       help="初始学习率 (专家改进默认2e-4)")
    parser.add_argument("--imgsz", type=int,
                       help="图像尺寸 (专家改进默认768)")
    
    # 数据参数
    parser.add_argument("--download", action="store_true", 
                       help="训练前先下载数据集")
    parser.add_argument("--data-config", default="config/data_config.yaml",
                       help="数据配置文件路径")
    
    # 其他选项
    parser.add_argument("--device", type=str, default="auto",
                       help="训练设备 (auto, cpu, 0, 1, 2, 3...)")
    parser.add_argument("--workers", type=int, default=4,
                       help="数据加载线程数")
    parser.add_argument("--verbose", action="store_true", 
                       help="详细输出")
    
    args = parser.parse_args()
    
    # 设置日志级别
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("🛰️ 本地专家改进版 - 卫星图像分割检测训练")
    print("=" * 60)
    
    # 环境检查
    if not check_environment():
        logger.error("❌ 环境检查失败")
        return 1
    
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
        use_expert = not args.no_expert
        train_kwargs = {
            'epochs': args.epochs,
            'batch': args.batch,
            'device': args.device,
            'workers': args.workers,
        }
        
        if args.lr0:
            train_kwargs['lr0'] = args.lr0
        if args.imgsz:
            train_kwargs['imgsz'] = args.imgsz
        
        # 显示训练信息
        logger.info("🚀 开始训练...")
        logger.info(f"📊 数据配置: {args.data}")
        logger.info(f"🎯 项目路径: {args.project}")
        logger.info(f"📝 任务名称: {args.name}")
        logger.info(f"🔧 专家改进: {'启用' if use_expert else '禁用'}")
        
        if use_expert:
            logger.info("🎯 专家改进功能:")
            logger.info("   ✅ 自动类别权重计算")
            logger.info("   ✅ 统一解像度768")
            logger.info("   ✅ 余弦退火+AdamW")
            logger.info("   ✅ 分割友好数据增强")
            logger.info("   ✅ 优化训练控制")
        
        if train_kwargs:
            logger.info(f"⚙️ 自定义参数: {train_kwargs}")
        
        # 6. 开始训练
        results = trainer.train(
            data_yaml=args.data,
            project=args.project,
            name=args.name,
            use_expert_improvements=use_expert,
            **train_kwargs
        )
        
        # 7. 显示结果
        best_model_path = trainer.get_best_model_path(args.project, args.name)
        results_dir = os.path.join(args.project, args.name)
        
        print("\n" + "=" * 60)
        print("🎉 训练完成!")
        print(f"📁 最佳模型: {best_model_path}")
        print(f"📊 结果目录: {results_dir}")
        print(f"📈 查看训练曲线: {os.path.join(results_dir, 'results.png')}")
        print(f"🔍 查看混淆矩阵: {os.path.join(results_dir, 'confusion_matrix.png')}")
        
        if use_expert:
            print("\n🎯 专家改进效果:")
            print("   • 自动类别权重 - 基于真实数据分布")
            print("   • 统一解像度 - 训练验证推理一致")
            print("   • 现代学习率 - 更稳定的收敛")
            print("   • 分割增强 - 更好的边缘质量")
        
        print("\n💡 下一步:")
        print(f"   python src/models/evaluate.py --model {best_model_path}")
        print(f"   jupyter notebook notebooks/03_结果分析.ipynb")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("⏹️ 训练被用户中断")
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
