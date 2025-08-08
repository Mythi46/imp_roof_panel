import cv2
import numpy as np
from PIL import Image

def letterbox(img: np.ndarray, new_shape: tuple[int,int]) -> np.ndarray:
    """YOLO入力サイズにリサイズ"""
    h0, w0 = img.shape[:2]
    nh, nw = new_shape
    r = min(nh/h0, nw/w0)
    nh_resize, nw_resize = int(h0 * r), int(w0 * r)
    resized = cv2.resize(img, (nw_resize, nh_resize))
    pad_w, pad_h = nw - nw_resize, nh - nh_resize
    left, right = pad_w//2, pad_w - pad_w//2
    top, bottom = pad_h//2, pad_h - pad_h//2
    return cv2.copyMakeBorder(resized, top, bottom, left, right,
                              cv2.BORDER_CONSTANT, value=(114,114,114))

def make_full_mask_png(orig_bgr: np.ndarray, mask: np.ndarray) -> Image.Image:
    """
    mask: (H,W) の 0/1 numpy array  
    orig_bgr: 同じサイズの BGR 画像  
    → RGBA の PIL.Image を返す
    """
    H, W = mask.shape
    full_mask = np.zeros((H, W), dtype=np.uint8)
    full_mask[mask > 0] = 255

    canvas = np.zeros((H, W, 4), dtype=np.uint8)
    canvas[..., :3] = orig_bgr[..., ::-1]  # BGR→RGB
    canvas[..., 3]     = full_mask         # α チャンネル
    return Image.fromarray(canvas, mode="RGBA")
