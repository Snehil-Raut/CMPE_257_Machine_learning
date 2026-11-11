from pathlib import Path

import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .data import data

app = FastAPI(title="Store Forecast Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parents[1] / "frontend"

app.mount(
    "/frontend",
    StaticFiles(directory=FRONTEND_DIR),
    name="frontend",
)


@app.get("/")
def frontend():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "items": len(data.items),
        "forecast_rows": len(data.forecasts),
        "stores": sorted(data.items["store_id"].unique().tolist()),
    }


@app.get("/model-info")
def model_info():
    return data.model_info


@app.get("/api/stores")
def stores():
    return sorted(data.items["store_id"].unique().tolist())


@app.get("/api/items")
def items(
    store_id: str | None = None,
    search: str = "",
    limit: int = Query(default=50, ge=1, le=200),
):
    result = data.items.copy()

    if store_id:
        result = result[result["store_id"] == store_id]

    if search:
        search = search.lower()
        result = result[
            result["id"].str.lower().str.contains(search)
            | result["item_id"].str.lower().str.contains(search)
            | result["dept_id"].str.lower().str.contains(search)
            | result["cat_id"].str.lower().str.contains(search)
        ]

    return result.head(limit).to_dict(orient="records")


@app.get("/api/summary")
def summary(store_id: str | None = None):
    items = data.items.copy()

    if store_id:
        items = items[items["store_id"] == store_id]

    item_ids = set(items["id"])

    sales = data.sales[data.sales["id"].isin(item_ids)].copy()
    forecasts = data.forecasts[data.forecasts["id"].isin(item_ids)].copy()

    sales_total = float(sales["sales"].sum())
    forecast_total = float(forecasts["forecast"].sum())

    sales_by_date = (
        sales.groupby("date", as_index=False)["sales"]
        .sum()
        .sort_values("date")
    )

    forecast_by_date = (
        forecasts.groupby("date", as_index=False)["forecast"]
        .sum()
        .sort_values("date")
    )

    return {
        "sales_total": round(sales_total, 2),
        "forecast_total": round(forecast_total, 2),
        "sales_days": [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "value": round(float(row["sales"]), 2),
            }
            for _, row in sales_by_date.iterrows()
        ],
        "forecast_days": [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "value": round(float(row["forecast"]), 2),
            }
            for _, row in forecast_by_date.iterrows()
        ],
    }


@app.get("/api/series")
def series(item_id: str, store_id: str):
    matching_items = data.items[
        (data.items["item_id"] == item_id)
        & (data.items["store_id"] == store_id)
    ]

    if matching_items.empty:
        return {"error": "Item not found"}

    series_id = matching_items.iloc[0]["id"]

    sales = data.sales[data.sales["id"] == series_id].copy()
    forecasts = data.forecasts[data.forecasts["id"] == series_id].copy()

    return {
        "item": matching_items.iloc[0].to_dict(),
        "sales": [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "value": float(row["sales"]),
            }
            for _, row in sales.sort_values("date").iterrows()
        ],
        "forecasts": [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "value": round(float(row["forecast"]), 2),
            }
            for _, row in forecasts.sort_values("date").iterrows()
        ],
    }