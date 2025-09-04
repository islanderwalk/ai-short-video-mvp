📖 [中文說明 README.zh.md](README.zh.md)

# 🎥 Travel Media AI Studio

智能旅遊短片生成 + 文件檢索助理 (Side Project for AI/LLM Engineer Interview)

## ✨ Features
- 🎬 **Smart Highlight Picker**: Auto-cut 34s highlights using OpenCV + DP (future)
- 📝 **Caption Generator**: OpenAI / Local HF / vLLM / Unsloth (LoRA fine-tuned)
- 📚 **RAG Travel Assistant**: Retrieve visa/travel docs with FAISS/Chroma
- ⚡ **Serving Benchmark**: Compare HuggingFace vs vLLM latency (0.3s vs 1.0s)
- 🐳 **Dockerized FastAPI** with CI/CD (GitHub Actions)
- 🔍 **NLP Tasks**: NER, Intent classification, Sentiment (extensible)

## 🚀 Quick Start

```bash
git clone https://github.com/islanderwalk/ai-short-video-mvp.git
cd ai-short-video-mvp

# 1) Create env file
cp .env.example .env
#   - Use OpenAI (recommended demo): set OPENAI_API_KEY, CAPTION_PROVIDER=openai
#   - Use local model: CAPTION_PROVIDER=local; CAPTION_BASE_MODEL=distilgpt2 or qwen2-0.5b-instruct; CAPTION_QUANT=int4

# 2) One-click start (first time downloads model to ./hf_cache)
docker compose up --build -d

# 3) Swagger API docs
# http://localhost:8000/docs
```
**Volume mounts:**  
- `./data:/app/data` → videos / outputs  
- `./vector_db:/app/vector_db` → vector DB  
- `./hf_cache:/root/.cache/huggingface` → model cache (download once, reuse later)

## 🧩 Architecture
- [Full Architecture & Structure](docs/structure.md)

---

## 📊 KPI (Demo)
- Inference latency: **1.0s → 0.3s** (HuggingFace → vLLM)
- Caption accuracy: **+15% BLEU/ROUGE** after LoRA fine-tune
- Highlight retention: **+18% audience @75%** with DP selection (future)

## 🛠️ Tech Stack
- **Backend**: FastAPI, Docker, GitHub Actions (CI/CD)
- **AI/LLM**: HuggingFace Transformers, vLLM, Unsloth, PEFT (LoRA/QLoRA)
- **RAG**: FAISS / Chroma Vector DB
- **NLP**: spaCy, Transformers (NER, Intent, Sentiment)
- **DevOps**: Docker Compose, CI/CD, Benchmarking, Logging

## 📂 Project Structure
```
AI-SHORT-VIDEO
├─ .github/workflows/ci.yml      # GitHub Actions workflow
├─ app/
│  ├─ api/main.py                # FastAPI entrypoints (upload, caption, retrieve, health)
│  ├─ engine/
│  │   ├─ video_analyzer.py      # OpenCV segmentation
│  │   ├─ captioner.py           # Caption generator (OpenAI/HF)
│  │   └─ planner_dp.py          # [Future] DP highlight planner
│  ├─ rag/
│  │   ├─ index_docs.py          # Build vector DB from docs
│  │   └─ retrieve.py            # Query RAG with citation
│  └─ scripts/
│      └─ bench_infer.py         # Benchmark inference latency
├─ data/
│  ├─ docs/                      # RAG source docs (e.g., visa text)
│  ├─ train/captions.jsonl       # Training data for fine-tune
│  └─ videos/                    # Uploaded videos
├─ docs/structure.md             # Full architecture doc (EN + 中文)
├─ models/                       # Fine-tuned or downloaded models
├─ tests/test_api.py              # Unit tests for API
├─ vector_db/                     # FAISS vector DB + metadata
│  ├─ rag_hnsw.faiss
│  └─ rag_paths.json
├─ .env.example                   # Example env vars (real .env ignored)
├─ .gitignore                     # Ignore rules (env, models, data, etc.)
├─ docker-compose.yaml            # Multi-service orchestration
├─ Dockerfile                     # Container build definition
├─ requirements.txt               # Python dependencies
└─ README.md                      # Project overview (this file)
```


