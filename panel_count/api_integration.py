#!/usr/bin/env python3
"""
API集成模块 - 与屋顶检测分割系统的集成
Integration module for roof detection segmentation system
"""

import cv2
import base64
import numpy as np
import json
import logging
from flask import Flask, request, jsonify
from roof_io import visualize_result, create_roof_mask
from geometry import pixels_from_meters, erode_with_margin, calculate_panel_layout_fast, estimate_by_area
import tempfile
import os

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def b64_to_cv2(b64str, flags=cv2.IMREAD_UNCHANGED):
    """
    Base64文字列をOpenCV画像(NumPy配列)に変換
    Convert Base64 string to OpenCV image (NumPy array)
    
    Args:
        b64str: Base64エンコードされた画像文字列
        flags: OpenCVの読み込みフラグ
        
    Returns:
        OpenCV画像(NumPy配列)
    """
    try:
        # data URIの場合はカンマ以降を取得
        img_bytes = base64.b64decode(b64str.split(",")[-1])
        img_np = np.frombuffer(img_bytes, dtype=np.uint8)
        return cv2.imdecode(img_np, flags)
    except Exception as e:
        logger.error(f"Base64デコードエラー: {e}")
        return None

def process_segmented_roof(mask_image, centers, map_scale, spacing_interval, panel_options=None):
    """
    分割された屋根画像を処理して太陽能板配置を計算
    Process segmented roof image and calculate solar panel layout
    
    Args:
        mask_image: 分割マスク画像 (0/255)
        centers: 中心点座標のリスト
        map_scale: 地図スケール (m/pixel)
        spacing_interval: 間隔 (meters)
        panel_options: パネルオプション辞書
        
    Returns:
        計算結果の辞書
    """
    if panel_options is None:
        panel_options = {
            "Sharp_NQ-256AF": (1.318, 0.990),
            "Standard_A": (1.65, 0.99),
            "Standard_B": (1.50, 0.80)
        }
    
    # マスクが有効かチェック
    if mask_image is None or np.sum(mask_image) == 0:
        logger.warning("空のマスクまたは無効なマスクです")
        return {
            "success": False,
            "error": "empty_or_invalid_mask",
            "message": "マスクが空または無効です"
        }
    
    # マスクを二値化 (0/255)
    mask_bin = (mask_image > 127).astype(np.uint8) * 255
    
    # 有効エリアの計算（腐食処理）
    offset_px = pixels_from_meters(spacing_interval, map_scale)
    usable_area_mask = erode_with_margin(mask_bin, offset_px)
    
    # 面積計算
    pixel_area = map_scale ** 2
    effective_pixels = np.sum(usable_area_mask) / 255
    effective_area_sqm = effective_pixels * pixel_area
    
    roof_pixels = np.sum(mask_bin) / 255
    roof_area_sqm = roof_pixels * pixel_area
    
    logger.info(f"屋根面積: {roof_area_sqm:.2f} m^2")
    logger.info(f"有効面積: {effective_area_sqm:.2f} m^2")
    
    results = {
        "success": True,
        "roof_area": roof_area_sqm,
        "effective_area": effective_area_sqm,
        "map_scale": map_scale,
        "spacing_interval": spacing_interval,
        "centers": centers,
        "panels": {},
        "best_panel": None,
        "max_count": -1
    }
    
    best_panel_for_vis = None
    max_panels_for_vis = -1
    
    # 各パネルタイプで計算
    for panel_name, panel_size in panel_options.items():
        panel_length, panel_width = panel_size
        logger.info(f"パネル計算: {panel_name} ({panel_length}m x {panel_width}m)")
        
        # 面積ベースの計算
        count_area = estimate_by_area(effective_area_sqm, panel_size)
        
        # パネル間の間隔を含めたサイズ計算
        panel_spacing_m = 0.02  # デフォルト2cm間隔
        panel_l_with_spacing = panel_length + panel_spacing_m
        panel_w_with_spacing = panel_width + panel_spacing_m
        
        # ピクセルへの変換
        panel_l_px = pixels_from_meters(panel_l_with_spacing, map_scale)
        panel_w_px = pixels_from_meters(panel_w_with_spacing, map_scale)
        
        # 縦置きと横置きの両方を試す
        count_v, panels_v = calculate_panel_layout_fast(usable_area_mask.copy(), panel_w_px, panel_l_px)
        count_h, panels_h = calculate_panel_layout_fast(usable_area_mask.copy(), panel_l_px, panel_w_px)
        
        # 最適な配置方向を選択
        if count_v >= count_h:
            count_placement = count_v
            best_panels_for_panel_type = panels_v
            orientation = "vertical"
        else:
            count_placement = count_h
            best_panels_for_panel_type = panels_h
            orientation = "horizontal"
        
        logger.info(f"配置結果: {count_placement} 枚 (縦:{count_v}, 横:{count_h})")
        
        # 結果を記録 (numpy型をPython標準型に変換)
        panel_result = {
            "panel_name": panel_name,
            "panel_size": list(panel_size),
            "count_area": int(count_area),
            "count_sim": int(count_placement),
            "orientation": orientation,
            "panels": [[int(p[0]), int(p[1]), int(p[2]), int(p[3])] for p in best_panels_for_panel_type]
        }
        
        results["panels"][panel_name] = panel_result
        
        # 最適なパネルを記録
        if count_placement > max_panels_for_vis:
            max_panels_for_vis = count_placement
            best_panel_for_vis = (best_panels_for_panel_type, panel_name)
            results["best_panel"] = panel_name
            results["max_count"] = int(count_placement)
    
    # 可視化画像を生成
    if best_panel_for_vis:
        panels, panel_name = best_panel_for_vis
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            visualize_result(mask_bin, panels, filename=tmp_file.name)
            results["visualization_file"] = tmp_file.name
    
    return results

