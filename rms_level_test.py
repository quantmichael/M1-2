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
# 2. RMS 기본 정보
# ==============================

rms = df["RMS"]

latest_rms = rms.iloc[-1]

print(
    "===== RMS LEVEL DISTRIBUTION ====="
)

print(
    "Count   :",
    len(rms)
)

print(
    "Mean    :",
    round(rms.mean(), 4)
)

print(
    "Median  :",
    round(rms.median(), 4)
)

print(
    "Minimum :",
    round(rms.min(), 4)
)

print(
    "Maximum :",
    round(rms.max(), 4)
)


# ==============================
# 3. RMS Percentile
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

    value = rms.quantile(p)

    print(
        f"{int(p * 100):>2}% :",
        round(value, 4)
    )


# ==============================
# 4. 현재 RMS의 Percentile Rank
# ==============================

percentile_rank = (
    (rms <= latest_rms).sum()
    / len(rms)
    * 100
)

print()
print(
    "===== CURRENT RMS LEVEL ====="
)

print(
    "Latest RMS      :",
    round(latest_rms, 4)
)

print(
    "Percentile Rank :",
    round(percentile_rank, 2),
    "%"
)


# ==============================
# 5. 전체 평균 대비 차이
# ==============================

difference = (
    latest_rms
    - rms.mean()
)

difference_percent = (
    difference
    / rms.mean()
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