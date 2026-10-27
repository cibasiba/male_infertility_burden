"""Forecasting via bootstrap log-linear regression (transparent, open alternative
to the manuscript's BAPC-INLA fit).

For the dashboard/pipeline we use a reproducible bootstrap log-linear model so the
whole workflow stays in Python and is fully open. The manuscript's authoritative
projections remain the Bayesian APC (BAPC) + INLA results computed in R.
"""
from __future__ import annotations
import numpy as np
from scipy import stats
from . import load_data


def bootstrap_loglinear(years, values, horizon: int = 2035, n_boot: int = 1000,
                        seed: int = 2021):
    """Fit ln(value) ~ year, project to `horizon`, return CIs from residual bootstrap.

    Returns dict with historical and forecast arrays.
    """
    rng = np.random.default_rng(seed)
    years = np.asarray(years, dtype=float)
    values = np.asarray(values, dtype=float)
    mask = np.isfinite(values) & (values > 0)
    years, values = years[mask], values[mask]

    log_v = np.log(values)
    fit = stats.linregress(years, log_v)
    a, b = fit.intercept, fit.slope
    resid = log_v - (a + b * years)

    fc_years = np.arange(years.max() + 1, horizon + 1)
    all_years = np.concatenate([years, fc_years])

    # point forecast (median of bootstrap medians ~ OLS point)
    point_log = a + b * all_years
    point = np.exp(point_log)

    # bootstrap
    boot_log = np.empty((n_boot, len(all_years)))
    for i in range(n_boot):
        sample_resid = rng.choice(resid, size=len(resid), replace=True)
        # refit on resampled residuals (non-parametric)
        new_log = (a + b * years) + sample_resid
        bf = stats.linregress(years, new_log)
        boot_log[i] = bf.intercept + bf.slope * all_years
    lower = np.exp(np.percentile(boot_log, 2.5, axis=0))
    upper = np.exp(np.percentile(boot_log, 97.5, axis=0))

    split = len(years)
    return {
        "hist_years": years,
        "hist_value": values,
        "fc_years": all_years,
        "fc_point": point,
        "fc_lower": lower,
        "fc_upper": upper,
        "hist_fit": point[:split],
        "forecast_start_year": int(years.max()) + 1,
    }


def forecast_region_metric(df: pd.DataFrame, region: str, metric: str, **kw):
    yrs, val, lo, hi = load_data.get_series(df, region, metric)
    return bootstrap_loglinear(yrs, val, **kw)
