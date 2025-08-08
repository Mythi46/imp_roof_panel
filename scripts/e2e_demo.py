#!/usr/bin/env python3
"""
Simple end-to-end demo (configurable):
- Read an image
- Call roof API /segment_masks
- Send masks to panel API /calculate_panels
- Save results under ./demo_results

Usage:
  python scripts/e2e_demo.py <image_path> [--roof-url URL] [--panel-url URL] \
      [--gsd 0.05] [--offset 0.3] [--panel-name Standard_B] \
      [--panel-len 1.65] [--panel-wid 1.0]
"""

import os
import sys
import json
import base64
import requests
import argparse
from pathlib import Path

def b64_to_file(data_url: str, out_path: Path):
    b64 = data_url.split(",")[-1]
    out_path.write_bytes(base64.b64decode(b64))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('image_path')
    p.add_argument('--roof-url', default=os.environ.get('ROOF_API_URL', 'http://localhost:8000'))
    p.add_argument('--panel-url', default=os.environ.get('PANEL_API_URL', 'http://localhost:8001'))
    p.add_argument('--gsd', type=float, default=float(os.environ.get('GSD', 0.05)))
    p.add_argument('--offset', type=float, default=float(os.environ.get('OFFSET_M', 0.3)))
    p.add_argument('--panel-name', default='Standard_B')
    p.add_argument('--panel-len', type=float, default=1.65)
    p.add_argument('--panel-wid', type=float, default=1.0)
    args = p.parse_args()

    img_path = Path(args.image_path)
    if not img_path.exists():
        print(f"Image not found: {img_path}")
        sys.exit(1)

    out_dir = Path("demo_results")
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1) Call /segment_masks
    print("[1/3] Calling roof /segment_masks ...")
    with img_path.open("rb") as f:
        files = {"image": (img_path.name, f, "image/jpeg")}
        r = requests.post(f"{args.roof_url}/segment_masks", files=files, timeout=180)
    r.raise_for_status()
    seg = r.json()
    masks = seg.get("masks", [])
    centers = seg.get("centers", [])
    print(f"  -> got {len(masks)} mask(s), {len(centers)} center(s)")

    # save first mask for inspection
    if masks:
        b64_to_file(masks[0], out_dir / "mask0.png")

    # 2) Send to panel API
    print("[2/3] Calling panel /calculate_panels ...")
    payload = {
        "roof_masks": masks,
        "gsd": args.gsd,
        "offset_m": args.offset,
        "panel_options": {args.panel_name: [args.panel_len, args.panel_wid]},
    }
    r2 = requests.post(f"{args.panel_url}/calculate_panels", json=payload, timeout=300)
    r2.raise_for_status()
    result = r2.json()

    (out_dir / "result.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    # Save visualization(s)
    if isinstance(result, dict):
        if "visualization_b64" in result:
            b64_to_file(result["visualization_b64"], out_dir / "vis.png")
        roofs = result.get("roofs", [])
        for i, roof in enumerate(roofs):
            vis = roof.get("visualization_b64")
            if vis:
                b64_to_file(vis, out_dir / f"vis_{i}.png")

    print("[3/3] Done. See demo_results/")


if __name__ == "__main__":
    main()

