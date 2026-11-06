"""Store forecast API: entry point."""
from fastapi import FastAPI

from .data import data

app = FastAPI(title="Store Forecast API", version="0.1.0")


@app.get("/health")
def health():
    """Quick check that the server is up and the data loaded."""
    return {
        "status": "ok",
        "items": len(data.items),
        "forecast_rows": len(data.forecasts),
        "stores": sorted(data.items["store_id"].unique().tolist()),
    }


@app.get("/model-info")
def model_info():
    """Which model made the forecasts (for the About page)."""
    return data.model_info