# app/api/main.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
import os, shutil

from app.engine.video_analyzer import analyze_video_to_segments

app = FastAPI(title="AI Short Video MVP", version="0.4.0")

UPLOAD_DIR = "data/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class GenerateReq(BaseModel):
    video_id: str
    target_duration_sec: float = 34.0
    # 可選：直接指名檔名；若未指定就用 video_id 當檔名
    video_filename: Optional[str] = None
    language: Optional[str] = "zh"

@app.get("/")
def root():
    return {"status":"ok","service":"ai-short-video-mvp"}

@app.post("/upload_video")
async def upload_video(file: UploadFile = File(...)):
    out_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(out_path,"wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"video_id": file.filename, "path": out_path}

@app.post("/generate_caption")
def generate_caption(req: GenerateReq):
    # 1) 找到影片路徑
    filename = req.video_filename or req.video_id
    video_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(video_path):
        return {
            "error": f"Video file not found: {video_path}",
            "hint": "先呼叫 /upload_video 上傳影片，或把檔案放進 data/videos/ 再試"
        }

    # 2) 真的做影片分析 → 產生片段
    segments = analyze_video_to_segments(video_path, window_sec=4.0, diff_threshold=18.0)

    # 3) 簡單選片段（先用分數排序、再湊總長 ≈ target）
    target = req.target_duration_sec
    picked, total = [], 0.0
    for seg in sorted(segments, key=lambda s: -s["score"]):
        dur = max(0.0, seg["end"] - seg["start"])
        if total + dur <= target:
            picked.append(seg)
            total += dur
        if total >= target * 0.95:  # 差不多就好
            break

    # 4) 暫時用假 caption（下一步再接 LLM/LoRA）
    caption = f"自動挑選 {len(picked)} 段（約 {int(total)} 秒）— 之後會用 LLM 生成旅遊語氣文案。"
    hashtags = ["#AutoHighlight", "#OpenCV", "#MVP"]

    return {
        "video_id": req.video_id,
        "target_duration_sec": req.target_duration_sec,
        "highlight_segments": picked,
        "caption": caption,
        "hashtags": hashtags
    }
