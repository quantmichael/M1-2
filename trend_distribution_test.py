import pandas as pd
import numpy as np


# ==============================
# 1. 데이터 로드
# ==============================

df = pd.read_csv("mixing_actuator_features.csv")

df["Date"] = pd.to_datetime(df["Date"])

df = (
    df
    .sort_values("Date")
    .reset_index(drop=True)
)


# ==============================
# 2. 특정 시점 기준 추세 계산
# ==============================

def calculate_trend_at_time(data, end_time, hours):

    start_time = (
        end_time
        - pd.Timedelta(hours=hours)
    )

    recent = data[
        (data["Date"] >= start_time)
        & (data["Date"] <= end_time)
    ].copy()

    # 너무 적은 데이터로 추세를 계산하지 않음
    if len(recent) < 5:
        return None

    recent["elapsed_minutes"] = (
        recent["Date"]
        - recent["Date"].iloc[0]
    ).dt.total_seconds() / 60

    # 시간 차이가 실제로 존재하는지 확인
    if recent["elapsed_minutes"].nunique() < 2:
        return None

    slope, intercept = np.polyfit(
        recent["elapsed_minutes"],
        recent["RMS"],
        1
    )

    last_minute = (
        recent["elapsed_minutes"].iloc[-1]
    )

    trend_start = intercept

    trend_end = (
        slope * last_minute
        + intercept
    )

    # 0에 지나치게 가까운 값 보호
    if abs(trend_start) < 1e-10:
        return None

    global_mean_rms = data["RMS"].mean()

    change_percent = (
        (trend_end - trend_start)
        / global_mean_rms
        * 100
    )

    return {
        "end_time": end_time,
        "count": len(recent),
        "change_percent": change_percent
    }


# ==============================
# 3. 전체 시점에 대해 계산
# ==============================

def build_distribution(data, hours):

    results = []

    for end_time in data["Date"]:

        result = calculate_trend_at_time(
            data,
            end_time,
            hours
        )

        if result is not None:
            results.append(result)

    return pd.DataFrame(results)


trend_3h = build_distribution(df, 3)
trend_6h = build_distribution(df, 6)


# ==============================
# 4. 분포 출력 함수
# ==============================

def print_distribution(name, trend_df):

    values = trend_df["change_percent"]

    print()
    print(
        "=====",
        name,
        "====="
    )

    print(
        "Valid Windows :",
        len(values)
    )

    print(
        "Mean          :",
        round(values.mean(), 2),
        "%"
    )

    print(
        "Median        :",
        round(values.median(), 2),
        "%"
    )

    print(
        "Std           :",
        round(values.std(), 2),
        "%"
    )

    print(
        "Minimum       :",
        round(values.min(), 2),
        "%"
    )

    print(
        "Maximum       :",
        round(values.max(), 2),
        "%"
    )

    print()
    print("Percentiles")

    for p in [
        0.05,
        0.10,
        0.25,
        0.50,
        0.75,
        0.90,
        0.95
    ]:

        value = values.quantile(p)

        print(
            f"{int(p * 100):>2}% :",
            round(value, 2),
            "%"
        )


# ==============================
# 5. 결과
# ==============================

print_distribution(
    "3 HOUR TREND DISTRIBUTION",
    trend_3h
)

print_distribution(
    "6 HOUR TREND DISTRIBUTION",
    trend_6h
)


# ==============================
# 6. 마지막 시점 위치 확인
# ==============================

print()
print(
    "===== CURRENT POSITION ====="
)

current_3h = calculate_trend_at_time(
    df,
    df["Date"].max(),
    3
)

current_6h = calculate_trend_at_time(
    df,
    df["Date"].max(),
    6
)

print(
    "Current 3H Change :",
    round(
        current_3h["change_percent"],
        2
    ),
    "%"
)

print(
    "Current 6H Change :",
    round(
        current_6h["change_percent"],
        2
    ),
    "%"
)