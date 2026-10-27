"""Decomposition of burden change into driver contributions.

Implements the **Das Gupta (1993) multiplicative decomposition** (a.k.a.
standardization & decomposition), the canonical demographic method also used in
the manuscript's decomposition analysis. Given a total that is the product of K
multiplicative drivers, it splits the relative change into percentage
contributions of each driver that sum to 100%.

The bundled driver table is ILLUSTRATIVE; feed real GBD demographic extracts
(age-specific population & rates) to obtain the authoritative decomposition.
"""
from __future__ import annotations
import numpy as np
import pandas as pd


def _log_mean(a: float, b: float) -> float:
    """Logarithmic mean S(a,b) = (a-b)/ln(a/b), limit a when a==b."""
    if a == b:
        return a
    return (a - b) / (np.log(a) - np.log(b))


def das_gupta(drivers_1990: dict, drivers_2021: dict):
    """Return (shares_pct, total_relative_change_log).

    shares_pct: dict driver -> % contribution to total relative change (sums to 100).
    total_relative_change_log: ln(T2021 / T1990).
    """
    keys = list(drivers_1990.keys())
    if set(keys) != set(drivers_2021.keys()):
        raise ValueError("driver sets must match between the two time points")
    dlog = {k: np.log(drivers_2021[k]) - np.log(drivers_1990[k]) for k in keys}
    total_change = sum(dlog.values())

    numer = {}
    denom = 0.0
    for i in keys:
        prod = 1.0
        for j in keys:
            if j == i:
                continue
            prod *= _log_mean(drivers_2021[j], drivers_1990[j])
        numer[i] = dlog[i] * prod
        denom += numer[i]

    if denom == 0:
        # no change -> equal attribution
        shares = {k: 100.0 / len(keys) for k in keys}
    else:
        shares = {k: (numer[k] / denom) * 100.0 for k in keys}
    return shares, total_change


def decomposition_for_region(df_decomp: pd.DataFrame, region: str):
    """Compute driver % contributions for one region from the driver table."""
    sub = df_decomp[df_decomp.region == region]
    d0 = dict(zip(sub.driver, sub.v1990))
    d1 = dict(zip(sub.driver, sub.v2021))
    shares, _ = das_gupta(d0, d1)
    return shares


def decomposition_all(df_decomp: pd.DataFrame) -> pd.DataFrame:
    """Contribution % table for every region (rows) x driver (columns)."""
    regions = sorted(df_decomp.region.unique().tolist())
    rows = []
    for region in regions:
        shares = decomposition_for_region(df_decomp, region)
        row = {"region": region}
        row.update(shares)
        rows.append(row)
    return pd.DataFrame(rows)
