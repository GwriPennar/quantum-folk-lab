from __future__ import annotations


def normalized_edit_similarity(left: tuple[object, ...], right: tuple[object, ...]) -> float:
    if not left and not right:
        return 1.0
    rows, cols = len(left) + 1, len(right) + 1
    dp = [[0] * cols for _ in range(rows)]
    for i in range(rows):
        dp[i][0] = i
    for j in range(cols):
        dp[0][j] = j
    for i in range(1, rows):
        for j in range(1, cols):
            cost = 0 if left[i - 1] == right[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return 1.0 - dp[-1][-1] / max(len(left), len(right))
