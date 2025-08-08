# segmentation.py
import io
import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Tuple

from ultralytics import YOLO
from dotenv import load_dotenv
from app.util import letterbox, make_full_mask_png
from typing import List,Tuple

from app.util import make_full_mask_png  

# ─── モデル読込 ─────────────────────────────────
import os
from pathlib import Path

# 開発環境とDocker環境の両方に対応 + preroof 強化版の自動検出
current_dir = Path(__file__).parent.parent  # /app/roof
repo_root = current_dir.parent             # プロジェクトルート

# 優先順位: 環境変数 > preroof 強化版（開発時のみ）
env_model_path = os.getenv("ROOF_MODEL_PATH")
if env_model_path:
    model_path = Path(env_model_path)
else:
    # 開発作業時の便宜上、preroof の学習成果を自動検出（本番では必ず ROOF_MODEL_PATH を指定）
    preroof_candidate = repo_root / "preroof/runs/segment/continue_training_optimized/weights/best.pt"
    if preroof_candidate.exists():
        model_path = preroof_candidate
    else:
        raise FileNotFoundError(
            "No model path provided. Set ROOF_MODEL_PATH to a valid model file. "
            "For development you can place preroof weights under preroof/runs/.../best.pt."
        )

# PyTorch version compatibility fix
import torch

# Only use add_safe_globals if available (PyTorch 2.1+)
if hasattr(torch.serialization, 'add_safe_globals'):
    try:
        # Import ultralytics classes
        from ultralytics.nn.tasks import SegmentationModel
        from ultralytics.nn.modules.conv import Conv
        from ultralytics.nn.modules.block import C2f
        from ultralytics.nn.modules.head import Segment

        # Import standard PyTorch classes that are commonly needed
        from torch.nn.modules.container import Sequential
        from torch.nn.modules.linear import Linear
        from torch.nn.modules.conv import Conv2d
        from torch.nn.modules.batchnorm import BatchNorm2d
        from torch.nn.modules.activation import ReLU, SiLU

        torch.serialization.add_safe_globals([
            # Ultralytics classes
            SegmentationModel,
            Conv,
            C2f,
            Segment,
            # Standard PyTorch classes
            Sequential,
            Linear,
            Conv2d,
            BatchNorm2d,
            ReLU,
            SiLU
        ])
    except ImportError:
        # If modules can't be imported, skip safe globals
        pass

# 默认禁用模拟模型，除非显式开启
USE_MOCK_MODEL = os.getenv('USE_MOCK_MODEL', 'false').lower() == 'true'

if USE_MOCK_MODEL:
    print("⚠️  Using mock model for development")
    model = None
else:
    # Load YOLO model with PyTorch 2.6+ compatibility
    print(f"🔄 Loading YOLO model from: {model_path}")
    print(f"📁 Model file exists: {model_path.exists()}")
    if model_path.exists():
        print(f"📊 Model file size: {model_path.stat().st_size} bytes")

    try:
        model = YOLO(str(model_path))
        print(f"✅ YOLO model loaded successfully")
        print(f"🏷️  Model task: {getattr(model, 'task', 'unknown')}")
        print(f"🔧 Model type: {type(model)}")
    except Exception as e:
        print(f"❌ Error loading YOLO model: {e}")
        print(f"🔍 Error type: {type(e)}")

        if "weights_only" in str(e):
            print("🔧 Attempting to load with weights_only=False...")
            # For PyTorch 2.6+, temporarily disable weights_only for trusted model
            import torch
            original_load = torch.load
            torch.load = lambda *args, **kwargs: original_load(*args, **{**kwargs, 'weights_only': False})
            try:
                model = YOLO(str(model_path))
                print("✅ YOLO model loaded successfully with weights_only=False")
            finally:
                torch.load = original_load
        else:
            print(f"💥 Model file incompatible, falling back to mock mode")
            print(f"🔄 Setting USE_MOCK_MODEL=True due to model compatibility issue")
            USE_MOCK_MODEL = True
            model = None

