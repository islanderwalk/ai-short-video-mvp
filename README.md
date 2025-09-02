# 🎬 AI Short Video MVP

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Container-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![CI](https://github.com/islanderwalk/ai-short-video-mvp/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/islanderwalk/ai-short-video-mvp/actions/workflows/ci.yml)

> MVP for AI-powered short-video captioning. **FastAPI + Docker + LoRA + RAG** with optional high-throughput inference (vLLM/Unsloth).

---

## 📌 Features
- `/upload_video` 上傳影片 → `/generate_caption` 自動產出標題/字幕  
- LoRA（PEFT）微調流程與資料範例（`train/`、`data/train/*.jsonl`）  
- RAG（`app/rag/*`）與向量資料夾（`vector_db/`，已被 .gitignore 排除）  
- Docker Compose 一鍵啟動  
- 測試腳本與基準測試雛型（`tests/`、`app/scripts/bench_infer.py`）

---

## 🧩 Architecture

```
    +-----------+
    |   User    |
    +-----+-----+
          |  HTTP (upload/generate)
          v
  +-------+--------+        +--------------------+
  |   FastAPI      |        |  Vector DB / RAG   |
  | app/api/main.py|<------>| app/rag/retrieve   |
  +---+---------+--+        +--------------------+
      |         |
      |         | calls
      |         v
      |   +-----+-------------------+
      |   |   Caption / Planner     |
      |   | app/engine/*            |
      |   +-----+-------------------+
      |         |
      |         | selects backend
      |         v
      |   +-----+-------------------+
      |   |  Inference Backends     |
      |   |  Transformers / vLLM    |
      |   |  / Unsloth (optional)   |
      |   +-------------------------+
      |
      | returns JSON
      v
+------+------+ 
| Response |
+----------+
```

---

## 🚀 Quick Start

```bash
git clone https://github.com/islanderwalk/ai-short-video-mvp.git
cd ai-short-video-mvp
docker-compose up --build
# Open Swagger: http://localhost:8000/docs
```

> 影音與大型模型檔已排除於版控（見 `.gitignore`）。Demo 影片/權重請放雲端連結或 GitHub Releases。

---

## 📡 API

### ▶️ Upload Video
`POST /upload_video` (multipart/form-data)

```bash
curl -X POST "http://localhost:8000/upload_video"   -F "file=@sample.mp4"   -F "video_id=demo"
```

**Response**
```json
{"status":"uploaded","video_id":"demo"}
```

### 📝 Generate Caption
`POST /generate_caption` (JSON)

```json
{
  "video_id": "demo",
  "target_duration_sec": 34
}
```

**Response**
```json
{"video_id":"demo","caption":"A traveler walking along the coast under the sunset."}
```

---

## 🧰 Tech Stack
- **Backend**：FastAPI, Python, pytest  
- **AI/ML**：LoRA(PEFT), optional vLLM / Unsloth, simple RAG  
- **Infra**：Docker & Compose, GitHub Actions CI  
- **Data**：JSONL samples（`data/train/`）

---

## 🗂️ Project Structure
```
ai-short-video-mvp/
│── app/                # api / engine / rag / scripts
│── data/               # docs, train samples (no large media in Git)
│── models/             # model files (gitignored)
│── vector_db/          # vector store (gitignored)
│── tests/              # pytest tests
│── Dockerfile
│── docker-compose.yaml
│── requirements.txt
│── README.md
```

---

## 📊 Roadmap
- [ ] GitHub Actions：pytest + lint + Docker build  
- [ ] 上傳 Demo（Releases/雲端連結）  
- [ ] vLLM/Unsloth 切換參數與基準數據  
- [ ] 簡易前端頁面（可選）  

---

## 📜 License
MIT © 2025 islan derwalk
