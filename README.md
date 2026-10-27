# Male Infertility Burden — Computational Analysis & Interactive Explorer

> Open, reproducible computational companion to the manuscript
> *"The Disease Burden and Temporal Trends of Male Infertility in China, Globally,
> and Across Regions Stratified by SDI, 1990–2021."*

This repository provides the **computer-science artifact** that backs the
manuscript: a reproducible analysis pipeline (Tier 1) **and** an interactive
web dashboard (Tier 2). Both are released as open source so the analysis can be
verified, re-run, and extended by others.

---

## 1. What this repository contributes

| Tier | Component | Location | What it demonstrates |
|------|-----------|----------|----------------------|
| 1 | Reproducible pipeline | `pipeline/run_pipeline.py` + `src/` | End-to-end, scripted, re-runnable analysis (no manual Excel/Origin steps) |
| 2 | Interactive web system | `app/streamlit_app.py` | A runnable software tool with a UI for exploring the burden data |

The manuscript reports the *epidemiological findings*; this repo reports the
*computational implementation* of those findings — exactly the "actual computer
technology content" expected by computing-venue reviewers.

---

## 2. Project structure

```
male_infertility_burden/
├── README.md                 # this file
├── requirements.txt          # Python dependencies
├── Dockerfile                # one-command reproducible runtime
├── data/
│   ├── make_sample_data.py   # generates the illustrative sample dataset
│   ├── sample_burden.csv      # sample time series (REPLACE with real GBD extracts)
│   └── decomp_drivers.csv     # sample decomposition drivers (illustrative)
├── src/                      # reusable computational modules
│   ├── load_data.py          # I/O + data validation
│   ├── trends.py             # AAPC (Joinpoint-style log-linear regression)
│   ├── decompose.py          # Das Gupta decomposition
│   ├── forecast.py           # bootstrap log-linear forecast to 2035 (95% CI)
│   └── plots.py              # publication-quality figures
├── pipeline/
│   └── run_pipeline.py       # orchestrates the full analysis -> results/
├── app/
│   └── streamlit_app.py      # interactive dashboard
└── results/                 # generated figures (git-ignored)
```

---

## 3. Quick start

### 3.1 Local (Python)

```bash
python -m pip install -r requirements.txt

# Tier 1 — run the reproducible pipeline (writes figures to results/)
python pipeline/run_pipeline.py

# Tier 2 — launch the interactive dashboard
streamlit run app/streamlit_app.py
# then open http://localhost:8501
```

### 3.2 Container (recommended for full reproducibility)

```bash
docker build -t mi-burden .
docker run -p 8501:8501 mi-burden
```

### 3.3 Public code URL

Push this repository to GitHub (or mirror to **Zenodo** for a citable DOI) and
cite the URL in the manuscript, e.g.:

> *"The analysis code and interactive explorer are openly available at
> https://github.com/<you>/male_infertility_burden."*

A live demo can be deployed for free on **Streamlit Community Cloud** or
**Hugging Face Spaces**; cite that URL as the interactive supplement.

---

## 4. Replacing the sample data with real GBD 2021 extracts

The bundled `data/sample_burden.csv` is **illustrative only** — it is generated
to match the endpoints reported in the manuscript so the software runs out of the
box. To produce the authoritative results:

1. Export from the **GBD 2021** database (`healthdata.org/gbd-2021`):
   - Measure: Prevalence & DALYs for "Male infertility"
   - Location: China, Global, and the 5 SDI regions
   - Age: 15–49, split into the seven 5-year age groups
   - Year: 1990–2021
2. Save the age-standardized rates (per 100,000) as
   `data/sample_burden.csv` with columns
   `region, year, metric, value, lower, upper`
   (`metric` ∈ {prevalence, dalys}).
3. For the decomposition, supply age-specific population & rate tables and feed
   them to `src/decompose.py` (see that module's docstring). Replace
   `data/decomp_drivers.csv` accordingly.
4. Re-run `python pipeline/run_pipeline.py`.

> **Data-use note.** GBD results are published under the Institute for Health
> Metrics and Evaluation (IHME) data-use agreement. Do **not** commit raw GBD
> downloads to a public repo without confirming they are redisseminable; the
> age-standardized summary tables used here are generally citeable, but verify
> the current IHME terms before publishing the data file.

---

## 5. Methods implemented (and how they map to the paper)

| Paper method | Repo implementation | Note |
|--------------|---------------------|------|
| AAPC via Joinpoint | `src/trends.py` (log-linear regression, 95% CI) | Single-segment AAPC; replicate Joinpoint for multi-segment |
| Decomposition (aging / population / epidemiological) | `src/decompose.py` (Das Gupta) | Function is exact; sample drivers are illustrative |
| BAPC + INLA forecasting | `src/forecast.py` (bootstrap log-linear, 95% CI to 2035) | Open, transparent alternative; manuscript's authoritative fit uses R/INLA |

The Python forecast is provided so the **dashboard and pipeline are fully open
and reproducible**; the manuscript's primary forecasts remain the BAPC–INLA
results computed in R, as reported.

---

## 6. License

Code: MIT. Data: see §4 data-use note.
