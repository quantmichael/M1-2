import pandas as pd
import matplotlib.pyplot as plt


# --------------------------------------------------
# 1. 특징 데이터 불러오기
# --------------------------------------------------

df = pd.read_csv("mixing_actuator_features.csv")

df["Date"] = pd.to_datetime(df["Date"])

df = df.sort_values("Date").reset_index(drop=True)

print("데이터 크기:", df.shape)
print("시작:", df["Date"].min())
print("종료:", df["Date"].max())


# --------------------------------------------------
# 2. RMS 시계열 그래프
# --------------------------------------------------

plt.figure(figsize=(14, 6))

plt.plot(
    df["Date"],
    df["RMS"],
    linewidth=1.5,
    label="RMS"
)

plt.title("Mixing Actuator - RMS Vibration Time Series")
plt.xlabel("Date")
plt.ylabel("RMS")
plt.grid(alpha=0.3)
plt.legend()

plt.tight_layout()

# Sample_Count가 2048인 측정 지점
special = df[df["Sample_Count"] == 2048]

plt.scatter(
    special["Date"],
    special["RMS"],
    s=60,
    marker="x",
    label="2048 samples"
)

print("\n=== Sample_Count 2048인 측정 ===")

print(
    special[
        ["Date", "Sample_Count", "RMS"]
    ].to_string(index=False)
)

plt.show()