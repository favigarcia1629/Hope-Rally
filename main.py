import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from data.fetch import fetch_data, compute_indicators
from analysis.scorecard import score_indicators, overall_score, verdict
from analysis.scenarios import run_scenarios, DEFAULT_SCENARIOS, WATCH_LIST
from visualizations.charts import export_all

OIL_BASELINE = "2026-01-31"

if __name__ == "__main__":
    print("Fetching live market data...")
    data = fetch_data()
    ind  = compute_indicators(data, OIL_BASELINE)

    print(f"\n=== CURRENT READINGS ===")
    print(f"S&P 500:       {ind['cur_sp500']:,.2f}  ({ind['cur_ext']:+.1f}% above 200MA)")
    print(f"VIX:           {ind['cur_vix']:.1f}  (90d avg: {ind['cur_vix_avg']:.1f})")
    print(f"WTI Oil:       ${ind['cur_oil']:.2f}  ({ind['cur_oil_prem']:+.1f}% above baseline)")
    print(f"10Y Treasury:  {ind['cur_treasury']:.2f}%")

    scores  = score_indicators(ind)
    overall = overall_score(scores)
    label, _ = verdict(overall)

    print(f"\n=== SCORECARD ===")
    for name, score in scores.items():
        signal = "BULLISH" if score >= 70 else "CAUTION" if score >= 40 else "WARNING"
        print(f"  {name:<28} {score:>4}  {signal}")
    print(f"  {'OVERALL':<28} {overall:>4.0f}  {label}")

    probs = {k: v["probability"] for k, v in DEFAULT_SCENARIOS.items()}
    results, expected, exp_change = run_scenarios(ind["cur_sp500"], probs)

    print(f"\n=== SCENARIOS ===")
    for name, s in results.items():
        print(f"  {s['emoji']} {name}: {s['target']:,.0f} ({s['change']:+.1f}%)  p={s['probability']:.0%}")
    print(f"  Expected S&P: {expected:,.0f} ({exp_change:+.1f}%)")

    export_all(ind, scores, overall, results, ind["cur_sp500"], expected, exp_change)
    print("\nDone. Run: streamlit run app.py")
