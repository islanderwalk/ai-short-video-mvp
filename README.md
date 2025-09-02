# AI Short Video Platform — MVP

## 一鍵啟動
```bash
docker compose up -d
# 首次使用：建立 RAG 索引
python app/rag/index_docs.py
```

## API 範例
```bash
curl -s -X POST http://localhost:8000/generate_caption   -H 'Content-Type: application/json'   -d '{"video_id":"demo","target_duration_sec":34}' | jq .

curl -s -X POST http://localhost:8000/retrieve_info   -H 'Content-Type: application/json'   -d '{"query":"台灣人去斯里蘭卡要簽證嗎？"}' | jq .

curl -s -X POST http://localhost:8000/recommend   -H 'Content-Type: application/json'   -d '{"user_id":"u_042","k":5}' | jq .
```

## 里程碑（極速）
- Day 1：骨架 + Docker + 三路由
- Day 2：RAG 可檢索 + citation
- Day 3：DP 選段 + 假分數 → 34s 精華
- Day 4：LoRA 資料蒐集與訓練腳本（或先用佔位）
- Day 5：Serving Benchmark（HF vs vLLM）

## 後續
- 用 PEFT/bitsandbytes 訓練 LoRA，替換 /generate_caption 佔位
- 加入 vLLM/DeepSpeed/Unsloth 實跑，更新 Serving Benchmark
- 推薦：建立影片/字幕 embedding → FAISS ANN + NLP 加權
- NLP：NER/意圖/情感 → 回饋推薦排序
- KPI：Latency、BLEU/ROUGE、Retention@75%、NDCG
