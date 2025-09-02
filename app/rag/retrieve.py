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
        _INDEX = faiss.read_index(INDEX_PATH)
    if _PATHS is None:
        with open(PATHS_PATH, "r", encoding="utf-8") as f:
            _PATHS = json.load(f)

def answer_with_citations(query: str, k: int = 3):
    _lazy_load()
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
    # MVP：先回固定摘要，之後串 LLM + 上下文拼接生成答案
    answer = "需要辦理 e-Visa；細節依官方公告為準（此為 MVP 摘要示例）。"
    return answer, hits
