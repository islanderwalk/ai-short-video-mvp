import cv2
import os
from typing import List, Dict

def analyze_video_to_segments(
    video_path: str,
    window_sec: float = 4.0,
    diff_threshold: float = 18.0,
) -> List[Dict]:
    """
    以固定窗格（window_sec）做畫面差分打分，回傳多個區段：
    [{"start": 0.0, "end": 4.0, "score": 12.3}, ...]
    """
    if not os.path.exists(video_path):
        return []

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return []

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    duration = total_frames / fps if fps > 0 else 0.0
    if duration <= 0:
        cap.release()
        return []

    step_frames = max(1, int(window_sec * fps))
    prev_gray = None
    scores = []

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if prev_gray is None:
            prev_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame_idx += 1
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        diff = cv2.absdiff(gray, prev_gray)
        score = float(diff.mean())
        scores.append(score)

        prev_gray = gray
        frame_idx += 1

    cap.release()

    # 聚合到每個窗格
    segments: List[Dict] = []
    # 以每窗的平均差分作為分數
    for start_f in range(0, max(1, len(scores)), step_frames):
        end_f = min(len(scores), start_f + step_frames)
        if end_f <= start_f:
            continue
        seg_scores = scores[start_f:end_f]
        avg = sum(seg_scores) / max(1, len(seg_scores))
        start_t = start_f / fps
        end_t = end_f / fps
        segments.append({"start": start_t, "end": end_t, "score": avg})

    # 簡單濾掉極低分
    segments = [s for s in segments if s["score"] >= 0.0]  # 你也可用 diff_threshold

    return segments
