"""Tier 2 — interactive web dashboard (Streamlit).

Run from the repository root:
    streamlit run app/streamlit_app.py
"""
from __future__ import annotations
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib.pyplot as plt
import streamlit as st

from src import load_data, trends, decompose, forecast, plots

st.set_page_config(page_title="Male Infertility Burden Explorer", layout="wide")

st.title("Male Infertility Burden Explorer")
st.caption("Interactive computational companion to the GBD 2021 male infertility "
           "disease-burden study (1990–2035).")

df = load_data.load_burden()
dec = load_data.load_decomp()
regions = load_data.regions(df)
metrics = load_data.metrics(df)

with st.sidebar:
    st.header("Controls")
    region = st.selectbox("Region", regions,
                          index=regions.index("China") if "China" in regions else 0)
    metric = st.selectbox("Metric", metrics, index=0)
    st.markdown("---")
    st.markdown("**Data note:** the bundled `sample_burden.csv` is *illustrative*. "
                "Replace it with real GBD 2021 extracts (see `README.md` §4) for "
                "authoritative results.")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{region} — {metric.capitalize()}")
    series = load_data.get_series(df, region, metric)
    fc = forecast.forecast_region_metric(df, region, metric)
    fig = plots.plot_trend_forecast_fig(region, metric, series, fc)
    st.pyplot(fig)

    r = trends.compute_aapc(series[0], series[1])
    st.metric("AAPC (%) 1990–2021", f"{r['aapc']:.3f}")
    st.caption(f"95% CI: [{r['lo']:.3f}, {r['hi']:.3f}] · p = {r['p_value']:.4f} · "
               f"{'significant' if r['p_value'] < 0.05 else 'not significant'}")

with col2:
    st.subheader(f"Decomposition — {region}")
    shares = decompose.decomposition_for_region(dec, region)
    fig2 = plots.plot_decomposition_fig(region, shares)
    st.pyplot(fig2)
    st.caption("Das Gupta multiplicative decomposition of total burden change "
               "(1990→2021). Illustrative drivers in the bundled table.")

st.markdown("---")
st.subheader("Compare all regions")
cmp_metric = st.selectbox("Metric for comparison", metrics, key="cmp")
fig3, ax = plt.subplots(figsize=(9, 4.5), dpi=120)
for rg in regions:
    yrs, val, _, _ = load_data.get_series(df, rg, cmp_metric)
    f = forecast.forecast_region_metric(df, rg, cmp_metric)
    ax.plot(yrs, val, lw=1.2, label=rg)
    fy = f["fc_years"]
    m = fy > yrs.max()
    ax.plot(fy[m], f["fc_point"][m], lw=1.2, ls="--")
ax.set_xlabel("Year")
ax.set_ylabel("ASR (per 100,000)")
ax.set_title(f"{cmp_metric.capitalize()} — all regions (observed + forecast)")
ax.legend(fontsize=7, ncol=2)
ax.grid(alpha=0.25)
fig3.tight_layout()
st.pyplot(fig3)
