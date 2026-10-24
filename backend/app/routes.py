from datetime import date

from fastapi import APIRouter, Query

from app.data_loader import load_wind_data
from app.metrics import compute_forecast_kpis

router = APIRouter()


@router.get("/day-ahead")
def day_ahead(delivery_date: date = Query(default=date(2026, 1, 15))) -> dict:
    if delivery_date.month != 1 or delivery_date.year != 2026:
        return {"records": [], "metrics": {}, "message": "Only January 2026 is in scope."}
    frame = load_wind_data(delivery_date)

    records = []
    for row in frame.to_dict(orient="records"):
        actual = float(row["actual"])
        forecast = float(row["forecast"])
        records.append(
            {
                "startTime": row["startTime"].isoformat(),
                "actual_mw": actual,
                "forecast_mw": forecast,
                "residual_mw": round(forecast - actual, 2),
            }
        )
    return {"records": records, "metrics": compute_forecast_kpis(frame)}


@router.get("/metrics")
def metrics() -> dict:
    frame = load_wind_data()
    return compute_forecast_kpis(frame)
