"""
Fetches live market data via yfinance.
Always pulls a rolling 1-year window ending today.
"""
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

# Use /tmp on Streamlit Cloud (read-only repo fs), local cache/ otherwise
try:
    CACHE_DIR = Path("/tmp/hope_rally_cache")
    CACHE_DIR.mkdir(exist_ok=True)
except Exception:
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
        try:
            df = pd.read_parquet(cache_path)
            result = {col: df[col].dropna() for col in df.columns}
            if all(len(v) > 0 for v in result.values()):
                return result
        except Exception:
            pass

    end   = date.today().isoformat()
    start = (date.today() - timedelta(days=LOOKBACK_DAYS)).isoformat()

    data = {}
    for key, ticker in TICKERS.items():
        try:
            raw = yf.download(ticker, start=start, end=end,
                              auto_adjust=True, progress=False)
            series = raw["Close"].squeeze().dropna()
            if len(series) == 0:
                raise ValueError(f"Empty data for {ticker}")
            data[key] = series
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {ticker}: {e}")

    df = pd.DataFrame(data).dropna(how="all")

    try:
        df.to_parquet(cache_path)
        for old in CACHE_DIR.glob("market_*.parquet"):
            if old.name != cache_path.name:
                old.unlink()
    except Exception:
        pass

    return {col: df[col].dropna() for col in df.columns}


def compute_indicators(data: dict, oil_baseline_date: str) -> dict:
    sp500    = data["sp500"]
    vix      = data["vix"]
    oil      = data["oil"]
    treasury = data["treasury"]

    for name, series in [("S&P 500", sp500), ("VIX", vix),
                          ("Oil", oil), ("Treasury", treasury)]:
        if len(series) == 0:
            raise RuntimeError(f"{name} data is empty — yfinance may be rate-limited. Try refreshing.")

    sp500_200ma   = sp500.rolling(200).mean()
    overextension = (sp500 - sp500_200ma) / sp500_200ma * 100
    vix_90avg     = vix.rolling(90).mean()

    try:
        oil_pre = oil[:oil_baseline_date]
        oil_baseline = float(oil_pre.mean()) if len(oil_pre) > 0 else float(oil.iloc[:60].mean())
    except Exception:
        oil_baseline = float(oil.iloc[:60].mean())

    oil_premium  = (oil - oil_baseline) / oil_baseline * 100
    oil_30d_std  = float(oil.iloc[-30:].std())
    oil_30d_mean = float(oil.iloc[-30:].mean())
    oil_cv       = oil_30d_std / oil_30d_mean if oil_30d_mean else 0

    # Use last valid value for each scalar
    def last(s): return float(s.dropna().iloc[-1])

    return {
        "sp500":         sp500,
        "sp500_200ma":   sp500_200ma,
        "overextension": overextension,
        "vix":           vix,
        "vix_90avg":     vix_90avg,
        "oil":           oil,
        "oil_baseline":  oil_baseline,
        "oil_premium":   oil_premium,
        "oil_cv":        oil_cv,
        "treasury":      treasury,
        "cur_sp500":     last(sp500),
        "cur_200ma":     last(sp500_200ma),
        "cur_ext":       last(overextension),
        "cur_vix":       last(vix),
        "cur_vix_avg":   last(vix_90avg),
        "cur_oil":       last(oil),
        "cur_oil_prem":  last(oil_premium),
        "cur_treasury":  last(treasury),
    }
