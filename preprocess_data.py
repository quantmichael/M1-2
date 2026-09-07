import pandas as pd
import numpy as np


# --------------------------------------------------
# 1. 원본 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv("mixing_actuator.csv")

print("원본 데이터 크기:", df.shape)


# --------------------------------------------------
# 2. Date 자료형 변환
# --------------------------------------------------

df["Date"] = pd.to_datetime(df["Date"])


# --------------------------------------------------
# 3. Date별 특징 추출
# --------------------------------------------------

features = (
    df.groupby("Date")
      .agg(
          Sample_Count=("Sensor", "count"),

          Mean=("Sensor", "mean"),
          Std=("Sensor", "std"),

          Min=("Sensor", "min"),
          Max=("Sensor", "max"),

          Failed_Count=(
              "Quality",
              lambda x: (x == "FAILED").sum()
          ),

          Passed_Count=(
              "Quality",
              lambda x: (x == "PASSED").sum()
          )
      )
      .reset_index()
)


# --------------------------------------------------
# 4. RMS 계산
# --------------------------------------------------

rms = (
    df.groupby("Date")["Sensor"]
      .apply(lambda x: np.sqrt(np.mean(x ** 2)))
      .reset_index(name="RMS")
)

features = features.merge(
    rms,
    on="Date",
    how="left"
)


# --------------------------------------------------
# 5. 추가 특징 계산
# --------------------------------------------------

features["Peak_to_Peak"] = (
    features["Max"] - features["Min"]
)

features["Failed_Ratio"] = (
    features["Failed_Count"]
    / features["Sample_Count"]
)


# --------------------------------------------------
# 6. 컬럼 순서 정리
# --------------------------------------------------

features = features[
    [
        "Date",
        "Sample_Count",
        "RMS",
        "Mean",
        "Std",
        "Min",
        "Max",
        "Peak_to_Peak",
        "Failed_Count",
        "Passed_Count",
        "Failed_Ratio"
    ]
]


# --------------------------------------------------
# 7. 시간순 정렬
# --------------------------------------------------

features = features.sort_values("Date")


# --------------------------------------------------
# 8. 결과 확인
# --------------------------------------------------

print("\n=== 생성된 특징 데이터 ===")
print(features.head(10))

print("\n데이터 크기:", features.shape)

print("\n=== 주요 특징 통계 ===")
print(
    features[
        [
            "RMS",
            "Std",
            "Peak_to_Peak",
            "Failed_Ratio"
        ]
    ].describe()
)


# --------------------------------------------------
# 9. CSV 저장
# --------------------------------------------------

features.to_csv(
    "mixing_actuator_features.csv",
    index=False
)

print(
    "\n저장 완료: mixing_actuator_features.csv"
)