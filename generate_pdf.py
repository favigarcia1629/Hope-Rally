"""
Generates a professional PDF report for the Hope Rally analysis.
Usage: python generate_pdf.py
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak, Image
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import date

from data.fetch import fetch_data, compute_indicators
from analysis.scorecard import score_indicators, overall_score, verdict, signal_label
from analysis.scenarios import run_scenarios, DEFAULT_SCENARIOS, POSITIONING, SIGNAL_COLORS, WATCH_LIST

OUTPUT = Path(__file__).parent / "exports" / "Hope_Rally_Report.pdf"
OIL_BASELINE = "2026-01-31"

RED    = colors.HexColor("#E74C3C")
ORANGE = colors.HexColor("#F39C12")
GREEN  = colors.HexColor("#2ECC71")
BLUE   = colors.HexColor("#2196F3")
DARK   = colors.HexColor("#1A1A2E")
ACCENT = colors.HexColor("#0D47A1")
LIGHT  = colors.HexColor("#F5F5F5")
GRAY   = colors.HexColor("#888888")


def build_styles():
    S = {}
    S["cover_title"] = ParagraphStyle("cover_title", fontSize=24, fontName="Helvetica-Bold",
        textColor=DARK, alignment=TA_CENTER, spaceAfter=8, leading=30)
    S["cover_sub"] = ParagraphStyle("cover_sub", fontSize=12, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=4)
    S["cover_date"] = ParagraphStyle("cover_date", fontSize=10, fontName="Helvetica",
        textColor=GRAY, alignment=TA_CENTER)
    S["section_header"] = ParagraphStyle("section_header", fontSize=16, fontName="Helvetica-Bold",
        textColor=ACCENT, spaceBefore=18, spaceAfter=6, leading=20)
    S["sub_header"] = ParagraphStyle("sub_header", fontSize=12, fontName="Helvetica-Bold",
        textColor=DARK, spaceBefore=12, spaceAfter=4)
    S["body"] = ParagraphStyle("body", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=16, alignment=TA_JUSTIFY, spaceAfter=6)
    S["bullet"] = ParagraphStyle("bullet", fontSize=10, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), leading=15, leftIndent=16, spaceAfter=3)
    S["linkedin"] = ParagraphStyle("linkedin", fontSize=10.5, fontName="Helvetica",
        textColor=colors.HexColor("#1a1a1a"), leading=17, alignment=TA_LEFT,
        spaceAfter=6, leftIndent=12, rightIndent=12)
    S["caption"] = ParagraphStyle("caption", fontSize=8.5, fontName="Helvetica-Oblique",
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=8)
    S["disclaimer"] = ParagraphStyle("disclaimer", fontSize=8, fontName="Helvetica-Oblique",
        textColor=GRAY, alignment=TA_CENTER, spaceAfter=4)
    return S


def build_pdf():
    print("Loading live data...")
    data = fetch_data()
    ind  = compute_indicators(data, OIL_BASELINE)
    scores  = score_indicators(ind)
    overall = overall_score(scores)
    label, vcolor_hex = verdict(overall)
    probs = {k: v["probability"] for k, v in DEFAULT_SCENARIOS.items()}
    results, expected, exp_change = run_scenarios(ind["cur_sp500"], probs)

    verdict_color = RED if overall < 45 else (ORANGE if overall < 70 else GREEN)

    doc = SimpleDocTemplate(str(OUTPUT), pagesize=letter,
        rightMargin=0.75*inch, leftMargin=0.75*inch,
        topMargin=0.75*inch, bottomMargin=0.75*inch)
    S = build_styles()
    story = []

    # ── COVER ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.4*inch))
    story.append(Paragraph("Hope Rally or Fundamental Rally?", S["cover_title"]))
    story.append(Paragraph("A Live Multi-Indicator Framework for S&P 500 Rally Sustainability", S["cover_sub"]))
    story.append(Spacer(1, 0.1*inch))
    story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(f"Generated {date.today().strftime('%B %d, %Y')}  |  S&P 500: {ind['cur_sp500']:,.0f}  |  Data: Yahoo Finance", S["cover_date"]))
    story.append(Spacer(1, 0.35*inch))

    verdict_data = [[Paragraph(
        f"<b>VERDICT: {label}</b><br/>Sustainability Score: {overall:.0f} / 100",
        ParagraphStyle("v", fontSize=14, fontName="Helvetica-Bold",
                       textColor=colors.white, alignment=TA_CENTER)
    )]]
    verdict_box = Table(verdict_data, colWidths=[6.5*inch])
    verdict_box.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), verdict_color),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
    ]))
    story.append(verdict_box)
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph(
        f"Probability-weighted S&P 500 fair value: {expected:,.0f} ({exp_change:+.1f}% from current {ind['cur_sp500']:,.0f})",
        S["cover_sub"]
    ))

    story.append(PageBreak())

    # ── SECTION 1: LinkedIn Post ─────────────────────────────────────────────
    story.append(Paragraph("Section 1 — LinkedIn Post Draft", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.1*inch))

    linkedin_lines = [
        f"The S&P 500 just hit {ind['cur_sp500']:,.0f}. Everyone is calling it a bull market.",
        "",
        "I built a 5-indicator framework to test whether this rally is fundamentally supported",
        "or driven purely by hope and sentiment.",
        "",
        "Here's what the data says:",
        "",
        f"  Price Momentum:       {scores['Price Momentum']}/100  ({ind['cur_ext']:+.1f}% above 200-day MA)",
        f"  Fear Index (VIX):     {scores['Fear Index (VIX)']}/100  (VIX falling as risks stay elevated)",
        f"  Oil Pressure:         {scores['Oil Pressure']}/100  (WTI {ind['cur_oil_prem']:+.1f}% above baseline)",
        f"  Rate Environment:     {scores['Rate Environment']}/100  (10Y Treasury at {ind['cur_treasury']:.2f}%)",
        f"  Geopolitical Stability: {scores['Geopolitical Stability']}/100  (oil volatility remains elevated)",
        "",
        f"  OVERALL SCORE: {overall:.0f}/100 — {label}",
        "",
        "4 of 5 indicators are flashing red or caution.",
        "The VIX is falling while risks stay elevated — that's dangerous complacency.",
        f"Oil is {ind['cur_oil_prem']:+.1f}% above its pre-shock baseline. Markets are ignoring it.",
        "",
        "I built a 3-scenario probability model to quantify the downside:",
        f"  Bull Case (25%): S&P -> {list(results.values())[0]['target']:,.0f} ({list(results.values())[0]['change']:+.1f}%)",
        f"  Base Case (45%): S&P -> {list(results.values())[1]['target']:,.0f} ({list(results.values())[1]['change']:+.1f}%)",
        f"  Bear Case (30%): S&P -> {list(results.values())[2]['target']:,.0f} ({list(results.values())[2]['change']:+.1f}%)",
        f"  Expected Value:  S&P -> {expected:,.0f} ({exp_change:+.1f}%)",
        "",
        "Optimism without fundamentals is a one-headline risk.",
        "The framework tells you what to watch — not what to fear.",
        "",
        "Full live dashboard in the comments. Scenario probabilities are adjustable.",
        "",
        "#Investing #MacroEconomics #StockMarket #DataScience #Python #Finance",
    ]

    for line in linkedin_lines:
        if line == "":
            story.append(Spacer(1, 0.07*inch))
        else:
            story.append(Paragraph(line, S["linkedin"]))

    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        "Tip: Post chart 01_dashboard.png as the primary image — it has all 4 panels in one frame. "
        "Add 02_scenarios.png as the second slide.",
        S["caption"]
    ))

    story.append(PageBreak())

    # ── SECTION 2: Thought Process ───────────────────────────────────────────
    story.append(Paragraph("Section 2 — Project Thought Process", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    story.append(Paragraph("The Research Question", S["sub_header"]))
    story.append(Paragraph(
        "Markets frequently rally on hope — anticipation of resolution, rate cuts, earnings beats, "
        "or geopolitical de-escalation. The challenge for investors is distinguishing a rally with "
        "fundamental backing (earnings growth, low rates, stable geopolitics) from one built on "
        "optimism that hasn't yet materialized in the data. This project builds a repeatable, "
        "data-driven framework to make that distinction quantitatively.",
        S["body"]
    ))

    story.append(Paragraph("Why These 5 Indicators?", S["sub_header"]))
    indicator_explanations = [
        ("<b>Price Momentum (200MA overextension):</b> The 200-day moving average is the most widely "
         "watched trend indicator. How far above it the S&P trades tells you how much optimism is "
         "already priced in. >10% overextension historically precedes mean reversion."),
        ("<b>Fear Index (VIX vs 90-day avg):</b> The VIX measures implied volatility — the market's "
         "collective fear. When VIX falls while macro risks remain elevated, it signals dangerous "
         "complacency. Investors are pricing out tail risks that haven't actually resolved."),
        ("<b>Oil Pressure:</b> Oil is the economy's tax. A sustained oil premium above the pre-shock "
         "baseline feeds into inflation, compresses margins, and delays Fed rate cuts. Markets often "
         "ignore oil until it becomes impossible to ignore."),
        ("<b>Rate Environment (10Y Treasury):</b> The 10-year yield is the discount rate for all "
         "future earnings. Above 4%, equity valuations face structural headwinds — especially for "
         "growth stocks trading at 20x+ earnings."),
        ("<b>Geopolitical Stability (Oil CV):</b> The 30-day coefficient of variation of oil prices "
         "captures ongoing volatility independent of the absolute price level. High CV means the "
         "situation is still actively evolving — not resolved."),
    ]
    for exp in indicator_explanations:
        story.append(Paragraph(f"• {exp}", S["bullet"]))
        story.append(Spacer(1, 0.04*inch))

    story.append(Paragraph("The Scenario Model", S["sub_header"]))
    story.append(Paragraph(
        "The 3-scenario model translates geopolitical and macro outcomes into S&P 500 price targets "
        "using two levers: earnings growth (EPS) and P/E multiple compression. "
        "In a bull case, resolution drives earnings beats and multiple expansion. "
        "In a bear case, deterioration triggers margin compression and risk-off de-rating. "
        "Probability weighting produces an expected value that can be compared to the current market price.",
        S["body"]
    ))

    story.append(PageBreak())

    # ── SECTION 3: Charts ────────────────────────────────────────────────────
    story.append(Paragraph("Section 3 — Charts & What They Tell You", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    charts = [
        (
            "Chart 1 — Live Dashboard (4-Panel)",
            "01_dashboard.png",
            "The headline chart. Top-left: S&P 500 vs its 200-day moving average — the primary "
            "trend indicator. Top-right: VIX vs its 90-day average — falling VIX with elevated "
            "risks = complacency. Bottom-left: the sustainability scorecard in bar form — each "
            "indicator color-coded green/yellow/red. Bottom-right: WTI Oil vs its pre-shock "
            "baseline — the most underappreciated risk in the current rally."
        ),
        (
            "Chart 2 — Scenario Analysis",
            "02_scenarios.png",
            "Left: S&P 500 price targets for each scenario, with the current price and "
            "probability-weighted expected value marked as horizontal lines. "
            "The gap between current price and expected value is the risk premium markets "
            "aren't pricing in. Right: the probability distribution — the pie chart makes it "
            "immediately clear that the market is implicitly assigning near-zero probability "
            "to the bear case, which our model sets at 30%."
        ),
    ]

    for title, filename, explanation in charts:
        story.append(Paragraph(title, S["sub_header"]))
        img_path = Path(__file__).parent / "exports" / filename
        if img_path.exists():
            story.append(Image(str(img_path), width=6.5*inch, height=3.3*inch))
        story.append(Paragraph(explanation, S["body"]))
        story.append(Spacer(1, 0.1*inch))

    story.append(PageBreak())

    # ── SECTION 4: Scorecard Table ───────────────────────────────────────────
    story.append(Paragraph("Section 4 — Scorecard & Scenario Detail", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))

    story.append(Paragraph("Current Scorecard", S["sub_header"]))
    sc_data = [["Indicator", "Score", "Signal", "Current Reading"]]
    readings = {
        "Price Momentum":        f"{ind['cur_ext']:+.1f}% above 200MA",
        "Fear Index (VIX)":      f"VIX {ind['cur_vix']:.1f} / 90d avg {ind['cur_vix_avg']:.1f}",
        "Oil Pressure":          f"${ind['cur_oil']:.0f} ({ind['cur_oil_prem']:+.1f}% above baseline)",
        "Rate Environment":      f"{ind['cur_treasury']:.2f}% 10Y yield",
        "Geopolitical Stability":f"30d oil CV: {ind['oil_cv']:.3f}",
    }
    for name, score in scores.items():
        sig, _ = signal_label(score)
        sc_data.append([name, str(score), sig, readings.get(name, "")])

    sc_table = Table(sc_data, colWidths=[1.7*inch, 0.65*inch, 0.9*inch, 3.25*inch])
    sc_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("ALIGN",         (0,1),(0,-1),  "LEFT"),
        ("ALIGN",         (3,1),(3,-1),  "LEFT"),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT, colors.white]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))
    story.append(sc_table)
    story.append(Spacer(1, 0.15*inch))

    story.append(Paragraph("Scenario Assumptions & Targets", S["sub_header"]))
    sc2_data = [["Scenario", "Prob", "Oil", "10Y", "EPS Growth", "PE Comp", "Target", "Change"]]
    for name, s in results.items():
        sc2_data.append([
            name, f"{s['probability']*100:.0f}%",
            f"${s['oil']}", f"{s['treasury']}%",
            f"{s['earnings_growth']:+.0%}", f"{s['pe_compression']:+.0%}",
            f"{s['target']:,.0f}", f"{s['change']:+.1f}%",
        ])
    sc2_data.append(["Expected Value", "", "", "", "", "", f"{expected:,.0f}", f"{exp_change:+.1f}%"])

    sc2_table = Table(sc2_data, colWidths=[1.2*inch, 0.45*inch, 0.6*inch, 0.5*inch,
                                            0.8*inch, 0.75*inch, 0.9*inch, 0.8*inch])
    sc2_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-2), [LIGHT, colors.white]),
        ("BACKGROUND",    (0,-1),(-1,-1),colors.HexColor("#E8F0FE")),
        ("FONTNAME",      (0,-1),(-1,-1),"Helvetica-Bold"),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
    ]))
    story.append(sc2_table)

    # ── SECTION 5: Positioning ───────────────────────────────────────────────
    story.append(Spacer(1, 0.15*inch))
    story.append(Paragraph("Section 5 — Investment Positioning", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    pos_data = [["Asset", "Ticker", "Bull", "Base", "Bear", "Rationale"]]
    for asset, ticker, bull, base, bear, rationale in POSITIONING:
        pos_data.append([asset, ticker, bull, base, bear, rationale])

    pos_table = Table(pos_data, colWidths=[1.3*inch, 0.7*inch, 0.75*inch, 0.75*inch, 0.75*inch, 2.25*inch])

    def signal_bg(val):
        if val in ("Overweight",):  return colors.HexColor("#E8F5E9")
        if val in ("Hold", "Neutral", "Consider"): return colors.HexColor("#FFF8E1")
        if val in ("Reduce", "Underweight", "Avoid"): return colors.HexColor("#FFEBEE")
        return colors.white

    pos_style = [
        ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 8),
        ("ALIGN",         (0,0),(-1,-1), "CENTER"),
        ("ALIGN",         (5,1),(5,-1),  "LEFT"),
        ("ALIGN",         (0,1),(0,-1),  "LEFT"),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT, colors.white]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0),(-1,-1), 4),
        ("BOTTOMPADDING", (0,0),(-1,-1), 4),
        ("LEFTPADDING",   (0,0),(-1,-1), 4),
    ]
    for i, (_, _, bull, base, bear, _) in enumerate(POSITIONING, start=1):
        for j, val in enumerate([bull, base, bear], start=2):
            pos_style.append(("BACKGROUND", (j, i), (j, i), signal_bg(val)))

    pos_table.setStyle(TableStyle(pos_style))
    story.append(pos_table)

    # ── SECTION 6: What to Watch ─────────────────────────────────────────────
    story.append(Spacer(1, 0.2*inch))
    story.append(Paragraph("Section 6 — Key Triggers to Monitor", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    for trigger, action in WATCH_LIST:
        row = Table([[
            Paragraph(f"<b>{trigger}</b><br/>{action}", S["body"])
        ]], colWidths=[6.5*inch])
        row.setStyle(TableStyle([
            ("LEFTPADDING",   (0,0),(-1,-1), 10),
            ("TOPPADDING",    (0,0),(-1,-1), 6),
            ("BOTTOMPADDING", (0,0),(-1,-1), 6),
            ("LINEBEFORE",    (0,0),(0,-1),  3, ORANGE),
            ("BACKGROUND",    (0,0),(-1,-1), colors.HexColor("#FAFAFA")),
        ]))
        story.append(row)
        story.append(Spacer(1, 0.05*inch))

    # ── SECTION 7: Methods & Tools ───────────────────────────────────────────
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph("Section 7 — Methods & Tools", S["section_header"]))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.08*inch))

    tech_data = [
        ["Tool", "Purpose"],
        ["Python 3.14",      "Core language"],
        ["yfinance",         "Live market data: S&P 500, VIX, WTI Oil, 10Y Treasury"],
        ["pandas / numpy",   "Indicator computation, rolling windows, time series"],
        ["plotly",           "Interactive charts in the Streamlit dashboard"],
        ["matplotlib",       "Static chart exports for LinkedIn posts"],
        ["Streamlit",        "Live web dashboard with adjustable sliders and filters"],
        ["reportlab",        "This PDF report"],
    ]
    tt = Table(tech_data, colWidths=[1.6*inch, 4.9*inch])
    tt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,0),  ACCENT),
        ("TEXTCOLOR",     (0,0),(-1,0),  colors.white),
        ("FONTNAME",      (0,0),(-1,0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0,0),(-1,-1), 9),
        ("ALIGN",         (0,0),(-1,-1), "LEFT"),
        ("FONTNAME",      (0,1),(-1,-1), "Helvetica"),
        ("ROWBACKGROUNDS",(0,1),(-1,-1), [LIGHT, colors.white]),
        ("GRID",          (0,0),(-1,-1), 0.4, colors.HexColor("#CCCCCC")),
        ("TOPPADDING",    (0,0),(-1,-1), 5),
        ("BOTTOMPADDING", (0,0),(-1,-1), 5),
        ("LEFTPADDING",   (0,0),(-1,-1), 6),
    ]))
    story.append(tt)

    # ── FOOTER ───────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3*inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#DDDDDD")))
    story.append(Spacer(1, 0.1*inch))
    story.append(Paragraph(
        f"Generated {date.today().strftime('%B %d, %Y')} · Data: Yahoo Finance via yfinance · "
        "Not financial advice — for educational and research purposes only.",
        S["disclaimer"]
    ))

    doc.build(story)
    print(f"PDF saved to: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
