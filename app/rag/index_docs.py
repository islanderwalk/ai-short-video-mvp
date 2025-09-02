import os, glob, json
import faiss
from sentence_transformers import SentenceTransformer

DATA_DIR = os.path.join("data", "docs")
INDEX_PATH = os.path.join("vector_db", "rag_hnsw.faiss")
PATHS_PATH = os.path.join("vector_db", "rag_paths.json")

MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMB = SentenceTransformer(MODEL)

texts, paths = [], []
for p in glob.glob(os.path.join(DATA_DIR, "**", "*"), recursive=True):
    if os.path.isfile(p) and any(p.endswith(ext) for ext in [".txt", ".md"]):
        with open(p, encoding="utf-8") as f:
            txt = f.read()
        texts.append(txt[:2000])  # MVP：長文截斷以加速
        paths.append(p)

if not texts:
    os.makedirs(DATA_DIR, exist_ok=True)
    demo_path = os.path.join(DATA_DIR, "sri_lanka_visa.txt")
    with open(demo_path, "w", encoding="utf-8") as f:
        f.write("台灣旅客申請斯里蘭卡 e-Visa：請至官方網站申辦；通常需上傳護照資料與照片。入境條件以官方公告為準。")
    texts.append("台灣旅客申請斯里蘭卡 e-Visa：請至官方網站申辦；通常需上傳護照資料與照片。入境條件以官方公告為準。")
    paths.append(demo_path)

vecs = EMB.encode(texts, convert_to_numpy=True, show_progress_bar=True)
d = vecs.shape[1]
index = faiss.index_factory(d, "HNSW32")
index.add(vecs)

os.makedirs("vector_db", exist_ok=True)
faiss.write_index(index, INDEX_PATH)
with open(PATHS_PATH, "w", encoding="utf-8") as f:
    json.dump(paths, f, ensure_ascii=False, indent=2)

print(f"Indexed {len(paths)} docs -> {INDEX_PATH}")
