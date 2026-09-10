import pandas as pd
import numpy as np


# 1. 데이터 불러오기
df = pd.read_csv("mixing_actuator_features.csv")


# 2. Date 변환
df["Date"] = pd.to_datetime(df["Date"])


# 3. 시간순 정렬
df = df.sort_values("Date").reset_index(drop=True)


# ==============================
# 기본 Summary
# ==============================

start_date = df["Date"].min()
end_date = df["Date"].max()

count = len(df)

avg_rms = df["RMS"].mean()
min_rms = df["RMS"].min()
max_rms = df["RMS"].max()
latest_rms = df.iloc[-1]["RMS"]


# ==============================
# 최근 추세 분석
# ==============================

RECENT_COUNT = 20

recent = df.tail(RECENT_COUNT).copy()


# 첫 번째 시간을 기준으로 경과 시간을 분 단위로 계산
recent["elapsed_minutes"] = (
    recent["Date"] - recent["Date"].iloc[0]
).dt.total_seconds() / 60


# 선형 추세선 계산
slope, intercept = np.polyfit(
    recent["elapsed_minutes"],
    recent["RMS"],
    1
)


# 추세선 기준 시작값 / 종료값
trend_start = intercept

last_minute = recent["elapsed_minutes"].iloc[-1]

trend_end = (
    slope * last_minute
    + intercept
)


# 추세 변화율
trend_change_percent = (
    (trend_end - trend_start)
    / trend_start
    * 100
)


# 증가 / 감소 / 안정 판단
if trend_change_percent >= 5:
    trend = "increase"

elif trend_change_percent <= -5:
    trend = "decrease"

else:
    trend = "stable"


# ==============================
# 결과 출력
# ==============================

print("===== RMS SUMMARY =====")

print("Period :", start_date, "~", end_date)
print("Count :", count)

print()
print("Average RMS :", round(avg_rms, 4))
print("Minimum RMS :", round(min_rms, 4))
print("Maximum RMS :", round(max_rms, 4))
print("Latest RMS  :", round(latest_rms, 4))

print()
print("===== RECENT TREND =====")

print("Recent Count :", len(recent))
print("Slope :", round(slope, 6))

print(
    "Trend Start :",
    round(trend_start, 4)
)

print(
    "Trend End   :",
    round(trend_end, 4)
)

print(
    "Trend Change:",
    round(trend_change_percent, 2),
    "%"
)

print(
    "Trend:",
    trend
)

def calculate_trend(data, recent_count):

    recent = data.tail(recent_count).copy()

    # 첫 측정 시점을 기준으로 실제 경과 시간(분) 계산
    recent["elapsed_minutes"] = (
        recent["Date"] - recent["Date"].iloc[0]
    ).dt.total_seconds() / 60

    # 선형 추세선
    slope, intercept = np.polyfit(
        recent["elapsed_minutes"],
        recent["RMS"],
        1
    )

    last_minute = recent["elapsed_minutes"].iloc[-1]

    trend_start = intercept
    trend_end = slope * last_minute + intercept

    trend_change_percent = (
        (trend_end - trend_start)
        / trend_start
        * 100
    )

    if trend_change_percent >= 5:
        trend = "increase"

    elif trend_change_percent <= -5:
        trend = "decrease"

    else:
        trend = "stable"

    return {
        "count": recent_count,
        "start": trend_start,
        "end": trend_end,
        "change_percent": trend_change_percent,
        "slope": slope,
        "trend": trend
    }


print()
print("===== WINDOW COMPARISON =====")

for window in [10, 20, 30, 50]:

    result = calculate_trend(df, window)

    print()
    print("Window :", result["count"])
    print("Start  :", round(result["start"], 4))
    print("End    :", round(result["end"], 4))
    print("Change :", round(result["change_percent"], 2), "%")
    print("Slope  :", round(result["slope"], 6))
    print("Trend  :", result["trend"])

def calculate_time_trend(data, hours=None, minutes=None):

    # 마지막 측정 시각
    end_time = data["Date"].max()

    # 분석 시작 시각
    if minutes is not None:
        start_time = end_time - pd.Timedelta(minutes=minutes)
        label = f"{minutes} minutes"

    else:
        start_time = end_time - pd.Timedelta(hours=hours)
        label = f"{hours} hours"

    # 해당 시간 범위의 데이터만 선택
    recent = data[
        (data["Date"] >= start_time) &
        (data["Date"] <= end_time)
    ].copy()

    # 데이터가 너무 적으면 추세 계산 불가
    if len(recent) < 2:
        return {
            "period": label,
            "count": len(recent),
            "trend": "insufficient_data"
        }

    # 선택된 첫 측정시점을 0분으로 설정
    recent["elapsed_minutes"] = (
        recent["Date"] - recent["Date"].iloc[0]
    ).dt.total_seconds() / 60

    # 선형 추세선
    slope, intercept = np.polyfit(
        recent["elapsed_minutes"],
        recent["RMS"],
        1
    )

    last_minute = recent["elapsed_minutes"].iloc[-1]

    trend_start = intercept
    trend_end = slope * last_minute + intercept

    trend_change_percent = (
        (trend_end - trend_start)
        / trend_start
        * 100
    )

    # 현재는 이전과 동일하게 ±5% 사용
    if trend_change_percent >= 5:
        trend = "increase"

    elif trend_change_percent <= -5:
        trend = "decrease"

    else:
        trend = "stable"

    return {
        "period": label,
        "count": len(recent),
        "actual_start": recent["Date"].iloc[0],
        "actual_end": recent["Date"].iloc[-1],
        "start": trend_start,
        "end": trend_end,
        "change_percent": trend_change_percent,
        "slope": slope,
        "trend": trend
    }


print()
print("===== TIME WINDOW COMPARISON =====")

time_windows = [
    {"minutes": 30},
    {"hours": 1},
    {"hours": 3},
    {"hours": 6}
]


for window in time_windows:

    result = calculate_time_trend(
        df,
        **window
    )

    print()
    print("Period :", result["period"])
    print("Count  :", result["count"])

    if result["trend"] == "insufficient_data":
        print("Trend  : insufficient_data")
        continue

    print("Actual :", result["actual_start"], "~", result["actual_end"])
    print("Start  :", round(result["start"], 4))
    print("End    :", round(result["end"], 4))
    print(
        "Change :",
        round(result["change_percent"], 2),
        "%"
    )
    print("Slope  :", round(result["slope"], 6))
    print("Trend  :", result["trend"])