def calculate_single_roof(roof_mask, gsd, panel_options, offset_m=1.0, panel_spacing_m=0.02):
    """
    单个屋顶的太阳能板配置计算
    Calculate solar panel layout for a single roof

    Args:
        roof_mask: Binary roof mask (numpy array)
        gsd: Ground Sample Distance (m/pixel)
        panel_options: Dictionary of panel options {name: (length, width)}
        offset_m: Safety margin in meters
        panel_spacing_m: Panel spacing in meters

    Returns:
        Dictionary with calculation results
    """
    # マスクが有効かチェック
    if roof_mask is None or np.sum(roof_mask) == 0:
        logger.warning("空のマスクまたは無効なマスクです")
        return {
            "success": False,
            "error": "empty_or_invalid_mask",
            "message": "マスクが空または無効です"
        }

    # マスクを二値化 (0/255)
    mask_bin = (roof_mask > 127).astype(np.uint8) * 255

    # 有効エリアの計算（腐食処理）
    offset_px = pixels_from_meters(offset_m, gsd)
    usable_area_mask = erode_with_margin(mask_bin, offset_px)

    # 面積計算
    pixel_area = gsd ** 2
    effective_pixels = np.sum(usable_area_mask) / 255
    effective_area_sqm = effective_pixels * pixel_area

    roof_pixels = np.sum(mask_bin) / 255
    roof_area_sqm = roof_pixels * pixel_area

    logger.info(f"屋根面積: {roof_area_sqm:.2f} m^2")
    logger.info(f"有効面積: {effective_area_sqm:.2f} m^2")

    results = {
        "success": True,
        "roof_area": float(roof_area_sqm),
        "effective_area": float(effective_area_sqm),
        "gsd": float(gsd),
        "offset_m": float(offset_m),
        "panel_spacing_m": float(panel_spacing_m),
        "panels": {},
        "best_panel": None,
        "max_count": -1
    }

    best_panel_for_vis = None
    max_panels_for_vis = -1

    # 各パネルタイプで計算
    for panel_name, panel_size in panel_options.items():
        panel_length, panel_width = panel_size
        logger.info(f"パネル計算: {panel_name} ({panel_length}m x {panel_width}m)")

        # 面積ベースの計算
        count_area = estimate_by_area(effective_area_sqm, panel_size)

        # パネル間の間隔を含めたサイズ計算
        panel_l_with_spacing = panel_length + panel_spacing_m
        panel_w_with_spacing = panel_width + panel_spacing_m

        # ピクセルへの変換
        panel_l_px = pixels_from_meters(panel_l_with_spacing, gsd)
        panel_w_px = pixels_from_meters(panel_w_with_spacing, gsd)

        # 縦置きと横置きの両方を試す
        count_v, panels_v = calculate_panel_layout_fast(usable_area_mask.copy(), panel_w_px, panel_l_px)
        count_h, panels_h = calculate_panel_layout_fast(usable_area_mask.copy(), panel_l_px, panel_w_px)

        # 最適な配置方向を選択
        if count_v >= count_h:
            count_placement = count_v
            best_panels_for_panel_type = panels_v
            orientation = "vertical"
        else:
            count_placement = count_h
            best_panels_for_panel_type = panels_h
            orientation = "horizontal"

        logger.info(f"配置結果: {count_placement} 枚 (縦:{count_v}, 横:{count_h})")

        # 結果を記録 (numpy型をPython標準型に変換)
        panel_result = {
            "panel_name": panel_name,
            "panel_size": list(panel_size),
            "count_area": int(count_area),
            "count_sim": int(count_placement),
            "orientation": orientation,
            "panels": [[int(p[0]), int(p[1]), int(p[2]), int(p[3])] for p in best_panels_for_panel_type]
        }

        results["panels"][panel_name] = panel_result

        # 最適なパネルを記録
        if count_placement > max_panels_for_vis:
            max_panels_for_vis = count_placement
            best_panel_for_vis = (best_panels_for_panel_type, panel_name)
            results["best_panel"] = panel_name
            results["max_count"] = int(count_placement)

    # 可視化画像を生成
    if best_panel_for_vis:
        panels, panel_name = best_panel_for_vis
        # 一時ファイルに保存
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
            visualize_result(mask_bin, panels, filename=tmp_file.name)
            results["visualization_file"] = tmp_file.name

    return results

