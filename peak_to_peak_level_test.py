import pandas as pd


# ==============================
# 1. 데이터 로드
# ==============================

df = pd.read_csv(
    "mixing_actuator_features.csv"
)

df["Date"] = pd.to_datetime(
    df["Date"]
)

df = (
    df
    .sort_values("Date")
    .reset_index(drop=True)
)


# ==============================
# 2. Peak-to-Peak 데이터
# ==============================

p2p = df["Peak_to_Peak"]

latest_p2p = p2p.iloc[-1]


# ==============================
# 3. 기본 분포
# ==============================

print(
    "===== PEAK-TO-PEAK DISTRIBUTION ====="
)

print(
    "Count   :",
    len(p2p)
)

print(
    "Mean    :",
    round(p2p.mean(), 4)
)

print(
    "Median  :",
    round(p2p.median(), 4)
)

print(
    "Minimum :",
    round(p2p.min(), 4)
)

print(
    "Maximum :",
    round(p2p.max(), 4)
)


# ==============================
# 4. Percentiles
# ==============================

print()
print("Percentiles")

percentiles = [
    0.05,
    0.10,
    0.25,
    0.50,
    0.75,
    0.90,
    0.95
]

for p in percentiles:

    value = p2p.quantile(p)

    print(
        f"{int(p * 100):>2}% :",
        round(value, 4)
    )


# ==============================
# 5. 현재 Peak-to-Peak 위치
# ==============================

percentile_rank = (
    (p2p <= latest_p2p).sum()
    / len(p2p)
    * 100
)

print()
print(
    "===== CURRENT PEAK-TO-PEAK LEVEL ====="
)

print(
    "Latest P2P      :",
    round(latest_p2p, 4)
)

print(
    "Percentile Rank :",
    round(percentile_rank, 2),
    "%"
)


# ==============================
# 6. 평균 대비 차이
# ==============================

difference = (
    latest_p2p
    - p2p.mean()
)

difference_percent = (
    difference
    / p2p.mean()
    * 100
)

print(
    "Mean Difference :",
    round(difference, 4)
)

print(
    "Mean Diff %     :",
    round(difference_percent, 2),
    "%"
)