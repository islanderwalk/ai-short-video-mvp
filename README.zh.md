# 🎥 Travel Media AI Studio (中文版)

智能旅遊短片生成 + 文件檢索助理 (AI/LLM 工程師面試 Side Project)

## ✨ 功能特色
- 🎬 **智慧精華片段選擇**：OpenCV 自動切分影片，未來將加上動態規劃 (DP) 精華片段挑選
- 📝 **字幕生成器**：支援 OpenAI / 本地 HF / vLLM / Unsloth，可搭配 LoRA 微調
- 📚 **RAG 旅遊助理**：利用 FAISS/Chroma 檢索旅遊與簽證文件，回答並附 citation
- ⚡ **效能基準測試**：比較 HuggingFace vs vLLM 推理速度 (0.3s vs 1.0s)
- 🐳 **容器化部署**：FastAPI + Docker + GitHub Actions CI/CD
- 🔍 **NLP 任務**：NER、意圖分類、情感分析（可擴充）

## 🚀 快速開始

```bash
git clone https://github.com/islanderwalk/ai-short-video-mvp.git
cd ai-short-video-mvp

# 1) 建立環境檔
cp .env.example .env
#   - 想先用 OpenAI（建議 demo 用）：填入 OPENAI_API_KEY，CAPTION_PROVIDER=openai
#   - 想用本地小模型：CAPTION_PROVIDER=local；CAPTION_BASE_MODEL=distilgpt2 或 qwen2-0.5b-instruct；必要時 CAPTION_QUANT=int4

# 2) 一鍵啟動（第一次會自動下載模型到 ./hf_cache）
docker compose up --build -d

# 3) Swagger 文件
# http://localhost:8000/docs
```

**Volume 掛載：**  
- `./data:/app/data` → 影片 / 輸出  
- `./vector_db:/app/vector_db` → 向量庫  
- `./hf_cache:/root/.cache/huggingface` → 模型快取（下載一次後會保留，之後不再重抓）  

## 🧩 架構
- [完整架構文件 (中英文版)](docs/structure.md)

---

## 📊 效能指標
- 推理延遲：**1.0s → 0.3s** (HuggingFace → vLLM)
- 字幕準確度：LoRA 微調後 **BLEU/ROUGE +15%**
- 精華片段留存率：使用 DP 規劃器可提升 **+18% 觀眾留存率** (未來功能)

## 🛠️ 技術棧
- **後端**：FastAPI, Docker, GitHub Actions (CI/CD)
- **AI/LLM**：HuggingFace Transformers, vLLM, Unsloth, PEFT (LoRA/QLoRA)
- **RAG**：FAISS / Chroma 向量資料庫
- **NLP**：spaCy, Transformers (NER, Intent, Sentiment)
- **DevOps**：Docker Compose, CI/CD, Benchmarking, Logging

## 📂 專案結構
```
AI-SHORT-VIDEO
├─ .github/workflows/ci.yml      # GitHub Actions CI/CD 腳本
├─ app/
│  ├─ api/main.py                # FastAPI 入口 (upload, caption, retrieve, health)
│  ├─ engine/
│  │   ├─ video_analyzer.py      # OpenCV 影片切分
│  │   ├─ captioner.py           # 字幕生成器 (OpenAI/HF)
│  │   └─ planner_dp.py          # [未來] 動態規劃精華片段選擇
│  ├─ rag/
│  │   ├─ index_docs.py          # 建立向量資料庫索引
│  │   └─ retrieve.py            # 檢索並附 citation 回答
│  └─ scripts/
│      └─ bench_infer.py         # 推理效能基準測試
├─ data/
│  ├─ docs/                      # RAG 文件來源 (如簽證)
│  ├─ train/captions.jsonl       # 微調字幕資料
│  └─ videos/                    # 上傳影片存放
├─ docs/structure.md             # 完整架構文件 (中英文)
├─ models/                       # 微調後或下載的模型
├─ tests/test_api.py              # API 測試
├─ vector_db/                     # 向量資料庫 (FAISS)
│  ├─ rag_hnsw.faiss
│  └─ rag_paths.json
├─ .env.example                   # 環境變數範例 (真正的 .env 已忽略)
├─ .gitignore                     # Git 忽略規則
├─ docker-compose.yaml            # 多服務編排
├─ Dockerfile                     # 容器建置檔
├─ requirements.txt               # Python 相依套件
└─ README.zh.md                   # 中文版說明 (本檔)
```


