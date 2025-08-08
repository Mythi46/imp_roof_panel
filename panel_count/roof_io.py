import cv2
import numpy as np
import logging
import os

def load_roof_mask_from_image(image_path, target_dimensions=None):
    """
    从图片文件加载屋顶掩膜

    Args:
        image_path: 图片文件路径
        target_dimensions: 目标尺寸 (高度, 宽度)，如果为None则使用原始尺寸

    Returns:
        二值化的屋顶掩膜
    """
    if not os.path.exists(image_path):
        logging.error(f"Image file not found: {image_path}")
        return None

    # 加载图片
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        logging.error(f"Failed to load image: {image_path}")
        return None

    # 调整尺寸（如果指定）
    if target_dimensions is not None:
        h, w = target_dimensions
        img = cv2.resize(img, (w, h))

    # 二值化处理
    # 使用Otsu阈值自动确定最佳阈值
    _, mask_bin = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    logging.info(f"Loaded roof mask from '{image_path}', size: {mask_bin.shape}")
    return mask_bin

def create_roof_mask(shape_name, dimensions=(400, 500)):
    """Generate binary mask for specified roof shape or load from image file"""
    # 检查是否是图片文件路径
    if shape_name.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        return load_roof_mask_from_image(shape_name, dimensions)

    # 原有的几何形状生成逻辑
    h, w = dimensions
    mask = np.zeros((h, w), np.uint8)

    if shape_name == "original_sample":
        cv2.rectangle(mask, (int(w*0.1), int(h*0.375)), (int(w*0.9), int(h*0.875)), 255, -1)
        pts = np.array([[int(w*0.1), int(h*0.375)], [int(w*0.5), int(h*0.125)], [int(w*0.9), int(h*0.375)]], np.int32)
        cv2.fillPoly(mask, [pts], 255)
    elif shape_name == "kiritsuma_side":  # 切妻屋根片面
        cv2.rectangle(mask, (int(w*0.1), int(h*0.1)), (int(w*0.9), int(h*0.9)), 255, -1)
    elif shape_name == "yosemune_main":  # 寄棟屋根主面
        pts = np.array([
            [int(w*0.1), int(h*0.7)], [int(w*0.9), int(h*0.7)],
            [int(w*0.7), int(h*0.2)], [int(w*0.3), int(h*0.2)]
        ], np.int32)
        cv2.fillPoly(mask, [pts], 255)
    elif shape_name == "katanagare":  # 片流れ屋根
        cv2.rectangle(mask, (int(w*0.1), int(h*0.15)), (int(w*0.9), int(h*0.85)), 255, -1)
    elif shape_name == "rikuyane":  # 陸屋根
        cv2.rectangle(mask, (int(w*0.05), int(h*0.05)), (int(w*0.95), int(h*0.95)), 255, -1)
    else:
        logging.warning(f"Unknown roof shape '{shape_name}', returning empty mask.")

    mask_bin = (mask > 127).astype(np.uint8) * 255
    return mask_bin

def visualize_result(original_mask, panels, filename="result_with_panels.png"):
    """Draw panels on roof mask and save image"""
    result_img = cv2.cvtColor(original_mask, cv2.COLOR_GRAY2BGR)
    for (x, y, w, h) in panels:
        cv2.rectangle(result_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
    cv2.imwrite(filename, result_img)
    logging.info(f"Saved result image to '{filename}'")
