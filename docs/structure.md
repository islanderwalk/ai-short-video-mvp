# 🧩 Travel Media AI Studio – Architecture / 系統架構

## English Version

```text
                         HTTP (upload / generate / retrieve / healthz)
    +-----------+                  +-----------------------------------------+
    |   User    | ---------------> |    FastAPI (app/api/main.py)            |
    +-----------+                  +-----------------+-----------------------+
                                           |           |            |
                                           |           |            +--------------------+
                                           |           |                                     /healthz
                                           |           v
                                           |   +-------+----------+
                                           |   |  RAG Router      |   /retrieve_info
                                           |   |  (app/rag/*)     |
                                           |   +---+--------------+
                                           |       | retrieve / cite
                                           |       v
                                           |   +---+---------------+
                                           |   | Vector DB         |  (FAISS/Chroma/Weaviate)
                                           |   | (vector_db/)      |
                                           |   +---+---------------+
                                           |       ^
                                           |       | builds from
                                           |       | data/docs/
                                           |
   /upload_video                           |
        |                                  |
        v                                  |
+-------+---------+                        |
| Save Video to   |                        |
| data/videos/    | <----------------------+
+-----------------+

   /generate_caption
        |
        v
+-------+------------------------------+
|  Engine (app/engine/*)              |
|  - video_analyzer.py                |
|      OpenCV diff / 4s window        |
|      -> score -> segments           |
|  - captioner.py                     |
|      provider switch:               |
|        openai | local(HF int8/int4) |
|  - planner.py [FUTURE]              |
|      DP-based segment selection     |
+-------+------------------+----------+
        |                  |
        | selects backend  | loads models / tokens (.env, NOT tracked)
        v                  v
+-------+------+     +-----+--------------------------+
| OpenAI API   |     | Local Inference               |
| (remote)     |     | (Transformers / vLLM /       |
+-------+------+     |  Unsloth / TensorRT-LLM [FUTURE]) 
        ^            +-----+--------------------------+
        |                   |                |
        |                   | quant/ft       | caching
        |                   v                v
        |             +-----+--------+   +---+-------------------+
        |             | Quantization |   | KV Cache / Emb Cache |
        |             | (LoRA/QLoRA, |   | (in-mem / disk)      |
        |             | bitsandbytes,|   +---+-------------------+
        |             | GPTQ/AWQ)    |       |
        |             +-----+--------+       |
        |                   |                |
        |                   v                |
        |             +-----+----------------+-------------------------------+
        |             | Fine-tune pipeline (train_lora.ipynb / scripts/)    |
        |             | - PEFT / LoRA adapters                               |
        |             | - Domain data (captions/hashtags)                    |
        |             | - Metrics: BLEU / ROUGE / human eval                 |
        |             +------------------------------------------------------+

                          returns JSON (segments, captions, citations)
                                         |
                                         v
                                   +-----+------ +
                                   |  Response  |
                                   +------------+

────────────────────────────────────────────────────────────────────────────────────────
Infra / DevOps / Observability
────────────────────────────────────────────────────────────────────────────────────────
+---------------------+     +---------------------+     +------------------------------+
| Dockerfile          |     | docker-compose.yml  |     | GitHub Actions (CI/CD)       |
| - runtime image     |     | - FastAPI + backend |     | - pytest / lint              |
| - GPU base [FUTURE] |     | - volumes: data/*   |     | - build & push image         |
+----------+----------+     +----------+----------+     +--------------+---------------+
           |                            |                                   |
           v                            v                                   v
   +-------+----------+        +--------+---------+                 +-------+--------+
   | Config / Secrets |        | Logging / Traces |                 | Benchmarking  |
   | (.env, ignored)  |        | (uvicorn,        |                 | (Serving perf)|
   | Git-ignored OK   |        |  OpenTelemetry   |                 | - HF vs vLLM  |
   +------------------+        |  [FUTURE])       |                 | - latency/QPS |
                               +------------------+                 +----------------

NLP Aux (used by RAG & Planning) [Extensible]
────────────────────────────────────────────────────────────────────────────────────────
+---------------------+   +---------------------+   +-------------------------------+
| NER (spaCy/HF)      |   | Intent Classifier   |   | Sentiment (reviews/comments) |
| - place/date/org    |   | - visa / transport  |   | - guides caption tone         |
| - improves retrieval|   |   / attraction      |   |                               |
+----------+----------+   +----------+----------+   +---------------+---------------+
           \__________________________  guide query routing ________________________/


Future / Research Hooks (for JD coverage)
────────────────────────────────────────────────────────────────────────────────────────
- Planner (DP): knapsack-style selection under time constraint → maximize “highlight score”
- Graph/Topology Retrieval: HNSW / Knowledge Graph fusion / TDA-based outlier detection
- Multilingual: zh/en auto-detect; tokenizer alignment; MT fallback [FUTURE]
- Streaming: server-sent events for token streaming [FUTURE]
- A/B Testing: prompt variants, CTR/retention comparison [FUTURE]
- Security: rate limit, auth (JWT/OAuth2), PII redaction in logs [FUTURE]
```

