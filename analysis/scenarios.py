"""
3-scenario probability-weighted S&P 500 price target model.
Probabilities are user-adjustable; must sum to 100%.
"""

DEFAULT_SCENARIOS = {
    "Bull Case": {
        "emoji":          "🟢",
        "oil":            72,
        "treasury":       3.75,
        "vix":            14,
        "pe_compression": 0.00,
        "earnings_growth": 0.08,
        "probability":    0.25,
        "description":    "Geopolitical resolution, oil normalizes, Fed cuts 2x",
    },
    "Base Case": {
        "emoji":          "🟡",
        "oil":            88,
        "treasury":       4.25,
        "vix":            20,
        "pe_compression": -0.08,
        "earnings_growth": 0.03,
        "probability":    0.45,
        "description":    "Partial resolution, oil stays elevated, Fed holds",
    },
    "Bear Case": {
        "emoji":          "🔴",
        "oil":            115,
        "treasury":       4.75,
        "vix":            35,
        "pe_compression": -0.18,
        "earnings_growth": -0.02,
        "probability":    0.30,
        "description":    "Situation deteriorates, oil spikes, recession fears mount",
    },
}

CURRENT_PE = 24.5   # S&P 500 forward P/E

POSITIONING = [
    ("S&P 500 Index",      "SPY/VOO", "Hold",       "Reduce",      "Underweight", "Overvalued vs probability-weighted expected value"),
    ("Energy Sector",      "XLE",     "Reduce",      "Overweight",  "Overweight",  "High oil benefits energy regardless of scenario"),
    ("Gold",               "GLD",     "Reduce",      "Overweight",  "Overweight",  "Geopolitical + inflation hedge in all downside cases"),
    ("Short Bonds (1-3Y)", "SHY",     "Neutral",     "Overweight",  "Overweight",  "Fed on hold — short duration wins over long"),
    ("Tech / Growth",      "QQQ",     "Overweight",  "Reduce",      "Avoid",       "Rate-cut dependent — no cuts = multiple headwind"),
    ("Airlines",           "JETS",    "Overweight",  "Neutral",     "Avoid",       "Oil normalization = immediate margin expansion"),
    ("Defensives",         "XLU/XLV", "Neutral",     "Overweight",  "Overweight",  "Outperform in corrections and slow growth"),
    ("Emerging Markets",   "EEM",     "Overweight",  "Neutral",     "Avoid",       "Dollar weakens on geopolitical resolution"),
    ("VIX Calls",          "VIXY",    "Avoid",       "Consider",    "Overweight",  "Asymmetric bear hedge — cheap when VIX is low"),
    ("Cash / T-Bills",     "SGOV",    "Reduce",      "Hold",        "Overweight",  "Risk-free rate beats expected S&P return in base/bear"),
]

SIGNAL_COLORS = {
    "Overweight":  "#2ECC71",
    "Hold":        "#F39C12",
    "Neutral":     "#F39C12",
    "Consider":    "#F39C12",
    "Reduce":      "#E67E22",
    "Underweight": "#E74C3C",
    "Avoid":       "#E74C3C",
}

WATCH_LIST = [
    ("WTI Crude < $85",       "Rotate into broad market and tech — bull case playing out"),
    ("Fed rate cut signal",   "Aggressively add QQQ — rate cuts reprice growth multiples fast"),
    ("VIX > 25",              "Reduce equities, add VIXY and cash — repricing has begun"),
    ("Geopolitical reopening","Airlines (JETS) become highest-conviction buy"),
    ("10Y Treasury > 4.75%",  "Increase short-duration bonds, reduce growth exposure"),
]


def run_scenarios(sp500_current: float, probabilities: dict) -> dict:
    current_eps = sp500_current / CURRENT_PE
    results = {}

    for name, s in DEFAULT_SCENARIOS.items():
        prob   = probabilities.get(name, s["probability"])
        new_eps = current_eps * (1 + s["earnings_growth"])
        new_pe  = CURRENT_PE  * (1 + s["pe_compression"])
        target  = new_eps * new_pe
        change  = (target - sp500_current) / sp500_current * 100
        results[name] = {
            **s,
            "probability": prob,
            "new_eps":     new_eps,
            "new_pe":      new_pe,
            "target":      target,
            "change":      change,
        }

    expected = sum(r["target"] * r["probability"] for r in results.values())
    exp_change = (expected - sp500_current) / sp500_current * 100

    return results, expected, exp_change
