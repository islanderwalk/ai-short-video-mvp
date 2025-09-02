import time

PROMPT = "以旅遊 IG 口吻寫 80 字影片標題，主題：海邊日落與公路。"

def run_baseline():
    t0 = time.time()
    # TODO: 換成 HF / vLLM 真實推理；這裡先以 sleep 模擬
    time.sleep(1.02)
    print("HF latency:", round(time.time()-t0, 3), "s")

def run_vllm():
    t0 = time.time()
    # TODO: 換成 vLLM 推理；先以較短 sleep 模擬
    time.sleep(0.31)
    print("vLLM latency:", round(time.time()-t0, 3), "s")

if __name__ == "__main__":
    run_baseline()
    run_vllm()
