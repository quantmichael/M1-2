import json
import numpy as np
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
# 2. 기본 RMS Summary
# ==============================

rms = df["RMS"]

latest_rms = rms.iloc[-1]

rms_percentile_rank = (
    (rms <= latest_rms).sum()
    / len(rms)
    * 100
)

rms_mean_difference_percent = (
    (latest_rms - rms.mean())
    / rms.mean()
    * 100
)


# ==============================
# 3. Trend 계산 함수
# ==============================

global_mean_rms = rms.mean()


def calculate_trend(
    data,
    end_time,
    hours
):

    start_time = (
        end_time
        - pd.Timedelta(hours=hours)
    )

    window = data[
        (data["Date"] >= start_time)
        & (data["Date"] <= end_time)
    ].copy()

    if len(window) < 5:
        return None

    elapsed_minutes = (
        window["Date"]
        - window["Date"].iloc[0]
    ).dt.total_seconds() / 60

    slope, intercept = np.polyfit(
        elapsed_minutes,
        window["RMS"],
        1
    )

    trend_start = intercept

    trend_end = (
        slope
        * elapsed_minutes.iloc[-1]
        + intercept
    )

    normalized_change = (
        (trend_end - trend_start)
        / global_mean_rms
        * 100
    )

    if slope > 0:
        direction = "increase"

    elif slope < 0:
        direction = "decrease"

    else:
        direction = "stable"

    return {
        "count": len(window),
        "direction": direction,
        "normalized_change_percent":
            normalized_change
    }


# ==============================
# 4. Trend Distribution 계산
# ==============================

def build_trend_distribution(
    data,
    hours
):

    values = []

    for end_time in data["Date"]:

        result = calculate_trend(
            data,
            end_time,
            hours
        )

        if result is not None:

            values.append(
                result[
                    "normalized_change_percent"
                ]
            )

    return values


trend_3h_distribution = (
    build_trend_distribution(
        df,
        3
    )
)

trend_6h_distribution = (
    build_trend_distribution(
        df,
        6
    )
)


# ==============================
# 5. 현재 Trend
# ==============================

latest_time = df["Date"].iloc[-1]

trend_3h = calculate_trend(
    df,
    latest_time,
    3
)

trend_6h = calculate_trend(
    df,
    latest_time,
    6
)


# ==============================
# 6. Trend Percentile Rank
# ==============================

def percentile_rank(
    distribution,
    value
):

    series = pd.Series(
        distribution
    )

    rank = (
        (series <= value).sum()
        / len(series)
        * 100
    )

    return rank


trend_3h["percentile_rank"] = (
    percentile_rank(
        trend_3h_distribution,
        trend_3h[
            "normalized_change_percent"
        ]
    )
)

trend_6h["percentile_rank"] = (
    percentile_rank(
        trend_6h_distribution,
        trend_6h[
            "normalized_change_percent"
        ]
    )
)


# ==============================
# 7. Peak-to-Peak
# ==============================

p2p = df["Peak_to_Peak"]

latest_p2p = p2p.iloc[-1]

p2p_percentile_rank = (
    (p2p <= latest_p2p).sum()
    / len(p2p)
    * 100
)


# ==============================
# 8. Manufacturing Summary
# ==============================

summary = {

    "equipment":
        "mixing_actuator",

    "value_metric":
        "RMS",

    "period": {

        "start":
            df["Date"]
            .iloc[0]
            .isoformat(),

        "end":
            df["Date"]
            .iloc[-1]
            .isoformat()
    },

    "count":
        len(df),

    "rms": {

        "average":
            round(
                rms.mean(),
                4
            ),

        "median":
            round(
                rms.median(),
                4
            ),

        "minimum":
            round(
                rms.min(),
                4
            ),

        "maximum":
            round(
                rms.max(),
                4
            ),

        "latest":
            round(
                latest_rms,
                4
            ),

        "percentile_rank":
            round(
                rms_percentile_rank,
                2
            ),

        "mean_difference_percent":
            round(
                rms_mean_difference_percent,
                2
            )
    },

    "trend": {

        "short_term_3h": {

            "count":
                trend_3h["count"],

            "direction":
                trend_3h["direction"],

            "normalized_change_percent":
                round(
                    trend_3h[
                        "normalized_change_percent"
                    ],
                    2
                ),

            "percentile_rank":
                round(
                    trend_3h[
                        "percentile_rank"
                    ],
                    2
                )
        },

        "mid_term_6h": {

            "count":
                trend_6h["count"],

            "direction":
                trend_6h["direction"],

            "normalized_change_percent":
                round(
                    trend_6h[
                        "normalized_change_percent"
                    ],
                    2
                ),

            "percentile_rank":
                round(
                    trend_6h[
                        "percentile_rank"
                    ],
                    2
                )
        }
    },

    "peak_to_peak": {

        "latest":
            round(
                latest_p2p,
                4
            ),

        "percentile_rank":
            round(
                p2p_percentile_rank,
                2
            )
    }
}


# ==============================
# 9. 출력
# ==============================

print(
    "===== MANUFACTURING SUMMARY ====="
)

print(
    json.dumps(
        summary,
        indent=2,
        ensure_ascii=False
    )
)