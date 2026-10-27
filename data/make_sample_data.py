"""
Generate the ILLUSTRATIVE sample dataset so the pipeline & dashboard run
out-of-the-box. These numbers are synthesised to match the endpoints reported in
the manuscript; they are NOT real GBD extracts. Replace the generated CSVs with
real GBD 2021 exports before producing authoritative results (see README §4).
"""
import numpy as np
import pandas as pd
from pathlib import Path

SEED = 20211027
rng = np.random.default_rng(SEED)
HERE = Path(__file__).resolve().parent

YEARS = list(range(1990, 2022))  # 1990..2021

# (region, metric) -> (value_1990, value_2021)
ENDPOINTS = {
    ("China", "prevalence"): (1516.72, 1590.82),
    ("Global", "prevalence"): (1158.65, 1352.93),
    ("High SDI", "prevalence"): (1176.87, 1289.89),
    ("High middle SDI", "prevalence"): (1196.43, 1379.74),
    ("Middle SDI", "prevalence"): (1116.53, 1378.17),
    ("Low middle SDI", "prevalence"): (1070.09, 1466.82),
    ("Low SDI", "prevalence"): (1136.75, 1277.19),
    ("China", "dalys"): (8.09, 8.62),
    ("Global", "dalys"): (6.68, 7.78),
    ("High SDI", "dalys"): (6.74, 7.41),
    ("High middle SDI", "dalys"): (6.68, 7.87),
    ("Middle SDI", "dalys"): (6.40, 7.99),
    ("Low middle SDI", "dalys"): (6.25, 8.52),
    ("Low SDI", "dalys"): (6.53, 7.34),
}

# Prevalence UI are ~ +/-40%; DALY UI are wide (~0.38x .. 2.8x).
UI_FACTORS = {
    "prevalence": (0.55, 1.75),
    "dalys": (0.38, 2.80),
}


def make_series(v0, v1, metric):
    """Smooth concave/convex curve in log space + small reproducible wiggle."""
    t = np.linspace(0, 1, len(YEARS))
    # blend linear and quadratic for a gentle bend
    shape = 0.7 * t + 0.3 * t**1.4
    log_v = np.log(v0) + (np.log(v1) - np.log(v0)) * shape
    wiggle = rng.normal(0, 0.012, len(YEARS))
    # random-walk-ish wiggle that returns near 0 at the end
    wiggle = np.cumsum(wiggle)
    wiggle -= np.linspace(wiggle[0], wiggle[-1], len(YEARS))
    vals = np.exp(log_v + wiggle)
    return vals


rows = []
for (region, metric), (v0, v1) in ENDPOINTS.items():
    vals = make_series(v0, v1, metric)
    lo_f, hi_f = UI_FACTORS[metric]
    for y, v in zip(YEARS, vals):
        lo = v * lo_f * rng.uniform(0.92, 1.0)
        hi = v * hi_f * rng.uniform(1.0, 1.08)
        rows.append({
            "region": region,
            "year": y,
            "metric": metric,
            "value": round(float(v), 3),
            "lower": round(float(lo), 3),
            "upper": round(float(hi), 3),
        })

burden = pd.DataFrame(rows)
burden.to_csv(HERE / "sample_burden.csv", index=False)
print(f"sample_burden.csv: {len(burden)} rows "
      f"({burden.region.nunique()} regions x {burden.metric.nunique()} metrics)")

# ---- Decomposition drivers (ILLUSTRATIVE) -------------------------------
# Three multiplicative drivers of total burden: population, age_structure,
# epidemiological_rate. Values are placeholders; replace with real GBD
# demographic extracts. Chosen so China shows epi-dominant decomposition
# (mirroring the manuscript's qualitative finding).
decomp_rows = []
DECOMP_SPEC = {
    # region: (pop0, pop1, age0, age1, epi0, epi1)
    "China":          (1.00, 0.98, 1.00, 1.03, 1.00, 1.11),
    "Global":         (1.00, 1.35, 1.00, 1.02, 1.00, 1.07),
    "High SDI":       (1.00, 1.05, 1.00, 1.04, 1.00, 1.06),
    "High middle SDI":(1.00, 1.20, 1.00, 1.03, 1.00, 1.08),
    "Middle SDI":     (1.00, 1.25, 1.00, 1.02, 1.00, 1.09),
    "Low middle SDI": (1.00, 1.30, 1.00, 1.02, 1.00, 1.10),
    "Low SDI":        (1.00, 1.40, 1.00, 1.01, 1.00, 1.05),
}
for region, (p0, p1, a0, a1, e0, e1) in DECOMP_SPEC.items():
    decomp_rows.append({"region": region, "driver": "population", "v1990": p0, "v2021": p1})
    decomp_rows.append({"region": region, "driver": "age_structure", "v1990": a0, "v2021": a1})
    decomp_rows.append({"region": region, "driver": "epidemiological_rate", "v1990": e0, "v2021": e1})

decomp = pd.DataFrame(decomp_rows)
decomp.to_csv(HERE / "decomp_drivers.csv", index=False)
print(f"decomp_drivers.csv: {len(decomp)} rows (illustrative)")
