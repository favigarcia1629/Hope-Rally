import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
from pathlib import Path

EXPORT_DIR = Path(__file__).parent.parent / "exports"
EXPORT_DIR.mkdir(exist_ok=True)

STYLE = {
    "figure.facecolor": "#0F1117",
    "axes.facecolor":   "#0F1117",
    "axes.edgecolor":   "#333333",
    "axes.labelcolor":  "#CCCCCC",
    "xtick.color":      "#CCCCCC",
    "ytick.color":      "#CCCCCC",
    "text.color":       "#FFFFFF",
    "grid.color":       "#222222",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
}

GREEN  = "#2ECC71"
ORANGE = "#F39C12"
RED    = "#E74C3C"
BLUE   = "#2196F3"
PURPLE = "#9C27B0"


def apply_style():
    plt.rcParams.update(STYLE)


def chart1_dashboard(ind: dict, scores: dict, overall: float, save: bool = True) -> plt.Figure:
    apply_style()
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f"Hope Rally or Fundamental Rally?  |  Sustainability Score: {overall:.0f}/100",
                 fontsize=15, fontweight="bold", y=1.01)

    # Panel 1: S&P 500 vs 200MA
    ax = axes[0, 0]
    sp = ind["sp500"].iloc[-252:]
    ma = ind["sp500_200ma"].iloc[-252:].dropna()
    ax.plot(sp.index, sp.values, color=BLUE, linewidth=2, label="S&P 500")
    ax.plot(ma.index, ma.values, color=ORANGE, linewidth=2, linestyle="--", label="200-Day MA")
    ax.set_title(f"S&P 500 vs 200MA  |  {ind['cur_ext']:+.1f}% above", fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.15)
    ax.grid(True)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))

    # Panel 2: VIX
    ax = axes[0, 1]
    vix = ind["vix"].iloc[-252:]
    vix_avg = ind["vix_90avg"].iloc[-252:].dropna()
    ax.plot(vix.index, vix.values, color="#E91E63", linewidth=2, label="VIX")
    ax.plot(vix_avg.index, vix_avg.values, color=PURPLE, linewidth=2, linestyle="--", label="90-Day Avg")
    ax.axhline(25, color=RED, linewidth=1, linestyle=":", alpha=0.7)
    ax.text(vix.index[-1], 25.5, "Danger: 25", fontsize=8, color=RED, alpha=0.8)
    ax.set_title(f"VIX Fear Index  |  Current: {ind['cur_vix']:.1f}", fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.15)
    ax.grid(True)

    # Panel 3: Scorecard bars
    ax = axes[1, 0]
    names  = list(scores.keys())
    vals   = list(scores.values())
    colors = [GREEN if v >= 70 else ORANGE if v >= 40 else RED for v in vals]
    bars = ax.barh(names, vals, color=colors, alpha=0.85, edgecolor="#333", height=0.55)
    ax.axvline(70, color=GREEN, linewidth=1.2, linestyle="--", alpha=0.7)
    ax.axvline(40, color=ORANGE, linewidth=1.2, linestyle="--", alpha=0.7)
    ax.set_xlim(0, 115)
    ax.set_title(f"Sustainability Scorecard  |  Overall: {overall:.0f}/100", fontweight="bold")
    for bar, val in zip(bars, vals):
        ax.text(val + 1.5, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=10, fontweight="bold")
    ax.grid(True, axis="x", alpha=0.4)

    # Panel 4: Oil vs baseline
    ax = axes[1, 1]
    oil = ind["oil"].iloc[-252:]
    ax.plot(oil.index, oil.values, color="#FF5722", linewidth=2, label="WTI Crude")
    ax.axhline(ind["oil_baseline"], color=GREEN, linewidth=1.5, linestyle="--",
               label=f"Baseline ${ind['oil_baseline']:.0f}")
    ax.set_title(f"WTI Oil  |  {ind['cur_oil_prem']:+.1f}% above baseline", fontweight="bold")
    ax.legend(fontsize=9, framealpha=0.15)
    ax.grid(True)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"${x:.0f}"))

    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "01_dashboard.png", dpi=150, bbox_inches="tight")
    return fig


def chart2_scenarios(results: dict, sp500_current: float, expected: float,
                     exp_change: float, save: bool = True) -> plt.Figure:
    apply_style()
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("S&P 500 Scenario Analysis", fontsize=14, fontweight="bold")

    # Bar chart
    ax = axes[0]
    names   = [f"{n.split()[0]}\n{s['change']:+.1f}%" for n, s in results.items()]
    targets = [s["target"] for s in results.values()]
    colors  = [GREEN, ORANGE, RED]
    bars = ax.bar(names, targets, color=colors, alpha=0.85, width=0.5, edgecolor="#333")
    ax.axhline(sp500_current, color="white", linewidth=1.5, linestyle="--",
               label=f"Current: {sp500_current:,.0f}")
    ax.axhline(expected, color="#87CEEB", linewidth=1.5, linestyle=":",
               label=f"Expected: {expected:,.0f} ({exp_change:+.1f}%)")
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.set_ylabel("S&P 500 Price Target")
    ax.legend(fontsize=9, framealpha=0.15)
    ax.grid(True, axis="y", alpha=0.4)
    for bar, val in zip(bars, targets):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 30,
                f"{val:,.0f}", ha="center", fontsize=11, fontweight="bold")

    # Probability pie
    ax = axes[1]
    probs  = [s["probability"] * 100 for s in results.values()]
    labels = [f"{s['emoji']} {n}\n({s['change']:+.1f}%)" for n, s in results.items()]
    wedges, texts, autotexts = ax.pie(
        probs, labels=labels, colors=colors,
        autopct="%1.0f%%", startangle=90,
        textprops={"color": "white", "fontsize": 9},
        wedgeprops={"edgecolor": "#333", "linewidth": 1.2},
    )
    for at in autotexts:
        at.set_fontweight("bold")
    ax.set_title("Probability Distribution", fontweight="bold")

    fig.tight_layout()
    if save:
        fig.savefig(EXPORT_DIR / "02_scenarios.png", dpi=150, bbox_inches="tight")
    return fig


def export_all(ind, scores, overall, results, sp500_current, expected, exp_change):
    print("Generating charts...")
    chart1_dashboard(ind, scores, overall)
    chart2_scenarios(results, sp500_current, expected, exp_change)
    print(f"Charts saved to: {EXPORT_DIR}")
