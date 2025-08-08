from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List,Dict
import base64
from app.segmentation import process_image   # (List[bytes], List[(x,y)]) を返す

app = FastAPI(title="Roof Segmentation API")

class SegResponse(BaseModel):
    images: List[str]             # data:image/png;base64,... の文字列リスト
    centers: List[Dict[str, int]] # { "x": ..., "y": ... } のリスト

@app.post("/segment", response_model=SegResponse)
async def segment_endpoint(image: UploadFile = File(...)):
    # 入力画像バイト列を読み込み
    data = await image.read()
    try:
        # process_image は now List[bytes] を返すように実装を変更
        png_bytes_list, centers = process_image(data, conf=0.8)
    except ValueError as e:
        # 画像読込失敗など
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # その他想定外エラー
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="内部エラー")

    # 各バイト列を Base64 エンコード
    base64_images = []
    center_list: List[Dict[str,int]] = []
    for b, center in zip(png_bytes_list, centers):
        cx, cy = center
        b64 = base64.b64encode(b).decode("utf-8")
        base64_images.append(f"data:image/png;base64,{b64}")
        center_list.append({"x": cx, "y": cy})
    return JSONResponse(content={
        "images": base64_images,
        "centers": center_list
    })

# 新しいエンドポイント: 二値マスク画像（PNG, 0/255）をBase64で返す
class MaskResponse(BaseModel):
    masks: List[str]
    centers: List[Dict[str, int]]

@app.post("/segment_masks", response_model=MaskResponse)
async def segment_masks_endpoint(image: UploadFile = File(...)):
    import numpy as np
    import cv2

    data = await image.read()
    try:
        png_bytes_list, centers = process_image(data, conf=0.8)
    except ValueError as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[ERROR] {e}")
        raise HTTPException(status_code=500, detail="内部エラー")

    # RGBA の α から 0/255 のグレースケールPNGへ統一変換
    base64_masks = []
    center_list: List[Dict[str,int]] = []
    for b, center in zip(png_bytes_list, centers):
        arr = np.frombuffer(b, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_UNCHANGED)  # 1ch or 3ch or 4ch
        if img is None:
            continue
        if img.ndim == 2:
            mask = (img > 0).astype(np.uint8) * 255
        elif img.shape[2] == 4:
            alpha = img[:, :, 3]
            mask = (alpha > 0).astype(np.uint8) * 255
        else:
            # フォールバック: グレースケール化して閾値
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            _, mask = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        _, mask_png = cv2.imencode('.png', mask)
        b64 = base64.b64encode(mask_png.tobytes()).decode("utf-8")
        base64_masks.append(f"data:image/png;base64,{b64}")
        cx, cy = center
        center_list.append({"x": cx, "y": cy})

    return JSONResponse(content={
        "masks": base64_masks,
        "centers": center_list
    })
