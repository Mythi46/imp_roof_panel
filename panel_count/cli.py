import argparse
import logging
import sys
import os

def setup_logging(log_level):
    """ロギングの設定"""
    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'無効なログレベル: {log_level}')
    
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('panel_calculator.log', mode='w')
        ]
    )

def validate_args(args):
    """引数の有効性を検証する"""
    if args.gsd <= 0:
        raise ValueError(f'GSD must be positive, got: {args.gsd}')

    if args.offset < 0:
        raise ValueError(f'Offset must be non-negative, got: {args.offset}')

    if args.spacing < 0:
        raise ValueError(f'Panel spacing must be non-negative, got: {args.spacing}')

    # 有効な屋根タイプのリスト（画像ファイルも許可）
    valid_roof_types = ["original_sample", "kiritsuma_side", "yosemune_main", "katanagare", "rikuyane"]
    valid_image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

    for roof_type in args.roof_types:
        # 画像ファイルかどうかチェック
        is_image_file = any(roof_type.lower().endswith(ext) for ext in valid_image_extensions)

        if not is_image_file and roof_type not in valid_roof_types:
            raise ValueError(f'Invalid roof type: {roof_type}. Valid types: {valid_roof_types} or image files ({valid_image_extensions})')

        # 画像ファイルの場合、存在確認
        if is_image_file and not os.path.isfile(roof_type):
            raise ValueError(f'Image file not found: {roof_type}')

def parse_args():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(description='太陽光パネル配置計算ツール')

    parser.add_argument('--gsd', type=float, default=0.05,
                        help='Ground Sample Distance (m/pixel), デフォルト: 0.05')

    parser.add_argument('--offset', type=float, default=0.3,
                        help='屋根端からのオフセット (m), デフォルト: 0.3')

    parser.add_argument('--spacing', type=float, default=0.02,
                        help='パネル間の間隔 (m), デフォルト: 0.02')

    parser.add_argument('--fast', action='store_true',
                        help='高速アルゴリズムを使用する')

    parser.add_argument('--roof-types', nargs='+',
                        default=["original_sample", "kiritsuma_side", "yosemune_main", "katanagare", "rikuyane"],
                        help='計算する屋根タイプのリスト')

    parser.add_argument('--output-csv', type=str, default='result_summary.csv',
                        help='結果を保存するCSVファイル名')

    parser.add_argument('--log-level', type=str, default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='ログレベル')

    args = parser.parse_args()
    validate_args(args)
    return args

def save_results_to_csv(results, filename):
    """結果をCSVファイルに保存する"""
    import csv
    
    # CSVファイルが存在しない場合はヘッダーを書き込む
    file_exists = os.path.isfile(filename)
    
    with open(filename, 'a', newline='') as csvfile:
        fieldnames = [
            'roof_type', 'panel_name', 'count_area', 'count_sim', 
            'orientation', 'roof_area', 'effective_area', 
            'gsd', 'offset', 'panel_spacing'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        for result in results:
            if not result.get('success', False):
                continue
                
            for panel_name, panel_data in result['panels'].items():
                row = {
                    'roof_type': result['roof_type'],
                    'panel_name': panel_name,
                    'count_area': panel_data['count_area'],
                    'count_sim': panel_data['count_sim'],
                    'orientation': panel_data['orientation'],
                    'roof_area': result['roof_area'],
                    'effective_area': result['effective_area'],
                    'gsd': result['gsd'],
                    'offset': result['offset'],
                    'panel_spacing': result['panel_spacing']
                }
                writer.writerow(row)
    
    logging.info(f"結果を '{filename}' に保存しました。")