# ─── 推論メイン関数 ─────────────────────────────
def process_image(image_bytes: bytes, conf: float = 0.8) -> Tuple[List[bytes], List[Tuple[int, int]]]:
    """
    Args:
        image_bytes : アップロード画像（バイト列）
        conf        : 信頼度閾値
    Returns:
        png_bytes_list : 個々のマスクを重ねた RGBA-PNG バイト列のリスト
        centers        : 各マスク重心座標 [(x, y), ...]  ※元画像座標系
    """
    # ① バイト列 → OpenCV BGR
    arr = np.frombuffer(image_bytes, np.uint8)
    img_bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img_bgr is None:
        raise ValueError("画像のデコードに失敗しました")

    H_orig, W_orig = img_bgr.shape[:2]

    # ② 推論
    if USE_MOCK_MODEL or model is None:
        # 模拟模式：返回测试数据
        print("🔧 Mock mode: generating test roof segments")

        # 创建模拟的屋顶区域
        h, w = H_orig, W_orig
        mock_mask = np.zeros((h, w), dtype=np.uint8)

        # 创建一个矩形屋顶区域
        x1, y1 = w//4, h//4
        x2, y2 = 3*w//4, 3*h//4
        mock_mask[y1:y2, x1:x2] = 255

        # 转换为PNG字节
        _, buffer = cv2.imencode('.png', mock_mask)
        png_bytes = buffer.tobytes()

        # 计算中心点
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2

        return [png_bytes], [(center_x, center_y)]

    else:
        # 真实模型推论
        try:
            print(f"🔍 Running model prediction with conf={conf}")
            print(f"🖼️  Input image shape: {img_bgr.shape}")
            print(f"🤖 Model object: {model}")
            print(f"🔧 Model attributes: {dir(model)}")

            # Try different prediction approaches
            try:
                results = model.predict(img_bgr, conf=conf, verbose=False)[0]
                print(f"✅ Model prediction completed")
                print(f"📊 Results type: {type(results)}")
                print(f"🔧 Results attributes: {dir(results)}")

                # Check if results has masks attribute
                if hasattr(results, 'masks'):
                    print(f"✅ Results has masks attribute")
                    if results.masks is None:
                        print("⚠️  No masks detected in results")
                        return [], []
                else:
                    print("❌ Results object has no masks attribute")
                    print(f"📋 Available attributes: {[attr for attr in dir(results) if not attr.startswith('_')]}")
                    return [], []

            except AttributeError as attr_e:
                print(f"❌ AttributeError during prediction: {attr_e}")
                # Try alternative prediction method
                try:
                    print("🔄 Trying alternative prediction method...")
                    results = model(img_bgr, conf=conf, verbose=False)[0]
                    print(f"✅ Alternative prediction completed")
                    print(f"📊 Results type: {type(results)}")
                except Exception as alt_e:
                    print(f"❌ Alternative method also failed: {alt_e}")
                    raise attr_e

        except Exception as e:
            print(f"❌ Error during model prediction: {e}")
            print(f"🔍 Error type: {type(e)}")

            # If model prediction fails due to compatibility issues, fall back to mock mode
            if "'Segment' object has no attribute 'detect'" in str(e):
                print("🔄 Model compatibility issue detected, falling back to mock mode for this request")
                # Generate mock result similar to mock mode
                h, w = H_orig, W_orig
                mock_mask = np.zeros((h, w), dtype=np.uint8)
                x1, y1 = w//4, h//4
                x2, y2 = 3*w//4, 3*h//4
                mock_mask[y1:y2, x1:x2] = 255

                _, buffer = cv2.imencode('.png', mock_mask)
                png_bytes = buffer.tobytes()
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2

                print("⚠️  Returned mock result due to model compatibility issue")
                return [png_bytes], [(center_x, center_y)]
            else:
                raise e

    masks_net = results.masks.data.cpu().numpy()  # (N, H_net, W_net)
    if masks_net.size == 0:
        return [], []

    png_bytes_list: List[bytes] = []
    centers: List[Tuple[int, int]] = []

    for mask_net in masks_net:
        # ─── (1) ネットワーク出力サイズ → 元画像サイズへリサイズ ───
        mask_resized = cv2.resize(
            mask_net,                     # float32 (0.0–1.0)
            (W_orig, H_orig),
            interpolation=cv2.INTER_NEAREST,
        )
        # (2) 2値化
        mask = (mask_resized > 0.5).astype(np.uint8)   # 0 or 1

        # ─── ここから変更 ───
        # ——— マスクだけの白黒画像 (Lモード) を作成 ———
        mask_img = (mask * 255).astype(np.uint8)    # 0→0, 1→255
        canvas = np.zeros((H_orig, W_orig, 4), dtype=np.uint8)
        canvas[..., :3] = img_bgr
        canvas[..., 3] = mask_img               # α チャンネルにマスク

        pil_rgba = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGRA2RGBA))  # PIL用に変換
        buf = io.BytesIO()
        pil_rgba.save(buf, format="PNG")
        png_bytes_list.append(buf.getvalue())

        # 重心だけはそのまま計算
        ys, xs = np.where(mask > 0)
        if len(xs) > 0 and len(ys) > 0:
            center_x = int(xs.mean())
            center_y = int(ys.mean())
        else:
            center_x = center_y = None
        centers.append((center_x, center_y))

    return png_bytes_list, centers