---

## 中文版本

```text
                         HTTP (upload / generate / retrieve / healthz)
    +-----------+                  +-----------------------------------------+
    |   使用者  | ---------------> |    FastAPI (app/api/main.py)             |
    +-----------+                  +-----------------+-----------------------+
                                           |           |            |
                                           |           |            +--------------------+
                                           |           |                                     /健康檢查
                                           |           v
                                           |   +-------+----------+
                                           |   |  RAG 路由器      |   /檢索查詢
                                           |   |  (app/rag/*)     |
                                           |   +---+--------------+
                                           |       | 檢索 / 引用
                                           |       v
                                           |   +---+---------------+
                                           |   | 向量資料庫        |  (FAISS/Chroma/Weaviate)
                                           |   | (vector_db/)      |
                                           |   +---+---------------+
                                           |       ^
                                           |       | 建立來源
                                           |       | data/docs/
                                           |
   /upload_video                           |
        |                                  |
        v                                  |
+-------+---------+                        |
| 儲存影片到      |                        |
| data/videos/    | <----------------------+
+-----------------+

   /generate_caption
        |
        v
+-------+------------------------------+
|  引擎 (app/engine/*)                |
|  - video_analyzer.py                |
|      OpenCV 畫面差分 / 4 秒窗口     |
|      → 計分 → 分段                  |
|  - captioner.py                     |
|      提供者切換：                   |
|        openai | 本地(HF int8/int4)  |
|  - planner.py [未來]                 |
|      動態規劃(DP)最佳片段選擇        |
+-------+------------------+----------+
        |                  |
        | 選擇後端         | 載入模型 / 金鑰 (.env，不追蹤)
        v                  v
+-------+------+     +-----+--------------------------+
| OpenAI API   |     | 本地推理                       |
| (雲端遠端)   |     | (Transformers / vLLM /        |
+-------+------+     |  Unsloth / TensorRT-LLM [未來]) 
        ^            +-----+--------------------------+
        |                   |                |
        |                   | 量化/微調      | 快取
        |                   v                v
        |             +-----+--------+   +---+-------------------+
        |             | 量化/微調     |   | KV Cache / 向量快取 |
        |             | (LoRA/QLoRA, |   | (記憶體 / 磁碟)      |
        |             | bitsandbytes,|   +---+-------------------+
        |             | GPTQ/AWQ)    |       |
        |             +-----+--------+       |
        |                   |                |
        |                   v                |
        |             +-----+----------------+-------------------------------+
        |             | 微調流程 (train_lora.ipynb / scripts/)               |
        |             | - PEFT / LoRA adapters                               |
        |             | - 特定資料集 (字幕/Hashtag)                          |
        |             | - 評估指標: BLEU / ROUGE / 人工評分                  |
        |             +------------------------------------------------------+

                          回傳 JSON (segments, captions, citations)
                                         |
                                         v
                                   +-----+------ +
                                   |  回應       |
                                   +------------+

────────────────────────────────────────────────────────────────────────────────────────
基礎建設 / DevOps / 監控
────────────────────────────────────────────────────────────────────────────────────────
+---------------------+     +---------------------+     +------------------------------+
| Dockerfile          |     | docker-compose.yml  |     | GitHub Actions (CI/CD)       |
| - 運行時映像        |     | - FastAPI + 後端    |     | - pytest / lint              |
| - GPU 基底 [未來]   |     | - 掛載資料夾 data/* |     | - 自動建置與發佈             |
+----------+----------+     +----------+----------+     +--------------+---------------+
           |                            |                                   |
           v                            v                                   v
   +-------+----------+        +--------+---------+                 +-------+--------+
   | 設定 / Secrets   |        | 日誌 / 追蹤      |                 | 基準測試       |
   | (.env, 已忽略)   |        | (uvicorn,       |                 | - HF vs vLLM   |
   | Git 已排除       |        |  OpenTelemetry) |                 | - 延遲 / QPS   |
   +------------------+        |  [未來]         |                 +----------------
                               +------------------+                 

NLP 輔助模組 (給 RAG 與規劃器使用，可擴展)
────────────────────────────────────────────────────────────────────────────────────────
+---------------------+   +---------------------+   +-------------------------------+
| NER 命名實體識別    |   | 意圖分類器          |   | 情感分析 (評論/留言)           |
| - 地點/日期/組織    |   | - 簽證 / 交通 / 景點|   | - 指導字幕語氣                 |
| - 改善檢索效果      |   |                     |   |                               |
+----------+----------+   +----------+----------+   +---------------+---------------+
           \__________________________  幫助查詢路由 ________________________/


未來 / 研究延伸 (對應 JD 技能)
────────────────────────────────────────────────────────────────────────────────────────
- 規劃器 (DP): 在時間限制內最大化精彩分數
- 圖/拓樸檢索: HNSW / 知識圖譜融合 / TDA 異常檢測
- 多語支援: 自動偵測 zh/en，Tokenizer 對齊，MT 後備 [未來]
- 流式輸出: SSE token streaming [未來]
- A/B 測試: Prompt 變體，CTR/Retention 比較 [未來]
- 安全: Rate limit, JWT/OAuth2, 日誌 PII 遮罩 [未來]
```

