import numpy as np
import logging
from roof_io import create_roof_mask, visualize_result
from geometry import pixels_from_meters, erode_with_margin, calculate_panel_layout_fast, calculate_panel_layout_original, estimate_by_area

def process_roof(roof_shape_name, gsd, panel_options, offset_m, panel_spacing_m=0.02, dimensions=(400,500), use_fast_algorithm=True):
    """
    屋根形状に対してパネル配置計算を行う
    
    Args:
        roof_shape_name: 屋根形状の名前
        gsd: Ground Sample Distance (m/pixel)
        panel_options: パネルオプションの辞書 {名前: (長さ, 幅)}
        offset_m: 屋根端からのオフセット (m)
        panel_spacing_m: パネル間の間隔 (m)
        dimensions: マスク画像のサイズ (高さ, 幅)
        use_fast_algorithm: 高速アルゴリズムを使用するかどうか
        
    Returns:
        計算結果の辞書
    """
    logging.info(f"\n--- {roof_shape_name} の計算開始 ---")
    
    # 屋根マスクの生成（自動的に二値化される）
    roof_mask = create_roof_mask(roof_shape_name, dimensions)
    if np.sum(roof_mask) == 0:  # マスクが空ならスキップ
        logging.warning(f"'{roof_shape_name}' は空のマスクのためスキップします。")
        return {
            "roof_type": roof_shape_name,
            "error": "empty_mask",
            "success": False
        }

    # 有効エリアの計算（腐食処理）
    offset_px = pixels_from_meters(offset_m, gsd)
    usable_area_mask = erode_with_margin(roof_mask, offset_px)

    # 有効面積(m^2)の計算
    pixel_area = gsd**2
    effective_pixels = np.sum(usable_area_mask) / 255
    effective_area_sqm = effective_pixels * pixel_area
    
    roof_pixels = np.sum(roof_mask) / 255
    roof_area_sqm = roof_pixels * pixel_area

    logging.info(f"  屋根面積: {roof_area_sqm:.2f} m^2")
    logging.info(f"  有効面積: {effective_area_sqm:.2f} m^2 (オフセット: {offset_m}m)")

    results = {
        "roof_type": roof_shape_name,
        "roof_area": roof_area_sqm,
        "effective_area": effective_area_sqm,
        "gsd": gsd,
        "offset": offset_m,
        "panel_spacing": panel_spacing_m,
        "panels": {},
        "success": True,
        "best_panel": None,
        "max_count": -1
    }
    
    best_panel_for_vis = None
    max_panels_for_vis = -1
    
    for panel_name, panel_size in panel_options.items():
        panel_length, panel_width = panel_size
        logging.info(f"  - パネル: {panel_name} ({panel_length}m x {panel_width}m)")

        # 面積ベースの計算
        count_area = estimate_by_area(effective_area_sqm, panel_size)
        logging.info(f"    - 面積ベースの概算: {count_area} 枚")

        # パネル間の間隔を含めたサイズ計算
        panel_l_with_spacing = panel_length + panel_spacing_m
        panel_w_with_spacing = panel_width + panel_spacing_m
        
        # ピクセルへの変換（切り上げ）
        panel_l_px = pixels_from_meters(panel_l_with_spacing, gsd)
        panel_w_px = pixels_from_meters(panel_w_with_spacing, gsd)

        # 配置アルゴリズムの選択
        calc_func = calculate_panel_layout_fast if use_fast_algorithm else calculate_panel_layout_original
        
        # 縦置きと横置きの両方を試す
        count_v, panels_v = calc_func(usable_area_mask.copy(), panel_w_px, panel_l_px)
        count_h, panels_h = calc_func(usable_area_mask.copy(), panel_l_px, panel_w_px)
        
        # 最適な配置方向を選択
        if count_v >= count_h:
            count_placement = count_v
            best_panels_for_panel_type = panels_v
            orientation = "vertical"
        else:
            count_placement = count_h
            best_panels_for_panel_type = panels_h
            orientation = "horizontal"

        logging.info(f"    - 配置シミュレーション: {count_placement} 枚 (縦:{count_v}, 横:{count_h})")
        
        # 結果を記録
        panel_result = {
            "panel_name": panel_name,
            "panel_size": panel_size,
            "count_area": count_area,
            "count_sim": count_placement,
            "orientation": orientation,
            "panels": best_panels_for_panel_type
        }
        
        results["panels"][panel_name] = panel_result
        
        # 最適なパネルを記録
        if count_placement > max_panels_for_vis:
            max_panels_for_vis = count_placement
            # ファイル名に安全な文字列を生成
            safe_roof_name = roof_shape_name.replace('/', '_').replace('\\', '_').replace(':', '_').replace('{', '').replace('}', '').replace("'", '').replace(' ', '_')
            safe_panel_name = panel_name.replace(' ', '_')
            best_panel_for_vis = (best_panels_for_panel_type, f"{safe_roof_name}_{safe_panel_name}")
            results["best_panel"] = panel_name
            results["max_count"] = count_placement

    # 最適なパネル配置の可視化
    if best_panel_for_vis:
        panels, name = best_panel_for_vis
        output_filename = f"result_{name}.png"
        visualize_result(roof_mask, panels, filename=output_filename)
        results["visualization_file"] = output_filename

    logging.info(f"--- {roof_shape_name} の計算終了 ---")
    return results
