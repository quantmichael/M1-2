from pathlib import Path

import pandas as pd

from app.firebase import db


BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "mixing_actuator_features.csv"


def main():
    df = pd.read_csv(CSV_PATH)

    print(f"CSV 데이터 수: {len(df)}")

    for index, row in df.iterrows():
        doc_ref = db.collection("data").document()

        doc_ref.set({
            "date": row["Date"],
            "value": float(row["RMS"]),
            "memo": "교반구동장치 진동 측정",
            "peak_to_peak": float(row["Peak_to_Peak"]),
            "sample_count": int(row["Sample_Count"]),
        })

    print("Firestore 데이터 저장 완료")


if __name__ == "__main__":
    main()