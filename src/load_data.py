"""Data loading & small validation helpers."""
from __future__ import annotations
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_burden(path: str | Path | None = None) -> pd.DataFrame:
    """Load the long-format burden table.

    Expected columns: region, year, metric, value, lower, upper
    (rates per 100,000).
    """
    path = Path(path) if path else DATA_DIR / "sample_burden.csv"
    df = pd.read_csv(path)
    required = {"region", "year", "metric", "value", "lower", "upper"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"burden file missing columns: {missing}")
    return df


def load_decomp(path: str | Path | None = None) -> pd.DataFrame:
    """Load the decomposition driver table.

    Expected columns: region, driver, v1990, v2021.
    """
    path = Path(path) if path else DATA_DIR / "decomp_drivers.csv"
    df = pd.read_csv(path)
    required = {"region", "driver", "v1990", "v2021"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"decomp file missing columns: {missing}")
    return df


def get_series(df: pd.DataFrame, region: str, metric: str):
    """Return (years, value, lower, upper) sorted by year for one region/metric."""
    sub = df[(df.region == region) & (df.metric == metric)].sort_values("year")
    return (
        sub["year"].to_numpy(),
        sub["value"].to_numpy(),
        sub["lower"].to_numpy(),
        sub["upper"].to_numpy(),
    )


def regions(df: pd.DataFrame) -> list[str]:
    return sorted(df["region"].unique().tolist())


def metrics(df: pd.DataFrame) -> list[str]:
    return sorted(df["metric"].unique().tolist())
