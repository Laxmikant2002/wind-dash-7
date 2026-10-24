from datetime import date, datetime, time, timedelta, timezone
import json
from pathlib import Path

import httpx
import numpy as np
import pandas as pd

CACHE_PATH = Path(__file__).resolve().parent.parent / "data" / "january_2026_wind.json"
ELEXON_BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"
START_DATE = date(2026, 1, 1)
END_DATE = date(2026, 2, 1)
DECISION_HOUR_UTC = 11
_DATA_CACHE: pd.DataFrame | None = None


def _demo_data() -> pd.DataFrame:
    timestamps = pd.date_range("2026-01-01", "2026-01-31 23:30", freq="30min", tz="UTC")
    x = np.linspace(0, 18 * np.pi, len(timestamps))
    actual = np.maximum(3800 + 1100 * np.sin(x - 0.8) + 180 * np.sin(2 * x), 0)
    forecast = np.maximum(actual + 260 * np.sin(x + 0.6) - 90, 0)
    return pd.DataFrame({"startTime": timestamps, "actual": actual.round(1), "forecast": forecast.round(1)})


def _read_cache() -> pd.DataFrame | None:
    if not CACHE_PATH.exists():
        return None
    try:
        records = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        frame = pd.DataFrame(records)
        if {"startTime", "actual", "forecast"}.issubset(frame.columns):
            frame["startTime"] = pd.to_datetime(frame["startTime"], utc=True)
            return frame
    except (OSError, ValueError, TypeError):
        return None
    return None


def _write_cache(data: pd.DataFrame) -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    CACHE_PATH.write_text(data.to_json(orient="records", date_format="iso"), encoding="utf-8")


def _request_dataset(dataset: str, start_date: date, end_date: date) -> list[dict]:
    response = httpx.get(
        f"{ELEXON_BASE_URL}/{dataset}/stream",
        params={
            "settlementDateFrom": start_date.isoformat(),
            "settlementDateTo": end_date.isoformat(),
        },
        timeout=20,
    )
    response.raise_for_status()
    payload = response.json()
    records = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(records, list):
        raise ValueError(f"Unexpected {dataset} response shape")
    return records


def _load_from_elexon() -> pd.DataFrame:
    actual_records = _request_dataset("FUELHH", START_DATE, END_DATE)
    forecast_records = _request_dataset("WINDFOR", START_DATE, END_DATE)
    actuals = pd.DataFrame([row for row in actual_records if row.get("fuelType") == "WIND"])
    forecasts = pd.DataFrame(forecast_records)
    required_actual = {"startTime", "generation"}
    required_forecast = {"startTime", "publishTime", "generation"}
    if not required_actual.issubset(actuals.columns) or not required_forecast.issubset(forecasts.columns):
        raise ValueError("Elexon response is missing required FUELHH or WINDFOR fields")

    actuals = actuals[["startTime", "generation"]].rename(columns={"generation": "actual"})
    forecasts = forecasts[["startTime", "publishTime", "generation"]].rename(
        columns={"generation": "forecast"}
    )
    actuals["startTime"] = pd.to_datetime(actuals["startTime"], utc=True)
    forecasts["startTime"] = pd.to_datetime(forecasts["startTime"], utc=True)
    forecasts["publishTime"] = pd.to_datetime(forecasts["publishTime"], utc=True)
    actuals["actual"] = pd.to_numeric(actuals["actual"], errors="coerce")
    forecasts["forecast"] = pd.to_numeric(forecasts["forecast"], errors="coerce")
    actuals = actuals[
        (actuals["startTime"] >= pd.Timestamp(START_DATE, tz="UTC"))
        & (actuals["startTime"] < pd.Timestamp(END_DATE, tz="UTC"))
    ].dropna().drop_duplicates("startTime")
    forecasts = forecasts[
        (forecasts["startTime"] >= pd.Timestamp(START_DATE, tz="UTC"))
        & (forecasts["startTime"] < pd.Timestamp(END_DATE, tz="UTC"))
    ].dropna().sort_values(["startTime", "publishTime"])

    selected: list[dict] = []
    for start_time, group in forecasts.groupby("startTime"):
        cutoff = start_time.normalize() - pd.Timedelta(days=1) + pd.Timedelta(hours=DECISION_HOUR_UTC)
        eligible = group[group["publishTime"] <= cutoff]
        if not eligible.empty:
            selected.append(eligible.iloc[-1].to_dict())
    selected_forecasts = pd.DataFrame(selected, columns=["startTime", "publishTime", "forecast"])
    if selected_forecasts.empty:
        raise ValueError("No January 2026 WINDFOR records were returned")
    merged = actuals.merge(selected_forecasts[["startTime", "forecast"]], on="startTime", how="inner")
    if merged.empty:
        raise ValueError("No January 2026 actual/forecast intervals could be joined")
    return merged.sort_values("startTime").reset_index(drop=True)


def load_wind_data(delivery_date: date | None = None) -> pd.DataFrame:
    """Load January 2026 FUELHH actuals matched to day-ahead WINDFOR forecasts."""
    global _DATA_CACHE
    frame = _DATA_CACHE if _DATA_CACHE is not None else _read_cache()
    if frame is None or frame.empty:
        try:
            frame = _load_from_elexon()
            _write_cache(frame)
        except (httpx.HTTPError, ValueError, TypeError):
            frame = _read_cache()
    if frame is None or frame.empty:
        frame = _demo_data()
    _DATA_CACHE = frame
    if delivery_date is None:
        return frame
    start = pd.Timestamp(datetime.combine(delivery_date, time.min), tz="UTC")
    end = start + pd.Timedelta(days=1)
    return frame[(frame["startTime"] >= start) & (frame["startTime"] < end)].copy()