---

## Overview
🧩 Travel Media AI Studio – Project Structure Overview
1. .github/workflows/ci.yml

CI/CD 自動化腳本：定義 GitHub Actions workflow。

功能：每次 push 時，自動執行測試 (pytest)、lint，並可進一步擴展自動 build Docker image。

2. app/ (主要後端應用)
api/

main.py

FastAPI 入口，定義所有 API endpoint：

/upload_video → 上傳影片，存到 data/videos/。

/generate_caption → 呼叫 Engine 切片 + 產生字幕。

/retrieve_info → 呼叫 RAG 查詢資訊（像簽證文件）。

/healthz → 健康檢查。

engine/

video_analyzer.py

影片分析器：用 OpenCV 做畫面差分，每 4 秒判斷一個 segment → 給出分數。

captioner.py

字幕產生器：根據設定，切換 provider：

OpenAI API（雲端）

Local HF / vLLM / Unsloth （本地模型）

planner_dp.py

[未來功能] Highlight 規劃器：用動態規劃 (DP) 解決「如何挑選一組片段，在限定長度下最大化精彩度」。

__init__.py

標示為 Python package。

rag/

index_docs.py

文件索引器：把 data/docs/ 內的文字轉成向量，存進 vector_db/ (例如 FAISS)。

retrieve.py

檢索器：根據 Query 搜索向量資料庫 → 回傳相關文件片段 + citation。

__init__.py

標示為 Python package。

scripts/

bench_infer.py

效能測試腳本：比較 HuggingFace Transformers vs vLLM (或 Unsloth)，量測推理延遲/吞吐量。

__init__.py

標示為 Python package。

3. data/

docs/

放知識文件，e.g. sri_lanka_visa.txt（用於 RAG 檢索）。

train/

放訓練資料，例如 captions.jsonl（字幕微調用）。

videos/

使用者上傳的影片存放處。

4. docs/

structure.md

完整架構文件（中英文版架構圖 + 說明），用來 demo。

5. models/

預留給微調後或下載的模型檔案 (LoRA weights, HF checkpoints)。

6. tests/

test_api.py

單元測試：測試 API 是否正常工作。

7. vector_db/

rag_hnsw.faiss

向量資料庫檔案 (FAISS HNSW 索引)。

rag_paths.json

metadata，紀錄索引對應的檔案/路徑。

8. Root files

.env.example

範例環境變數（API key 等），真正的 .env 被 gitignore。

.gitignore

忽略檔案規則（.env, model weights, video files…）。

docker-compose.yaml

定義一鍵啟動多服務（FastAPI + 向量資料庫）。

Dockerfile

定義後端服務環境（Python、依賴、運行指令）。

requirements.txt

Python 套件需求。

README.md

簡介、安裝教學、快速啟動。

🔗 串起來的故事（Pipeline）

使用者上傳影片
→ /upload_video → 儲存到 data/videos/。

產生字幕 / highlight
→ /generate_caption → engine/video_analyzer.py 切片 → engine/captioner.py 產生字幕。
→ [未來] engine/planner_dp.py 用 DP 選最精彩 34 秒 → 回傳字幕 + highlight。

知識檢索 (RAG)
→ /retrieve_info → rag/retrieve.py → 搜索 vector_db/ (由 rag/index_docs.py 建立)。
→ 回傳答案 + citation（例如簽證資訊）。

效能與微調

scripts/bench_infer.py：比較 HuggingFace vs vLLM 的延遲。

data/train/captions.jsonl：可做 LoRA 微調 → 存在 models/。

Infra/DevOps

用 Docker 打包，docker-compose up 一鍵啟動 API + DB。

GitHub Actions (ci.yml) 自動測試 & build。

tests/test_api.py 確保 API 正常。

docs/structure.md：完整技術說明。
```text
