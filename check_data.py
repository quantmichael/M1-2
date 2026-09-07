import pandas as pd

# 1. 데이터 불러오기
df = pd.read_csv("mixing_actuator.csv")

# 2. Date를 날짜/시간 자료형으로 변환
df["Date"] = pd.to_datetime(df["Date"])

# --------------------------------------------------
# 기본 정보
# --------------------------------------------------
print("=== 기본 정보 ===")
print("전체 행 수:", len(df))
print("Date 고유 개수:", df["Date"].nunique())

# --------------------------------------------------
# Date별 Sensor 개수
# --------------------------------------------------
date_counts = df.groupby("Date").size()

print("\n=== Date별 Sensor 개수 ===")
print(date_counts.head(20))

print("\nDate당 최소 Sensor 개수:", date_counts.min())
print("Date당 최대 Sensor 개수:", date_counts.max())
print("Date당 평균 Sensor 개수:", round(date_counts.mean(), 2))
print("Date당 Sensor 개수 중앙값:", date_counts.median())

# --------------------------------------------------
# Date 간 시간 간격
# --------------------------------------------------
unique_dates = (
    df["Date"]
    .drop_duplicates()
    .sort_values()
)

time_diff = unique_dates.diff().dropna()

print("\n=== Date 간 시간 간격 ===")
print(time_diff.head(20))

print("\n가장 많이 나타나는 시간 간격:")
print(time_diff.value_counts().head(10))

# --------------------------------------------------
# Quality 분포도 참고로 확인
# --------------------------------------------------
print("\n=== Quality 분포 ===")
print(df["Quality"].value_counts())

print("\n=== Quality 비율 (%) ===")
print(
    (df["Quality"].value_counts(normalize=True) * 100)
    .round(2)
)

# --------------------------------------------------
# Date별 Quality 구성 확인
# --------------------------------------------------

quality_by_date = (
    df.groupby(["Date", "Quality"])
      .size()
      .unstack(fill_value=0)
)

print("\n=== Date별 Quality 구성 ===")
print(quality_by_date.head(20))

# PASSED와 FAILED가 동시에 존재하는 Date
mixed_dates = quality_by_date[
    (quality_by_date.get("PASSED", 0) > 0) &
    (quality_by_date.get("FAILED", 0) > 0)
]

print("\n전체 Date 수:", len(quality_by_date))
print("PASSED/FAILED가 섞여 있는 Date 수:", len(mixed_dates))

# FAILED 비율
quality_by_date["FAILED_RATIO"] = (
    quality_by_date.get("FAILED", 0) /
    quality_by_date.sum(axis=1)
)

print("\n=== Date별 FAILED 비율 ===")
print(quality_by_date[["FAILED_RATIO"]].head(20))

print("\nFAILED 비율 최소:",
      quality_by_date["FAILED_RATIO"].min())

print("FAILED 비율 최대:",
      quality_by_date["FAILED_RATIO"].max())

print("FAILED 비율 평균:",
      quality_by_date["FAILED_RATIO"].mean())

print("\n=== Date별 Sensor 개수 분포 ===")
print(date_counts.value_counts().sort_index())

print("\n=== Sensor가 1024개가 아닌 Date ===")
abnormal_counts = date_counts[date_counts != 1024]

print(abnormal_counts)
print("\n1024개가 아닌 Date 수:", len(abnormal_counts))

import numpy as np

# --------------------------------------------------
# 2048개 Date 하나 상세 분석
# --------------------------------------------------

target_date = abnormal_counts.index[0]

target = (
    df[df["Date"] == target_date]
    .reset_index(drop=True)
)

first = target.iloc[:1024]
second = target.iloc[1024:]

print("\n=== 분석 대상 ===")
print("Date:", target_date)
print("전체 샘플:", len(target))
print("앞부분:", len(first))
print("뒷부분:", len(second))


def analyze_part(name, data):
    sensor = data["Sensor"]

    rms = np.sqrt(np.mean(sensor ** 2))

    print(f"\n=== {name} ===")
    print("Sensor 평균:", sensor.mean())
    print("Sensor 표준편차:", sensor.std())
    print("Sensor 최소:", sensor.min())
    print("Sensor 최대:", sensor.max())
    print("RMS:", rms)

    print("\nQuality:")
    print(data["Quality"].value_counts())

    print("\nQuality 비율(%):")
    print(
        (data["Quality"].value_counts(normalize=True) * 100)
        .round(2)
    )


analyze_part("앞 1024개", first)
analyze_part("뒤 1024개", second)