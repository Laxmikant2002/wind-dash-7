import numpy as np
import pandas as pd


def compute_forecast_kpis(df: pd.DataFrame) -> dict[str, float | int]:
    """Compute forecast accuracy metrics for rows containing actual and forecast MW."""
    required_columns = {"actual", "forecast"}
    missing = required_columns.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    if df.empty:
        return {
            "mae_mw": 0.0,
            "rmse_mw": 0.0,
            "bias_mw": 0.0,
            "wape_percent": 0.0,
            "data_points": 0,
        }

    values = df[["actual", "forecast"]].dropna()
    if values.empty:
        return {
            "mae_mw": 0.0,
            "rmse_mw": 0.0,
            "bias_mw": 0.0,
            "wape_percent": 0.0,
            "data_points": 0,
        }

    residuals = values["forecast"] - values["actual"]
    abs_errors = np.abs(residuals)
    total_actual = values["actual"].sum()
    wape = abs_errors.sum() / total_actual * 100 if total_actual > 0 else 0.0

    return {
        "mae_mw": round(float(abs_errors.mean()), 2),
        "rmse_mw": round(float(np.sqrt((residuals**2).mean())), 2),
        "bias_mw": round(float(residuals.mean()), 2),
        "wape_percent": round(float(wape), 2),
        "data_points": int(len(values)),
    }
