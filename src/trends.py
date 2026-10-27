"""Temporal trend metrics: AAPC via Joinpoint-style log-linear regression.

Mirrors the single-segment Average Annual Percent Change (AAPC) reported by the
Joinpoint software: fit ln(rate) ~ year and report (exp(slope)-1)*100 with a
95% CI. For multi-segment AAPC, fit Joinpoint on the real extract.
"""
from __future__ import annotations
import numpy as np
from scipy import stats
import pandas as pd
from . import load_data


def compute_aapc(years, values):
    """Return dict with aapc, lo, hi (95% CI) and p_value."""
    years = np.asarray(years, dtype=float)
    values = np.asarray(values, dtype=float)
    mask = np.isfinite(values) & (values > 0)
    years, values = years[mask], values[mask]
    if len(years) < 3:
        return {"aapc": np.nan, "lo": np.nan, "hi": np.nan, "p_value": np.nan}
    log_v = np.log(values)
    res = stats.linregress(years, log_v)
    slope = res.slope
    # delta method CI on slope -> CI on AAPC
    slope_lo = res.slope - 1.96 * res.stderr
    slope_hi = res.slope + 1.96 * res.stderr
    aapc = (np.exp(slope) - 1.0) * 100.0
    lo = (np.exp(slope_lo) - 1.0) * 100.0
    hi = (np.exp(slope_hi) - 1.0) * 100.0
    return {"aapc": aapc, "lo": lo, "hi": hi, "p_value": res.pvalue}


def aapc_table(df: pd.DataFrame) -> pd.DataFrame:
    """AAPC for every region x metric in the burden table."""
    out = []
    for region in load_data.regions(df):
        for metric in load_data.metrics(df):
            yrs, val, _, _ = load_data.get_series(df, region, metric)
            r = compute_aapc(yrs, val)
            out.append({
                "region": region,
                "metric": metric,
                "AAPC": round(r["aapc"], 4),
                "AAPC_lo": round(r["lo"], 4),
                "AAPC_hi": round(r["hi"], 4),
                "p_value": round(r["p_value"], 5),
                "significant": bool(r["p_value"] < 0.05),
            })
    return pd.DataFrame(out)
