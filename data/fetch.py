"""
Fetches live market data via yfinance.
Always pulls a rolling 1-year window ending today.
"""
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)

TICKERS = {
    "sp500":    "^GSPC",
    "vix":      "^VIX",
    "oil":      "CL=F",
    "treasury": "^TNX",
}

LOOKBACK_DAYS = 400   # ~1yr + buffer for 200MA


def fetch_data(force_refresh: bool = False) -> dict[str, pd.Series]:
    cache_path = CACHE_DIR / f"market_{date.today()}.parquet"

    if cache_path.exists() and not force_refresh:
        df = pd.read_parquet(cache_path)
        return {col: df[col].dropna() for col in df.columns}

    end   = date.today().isoformat()
    start = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()

    data = {}
    for key, ticker in TICKERS.items():
        raw = yf.download(ticker, start=start, end=end,
                          auto_adjust=True, progress=False)
        data[key] = raw["Close"].squeeze().dropna()

    df = pd.DataFrame(data)
    df.to_parquet(cache_path)

    # Clean old cache files
    for old in CACHE_DIR.glob("market_*.parquet"):
        if old.name != cache_path.name:
            old.unlink()

    return {col: df[col].dropna() for col in df.columns}


def compute_indicators(data: dict, oil_baseline_date: str) -> dict:
    sp500    = data["sp500"]
    vix      = data["vix"]
    oil      = data["oil"]
    treasury = data["treasury"]

    sp500_200ma  = sp500.rolling(200).mean()
    overextension = ((sp500 - sp500_200ma) / sp500_200ma * 100)
    vix_90avg    = vix.rolling(90).mean()

    try:
        oil_baseline = oil[:oil_baseline_date].mean()
    except Exception:
        oil_baseline = oil.iloc[:60].mean()

    oil_premium = ((oil - oil_baseline) / oil_baseline * 100)

    oil_30d_std  = float(oil.iloc[-30:].std())
    oil_30d_mean = float(oil.iloc[-30:].mean())
    oil_cv       = oil_30d_std / oil_30d_mean if oil_30d_mean else 0

    return {
        "sp500":          sp500,
        "sp500_200ma":    sp500_200ma,
        "overextension":  overextension,
        "vix":            vix,
        "vix_90avg":      vix_90avg,
        "oil":            oil,
        "oil_baseline":   oil_baseline,
        "oil_premium":    oil_premium,
        "oil_cv":         oil_cv,
        "treasury":       treasury,
        # Current readings
        "cur_sp500":      float(sp500.iloc[-1]),
        "cur_200ma":      float(sp500_200ma.iloc[-1]),
        "cur_ext":        float(overextension.iloc[-1]),
        "cur_vix":        float(vix.iloc[-1]),
        "cur_vix_avg":    float(vix_90avg.iloc[-1]),
        "cur_oil":        float(oil.iloc[-1]),
        "cur_oil_prem":   float(oil_premium.iloc[-1]),
        "cur_treasury":   float(treasury.iloc[-1]),
        "oil_cv":         oil_cv,
    }
