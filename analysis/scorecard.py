"""
Rally Sustainability Scorecard.
Each indicator scored 0–100:
  100 = fully fundamental (healthy)
    0 = purely hope-driven (dangerous)
"""


def score_indicators(ind: dict) -> dict[str, int]:
    scores = {}

    # 1. Price Momentum — how far above 200MA?
    ext = ind["cur_ext"]
    if ext < 2:
        scores["Price Momentum"] = 100
    elif ext < 5:
        scores["Price Momentum"] = 75
    elif ext < 10:
        scores["Price Momentum"] = 50
    else:
        scores["Price Momentum"] = 25

    # 2. Fear Index — VIX vs 90-day average
    vix_ratio = ind["cur_vix"] / ind["cur_vix_avg"] if ind["cur_vix_avg"] else 1
    if vix_ratio > 1.1:
        scores["Fear Index (VIX)"] = 100    # healthy fear/skepticism
    elif vix_ratio > 0.95:
        scores["Fear Index (VIX)"] = 60
    elif vix_ratio > 0.80:
        scores["Fear Index (VIX)"] = 30
    else:
        scores["Fear Index (VIX)"] = 10     # dangerous complacency

    # 3. Oil Pressure — % above baseline
    oil_prem = ind["cur_oil_prem"]
    if oil_prem < 10:
        scores["Oil Pressure"] = 100
    elif oil_prem < 25:
        scores["Oil Pressure"] = 75
    elif oil_prem < 50:
        scores["Oil Pressure"] = 40
    else:
        scores["Oil Pressure"] = 10

    # 4. Rate Environment — 10Y Treasury yield
    rate = ind["cur_treasury"]
    if rate < 3.0:
        scores["Rate Environment"] = 100
    elif rate < 3.5:
        scores["Rate Environment"] = 80
    elif rate < 4.0:
        scores["Rate Environment"] = 60
    elif rate < 4.5:
        scores["Rate Environment"] = 35
    else:
        scores["Rate Environment"] = 15

    # 5. Geopolitical Stability — oil 30-day coefficient of variation
    cv = ind["oil_cv"]
    if cv < 0.02:
        scores["Geopolitical Stability"] = 100
    elif cv < 0.05:
        scores["Geopolitical Stability"] = 70
    elif cv < 0.08:
        scores["Geopolitical Stability"] = 40
    else:
        scores["Geopolitical Stability"] = 15

    return scores


def overall_score(scores: dict) -> float:
    return sum(scores.values()) / len(scores)


def verdict(score: float) -> tuple[str, str]:
    if score >= 70:
        return "FUNDAMENTAL RALLY", "#2ECC71"
    elif score >= 45:
        return "MIXED SIGNALS", "#F39C12"
    else:
        return "HOPE-DRIVEN RALLY", "#E74C3C"


def signal_label(score: int) -> tuple[str, str]:
    if score >= 70:
        return "Bullish", "#2ECC71"
    elif score >= 40:
        return "Caution", "#F39C12"
    else:
        return "Warning", "#E74C3C"
