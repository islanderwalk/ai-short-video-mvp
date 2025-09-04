# app/rag/retrieve.py
import os, json
import faiss
from sentence_transformers import SentenceTransformer

INDEX_PATH = os.path.join("vector_db", "rag_hnsw.faiss")
PATHS_PATH = os.path.join("vector_db", "rag_paths.json")
MODEL = "sentence-transformers/all-MiniLM-L6-v2"

_EMB = None
_INDEX = None
_PATHS = None

def _lazy_load():
    global _EMB, _INDEX, _PATHS
    if _EMB is None:
        _EMB = SentenceTransformer(MODEL)
    if _INDEX is None:
        if not os.path.exists(INDEX_PATH):
            raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")
        _INDEX = faiss.read_index(INDEX_PATH)
    if _PATHS is None:
        if not os.path.exists(PATHS_PATH):
            raise FileNotFoundError(f"Paths file not found: {PATHS_PATH}")
        with open(PATHS_PATH, "r", encoding="utf-8") as f:
            _PATHS = json.load(f)

def _index_size() -> int:
    try:
        return int(getattr(_INDEX, "ntotal"))
    except Exception:
        return len(_PATHS) if _PATHS is not None else 0

def answer_with_citations(query: str, k: int = 3):
    _lazy_load()
    n = _index_size()
    if n <= 0:
        # 空索引時不要炸掉；回傳友善訊息
        return "（索引為空）目前沒有可檢索的資料。", []

    k = max(1, min(k, n))
    q = _EMB.encode([query], convert_to_numpy=True)
    D, I = _INDEX.search(q, k)

    hits = []
    for i in I[0]:
        path = _PATHS[i]
        hits.append({
            "title": os.path.basename(path),
            "source": path,
            "page": 1
        })

    # MVP：先回固定摘要，之後串 LLM + 上下文生成答案
    answer = "需要辦理 e-Visa；細節依官方公告為準（此為 MVP 摘要示例）。"
    return answer, hits
