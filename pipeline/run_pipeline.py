"""Tier 1 — reproducible analysis pipeline.

Run from the repository root:
    python pipeline/run_pipeline.py

Produces all figures & tables into results/.
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src import load_data, trends, decompose, forecast, plots  # noqa: E402

RESULTS = ROOT / "results"
RESULTS.mkdir(exist_ok=True)


def main():
    df = load_data.load_burden()
    dec = load_data.load_decomp()

    # --- 1. AAPC table (Joinpoint-style) ---
    aapc = trends.aapc_table(df)
    aapc.to_csv(RESULTS / "aapc_table.csv", index=False)
    print(f"[1/3] AAPC table -> results/aapc_table.csv ({len(aapc)} rows)")

    # --- 2. Decomposition table & figures ---
    decomp_tbl = decompose.decomposition_all(dec)
    decomp_tbl.to_csv(RESULTS / "decomposition_table.csv", index=False)
    print(f"[2/3] Decomposition table -> results/decomposition_table.csv")

    # --- 3. Forecasts + figures for every region/metric ---
    n = 0
    for region in load_data.regions(df):
        # decomposition figure
        shares = decompose.decomposition_for_region(dec, region)
        safe = region.replace(" ", "_")
        plots.plot_decomposition(region, shares,
                                 str(RESULTS / f"fig_decomp_{safe}.png"))
        for metric in load_data.metrics(df):
            series = load_data.get_series(df, region, metric)
            fc = forecast.forecast_region_metric(df, region, metric)
            plots.plot_trend_forecast(region, metric, series, fc,
                                      str(RESULTS / f"fig_trend_{safe}_{metric}.png"))
            n += 1
    print(f"[3/3] {n} trend+forecast figures + {len(load_data.regions(df))} "
          f"decomposition figures -> results/")
    print("Pipeline finished successfully.")


if __name__ == "__main__":
    main()
