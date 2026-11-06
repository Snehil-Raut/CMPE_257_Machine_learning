from pathlib import Path
import json

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


class AppData:
    def __init__(self):
        self.items = pd.read_parquet(DATA_DIR / "items.parquet")
        self.forecasts = pd.read_parquet(DATA_DIR / "forecasts.parquet")
        self.sales = pd.read_parquet(DATA_DIR / "sales.parquet")
        self.model_info = json.loads((DATA_DIR / "model_info.json").read_text())


data = AppData()