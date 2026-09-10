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
# 2. 분석 대상
# ==============================

features = df[
    [
        "RMS",
        "Std",
        "Peak_to_Peak"
    ]
]


# ==============================
# 3. 상관계수
# ==============================

correlation = features.corr()

print(
    "===== FEATURE CORRELATION ====="
)

print(
    correlation.round(4)
)


# ==============================
# 4. RMS와 Std 차이
# ==============================

df["RMS_Std_Diff"] = (
    df["RMS"] - df["Std"]
).abs()

print()
print(
    "===== RMS vs STD ====="
)

print(
    "Mean Absolute Difference :",
    round(
        df["RMS_Std_Diff"].mean(),
        6
    )
)

print(
    "Median Absolute Difference :",
    round(
        df["RMS_Std_Diff"].median(),
        6
    )
)

print(
    "Maximum Absolute Difference :",
    round(
        df["RMS_Std_Diff"].max(),
        6
    )
)


# ==============================
# 5. RMS와 Std 상대 차이
# ==============================

df["RMS_Std_Diff_Percent"] = (
    df["RMS_Std_Diff"]
    / df["RMS"]
    * 100
)

print()
print(
    "Mean Difference % :",
    round(
        df["RMS_Std_Diff_Percent"].mean(),
        4
    ),
    "%"
)

print(
    "Median Difference % :",
    round(
        df["RMS_Std_Diff_Percent"].median(),
        4
    ),
    "%"
)

print(
    "Maximum Difference % :",
    round(
        df["RMS_Std_Diff_Percent"].max(),
        4
    ),
    "%"
)


# ==============================
# 6. 기본 통계 비교
# ==============================

print()
print(
    "===== FEATURE SUMMARY ====="
)

print(
    features.describe().round(4)
)