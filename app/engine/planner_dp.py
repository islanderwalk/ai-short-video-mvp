# Knapsack 變體：選段總長 ≤ target，最大化分數總和

def pick_segments(segments, target_sec=34.0):
    # segments: [{start, end, score}, ...]
    n = len(segments)
    weights = [max(0.0, s["end"] - s["start"]) for s in segments]
    values  = [float(s["score"]) for s in segments]
    T = int(target_sec * 10)  # 0.1s 精度

    # DP 表
    dp = [[0.0] * (T + 1) for _ in range(n + 1)]
    take = [[0] * (T + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        w = int(weights[i - 1] * 10)
        v = values[i - 1]
        for t in range(T + 1):
            dp[i][t] = dp[i - 1][t]
            if w <= t and dp[i - 1][t - w] + v > dp[i][t]:
                dp[i][t] = dp[i - 1][t - w] + v
                take[i][t] = 1

    # 回溯
    t = T
    chosen = []
    for i in range(n, 0, -1):
        if take[i][t]:
            chosen.append(segments[i - 1])
            t -= int(weights[i - 1] * 10)

    return list(reversed(chosen))
