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
