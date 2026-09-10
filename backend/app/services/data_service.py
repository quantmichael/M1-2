import numpy as np
import pandas as pd

from fastapi import HTTPException

from app.firebase import db


# --------------------------------------------------
# 추세 변화량 계산
# --------------------------------------------------
def calculate_trend(window_df, mean_value):

    if len(window_df) < 2:
        return 0.0

    elapsed_minutes = (
        window_df["date"]
        - window_df["date"].iloc[0]
    ).dt.total_seconds() / 60

    slope, intercept = np.polyfit(
        elapsed_minutes,
        window_df["value"],
        1
    )

    trend_start = intercept

    trend_end = (
        slope * elapsed_minutes.iloc[-1]
        + intercept
    )

    normalized_change_percent = (
        (trend_end - trend_start)
        / mean_value
        * 100
    )

    return float(
        normalized_change_percent
    )


# --------------------------------------------------
# 추세 방향 계산
# --------------------------------------------------
def get_trend_direction(
    change_percent
):

    if change_percent > 0:
        return "increase"

    elif change_percent < 0:
        return "decrease"

    return "stable"


# --------------------------------------------------
# 과거 동일 시간 구간의 추세 변화량 계산
# --------------------------------------------------
def calculate_historical_trends(
    df,
    hours,
    mean_value
):

    historical_changes = []

    for current_time in df["date"]:

        start_time = (
            current_time
            - pd.Timedelta(hours=hours)
        )

        window_df = df[
            (df["date"] >= start_time)
            & (df["date"] <= current_time)
        ]

        if len(window_df) >= 2:

            change_percent = (
                calculate_trend(
                    window_df,
                    mean_value
                )
            )

            historical_changes.append(
                change_percent
            )

    return historical_changes


# --------------------------------------------------
# 백분위 위치 계산
# --------------------------------------------------
def calculate_percentile_rank(
    values,
    current_value
):

    if len(values) == 0:
        return None

    values = np.array(
        values
    )

    percentile_rank = (
        (values <= current_value).sum()
        / len(values)
        * 100
    )

    return float(
        percentile_rank
    )


# --------------------------------------------------
# Manufacturing Summary 생성
# --------------------------------------------------
def get_data_summary():

    docs = db.collection(
        "data"
    ).stream()

    records = []

    for doc in docs:

        item = doc.to_dict()

        records.append({
            "date": item["date"],
            "value": item["value"],
            "peak_to_peak": item.get(
                "peak_to_peak"
            ),
        })

    if not records:

        raise HTTPException(
            status_code=404,
            detail="분석할 데이터가 없습니다."
        )

    # ==================================================
    # DataFrame 준비
    # ==================================================

    df = pd.DataFrame(
        records
    )

    df["date"] = pd.to_datetime(
        df["date"],
        utc=True
    )

    df["value"] = pd.to_numeric(
        df["value"]
    )

    df["peak_to_peak"] = pd.to_numeric(
        df["peak_to_peak"],
        errors="coerce"
    )

    df = (
        df.sort_values("date")
        .reset_index(drop=True)
    )


    # ==================================================
    # RMS 기본 통계
    # ==================================================

    mean_value = (
        df["value"].mean()
    )

    latest_value = (
        df.iloc[-1]["value"]
    )

    percentile_rank = (
        (df["value"] <= latest_value).sum()
        / len(df)
        * 100
    )

    mean_difference_percent = (
        (latest_value - mean_value)
        / mean_value
        * 100
    )


    # ==================================================
    # 최신 측정 시각
    # ==================================================

    latest_time = (
        df["date"].max()
    )


    # ==================================================
    # 최근 3시간 추세
    # ==================================================

    three_hours_ago = (
        latest_time
        - pd.Timedelta(hours=3)
    )

    recent_3h = df[
        df["date"] >= three_hours_ago
    ].copy()

    change_3h = (
        calculate_trend(
            recent_3h,
            mean_value
        )
    )

    direction_3h = (
        get_trend_direction(
            change_3h
        )
    )


    # ==================================================
    # 과거 3시간 추세 분포
    # ==================================================

    historical_3h = (
        calculate_historical_trends(
            df,
            3,
            mean_value
        )
    )

    change_percentile_3h = (
        calculate_percentile_rank(
            historical_3h,
            change_3h
        )
    )


    # ==================================================
    # 최근 6시간 추세
    # ==================================================

    six_hours_ago = (
        latest_time
        - pd.Timedelta(hours=6)
    )

    recent_6h = df[
        df["date"] >= six_hours_ago
    ].copy()

    change_6h = (
        calculate_trend(
            recent_6h,
            mean_value
        )
    )

    direction_6h = (
        get_trend_direction(
            change_6h
        )
    )


    # ==================================================
    # 과거 6시간 추세 분포
    # ==================================================

    historical_6h = (
        calculate_historical_trends(
            df,
            6,
            mean_value
        )
    )

    change_percentile_6h = (
        calculate_percentile_rank(
            historical_6h,
            change_6h
        )
    )


    # ==================================================
    # Peak-to-Peak 분석
    # ==================================================

    p2p_df = df.dropna(
        subset=["peak_to_peak"]
    )

    latest_p2p = None
    p2p_percentile_rank = None

    if not p2p_df.empty:

        latest_p2p = (
            p2p_df
            .iloc[-1]["peak_to_peak"]
        )

        p2p_percentile_rank = (
            (
                p2p_df["peak_to_peak"]
                <= latest_p2p
            ).sum()
            / len(p2p_df)
            * 100
        )


    # ==================================================
    # Manufacturing Summary
    # ==================================================

    summary = {

        "equipment": (
            "mixing_actuator"
        ),

        "value_metric": (
            "RMS"
        ),

        "period": {

            "start": (
                df["date"]
                .min()
                .isoformat()
            ),

            "end": (
                df["date"]
                .max()
                .isoformat()
            ),
        },

        "count": len(df),

        "rms": {

            "average": round(
                mean_value,
                4
            ),

            "median": round(
                df["value"].median(),
                4
            ),

            "minimum": round(
                df["value"].min(),
                4
            ),

            "maximum": round(
                df["value"].max(),
                4
            ),

            "latest": round(
                latest_value,
                4
            ),

            "percentile_rank": round(
                percentile_rank,
                2
            ),

            "mean_difference_percent": round(
                mean_difference_percent,
                2
            ),
        },

        "trend": {

            "short_term_3h": {

                "count": len(
                    recent_3h
                ),

                "direction": (
                    direction_3h
                ),

                "normalized_change_percent": round(
                    change_3h,
                    2
                ),

                "change_percentile_rank": (
                    round(
                        change_percentile_3h,
                        2
                    )
                    if change_percentile_3h
                    is not None
                    else None
                ),
            },

            "mid_term_6h": {

                "count": len(
                    recent_6h
                ),

                "direction": (
                    direction_6h
                ),

                "normalized_change_percent": round(
                    change_6h,
                    2
                ),

                "change_percentile_rank": (
                    round(
                        change_percentile_6h,
                        2
                    )
                    if change_percentile_6h
                    is not None
                    else None
                ),
            },
        },

        "peak_to_peak": {

            "latest": (
                round(
                    latest_p2p,
                    4
                )
                if latest_p2p
                is not None
                else None
            ),

            "percentile_rank": (
                round(
                    p2p_percentile_rank,
                    2
                )
                if p2p_percentile_rank
                is not None
                else None
            ),
        },
    }

    return summary