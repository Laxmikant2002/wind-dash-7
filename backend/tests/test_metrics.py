import pandas as pd

from app import data_loader
from app.metrics import compute_forecast_kpis


def test_compute_forecast_kpis():
    frame = pd.DataFrame({"actual": [100, 200], "forecast": [110, 180]})

    assert compute_forecast_kpis(frame) == {
        "mae_mw": 15.0,
        "rmse_mw": 15.81,
        "bias_mw": -5.0,
        "wape_percent": 10.0,
        "data_points": 2,
    }


def test_empty_frame_returns_zero_metrics():
    result = compute_forecast_kpis(pd.DataFrame(columns=["actual", "forecast"]))

    assert result["data_points"] == 0
    assert result["mae_mw"] == 0.0


def test_elexon_join_uses_latest_forecast_before_decision_cutoff(monkeypatch):
    datasets = {
        "FUELHH": [
            {"fuelType": "WIND", "startTime": "2026-01-15T12:00:00Z", "generation": 100},
            {"fuelType": "SOLAR", "startTime": "2026-01-15T12:00:00Z", "generation": 900},
        ],
        "WINDFOR": [
            {"startTime": "2026-01-15T12:00:00Z", "publishTime": "2026-01-14T10:00:00Z", "generation": 80},
            {"startTime": "2026-01-15T12:00:00Z", "publishTime": "2026-01-15T10:59:00Z", "generation": 120},
            {"startTime": "2026-01-15T12:00:00Z", "publishTime": "2026-01-15T11:01:00Z", "generation": 140},
        ],
    }

    monkeypatch.setattr(data_loader, "_request_dataset", lambda dataset, start, end: datasets[dataset])

    result = data_loader._load_from_elexon()

    assert result[["actual", "forecast"]].to_dict("records") == [{"actual": 100, "forecast": 80}]


def test_elexon_join_excludes_forecast_after_cutoff(monkeypatch):
    datasets = {
        "FUELHH": [
            {"fuelType": "WIND", "startTime": "2026-01-15T14:00:00Z", "generation": 250},
        ],
        "WINDFOR": [
            {"startTime": "2026-01-15T14:00:00Z", "publishTime": "2026-01-14T10:30:00Z", "generation": 200},
            {"startTime": "2026-01-15T14:00:00Z", "publishTime": "2026-01-14T11:30:00Z", "generation": 999},
        ],
    }

    monkeypatch.setattr(data_loader, "_request_dataset", lambda dataset, start, end: datasets[dataset])

    result = data_loader._load_from_elexon()

    assert result.iloc[0]["forecast"] == 200
