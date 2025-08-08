import logging
import sys
import traceback
from cli import parse_args, setup_logging, save_results_to_csv
from planner import process_roof

def main():
    """メイン関数"""
    try:
        # コマンドライン引数の解析
        args = parse_args()

        # ロギングの設定
        setup_logging(args.log_level)
    except ValueError as e:
        print(f"引数エラー: {e}", file=sys.stderr)
        return 1
    
    # テストするパネルのサイズ (名前: (縦, 横))
    panel_options = {
        "Sharp_NQ-256AF": (1.318, 0.990),
        "Standard_A": (1.65, 0.99),
        "Standard_B": (1.50, 0.80)
    }
    
    # 各屋根タイプに対して計算を実行
    results = []
    for roof_type in args.roof_types:
        result = process_roof(
            roof_type, 
            args.gsd, 
            panel_options, 
            args.offset, 
            args.spacing, 
            use_fast_algorithm=args.fast
        )
        results.append(result)
    
    # 結果をCSVに保存
    save_results_to_csv(results, args.output_csv)
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        logging.error(f"スクリプトの実行中に予期せぬエラーが発生しました: {e}")
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)
