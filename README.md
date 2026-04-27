# Hope Rally or Fundamental Rally?

**A live multi-indicator framework scoring S&P 500 rally sustainability in real time**

> The market rallied to all-time highs in April 2026. But was it driven by fundamentals — or hope?

🔗 **[Live Interactive Dashboard](#)** *(link added after Streamlit deployment)*

---

## The Question

When markets surge, the critical question isn't *how much* — it's *why*. This project builds a real-time scoring framework that evaluates whether a rally is supported by economic fundamentals or driven by sentiment and optimism. The framework updates daily with live data.

---

## Methodology: The Sustainability Scorecard

Five indicators, each scored 0–100:

| Indicator | What It Measures | Red Flag |
|---|---|---|
| **Price Momentum** | % above 200-day moving average | >10% overextension |
| **Fear Index (VIX)** | VIX vs 90-day average | VIX falling as risks rise = complacency |
| **Oil Pressure** | WTI vs user-defined baseline | >50% above baseline = stagflation risk |
| **Rate Environment** | 10-Year Treasury yield | >4.5% compresses P/E multiples |
| **Geopolitical Stability** | Oil 30-day coefficient of variation | High volatility = ongoing shock |

**Overall score ≥ 70 → Fundamental Rally | 45–70 → Mixed | < 45 → Hope-Driven**

---

## Live Results (as of last data pull)

| Metric | Reading | Signal |
|---|---|---|
| S&P 500 vs 200MA | +6.9% above | 🟡 Caution |
| VIX / 90-Day Avg | 0.95x | 🔴 Warning |
| Oil Premium | +50.8% above baseline | 🔴 Warning |
| 10Y Treasury | 4.31% | 🔴 Warning |
| Oil 30d Volatility | Moderate | 🟡 Caution |
| **Overall Score** | **33 / 100** | **🔴 Hope-Driven** |

---

## Scenario Model

Three probability-weighted outcomes:

| Scenario | Probability | S&P Target | Change |
|---|---|---|---|
| 🟢 Bull Case (full resolution) | 25% | ~7,738 | +8.0% |
| 🟡 Base Case (partial resolution) | 45% | ~6,790 | -5.2% |
| 🔴 Bear Case (deterioration) | 30% | ~5,758 | -19.6% |
| **Expected Value** | — | **~6,717** | **-6.2%** |

*Scenario probabilities are adjustable via sidebar sliders.*

---

## Dashboard Features

- **Live Dashboard** — S&P 500 vs 200MA, VIX, WTI Oil, 10Y Treasury updated daily
- **Scorecard** — 5-indicator sustainability scoring with current readings
- **Scenarios** — Adjustable probability sliders, price targets, assumption tables
- **Positioning** — 10 asset classes rated across Bull/Base/Bear scenarios
- **What to Watch** — Key trigger levels that signal regime change

---

## Project Structure

```
hope_rally/
├── data/
│   └── fetch.py            # yfinance data + indicator computation
├── analysis/
│   ├── scorecard.py        # 5-indicator scoring system
│   └── scenarios.py        # 3-scenario model + positioning table
├── visualizations/
│   └── charts.py           # Static chart exports (matplotlib)
├── exports/                # LinkedIn-ready PNGs + PDF (gitignored)
├── app.py                  # Streamlit live dashboard
├── main.py                 # Headless run: fetch + analyze + export
└── generate_pdf.py         # PDF report generator
```

---

## Run Locally

```bash
git clone https://github.com/favigarcia1629/Hope-Rally.git
cd Hope-Rally
pip install -r requirements.txt

# Run analysis and export charts
python main.py

# Launch live dashboard
streamlit run app.py

# Generate PDF report
python generate_pdf.py
```

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.14 | Core language |
| yfinance | Live market data (S&P 500, VIX, WTI Oil, 10Y Treasury) |
| pandas / numpy | Indicator computation and time series |
| plotly | Interactive dashboard charts |
| matplotlib | Static export charts |
| Streamlit | Web dashboard + free cloud deployment |
| reportlab | PDF report generation |

---

## Methodology Notes

- **Oil baseline** is user-configurable — set it to the date before the geopolitical event you're studying
- **Scenario probabilities** are adjustable in the sidebar and must sum to 100%
- **Data refreshes daily** — no hardcoded dates anywhere in the codebase
- The framework is designed to be reused for any future rally/correction analysis

---

*Data: Yahoo Finance via yfinance. Not financial advice — built for research and education.*