def visualize_panels_on_mask(roof_mask, panels):
    """
    在屋顶掩码上可视化太阳能板
    Visualize solar panels on roof mask
    """
    # 创建彩色图像
    vis_img = cv2.cvtColor(roof_mask, cv2.COLOR_GRAY2BGR)

    # 绘制太阳能板
    for panel in panels:
        x, y, w, h = panel
        # 绘制矩形框 (蓝色)
        cv2.rectangle(vis_img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        # 填充半透明 (绿色)
        overlay = vis_img.copy()
        cv2.rectangle(overlay, (x, y), (x + w, y + h), (0, 255, 0), -1)
        cv2.addWeighted(overlay, 0.3, vis_img, 0.7, 0, vis_img)

    return vis_img

def process_multiple_roof_masks(roof_masks_b64, gsd, offset_m, panel_spacing_m, panel_options):
    """
    批量处理多个屋顶掩码
    Process multiple roof masks in batch
    """
    try:
        results = {
            "success": True,
            "total_roofs": len(roof_masks_b64),
            "roofs": [],
            "summary": {
                "total_panels": 0,
                "total_capacity_kw": 0.0,
                "total_roof_area": 0.0,
                "total_effective_area": 0.0
            }
        }

        for i, roof_mask_b64 in enumerate(roof_masks_b64):
            logger.info(f"処理中の屋根 {i+1}/{len(roof_masks_b64)}")

            # Base64をデコード
            roof_mask = b64_to_cv2(roof_mask_b64, cv2.IMREAD_GRAYSCALE)

            if roof_mask is None:
                results["roofs"].append({
                    "roof_id": i,
                    "success": False,
                    "error": "decode_error",
                    "message": f"屋根{i+1}のマスクデコードに失敗"
                })
                continue

            # 個別の屋根を処理
            try:
                roof_result = calculate_panel_layout_fast(
                    roof_mask, gsd, offset_m, panel_spacing_m, panel_options
                )

                # 結果を追加
                roof_result["roof_id"] = i
                roof_result["success"] = True

                # 可視化を生成
                if roof_result.get("panels"):
                    best_panel = roof_result["best_panel"]
                    panels = roof_result["panels"][best_panel]["panels"]

                    # 可視化画像をBase64で生成
                    vis_img = visualize_panels_on_mask(roof_mask, panels)
                    _, buffer = cv2.imencode('.png', vis_img)
                    vis_b64 = base64.b64encode(buffer).decode('utf-8')
                    roof_result["visualization_b64"] = f"data:image/png;base64,{vis_b64}"

                results["roofs"].append(roof_result)

                # サマリーを更新
                results["summary"]["total_panels"] += roof_result.get("max_count", 0)
                results["summary"]["total_capacity_kw"] += roof_result.get("total_capacity_kw", 0.0)
                results["summary"]["total_roof_area"] += roof_result.get("roof_area", 0.0)
                results["summary"]["total_effective_area"] += roof_result.get("effective_area", 0.0)

            except Exception as e:
                logger.error(f"屋根{i+1}の処理エラー: {str(e)}")
                results["roofs"].append({
                    "roof_id": i,
                    "success": False,
                    "error": "calculation_error",
                    "message": f"屋根{i+1}の計算エラー: {str(e)}"
                })

        return jsonify(results)

    except Exception as e:
        logger.error(f"批量処理エラー: {str(e)}")
        return jsonify({
            "success": False,
            "error": "batch_processing_error",
            "message": f"批量処理エラー: {str(e)}"
        }), 500

@app.route('/calculate_panels', methods=['POST'])
def calculate_panels():
    """
    太陽光パネル配置を計算する標準API
    Standard API for calculating solar panel layout

    Supports three input methods:
    1. roof_masks: Array of Base64 encoded roof masks (NEW - for batch processing)
    2. roof_mask: Single Base64 encoded binary roof mask
    3. roof_shape_name: Predefined roof shape for testing

    Example for batch processing:
    {
        "roof_masks": [
            "data:image/png;base64,iVBORw0KGg...",
            "data:image/png;base64,iVBORw0KGg..."
        ],
        "gsd": 0.05,
        "panel_options": {"Standard_B": [1.65, 1.0]},
        "offset_m": 1.0
    }
    """
    try:
        # リクエストデータを取得
        data = request.get_json()

        if not data:
            return jsonify({
                "success": False,
                "error": "no_data",
                "message": "リクエストデータがありません"
            }), 400

        # パラメータを取得
        gsd = data.get('gsd', 0.05)
        offset_m = data.get('offset_m', 1.0)
        panel_spacing_m = data.get('panel_spacing_m', 0.02)
        panel_options = data.get('panel_options', {
            "Standard_B": [1.65, 1.0]
        })

        # パネルオプションを辞書形式に変換
        if isinstance(panel_options, dict):
            panel_options = {k: tuple(v) if isinstance(v, list) else v for k, v in panel_options.items()}

        logger.info(f"リクエスト受信: gsd={gsd}, offset_m={offset_m}")

        # 入力方法を判定
        roof_mask_b64 = data.get('roof_mask')
        roof_masks_b64 = data.get('roof_masks')  # 新增：批量处理
        roof_shape_name = data.get('roof_shape_name')

        if roof_masks_b64:
            # Method 1a: Multiple Base64 encoded roof masks (NEW)
            logger.info(f"批量Base64屋根マスクを使用: {len(roof_masks_b64)}個")
            return process_multiple_roof_masks(roof_masks_b64, gsd, offset_m, panel_spacing_m, panel_options)

        elif roof_mask_b64:
            # Method 1: Base64 encoded roof mask
            logger.info("Base64屋根マスクを使用")
            roof_mask = b64_to_cv2(roof_mask_b64, cv2.IMREAD_GRAYSCALE)

            if roof_mask is None:
                return jsonify({
                    "success": False,
                    "error": "decode_error",
                    "message": "屋根マスクのデコードに失敗しました"
                }), 400

        elif roof_shape_name:
            # Method 2: Predefined roof shape
            logger.info(f"事前定義屋根形状を使用: {roof_shape_name}")
            dimensions = data.get('dimensions', [400, 500])

            try:
                roof_mask = create_roof_mask(roof_shape_name, tuple(dimensions))
                if roof_mask is None or np.sum(roof_mask) == 0:
                    return jsonify({
                        "success": False,
                        "error": "invalid_roof_shape",
                        "message": f"屋根形状 '{roof_shape_name}' が見つからないか無効です"
                    }), 400
            except Exception as e:
                return jsonify({
                    "success": False,
                    "error": "roof_shape_error",
                    "message": f"屋根形状の生成エラー: {str(e)}"
                }), 400

        else:
            return jsonify({
                "success": False,
                "error": "missing_input",
                "message": "roof_mask または roof_shape_name のいずれかが必要です"
            }), 400

        # 太陽光パネル配置を計算
        result = calculate_single_roof(
            roof_mask=roof_mask,
            gsd=gsd,
            panel_options=panel_options,
            offset_m=offset_m,
            panel_spacing_m=panel_spacing_m
        )

        if not result.get('success'):
            return jsonify(result), 400

        # 可視化ファイルがある場合はBase64エンコードして返す
        if "visualization_file" in result:
            try:
                with open(result["visualization_file"], 'rb') as img_file:
                    img_b64 = base64.b64encode(img_file.read()).decode('utf-8')
                    result["visualization_b64"] = f"data:image/png;base64,{img_b64}"
                # 一時ファイルを削除
                os.unlink(result["visualization_file"])
                del result["visualization_file"]
            except Exception as e:
                logger.warning(f"可視化画像の処理エラー: {e}")

        # 追加情報を含める
        if roof_shape_name:
            result["roof_type"] = roof_shape_name

        # 総容量を計算 (400W per panel assumed)
        if result.get('max_count', 0) > 0:
            result["total_capacity_kw"] = result['max_count'] * 0.4

        return jsonify(result)

    except Exception as e:
        logger.error(f"処理エラー: {e}")
        return jsonify({
            "success": False,
            "error": "processing_error",
            "message": str(e)
        }), 500

# REMOVED: Deprecated endpoint - see ARCHITECTURE_REFACTOR_PLAN.md
def process_roof_segments_deprecated():
    """
    DEPRECATED: 旧API端点 - 互換性のために残されています
    DEPRECATED: Legacy API endpoint - kept for compatibility

    Please use /calculate_panels instead
    """
    logger.warning("DEPRECATED: /process_roof_segments endpoint used. Please migrate to /calculate_panels")

    return jsonify({
        "success": False,
        "error": "deprecated_endpoint",
        "message": "このエンドポイントは非推奨です。/calculate_panels を使用してください。",
        "deprecated": True,
        "new_endpoint": "/calculate_panels",
        "migration_guide": {
            "old_format": "segments array with mask_base64",
            "new_format": "single roof_mask (base64) or roof_shape_name",
            "example": {
                "roof_mask": "base64_encoded_image",
                "gsd": 0.05,
                "panel_options": {"Standard_B": [1.65, 1.0]},
                "offset_m": 1.0
            }
        }
    }), 410  # HTTP 410 Gone

# REMOVED: Deprecated endpoint - see ARCHITECTURE_REFACTOR_PLAN.md
def segment_click_adapter():
    """
    DEPRECATED: 屋根分割システムとの互換性のためのアダプター
    DEPRECATED: Adapter for compatibility with roof segmentation system

    This endpoint redirects to /calculate_panels with converted parameters
    """
    logger.warning("DEPRECATED: /segment_click endpoint used. Redirecting to /calculate_panels")

    try:
        # リクエストデータを取得 (JSONまたはForm data)
        if request.is_json:
            data = request.get_json()
            mask_b64 = data.get('mask')
            centers = data.get('centers', [])
            center_latitude = data.get('center_latitude', 35.6895)
            map_scale = data.get('map_scale', 0.05)
            spacing_interval = data.get('spacing_interval', 0.3)
        else:
            return jsonify({
                "success": False,
                "error": "form_data_not_supported",
                "message": "このエンドポイントはJSONデータのみサポートします。/calculate_panels を使用してください。"
            }), 400

        # 新しいAPI形式に変換
        new_request_data = {
            "roof_mask": mask_b64,
            "gsd": map_scale,
            "offset_m": spacing_interval,
            "panel_options": {
                "Standard_B": [1.65, 1.0]
            }
        }

        # 内部的に新しいAPIを呼び出し
        with app.test_request_context('/calculate_panels', method='POST', json=new_request_data):
            response = calculate_panels()

        # レスポンスにdeprecation警告を追加
        if hasattr(response, 'get_json'):
            result = response.get_json()
            if isinstance(result, dict):
                result["deprecated_endpoint_used"] = "/segment_click"
                result["recommended_endpoint"] = "/calculate_panels"
                result["migration_note"] = "このエンドポイントは非推奨です。/calculate_panels を使用してください。"

        return response

    except Exception as e:
        logger.error(f"アダプター処理エラー: {e}")
        return jsonify({
            "success": False,
            "error": "processing_error",
            "message": str(e),
            "deprecated_endpoint_used": "/segment_click",
            "recommended_endpoint": "/calculate_panels"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        "status": "healthy",
        "service": "solar_panel_calculator",
        "version": "2.0.0",
        "api_endpoints": {
            "primary": "/calculate_panels",
            "deprecated": ["/process_roof_segments", "/segment_click"],
            "health": "/health"
        },
        "supported_input_methods": [
            "roof_mask (base64 encoded binary image)",
            "roof_shape_name (predefined shapes for testing)"
        ]
    })

if __name__ == '__main__':
    # 開発用サーバーを起動 (ポート8001で起動、屋根検出システムは8000)
    port = int(os.environ.get('FLASK_RUN_PORT', 8001))
    app.run(host='0.0.0.0', port=port, debug=True)
