# app/engine/video_analyzer.py
import cv2
import numpy as np
from typing import List, Dict

def analyze_video_to_segments(
    video_path: str,
    window_sec: float = 4.0,
    diff_threshold: float = 18.0,
) -> List[Dict]:
    """
    極簡版「畫面變化」偵測：
    - 每一幀取灰階 + 高斯模糊
    - 計算相鄰幀的差異（平均絕對差）
    - 累積分數，分到固定 window（預設 4 秒）裡
    - 每個 window 輸出一個片段 {start, end, score}

    回傳：List[{"start":float, "end":float, "score":float}]
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps > 0 else 0.0
    if duration == 0:
        cap.release()
        return []

    window_frames = max(1, int(window_sec * fps))
    prev = None
    frame_idx = 0
    window_score = 0.0
    segments = []
    window_start_sec = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            # 收尾：把最後一個 window 輸出
            if frame_idx % window_frames != 0:
                seg_end = duration
                segments.append({
                    "start": window_start_sec,
                    "end": seg_end,
                    "score": float(window_score),
                })
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5,5), 0)

        if prev is not None:
            diff = cv2.absdiff(gray, prev)
            score = float(np.mean(diff))  # 畫面差異平均值
            # 大於門檻就視為「精彩度」累加
            if score > diff_threshold:
                window_score += score

        prev = gray
        frame_idx += 1

        # 到了一個 window，切出片段
        if frame_idx % window_frames == 0:
            seg_end = frame_idx / fps
            segments.append({
                "start": window_start_sec,
                "end": seg_end,
                "score": float(window_score),
            })
            window_start_sec = seg_end
            window_score = 0.0

    cap.release()
    # 過濾掉太短或異常的片段
    cleaned = []
    for s in segments:
        dur = max(0.0, s["end"] - s["start"])
        if dur >= 0.5:  # 半秒以下丟掉
            cleaned.append(s)
    return cleaned
