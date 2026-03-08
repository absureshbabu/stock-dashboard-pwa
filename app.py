"""
Stock Analysis Dashboard — PWA / Mobile Edition
================================================
Mobile-optimised version of the NSE/BSE dashboard, deployed on
Streamlit Community Cloud and usable as a Progressive Web App (PWA).

• Add to Home Screen on Android : open in Chrome → ⋮ → "Add to Home screen"
• Add to Home Screen on iOS     : open in Safari → Share → "Add to Home Screen"

Run locally : streamlit run app.py
Deploy      : push this folder to GitHub → connect to share.streamlit.io
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Dashboard",        # Short title fits mobile status bar
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed",   # Mobile: content-first, sidebar on demand
)

# ─── Ticker Lists (same as daily_stock_report.py) ───────────────────────────
NIFTY50_TICKERS = {
    "RELIANCE.NS": "Reliance Industries", "TCS.NS": "TCS", "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys", "ICICIBANK.NS": "ICICI Bank", "HINDUNILVR.NS": "Hindustan Unilever",
    "ITC.NS": "ITC", "SBIN.NS": "SBI", "BHARTIARTL.NS": "Bharti Airtel",
    "KOTAKBANK.NS": "Kotak Mahindra Bank", "LT.NS": "L&T", "AXISBANK.NS": "Axis Bank",
    "WIPRO.NS": "Wipro", "ASIANPAINT.NS": "Asian Paints", "MARUTI.NS": "Maruti Suzuki",
    "SUNPHARMA.NS": "Sun Pharma", "TITAN.NS": "Titan", "ULTRACEMCO.NS": "UltraTech Cement",
    "BAJFINANCE.NS": "Bajaj Finance", "NESTLEIND.NS": "Nestle India",
    "NTPC.NS": "NTPC", "POWERGRIDCORP.NS": "Power Grid",
    "TECHM.NS": "Tech Mahindra", "HCLTECH.NS": "HCL Technologies",
    "TATAMOTORS.NS": "Tata Motors", "TATASTEEL.NS": "Tata Steel",
    "JSWSTEEL.NS": "JSW Steel", "CIPLA.NS": "Cipla",
    "IOC.NS": "Indian Oil Corporation", "ONGC.NS": "ONGC",
    "ADANIENT.NS": "Adani Enterprises", "ADANIPORTS.NS": "Adani Ports",
    "BAJAJFINSV.NS": "Bajaj Finserv", "DRREDDY.NS": "Dr. Reddy's",
    "EICHERMOT.NS": "Eicher Motors", "GRASIM.NS": "Grasim Industries",
    "HEROMOTOCO.NS": "Hero MotoCorp", "HINDALCO.NS": "Hindalco",
    "INDUSINDBK.NS": "IndusInd Bank", "M&M.NS": "M&M",
    "COALINDIA.NS": "Coal India", "DIVISLAB.NS": "Divi's Labs",
    "APOLLOHOSP.NS": "Apollo Hospitals", "BPCL.NS": "BPCL",
    "TRENT.NS": "Trent", "BEL.NS": "BEL",
    "SBILIFE.NS": "SBI Life", "BAJAJ-AUTO.NS": "Bajaj Auto",
    "SHRIRAMFIN.NS": "Shriram Finance",
}
MIDCAP_TICKERS = {
    "BANDHANBNK.NS": "Bandhan Bank", "FEDERALBNK.NS": "Federal Bank",
    "IDFCFIRSTB.NS": "IDFC First Bank", "PNB.NS": "Punjab National Bank",
    "CANBK.NS": "Canara Bank", "BANKBARODA.NS": "Bank of Baroda",
    "AUBANK.NS": "AU Small Finance Bank", "MANAPPURAM.NS": "Manappuram Finance",
    "MUTHOOTFIN.NS": "Muthoot Finance", "CHOLAFIN.NS": "Cholamandalam Finance",
    "LICHSGFIN.NS": "LIC Housing Finance", "L&TFH.NS": "L&T Finance",
    "MPHASIS.NS": "Mphasis", "PERSISTENT.NS": "Persistent Systems",
    "COFORGE.NS": "Coforge", "LTIM.NS": "LTIMindtree",
    "TATACOMM.NS": "Tata Communications", "TATAELXSI.NS": "Tata Elxsi",
    "OFSS.NS": "Oracle Financial", "HAPPSTMNDS.NS": "Happiest Minds",
    "INDOCO.NS": "Indoco Remedies", "ZYDUSLIFE.NS": "Zydus Lifesciences",
    "AUROPHARMA.NS": "Aurobindo Pharma", "BIOCON.NS": "Biocon",
    "IPCALAB.NS": "IPCA Labs", "TORNTPHARM.NS": "Torrent Pharma",
    "ALKEM.NS": "Alkem Labs", "MAXHEALTH.NS": "Max Healthcare",
    "FORTIS.NS": "Fortis Healthcare", "LAURUSLABS.NS": "Laurus Labs",
    "CROMPTON.NS": "Crompton Greaves", "VOLTAS.NS": "Voltas",
    "POLYCAB.NS": "Polycab India", "CUMMINSIND.NS": "Cummins India",
    "APLAPOLLO.NS": "APL Apollo Tubes", "BHEL.NS": "BHEL", "SAIL.NS": "SAIL",
    "ASHOKLEY.NS": "Ashok Leyland", "TVSMOTOR.NS": "TVS Motor",
    "GODREJCP.NS": "Godrej Consumer Products", "MARICO.NS": "Marico",
    "DABUR.NS": "Dabur India", "COLPAL.NS": "Colgate-Palmolive",
    "TATACONSUM.NS": "Tata Consumer",
    "OBEROIRLTY.NS": "Oberoi Realty", "GODREJPROP.NS": "Godrej Properties",
    "PRESTIGE.NS": "Prestige Estates", "LODHA.NS": "Macrotech Developers",
    "RECLTD.NS": "REC Limited", "PFC.NS": "Power Finance Corp", "IRFC.NS": "IRFC",
    "PIIND.NS": "PI Industries", "DEEPAKNTR.NS": "Deepak Nitrite",
    "SOLARINDS.NS": "Solar Industries",
    "PETRONET.NS": "Petronet LNG", "GAIL.NS": "GAIL", "TATAPOWER.NS": "Tata Power",
    "ZOMATO.NS": "Zomato", "INDHOTEL.NS": "Indian Hotels",
}
SMALLCAP_TICKERS = {
    "TANLA.NS": "Tanla Platforms", "KPITTECH.NS": "KPIT Technologies",
    "MASTEK.NS": "Mastek", "ZENSAR.NS": "Zensar Technologies",
    "NEWGEN.NS": "Newgen Software", "BIRLASOFT.NS": "Birlasoft",
    "GRANULES.NS": "Granules India", "AJANTPHARM.NS": "Ajanta Pharma",
    "LALPATHLAB.NS": "Dr Lal PathLabs", "ERIS.NS": "Eris Lifesciences",
    "EQUITASBNK.NS": "Equitas Small Finance", "UJJIVANSFB.NS": "Ujjivan Small Finance",
    "CDSL.NS": "CDSL", "CAMS.NS": "CAMS",
    "AARTIIND.NS": "Aarti Industries", "TATACHEM.NS": "Tata Chemicals",
    "VINATIORG.NS": "Vinati Organics",
    "IRCTC.NS": "IRCTC", "RVNL.NS": "Rail Vikas Nigam",
    "SUZLON.NS": "Suzlon Energy", "INOXWIND.NS": "Inox Wind",
    "KAYNES.NS": "Kaynes Technology", "AFFLE.NS": "Affle India",
    "JYOTHYLAB.NS": "Jyothy Labs", "SAFARI.NS": "Safari Industries",
}

ALL_TICKERS = {**NIFTY50_TICKERS, **MIDCAP_TICKERS, **SMALLCAP_TICKERS}

# ─── Sector Map ─────────────────────────────────────────────────────────────
SECTOR_MAP = {
    # IT / Technology
    "TCS.NS": "IT", "INFY.NS": "IT", "WIPRO.NS": "IT", "TECHM.NS": "IT",
    "HCLTECH.NS": "IT", "MPHASIS.NS": "IT", "PERSISTENT.NS": "IT",
    "COFORGE.NS": "IT", "LTIM.NS": "IT", "TATAELXSI.NS": "IT",
    "OFSS.NS": "IT", "HAPPSTMNDS.NS": "IT", "TATACOMM.NS": "IT",
    "TANLA.NS": "IT", "KPITTECH.NS": "IT", "MASTEK.NS": "IT",
    "ZENSAR.NS": "IT", "NEWGEN.NS": "IT", "BIRLASOFT.NS": "IT", "AFFLE.NS": "IT",
    # Banking
    "HDFCBANK.NS": "Banking", "ICICIBANK.NS": "Banking", "SBIN.NS": "Banking",
    "KOTAKBANK.NS": "Banking", "AXISBANK.NS": "Banking",
    "INDUSINDBK.NS": "Banking", "BANDHANBNK.NS": "Banking",
    "FEDERALBNK.NS": "Banking", "IDFCFIRSTB.NS": "Banking",
    "PNB.NS": "Banking", "CANBK.NS": "Banking", "BANKBARODA.NS": "Banking",
    "AUBANK.NS": "Banking", "EQUITASBNK.NS": "Banking", "UJJIVANSFB.NS": "Banking",
    # Finance / NBFC
    "BAJFINANCE.NS": "Finance", "BAJAJFINSV.NS": "Finance", "SHRIRAMFIN.NS": "Finance",
    "MANAPPURAM.NS": "Finance", "MUTHOOTFIN.NS": "Finance", "CHOLAFIN.NS": "Finance",
    "LICHSGFIN.NS": "Finance", "L&TFH.NS": "Finance", "SBILIFE.NS": "Finance",
    "RECLTD.NS": "Finance", "PFC.NS": "Finance", "IRFC.NS": "Finance",
    "CDSL.NS": "Finance", "CAMS.NS": "Finance",
    # Pharma & Healthcare
    "SUNPHARMA.NS": "Pharma", "CIPLA.NS": "Pharma", "DRREDDY.NS": "Pharma",
    "DIVISLAB.NS": "Pharma", "BIOCON.NS": "Pharma", "ZYDUSLIFE.NS": "Pharma",
    "AUROPHARMA.NS": "Pharma", "IPCALAB.NS": "Pharma", "TORNTPHARM.NS": "Pharma",
    "ALKEM.NS": "Pharma", "LAURUSLABS.NS": "Pharma", "GRANULES.NS": "Pharma",
    "AJANTPHARM.NS": "Pharma", "ERIS.NS": "Pharma",
    "APOLLOHOSP.NS": "Healthcare", "MAXHEALTH.NS": "Healthcare",
    "FORTIS.NS": "Healthcare", "LALPATHLAB.NS": "Healthcare",
    # Auto
    "MARUTI.NS": "Auto", "TATAMOTORS.NS": "Auto", "BAJAJ-AUTO.NS": "Auto",
    "HEROMOTOCO.NS": "Auto", "EICHERMOT.NS": "Auto",
    "TVSMOTOR.NS": "Auto", "ASHOKLEY.NS": "Auto",
    # FMCG & Consumer
    "HINDUNILVR.NS": "FMCG", "ITC.NS": "FMCG", "NESTLEIND.NS": "FMCG",
    "ASIANPAINT.NS": "FMCG", "GODREJCP.NS": "FMCG", "MARICO.NS": "FMCG",
    "DABUR.NS": "FMCG", "COLPAL.NS": "FMCG", "TATACONSUM.NS": "FMCG",
    "JYOTHYLAB.NS": "FMCG",
    "TITAN.NS": "Consumer", "SAFARI.NS": "Consumer", "IRCTC.NS": "Consumer",
    "ZOMATO.NS": "Consumer", "INDHOTEL.NS": "Consumer",
    # Metals & Mining
    "TATASTEEL.NS": "Metals", "JSWSTEEL.NS": "Metals", "HINDALCO.NS": "Metals",
    "COALINDIA.NS": "Metals", "SAIL.NS": "Metals",
    # Energy & Oil
    "RELIANCE.NS": "Energy", "ONGC.NS": "Energy", "IOC.NS": "Energy",
    "BPCL.NS": "Energy", "PETRONET.NS": "Energy", "GAIL.NS": "Energy",
    # Power & Renewables
    "NTPC.NS": "Power", "POWERGRIDCORP.NS": "Power", "TATAPOWER.NS": "Power",
    "SUZLON.NS": "Power", "INOXWIND.NS": "Power",
    # Capital Goods & Infra
    "LT.NS": "Infra", "ADANIENT.NS": "Infra", "ADANIPORTS.NS": "Infra",
    "BHEL.NS": "Infra", "RVNL.NS": "Infra",
    "BEL.NS": "Defence", "SOLARINDS.NS": "Defence",
    "POLYCAB.NS": "Cap. Goods", "CUMMINSIND.NS": "Cap. Goods",
    "APLAPOLLO.NS": "Cap. Goods", "CROMPTON.NS": "Cap. Goods",
    "VOLTAS.NS": "Cap. Goods", "KAYNES.NS": "Cap. Goods",
    # Cement
    "ULTRACEMCO.NS": "Cement",
    # Chemicals
    "AARTIIND.NS": "Chemicals", "TATACHEM.NS": "Chemicals",
    "VINATIORG.NS": "Chemicals", "PIIND.NS": "Chemicals", "DEEPAKNTR.NS": "Chemicals",
    # Real Estate
    "OBEROIRLTY.NS": "Realty", "GODREJPROP.NS": "Realty",
    "PRESTIGE.NS": "Realty", "LODHA.NS": "Realty",
    # Diversified
    "GRASIM.NS": "Diversified",
}

# ─── Helpers ────────────────────────────────────────────────────────────────
def safe_val(val, decimals=2):
    if val is None:
        return np.nan
    try:
        if np.isnan(float(val)):
            return np.nan
        return round(float(val), decimals)
    except (TypeError, ValueError):
        return np.nan


def fmt_crore(val):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return "N/A"
    try:
        v = float(val)
        if v >= 1e12:
            return f"₹{v/1e7/100:.1f}L Cr"
        elif v >= 1e9:
            return f"₹{v/1e7:.0f} Cr"
        else:
            return f"₹{v/1e7:.1f} Cr"
    except Exception:
        return "N/A"


def is_market_open() -> bool:
    """Return True if NSE is currently in its regular trading session (9:15–15:30 IST, Mon–Fri)."""
    from datetime import timezone, timedelta
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)
    if now.weekday() >= 5:  # Sat=5, Sun=6
        return False
    open_t  = now.replace(hour=9,  minute=15, second=0, microsecond=0)
    close_t = now.replace(hour=15, minute=30, second=0, microsecond=0)
    return open_t <= now <= close_t


# ─── Pattern Detection ───────────────────────────────────────────────────────
def detect_candlestick_patterns(hist) -> list:
    patterns = []
    if len(hist) < 3:
        return [("No Data", "Insufficient candles for pattern detection.")]
    c, p, pp = hist.iloc[-1], hist.iloc[-2], hist.iloc[-3]
    body         = abs(c["Close"] - c["Open"])
    full_range   = c["High"] - c["Low"]
    upper_shadow = c["High"] - max(c["Close"], c["Open"])
    lower_shadow = min(c["Close"], c["Open"]) - c["Low"]
    p_body       = abs(p["Close"] - p["Open"])

    if full_range > 0 and body < full_range * 0.1:
        patterns.append(("Doji", "neutral", "Indecision — market at equilibrium. Watch for confirmation candle."))
    if full_range > 0 and lower_shadow > body * 2 and upper_shadow < body * 0.3 and c["Close"] > c["Open"]:
        patterns.append(("Hammer", "bullish", "Long lower shadow near lows. Potential bullish reversal if confirmed."))
    if full_range > 0 and upper_shadow > body * 2 and lower_shadow < body * 0.3 and c["Close"] < c["Open"]:
        patterns.append(("Shooting Star", "bearish", "Long upper shadow near highs. Potential bearish reversal signal."))
    if p["Close"] < p["Open"] and c["Close"] > c["Open"] and c["Close"] > p["Open"] and c["Open"] < p["Close"]:
        patterns.append(("Bullish Engulfing", "bullish", "Green candle fully engulfs prior red candle. Strong bullish reversal."))
    if p["Close"] > p["Open"] and c["Close"] < c["Open"] and c["Close"] < p["Open"] and c["Open"] > p["Close"]:
        patterns.append(("Bearish Engulfing", "bearish", "Red candle fully engulfs prior green candle. Strong bearish reversal."))
    pp_bear  = pp["Close"] < pp["Open"]
    p_small  = p_body < abs(pp["Close"] - pp["Open"]) * 0.3
    c_bull   = c["Close"] > c["Open"] and c["Close"] > (pp["Open"] + pp["Close"]) / 2
    if pp_bear and p_small and c_bull:
        patterns.append(("Morning Star", "bullish", "3-candle bullish reversal. Strong indication of trend change."))
    pp_bull  = pp["Close"] > pp["Open"]
    c_bear   = c["Close"] < c["Open"] and c["Close"] < (pp["Open"] + pp["Close"]) / 2
    if pp_bull and p_small and c_bear:
        patterns.append(("Evening Star", "bearish", "3-candle bearish reversal. Strong indication of trend change."))
    if full_range > 0 and body > full_range * 0.9:
        if c["Close"] > c["Open"]:
            patterns.append(("Bullish Marubozu", "bullish", "Full body candle with no shadows. High conviction buying."))
        else:
            patterns.append(("Bearish Marubozu", "bearish", "Full body candle with no shadows. High conviction selling."))
    if not patterns:
        patterns.append(("No Pattern", "neutral", "No decisive candlestick pattern detected. Wait for signal."))
    return patterns


def detect_chart_patterns(hist, last_close: float) -> list:
    patterns = []
    sma50  = hist["SMA_50"].iloc[-1]  if "SMA_50"  in hist.columns else np.nan
    sma50p = hist["SMA_50"].iloc[-6]  if "SMA_50"  in hist.columns and len(hist) > 6 else np.nan
    sma200 = hist["SMA_200"].iloc[-1] if "SMA_200" in hist.columns else np.nan
    sma200p= hist["SMA_200"].iloc[-6] if "SMA_200" in hist.columns and len(hist) > 6 else np.nan

    # Golden / Death Cross
    if not any(np.isnan(v) for v in [sma50, sma200, sma50p, sma200p]):
        if sma50 > sma200 and sma50p <= sma200p:
            patterns.append(("Golden Cross", "bullish", "SMA50 just crossed above SMA200 — strong long-term bullish signal."))
        elif sma50 < sma200 and sma50p >= sma200p:
            patterns.append(("Death Cross", "bearish", "SMA50 just crossed below SMA200 — strong long-term bearish signal."))
        elif sma50 > sma200:
            patterns.append(("Bullish Alignment", "bullish", "SMA50 > SMA200. Price above both MAs — uptrend intact."))
        else:
            patterns.append(("Bearish Alignment", "bearish", "SMA50 < SMA200. Price below both MAs — downtrend intact."))

    # Bollinger Squeeze
    if "BB_Upper" in hist.columns and "BB_Lower" in hist.columns and "BB_Mid" in hist.columns:
        bw_series = (hist["BB_Upper"] - hist["BB_Lower"]) / (hist["BB_Mid"] + 1e-10)
        bw_curr   = bw_series.iloc[-1]
        bw_min20  = bw_series.tail(20).min()
        if bw_curr <= bw_min20 * 1.05:
            patterns.append(("Bollinger Squeeze", "neutral", "BB width at 20-day low — volatility contraction, potential breakout ahead."))

    # Volume Spike
    avg_vol  = hist["Volume"].mean()
    curr_vol = hist["Volume"].iloc[-1]
    if avg_vol > 0 and curr_vol > avg_vol * 2:
        lbl = "bullish" if hist["Close"].iloc[-1] >= hist["Open"].iloc[-1] else "bearish"
        patterns.append(("Volume Spike", lbl, f"Volume {curr_vol/avg_vol:.1f}× average — high conviction move."))

    # Price vs 50-DMA
    if not np.isnan(sma50) and sma50 > 0:
        pct = (last_close / sma50 - 1) * 100
        if pct > 8:
            patterns.append(("Extended Above 50-DMA", "neutral", f"Price {pct:.1f}% above 50-DMA — watch for mean-reversion pullback."))
        elif pct < -8:
            patterns.append(("Extended Below 50-DMA", "neutral", f"Price {abs(pct):.1f}% below 50-DMA — potential bounce zone."))

    # MACD Divergence (simple)
    if "MACD_Hist" in hist.columns and len(hist) >= 5:
        mh = hist["MACD_Hist"].dropna()
        if len(mh) >= 5:
            if all(mh.iloc[-i] > mh.iloc[-i-1] for i in range(1, 4)):
                patterns.append(("MACD Momentum Rising", "bullish", "MACD histogram expanding upward — bullish momentum building."))
            elif all(mh.iloc[-i] < mh.iloc[-i-1] for i in range(1, 4)):
                patterns.append(("MACD Momentum Falling", "bearish", "MACD histogram expanding downward — bearish momentum building."))

    if not patterns:
        patterns.append(("No Chart Pattern", "neutral", "No significant chart pattern detected currently."))
    return patterns


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stock_history(ticker: str) -> pd.DataFrame:
    """Return indicator-enriched OHLCV history for chart rendering."""
    try:
        import yfinance as yf
        hist = yf.Ticker(ticker).history(period="6mo")
        if hist.empty or len(hist) < 20:
            return pd.DataFrame()
        hist["SMA_50"]  = hist["Close"].rolling(50).mean()
        hist["SMA_200"] = hist["Close"].rolling(min(200, len(hist))).mean()
        hist["EMA_12"]  = hist["Close"].ewm(span=12).mean()
        hist["EMA_26"]  = hist["Close"].ewm(span=26).mean()
        hist["MACD"]        = hist["EMA_12"] - hist["EMA_26"]
        hist["MACD_Signal"] = hist["MACD"].ewm(span=9).mean()
        hist["MACD_Hist"]   = hist["MACD"] - hist["MACD_Signal"]
        hist["BB_Mid"]   = hist["Close"].rolling(20).mean()
        bb_std           = hist["Close"].rolling(20).std()
        hist["BB_Upper"] = hist["BB_Mid"] + 2 * bb_std
        hist["BB_Lower"] = hist["BB_Mid"] - 2 * bb_std
        delta = hist["Close"].diff()
        gain  = delta.where(delta > 0, 0).rolling(14).mean()
        loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
        hist["RSI"] = 100 - (100 / (1 + gain / loss))
        return hist
    except Exception:
        return pd.DataFrame()


# ─── NSE/BSE Live Search ─────────────────────────────────────────────────────
_NSE_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
}

@st.cache_data(ttl=300, show_spinner=False)
def search_nse_stocks(query: str) -> list:
    """Query NSE India autocomplete API. Returns list of {symbol, name, type}."""
    try:
        session = requests.Session()
        # Seed cookies by visiting homepage first
        session.get("https://www.nseindia.com", headers=_NSE_HEADERS, timeout=10)
        resp = session.get(
            f"https://www.nseindia.com/api/search/autocomplete?q={query}",
            headers=_NSE_HEADERS,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            # Filter to equity only, return top 10
            return [
                s for s in data.get("symbols", [])
                if s.get("instrument_type", "").upper() in ("", "EQ", "EQUITY")
                   or s.get("type", "").upper() == "EQ"
            ][:10]
    except Exception:
        pass
    return []


@st.cache_data(ttl=300, show_spinner=False)
def search_bse_stocks(query: str) -> list:
    """Query BSE India scrip search API. Returns list of {symbol, name}."""
    try:
        resp = requests.get(
            "https://api.bseindia.com/BseIndiaAPI/api/ListofScripData/w",
            params={"Group": "", "Scripcode": "", "segment": "Equity",
                    "Status": "Active", "scrip": query, "industry": ""},
            headers={"User-Agent": _NSE_HEADERS["User-Agent"],
                     "Referer": "https://www.bseindia.com/"},
            timeout=10,
        )
        if resp.status_code == 200:
            items = resp.json().get("Table", [])
            return [
                {"symbol": i.get("SCRIP_CD", ""), "name": i.get("Scrip_Name", "")}
                for i in items[:10]
            ]
    except Exception:
        pass
    return []


# ─── Data Fetching ───────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_index_data():
    try:
        import yfinance as yf
        out = {}
        for sym, key in [
            ("^NSEI",     "nifty"),
            ("^BSESN",   "sensex"),
            ("^NSEBANK", "banknifty"),
            ("^INDIAVIX","vix"),
        ]:
            h = yf.Ticker(sym).history(period="5d")
            if not h.empty and len(h) >= 2:
                close = round(h["Close"].iloc[-1], 2)
                prev  = round(h["Close"].iloc[-2], 2)
                chg   = round(close - prev, 2)
                pct   = round(chg / prev * 100, 2)
                out[key] = {"close": close, "change": chg, "pct": pct}
        return out
    except Exception:
        return {}


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_stocks(selected_tickers: tuple):
    try:
        import yfinance as yf
    except ImportError:
        st.error("yfinance not installed. Run: pip install yfinance")
        return pd.DataFrame()

    rows = []
    progress = st.progress(0, text="Fetching stock data…")
    total = len(selected_tickers)

    for i, ticker in enumerate(selected_tickers):
        name = ALL_TICKERS.get(ticker, ticker)
        try:
            stock = yf.Ticker(ticker)
            hist  = stock.history(period="6mo")
            if hist.empty or len(hist) < 20:
                continue

            info       = stock.info
            last_close = float(hist["Close"].iloc[-1])
            prev_close = float(hist["Close"].iloc[-2]) if len(hist) > 1 else last_close
            pct_change = (last_close - prev_close) / prev_close * 100

            if last_close < 50:
                continue

            # ── Technical Indicators ──
            hist["SMA_50"]  = hist["Close"].rolling(50).mean()
            hist["SMA_200"] = hist["Close"].rolling(min(200, len(hist))).mean()
            hist["EMA_12"]  = hist["Close"].ewm(span=12).mean()
            hist["EMA_26"]  = hist["Close"].ewm(span=26).mean()
            hist["EMA_50"]  = hist["Close"].ewm(span=50).mean()

            # RSI
            delta = hist["Close"].diff()
            gain  = delta.where(delta > 0, 0).rolling(14).mean()
            loss  = (-delta.where(delta < 0, 0)).rolling(14).mean()
            hist["RSI"] = 100 - (100 / (1 + gain / loss))

            # MACD
            hist["MACD"]        = hist["EMA_12"] - hist["EMA_26"]
            hist["MACD_Signal"] = hist["MACD"].ewm(span=9).mean()
            hist["MACD_Hist"]   = hist["MACD"] - hist["MACD_Signal"]

            # Bollinger
            hist["BB_Mid"]   = hist["Close"].rolling(20).mean()
            bb_std           = hist["Close"].rolling(20).std()
            hist["BB_Upper"] = hist["BB_Mid"] + 2 * bb_std
            hist["BB_Lower"] = hist["BB_Mid"] - 2 * bb_std

            # ATR
            hl  = hist["High"] - hist["Low"]
            hc  = (hist["High"] - hist["Close"].shift()).abs()
            lc  = (hist["Low"]  - hist["Close"].shift()).abs()
            tr  = hl.combine(hc, max).combine(lc, max)
            hist["ATR"] = tr.rolling(14).mean()

            # ADX
            pdm = hist["High"].diff().clip(lower=0)
            ndm = (-hist["Low"].diff()).clip(lower=0)
            atr14  = hist["ATR"]
            pdi    = 100 * (pdm.rolling(14).mean() / atr14)
            ndi    = 100 * (ndm.rolling(14).mean() / atr14)
            dx     = 100 * ((pdi - ndi).abs() / (pdi + ndi))
            hist["ADX"] = dx.rolling(14).mean()

            # Stochastic
            low14  = hist["Low"].rolling(14).min()
            high14 = hist["High"].rolling(14).max()
            hist["Stoch_K"] = 100 * (hist["Close"] - low14) / (high14 - low14)
            hist["Stoch_D"] = hist["Stoch_K"].rolling(3).mean()

            # Williams %R
            hist["Williams_R"] = -100 * (high14 - hist["Close"]) / (high14 - low14)

            # MFI
            hist["TP"]  = (hist["High"] + hist["Low"] + hist["Close"]) / 3
            hist["RMF"] = hist["TP"] * hist["Volume"]
            pos = hist["RMF"].where(hist["TP"] > hist["TP"].shift(), 0).rolling(14).sum()
            neg = hist["RMF"].where(hist["TP"] <= hist["TP"].shift(), 0).rolling(14).sum()
            hist["MFI"] = 100 - (100 / (1 + pos / (neg + 1e-10)))

            # VWAP
            hist["VWAP"] = (hist["TP"] * hist["Volume"]).rolling(14).sum() / (
                hist["Volume"].rolling(14).sum() + 1e-10
            )

            # OBV
            obv = [0]
            for j in range(1, len(hist)):
                if hist["Close"].iloc[j] > hist["Close"].iloc[j - 1]:
                    obv.append(obv[-1] + hist["Volume"].iloc[j])
                elif hist["Close"].iloc[j] < hist["Close"].iloc[j - 1]:
                    obv.append(obv[-1] - hist["Volume"].iloc[j])
                else:
                    obv.append(obv[-1])
            hist["OBV"] = obv

            # Fibonacci (3-month)
            h3m   = float(hist["High"].tail(63).max())
            l3m   = float(hist["Low"].tail(63).min())
            fd    = h3m - l3m
            fib38 = h3m - 0.382 * fd
            fib50 = h3m - 0.500 * fd
            fib61 = h3m - 0.618 * fd

            # Pivot points (full R1/R2/R3 + S1/S2/S3)
            ph    = float(hist["High"].iloc[-2])
            pl    = float(hist["Low"].iloc[-2])
            pc    = float(hist["Close"].iloc[-2])
            pivot = (ph + pl + pc) / 3
            r1    = 2 * pivot - pl
            r2    = pivot + (ph - pl)
            r3    = r1 + (ph - pl)
            s1    = 2 * pivot - ph
            s2    = pivot - (ph - pl)
            s3    = s1 - (ph - pl)

            # Patterns
            candle_patterns = detect_candlestick_patterns(hist)
            chart_patterns  = detect_chart_patterns(hist, last_close)

            # Entry zone (Fib 50–61.8)
            entry_zone = f"₹{fib50:.2f} – ₹{fib61:.2f}"

            latest = hist.iloc[-1]

            # Category
            cap = info.get("marketCap", 0) or 0
            if ticker in NIFTY50_TICKERS:
                category = "Large Cap"
            elif ticker in MIDCAP_TICKERS:
                category = "Mid Cap"
            else:
                category = "Small Cap"

            # Signal labels
            rsi_val  = safe_val(latest.get("RSI"))
            macd_val = safe_val(latest.get("MACD"), 4)
            macs_val = safe_val(latest.get("MACD_Signal"), 4)
            adx_val  = safe_val(latest.get("ADX"))

            if not np.isnan(rsi_val):
                rsi_signal = "Overbought" if rsi_val > 70 else ("Oversold" if rsi_val < 30 else "Neutral")
            else:
                rsi_signal = "N/A"

            if not (np.isnan(macd_val) or np.isnan(macs_val)):
                macd_signal = "Bullish" if macd_val > macs_val else "Bearish"
            else:
                macd_signal = "N/A"

            if not np.isnan(adx_val):
                adx_signal = "Strong" if adx_val > 25 else "Weak"
            else:
                adx_signal = "N/A"

            vol     = int(latest.get("Volume", 0))
            avg_vol = int(hist["Volume"].mean())
            vol_ratio = round(vol / avg_vol, 2) if avg_vol > 0 else np.nan

            rows.append({
                "Ticker": ticker, "Name": name, "Category": category,
                "Close": round(last_close, 2), "Prev Close": round(prev_close, 2),
                "% Change": round(pct_change, 2),
                # Fundamentals
                "Market Cap": cap if cap else np.nan,
                "PE Ratio":   safe_val(info.get("trailingPE")),
                "EPS":        safe_val(info.get("trailingEps")),
                "PB Ratio":   safe_val(info.get("priceToBook")),
                "ROE":        safe_val(info.get("returnOnEquity")),
                "Div Yield":  safe_val(info.get("dividendYield")),
                "D/E Ratio":  safe_val(info.get("debtToEquity")),
                "Beta":       safe_val(info.get("beta")),
                "52W High":   safe_val(info.get("fiftyTwoWeekHigh")),
                "52W Low":    safe_val(info.get("fiftyTwoWeekLow")),
                # Technical
                "RSI":        rsi_val, "RSI Signal": rsi_signal,
                "MACD":       macd_val, "MACD Signal": macd_signal,
                "ADX":        adx_val, "ADX Signal": adx_signal,
                "SMA 50":     safe_val(latest.get("SMA_50")),
                "SMA 200":    safe_val(latest.get("SMA_200")),
                "EMA 12":     safe_val(latest.get("EMA_12")),
                "EMA 26":     safe_val(latest.get("EMA_26")),
                "BB Upper":   safe_val(latest.get("BB_Upper")),
                "BB Mid":     safe_val(latest.get("BB_Mid")),
                "BB Lower":   safe_val(latest.get("BB_Lower")),
                "ATR":        safe_val(latest.get("ATR")),
                "Stoch K":    safe_val(latest.get("Stoch_K")),
                "Stoch D":    safe_val(latest.get("Stoch_D")),
                "Williams %R":safe_val(latest.get("Williams_R")),
                "MFI":        safe_val(latest.get("MFI")),
                "VWAP":       safe_val(latest.get("VWAP")),
                # Volume
                "Volume":     vol, "Avg Volume": avg_vol, "Vol Ratio": vol_ratio,
                "OBV Trend":  "Rising" if int(hist["OBV"].iloc[-1]) > int(hist["OBV"].iloc[-5]) else "Falling",
                # Levels
                "Fib 38.2":  round(fib38, 2), "Fib 50":  round(fib50, 2), "Fib 61.8": round(fib61, 2),
                "Pivot":     round(pivot, 2),
                "R1": round(r1, 2), "R2": round(r2, 2), "R3": round(r3, 2),
                "S1": round(s1, 2), "S2": round(s2, 2), "S3": round(s3, 2),
                "Entry Zone": entry_zone,
                "Stop Loss": round(l3m - safe_val(latest.get("ATR"), 2), 2),
                "Target 1":  round(h3m + safe_val(latest.get("ATR"), 2) * 0.5, 2),
                "Target 2":  round(h3m + safe_val(latest.get("ATR"), 2) * 1.0, 2),
                "Key Support":    f"₹{s1:.2f}, ₹{s2:.2f}",
                "Key Resistance": f"₹{r1:.2f}, ₹{r2:.2f}",
                # Patterns (stored as lists)
                "Candlestick Patterns": candle_patterns,
                "Chart Patterns":       chart_patterns,
            })

            # Stamp recommendation (uses the dict we just built)
            rec = compute_recommendation(rows[-1])
            rows[-1].update({
                "Recommendation": rec["Recommendation"],
                "Rec Color":      rec["Rec Color"],
                "Score":          rec["Score"],
                "Score %":        rec["Score %"],
                "Bull Signals":   rec["Bull Signals"],
                "Bear Signals":   rec["Bear Signals"],
            })

            # Placeholder so the dict key exists for 52W position (added below)
            rows[-1].update({
                # 52W position
                "52W Position": round((last_close - safe_val(info.get("fiftyTwoWeekLow"))) /
                    max(safe_val(info.get("fiftyTwoWeekHigh")) - safe_val(info.get("fiftyTwoWeekLow")), 1) * 100, 1)
                    if not np.isnan(safe_val(info.get("fiftyTwoWeekHigh"))) else np.nan,
            })

        except Exception:
            pass

        progress.progress((i + 1) / total, text=f"Fetching {name}…")

    progress.empty()
    return pd.DataFrame(rows)


# ─── Analyst / Broker Data ───────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_analyst_data(ticker: str) -> dict:
    """
    Fetch analyst consensus, price targets and broker upgrades/downgrades
    from Yahoo Finance via yfinance.
    Returns a dict with keys: targets, consensus, upgrades.
    """
    empty = {"targets": {}, "consensus": {}, "upgrades": []}
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info  = stock.info

        current = safe_val(info.get("currentPrice") or info.get("regularMarketPrice"))

        # ── Price targets ────────────────────────────────────────────────────
        t_mean   = safe_val(info.get("targetMeanPrice"))
        t_high   = safe_val(info.get("targetHighPrice"))
        t_low    = safe_val(info.get("targetLowPrice"))
        t_median = safe_val(info.get("targetMedianPrice"))

        upside_mean = round((t_mean - current) / current * 100, 1) \
            if not any(np.isnan(v) for v in [t_mean, current]) and current > 0 else np.nan

        targets = {
            "current":     current,
            "mean":        t_mean,
            "high":        t_high,
            "low":         t_low,
            "median":      t_median,
            "upside_mean": upside_mean,
        }

        # ── Analyst consensus ────────────────────────────────────────────────
        key   = (info.get("recommendationKey") or "").replace("_", " ").title()
        score = safe_val(info.get("recommendationMean"))  # 1=Strong Buy … 5=Strong Sell
        count = int(info.get("numberOfAnalystOpinions") or 0)

        # Derive breakdown from recommendationKey score bucket
        consensus = {"key": key, "score": score, "count": count}

        # ── Upgrades / Downgrades ────────────────────────────────────────────
        upg_list = []
        try:
            upg = stock.upgrades_downgrades
            if upg is not None and not upg.empty:
                upg = upg.reset_index()
                # Normalize column names
                upg.columns = [c.strip() for c in upg.columns]
                date_col = next((c for c in upg.columns
                                 if c.lower() in ("date", "gradedate", "index")), None)
                if date_col:
                    upg = upg.sort_values(date_col, ascending=False).head(15)
                    upg[date_col] = pd.to_datetime(upg[date_col]).dt.strftime("%d %b %Y")
                upg_list = upg.to_dict("records")
        except Exception:
            pass

        return {"targets": targets, "consensus": consensus, "upgrades": upg_list}

    except Exception:
        return empty


def _analyst_consensus_color(key: str) -> str:
    k = key.lower()
    if "strong buy" in k:   return "#00c853"
    if "buy" in k:           return "#1e8a3e"
    if "hold" in k:          return "#f9a825"
    if "underperform" in k or "sell" in k: return "#d32f2f"
    return "#888"


# ─── Company Overview helpers (module-level so cache hasher works) ───────────
def _add_news_item(news: list, news_seen: set, cutoff_ts: float,
                   title: str, publisher: str, link: str, pub_ts: float):
    """Deduplicate and append one news item to the list."""
    key = title.strip().lower()[:80]
    if not key or key in news_seen or pub_ts < cutoff_ts:
        return
    news_seen.add(key)
    try:
        date_str = datetime.fromtimestamp(int(pub_ts)).strftime("%d %b %Y")
        year_str = datetime.fromtimestamp(int(pub_ts)).strftime("%Y")
    except Exception:
        date_str = year_str = ""
    news.append({
        "title":     title,
        "publisher": publisher,
        "link":      link,
        "date":      date_str,
        "year":      year_str,
        "ts":        pub_ts,
    })


# ─── Company Overview ────────────────────────────────────────────────────────
@st.cache_data(ttl=3600, show_spinner=False)
def fetch_company_overview(ticker: str) -> dict:
    """
    Fetch company description, management, financials, dividend history
    and recent news from Yahoo Finance via yfinance.
    """
    try:
        import yfinance as yf
        stock = yf.Ticker(ticker)
        info  = stock.info

        # ── Basic company info ───────────────────────────────────────────────
        overview = {
            "description": info.get("longBusinessSummary", ""),
            "sector":      info.get("sector", ""),
            "industry":    info.get("industry", ""),
            "employees":   info.get("fullTimeEmployees"),
            "website":     info.get("website", ""),
            "city":        info.get("city", ""),
            "country":     info.get("country", "India"),
        }

        # ── Key management officers ──────────────────────────────────────────
        management = [
            {
                "name":  o.get("name", ""),
                "title": o.get("title", ""),
                "age":   o.get("age", ""),
                "pay":   o.get("totalPay"),
            }
            for o in (info.get("companyOfficers") or [])[:8]
        ]

        # ── Financial highlights ─────────────────────────────────────────────
        financials = {
            "revenue":         info.get("totalRevenue"),
            "revenue_growth":  info.get("revenueGrowth"),
            "earnings_growth": info.get("earningsGrowth"),
            "gross_margin":    info.get("grossMargins"),
            "op_margin":       info.get("operatingMargins"),
            "net_margin":      info.get("profitMargins"),
            "ebitda":          info.get("ebitda"),
            "free_cashflow":   info.get("freeCashflow"),
            "total_debt":      info.get("totalDebt"),
            "total_cash":      info.get("totalCash"),
            "roa":             info.get("returnOnAssets"),
            "roe":             info.get("returnOnEquity"),
            # Valuation multiples
            "trailing_pe":    info.get("trailingPE"),
            "forward_pe":     info.get("forwardPE"),
            "peg_ratio":      info.get("pegRatio"),
            "price_to_sales": info.get("priceToSalesTrailing12Months"),
            "ev_ebitda":      info.get("enterpriseToEbitda"),
            "ev_revenue":     info.get("enterpriseToRevenue"),
        }

        # ── Dividend history (last 12 payments) ──────────────────────────────
        div_hist = []
        try:
            divs = stock.dividends
            if divs is not None and not divs.empty:
                d = divs.reset_index()
                d.columns = ["Date", "Dividend"]
                d["Date"] = pd.to_datetime(d["Date"]).dt.strftime("%d %b %Y")
                div_hist = d.tail(12).iloc[::-1].to_dict("records")
        except Exception:
            pass

        # ── News: last 3 years from multiple sources ─────────────────────────
        cutoff_ts = (datetime.now() - pd.DateOffset(years=3)).timestamp()
        news_seen: set  = set()   # deduplicate by title
        news:      list = []

        # Source 1: yfinance built-in news
        try:
            for n in (stock.news or []):
                _add_news_item(
                    news, news_seen, cutoff_ts,
                    n.get("title", ""), n.get("publisher", ""),
                    n.get("link", ""),
                    n.get("providerPublishTime") or n.get("published") or 0,
                )
        except Exception:
            pass

        # Source 2: Yahoo Finance search API (returns more articles)
        try:
            sym_base = ticker.replace(".NS", "").replace(".BO", "")
            resp = requests.get(
                "https://query2.finance.yahoo.com/v1/finance/search",
                params={"q": sym_base, "newsCount": 100, "quotesCount": 0},
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=10,
            )
            if resp.status_code == 200:
                for n in resp.json().get("news", []):
                    _add_news_item(
                        news, news_seen, cutoff_ts,
                        n.get("title", ""), n.get("publisher", ""),
                        n.get("link", ""),
                        n.get("providerPublishTime") or 0,
                    )
        except Exception:
            pass

        # Source 3: Google News RSS (company name + NSE)
        try:
            company_q = (info.get("longName") or info.get("shortName") or ticker)
            company_q = company_q.split("(")[0].strip().replace(" ", "+")
            rss_url   = (
                f"https://news.google.com/rss/search"
                f"?q={company_q}+NSE+stock&hl=en-IN&gl=IN&ceid=IN:en"
            )
            rss_resp = requests.get(
                rss_url,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=10,
            )
            if rss_resp.status_code == 200:
                root = ET.fromstring(rss_resp.content)
                for item in root.findall(".//item"):
                    _title     = item.findtext("title", "")
                    _link      = item.findtext("link", "")
                    _pub_str   = item.findtext("pubDate", "")
                    _src_el    = item.find("source")
                    _publisher = _src_el.text if _src_el is not None else "Google News"
                    try:
                        _pub_ts = parsedate_to_datetime(_pub_str).timestamp()
                    except Exception:
                        continue
                    _add_news_item(news, news_seen, cutoff_ts,
                                   _title, _publisher, _link, _pub_ts)
        except Exception:
            pass

        # Sort newest first
        news.sort(key=lambda x: x.get("ts", 0), reverse=True)

        return {
            "overview":   overview,
            "management": management,
            "financials": financials,
            "div_hist":   div_hist,
            "news":       news,
        }
    except Exception:
        return {}


def _pct_str(val, scale=1):
    """Format a fraction (0-1) or percentage as colored string."""
    try:
        v = float(val) * scale
        color = "#1e8a3e" if v >= 0 else "#d32f2f"
        return f"<span style='color:{color};font-weight:600'>{v:+.1f}%</span>"
    except Exception:
        return "<span style='color:#aaa'>N/A</span>"


def _crore(val):
    if val is None:
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 1e12: return f"₹{v/1e7/100:.1f}L Cr"
        if abs(v) >= 1e9:  return f"₹{v/1e7:.0f} Cr"
        return f"₹{v/1e7:.1f} Cr"
    except Exception:
        return "N/A"


# ─── Recommendation Engine ───────────────────────────────────────────────────
def compute_recommendation(row) -> dict:
    """
    Score a stock across 11 technical signals and return a BUY/HOLD/SELL verdict.
    row: dict (from fetch_stocks loop) or pandas Series (from render_stock_detail).
    """
    get = lambda k, d=np.nan: row.get(k, d) if isinstance(row, dict) else row.get(k, d)

    score   = 0
    signals = []   # list of (label, sentiment, detail)

    # 1 ─ RSI
    rsi = get("RSI")
    if not (isinstance(rsi, float) and np.isnan(float(rsi) if rsi is not None else float("nan"))):
        try:
            rsi = float(rsi)
            if rsi < 30:
                score += 2
                signals.append(("RSI Oversold", "bullish", f"RSI {rsi:.1f} — deeply oversold, potential reversal"))
            elif rsi < 50:
                score += 1
                signals.append(("RSI Recovering", "bullish", f"RSI {rsi:.1f} — recovering from oversold zone"))
            elif rsi > 70:
                score -= 1
                signals.append(("RSI Overbought", "bearish", f"RSI {rsi:.1f} — overbought, watch for pullback"))
        except Exception:
            pass

    # 2 ─ MACD
    macd_sig = get("MACD Signal", "")
    macd_val = get("MACD", np.nan)
    if macd_sig == "Bullish":
        score += 2
        signals.append(("MACD Bullish", "bullish", f"MACD {macd_val:.3f} above signal line — bullish momentum"))
    elif macd_sig == "Bearish":
        score -= 2
        signals.append(("MACD Bearish", "bearish", f"MACD {macd_val:.3f} below signal line — bearish momentum"))

    # 3 ─ Price vs 50-DMA
    close  = float(get("Close", 0) or 0)
    sma50  = get("SMA 50", np.nan)
    try:
        sma50 = float(sma50)
        if not np.isnan(sma50) and sma50 > 0:
            pct = (close - sma50) / sma50 * 100
            if close > sma50:
                score += 1
                signals.append(("Above 50-DMA", "bullish", f"Price {pct:.1f}% above 50-DMA"))
            else:
                score -= 1
                signals.append(("Below 50-DMA", "bearish", f"Price {abs(pct):.1f}% below 50-DMA"))
    except Exception:
        pass

    # 4 ─ Price vs 200-DMA
    sma200 = get("SMA 200", np.nan)
    try:
        sma200 = float(sma200)
        if not np.isnan(sma200) and sma200 > 0:
            pct = (close - sma200) / sma200 * 100
            if close > sma200:
                score += 1
                signals.append(("Above 200-DMA", "bullish", f"Price {pct:.1f}% above 200-DMA"))
            else:
                score -= 1
                signals.append(("Below 200-DMA", "bearish", f"Price {abs(pct):.1f}% below 200-DMA"))
    except Exception:
        pass

    # 5 ─ Golden / Death Cross alignment
    try:
        if not any(np.isnan(v) for v in [sma50, sma200]):
            if sma50 > sma200:
                score += 1
                signals.append(("Golden Cross Alignment", "bullish", "SMA50 > SMA200 — long-term bullish structure"))
            else:
                score -= 1
                signals.append(("Death Cross Alignment", "bearish", "SMA50 < SMA200 — long-term bearish structure"))
    except Exception:
        pass

    # 6 ─ Stochastic %K
    sk = get("Stoch K", np.nan)
    try:
        sk = float(sk)
        if not np.isnan(sk):
            if sk < 20:
                score += 1
                signals.append(("Stochastic Oversold", "bullish", f"Stoch %K {sk:.1f} — oversold zone"))
            elif sk > 80:
                score -= 1
                signals.append(("Stochastic Overbought", "bearish", f"Stoch %K {sk:.1f} — overbought zone"))
    except Exception:
        pass

    # 7 ─ Williams %R
    wr = get("Williams %R", np.nan)
    try:
        wr = float(wr)
        if not np.isnan(wr):
            if wr < -80:
                score += 1
                signals.append(("Williams %R Oversold", "bullish", f"Williams %R {wr:.1f} — oversold"))
            elif wr > -20:
                score -= 1
                signals.append(("Williams %R Overbought", "bearish", f"Williams %R {wr:.1f} — overbought"))
    except Exception:
        pass

    # 8 ─ MFI
    mfi = get("MFI", np.nan)
    try:
        mfi = float(mfi)
        if not np.isnan(mfi):
            if mfi < 20:
                score += 1
                signals.append(("MFI Oversold", "bullish", f"MFI {mfi:.1f} — low money flow, accumulation likely"))
            elif mfi > 80:
                score -= 1
                signals.append(("MFI Overbought", "bearish", f"MFI {mfi:.1f} — high money flow, distribution likely"))
    except Exception:
        pass

    # 9 ─ OBV Trend
    obv = get("OBV Trend", "")
    if obv == "Rising":
        score += 1
        signals.append(("OBV Rising", "bullish", "On-Balance Volume rising — buying pressure confirmed"))
    elif obv == "Falling":
        score -= 1
        signals.append(("OBV Falling", "bearish", "On-Balance Volume falling — selling pressure confirmed"))

    # 10 ─ ADX trend strength
    adx = get("ADX", np.nan)
    try:
        adx = float(adx)
        if not np.isnan(adx) and adx > 25:
            if macd_sig == "Bullish":
                score += 1
                signals.append(("Strong Bullish Trend (ADX)", "bullish", f"ADX {adx:.1f} confirms strong uptrend"))
            elif macd_sig == "Bearish":
                score -= 1
                signals.append(("Strong Bearish Trend (ADX)", "bearish", f"ADX {adx:.1f} confirms strong downtrend"))
    except Exception:
        pass

    # 11 ─ Bollinger Band position
    bbu = get("BB Upper", np.nan)
    bbl = get("BB Lower", np.nan)
    try:
        bbu, bbl = float(bbu), float(bbl)
        if not any(np.isnan(v) for v in [bbu, bbl]) and (bbu - bbl) > 0:
            bb_pos = (close - bbl) / (bbu - bbl) * 100
            if bb_pos < 20:
                score += 1
                signals.append(("Near BB Lower (Support)", "bullish", "Price near lower Bollinger Band — potential bounce"))
            elif bb_pos > 80:
                score -= 1
                signals.append(("Near BB Upper (Resistance)", "bearish", "Price near upper Bollinger Band — potential reversal"))
    except Exception:
        pass

    bull_count = sum(1 for _, s, _ in signals if s == "bullish")
    bear_count = sum(1 for _, s, _ in signals if s == "bearish")
    total      = bull_count + bear_count
    score_pct  = round(bull_count / total * 100) if total > 0 else 50

    if score >= 7:
        rec, color = "STRONG BUY",  "#00c853"
    elif score >= 3:
        rec, color = "BUY",         "#69f0ae"
    elif score >= -2:
        rec, color = "HOLD",        "#ffd740"
    elif score >= -6:
        rec, color = "SELL",        "#ff6b6b"
    else:
        rec, color = "STRONG SELL", "#ff1744"

    return {
        "Recommendation": rec,
        "Rec Color":      color,
        "Score":          score,
        "Score %":        score_pct,
        "Bull Signals":   bull_count,
        "Bear Signals":   bear_count,
        "Signal Details": signals,
    }


# ─── Recommendation colour map (module-level for shared use) ─────────────────
_CMAP = {
    "STRONG BUY":  "#00c853",
    "BUY":         "#69f0ae",
    "HOLD":        "#ffd740",
    "SELL":        "#ff6b6b",
    "STRONG SELL": "#ff1744",
}


# ─── Colour helpers ──────────────────────────────────────────────────────────
def color_pct(val):
    if pd.isna(val):
        return ""
    return "color: #1e8a3e; font-weight:600" if val > 0 else ("color: #d32f2f; font-weight:600" if val < 0 else "color: #555")


def color_rsi(val):
    if pd.isna(val):
        return ""
    if val > 70:
        return "background-color: #ffcdd2; color: #b71c1c; font-weight:600"
    if val < 30:
        return "background-color: #c8e6c9; color: #1b5e20; font-weight:600"
    return ""


# ─── Sidebar ─────────────────────────────────────────────────────────────────
def build_sidebar():
    # Styled sidebar header (replaces broken SVG logo)
    st.sidebar.markdown(
        """
        <div style="background:linear-gradient(135deg,#0d1b2a,#1a3a5c);
                    border-radius:10px;padding:12px 16px;margin-bottom:8px;text-align:center">
          <div style="color:#fff;font-size:1.1em;font-weight:800;letter-spacing:0.5px">
            📊 NSE / BSE
          </div>
          <div style="color:#93b4d0;font-size:0.72em;margin-top:2px">Stock Analysis Dashboard</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("### ⚙️ Filters")

    # ── NSE / BSE Live Search ──
    st.sidebar.markdown("### 🔍 Search NSE / BSE")
    exchange = st.sidebar.radio("Exchange", ["NSE", "BSE"], horizontal=True)
    search_input = st.sidebar.text_input(
        "Stock name or symbol",
        placeholder="Type 2+ chars (e.g. Tata, INFY…)",
        key="live_search",
    )

    searched_ticker = None
    if len(search_input.strip()) >= 2:
        q = search_input.strip()
        if exchange == "NSE":
            results = search_nse_stocks(q)
            opts = {
                f"{r.get('symbol_info', r.get('name', r.get('symbol', '')))} "
                f"({r.get('symbol', '')})": r.get("symbol", "") + ".NS"
                for r in results if r.get("symbol")
            }
        else:
            results = search_bse_stocks(q)
            opts = {
                f"{r.get('name', r.get('symbol', ''))} ({r.get('symbol', '')})": r.get("symbol", "") + ".BO"
                for r in results if r.get("symbol")
            }

        if opts:
            choice = st.sidebar.selectbox(
                f"{exchange} results for '{q}'",
                ["-- Select a stock --"] + list(opts.keys()),
                key="search_pick",
            )
            if choice != "-- Select a stock --":
                searched_ticker = opts[choice]
                st.sidebar.caption(f"Selected: **{searched_ticker}**")
        elif search_input:
            st.sidebar.caption("No results found. Try a different term.")

    st.sidebar.markdown("---")

    categories = st.sidebar.multiselect(
        "Cap Category",
        ["Large Cap", "Mid Cap", "Small Cap"],
        default=["Large Cap", "Mid Cap", "Small Cap"],
    )

    ticker_pool = {}
    if "Large Cap" in categories:
        ticker_pool.update(NIFTY50_TICKERS)
    if "Mid Cap" in categories:
        ticker_pool.update(MIDCAP_TICKERS)
    if "Small Cap" in categories:
        ticker_pool.update(SMALLCAP_TICKERS)

    options = [f"{v} ({k})" for k, v in ticker_pool.items()]
    selected_labels = st.sidebar.multiselect(
        "Stocks to include (leave blank = all)",
        options,
        default=[],
        placeholder="All stocks in selected categories",
    )

    if selected_labels:
        label_to_ticker = {f"{v} ({k})": k for k, v in ticker_pool.items()}
        selected_tickers = tuple(label_to_ticker[l] for l in selected_labels)
    else:
        selected_tickers = tuple(ticker_pool.keys())

    st.sidebar.markdown("---")

    # ── Quick Filters ──────────────────────────────────────────────────────────
    st.sidebar.markdown("### ⚡ Quick Filters")
    quick_filter = st.sidebar.radio(
        "Show only:",
        ["All Stocks", "Only BUY", "Only Oversold (RSI < 30)", "High Volume (>1.5× avg)"],
        index=0,
        key="quick_filter",
        help="Filters all tabs to matching stocks instantly",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption(f"📦 {len(selected_tickers)} stocks selected")
    st.sidebar.caption(f"🕐 Data cached 1 hr · refreshes automatically")
    if st.sidebar.button("🔄 Refresh Data Now"):
        st.cache_data.clear()
        st.rerun()

    return selected_tickers, searched_ticker, quick_filter


# ─── Market Overview Cards ────────────────────────────────────────────────────
def render_market_overview(idx):
    # Market status badge
    market_open = is_market_open()
    badge_bg   = "#00c853" if market_open else "#e53935"
    badge_text = "🟢 MARKET OPEN" if market_open else "🔴 MARKET CLOSED"
    st.markdown(
        f"<div style='display:flex;align-items:center;gap:14px;margin-bottom:6px'>"
        f"<span style='font-size:1.05em;font-weight:700;color:#1a1a2e'>🌐 Market Overview</span>"
        f"<span style='background:{badge_bg};color:#fff;padding:3px 13px;"
        f"border-radius:20px;font-size:0.76em;font-weight:700;letter-spacing:0.4px'>"
        f"{badge_text}</span></div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)

    def index_card(col, label, data, key, invert_delta=False):
        if key in data:
            d = data[key]
            arrow = "▲" if d["change"] >= 0 else "▼"
            fmt = f"{d['close']:.2f}" if key == "vix" else f"{d['close']:,.2f}"
            col.metric(
                label=label,
                value=fmt,
                delta=f"{arrow} {abs(d['change']):.2f}  ({d['pct']:+.2f}%)",
                delta_color=("inverse" if d["change"] >= 0 else "normal") if invert_delta
                             else ("normal" if d["change"] >= 0 else "inverse"),
            )
        else:
            col.metric(label, "N/A", "–")

    index_card(c1, "NIFTY 50",   idx, "nifty")
    index_card(c2, "SENSEX",     idx, "sensex")
    index_card(c3, "BANK NIFTY", idx, "banknifty")
    index_card(c4, "India VIX",  idx, "vix", invert_delta=True)  # VIX up = bad


# ─── Tab 1: Market Overview ──────────────────────────────────────────────────
def _gainer_loser_html(rows_df: pd.DataFrame, is_gainer: bool) -> str:
    """Render a styled HTML table for gainers or losers."""
    accent = "#00c853" if is_gainer else "#e53935"
    icon   = "▲" if is_gainer else "▼"
    title  = "🟢 Top 10 Gainers" if is_gainer else "🔴 Top 10 Losers"
    html   = (
        f"<div style='background:#fff;border-radius:12px;border:1px solid #e8edf5;"
        f"overflow:hidden;margin-bottom:4px'>"
        f"<div style='background:{accent}18;padding:10px 16px;font-weight:700;"
        f"font-size:0.95em;border-bottom:1px solid #e8edf5'>{title}</div>"
        f"<table style='width:100%;border-collapse:collapse;font-size:0.82em'>"
        f"<thead><tr style='background:#f7f9ff;color:#555'>"
        f"<th style='padding:7px 12px;text-align:left'>Name</th>"
        f"<th style='padding:7px 8px;text-align:center'>Cap</th>"
        f"<th style='padding:7px 8px;text-align:right'>Close</th>"
        f"<th style='padding:7px 8px;text-align:right'>% Chg</th>"
        f"<th style='padding:7px 8px;text-align:center'>RSI</th>"
        f"<th style='padding:7px 8px;text-align:center'>Signal</th>"
        f"</tr></thead><tbody>"
    )
    rsi_col  = "RSI"  if "RSI"  in rows_df.columns else None
    rec_col  = "Recommendation" if "Recommendation" in rows_df.columns else None
    for _, r in rows_df.iterrows():
        pct   = r["% Change"]
        pct_c = "#00873a" if pct >= 0 else "#c62828"
        bar_w = min(abs(pct) * 8, 100)
        bar_c = "#00c85355" if pct >= 0 else "#e5393555"

        rsi_val = r.get(rsi_col, np.nan) if rsi_col else np.nan
        rsi_str = f"{rsi_val:.0f}" if not pd.isna(rsi_val) else "–"
        rsi_bg  = ("#ffd6d6" if rsi_val > 70 else ("#d4f0dc" if rsi_val < 30 else "transparent")) \
                  if not pd.isna(rsi_val) else "transparent"

        rec_val = r.get(rec_col, "") if rec_col else ""
        rec_c   = _CMAP.get(rec_val, "#888") if rec_val else "#888"

        # Category badge color
        cat = r.get("Category", "")
        cat_c = {"Large Cap": "#4c9be8", "Mid Cap": "#f4a261", "Small Cap": "#2ec4b6"}.get(cat, "#aaa")

        html += (
            f"<tr style='border-bottom:1px solid #f0f0f0'>"
            f"<td style='padding:7px 12px;font-weight:600;max-width:160px;overflow:hidden;"
            f"white-space:nowrap;text-overflow:ellipsis'>{r['Name']}</td>"
            f"<td style='padding:7px 8px;text-align:center'>"
            f"<span style='background:{cat_c}22;color:{cat_c};border-radius:4px;"
            f"padding:2px 6px;font-size:0.78em;font-weight:600'>{cat.replace(' Cap','')}</span></td>"
            f"<td style='padding:7px 8px;text-align:right;font-weight:600'>₹{r['Close']:,.2f}</td>"
            f"<td style='padding:7px 8px;text-align:right'>"
            f"<span style='color:{pct_c};font-weight:700'>{icon} {abs(pct):.2f}%</span>"
            f"<div style='background:{bar_c};height:3px;border-radius:2px;width:{bar_w:.0f}%;margin-top:2px;margin-left:auto'></div>"
            f"</td>"
            f"<td style='padding:7px 8px;text-align:center;background:{rsi_bg};border-radius:4px'>"
            f"<span style='font-weight:600'>{rsi_str}</span></td>"
            f"<td style='padding:7px 8px;text-align:center'>"
            f"<span style='color:{rec_c};font-weight:700;font-size:0.8em'>{rec_val or '–'}</span></td>"
            f"</tr>"
        )
    html += "</tbody></table></div>"
    return html


def tab_overview(df: pd.DataFrame):
    if df.empty:
        st.warning("No stocks match the current filter.")
        return

    # ── Sector Treemap ─────────────────────────────────────────────────────────
    st.markdown("### 🗺️ Sector Performance Heatmap")
    df_tm = df.copy()
    df_tm["Sector"] = df_tm["Ticker"].map(SECTOR_MAP).fillna("Other")
    df_tm["AbsChg"] = df_tm["% Change"].abs().clip(lower=0.01)
    df_tm["Label"]  = df_tm["Name"].str[:18]

    fig_tm = px.treemap(
        df_tm,
        path=[px.Constant("Market"), "Sector", "Label"],
        values="AbsChg",
        color="% Change",
        color_continuous_scale=["#c62828", "#e57373", "#ffffff", "#81c784", "#1b5e20"],
        color_continuous_midpoint=0,
        hover_data={"% Change": ":.2f", "Close": ":,.2f", "Sector": True, "AbsChg": False},
        custom_data=["Name", "% Change", "Close", "Sector"],
    )
    fig_tm.update_traces(
        texttemplate="<b>%{label}</b><br>%{customdata[1]:.2f}%",
        hovertemplate="<b>%{customdata[0]}</b><br>Sector: %{customdata[3]}<br>"
                      "Change: %{customdata[1]:+.2f}%<br>Close: ₹%{customdata[2]:,.2f}<extra></extra>",
        textfont_size=12,
    )
    fig_tm.update_layout(
        height=420,
        margin=dict(t=30, l=0, r=0, b=0),
        coloraxis_colorbar=dict(title="% Change", ticksuffix="%"),
    )
    st.plotly_chart(fig_tm, use_container_width=True)

    # ── Top Gainers & Losers ───────────────────────────────────────────────────
    st.markdown("### 📋 Top Gainers & Losers")
    cols_needed = ["Name", "Category", "Ticker", "Close", "% Change", "RSI", "Recommendation"]
    avail = [c for c in cols_needed if c in df.columns]
    gainers = df.nlargest(10,  "% Change")[avail].reset_index(drop=True)
    losers  = df.nsmallest(10, "% Change")[avail].reset_index(drop=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(_gainer_loser_html(gainers, is_gainer=True), unsafe_allow_html=True)
    with col2:
        st.markdown(_gainer_loser_html(losers,  is_gainer=False), unsafe_allow_html=True)

    # ── Category-wise Performance ─────────────────────────────────────────────
    st.markdown("### 📊 Category-wise Performance")
    cat_perf = df.groupby("Category")["% Change"].mean().reset_index()
    cat_perf.columns = ["Category", "Avg % Change"]
    fig = px.bar(
        cat_perf, x="Category", y="Avg % Change",
        color="Avg % Change", color_continuous_scale=["#c62828", "#aaa", "#00c853"],
        text="Avg % Change", title="Average % Change by Market Cap Category",
    )
    fig.update_traces(texttemplate="%{text:.2f}%", textposition="outside")
    fig.update_layout(showlegend=False, height=320)
    st.plotly_chart(fig, use_container_width=True)

    # ── 52-Week Position Scatter ───────────────────────────────────────────────
    st.markdown("### 📍 52-Week Position Heatmap")
    df_52 = df[["Name", "Category", "52W Position", "% Change"]].dropna()
    fig2 = px.scatter(
        df_52, x="52W Position", y="% Change", color="Category",
        hover_name="Name", title="52-Week Position vs Daily % Change",
        labels={"52W Position": "Position in 52W Range (%)", "% Change": "Daily % Change"},
        color_discrete_map={"Large Cap": "#4c9be8", "Mid Cap": "#f4a261", "Small Cap": "#2ec4b6"},
        size_max=12,
    )
    fig2.add_vline(x=80, line_dash="dash", line_color="red",   annotation_text="Near 52W High")
    fig2.add_vline(x=20, line_dash="dash", line_color="green", annotation_text="Near 52W Low")
    fig2.update_layout(height=400)
    st.plotly_chart(fig2, use_container_width=True)


# ─── Tab 2: Technical Indicators ─────────────────────────────────────────────
def tab_technical(df: pd.DataFrame):
    st.markdown("### RSI Distribution")
    col1, col2 = st.columns(2)

    with col1:
        # RSI histogram
        rsi_df = df[["Name", "RSI", "Category"]].dropna()
        fig = px.histogram(rsi_df, x="RSI", color="Category", nbins=30,
                           title="RSI Distribution", opacity=0.75,
                           color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"})
        fig.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig.add_vline(x=30, line_dash="dash", line_color="green", annotation_text="Oversold")
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # RSI zones pie
        zones = df["RSI Signal"].value_counts().reset_index()
        zones.columns = ["Zone", "Count"]
        fig2 = px.pie(zones, values="Count", names="Zone",
                      color="Zone", title="RSI Zone Breakdown",
                      color_discrete_map={"Overbought":"#ff6b6b","Oversold":"#51cf66","Neutral":"#aaa","N/A":"#ddd"})
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    # MACD signals
    st.markdown("### MACD Signals")
    macd_df = df[["Name", "Category", "MACD", "MACD Signal", "% Change"]].dropna()
    fig3 = px.scatter(
        macd_df, x="MACD", y="% Change", color="MACD Signal",
        hover_name="Name", symbol="Category",
        color_discrete_map={"Bullish": "#00c853", "Bearish": "#ff1744"},
        title="MACD Value vs Daily % Change",
    )
    fig3.add_vline(x=0, line_dash="dash", line_color="gray")
    fig3.update_layout(height=400)
    st.plotly_chart(fig3, use_container_width=True)

    # ADX trend strength
    st.markdown("### ADX Trend Strength")
    col3, col4 = st.columns(2)
    with col3:
        adx_df = df[["Name", "ADX", "Category", "% Change"]].dropna().nlargest(20, "ADX")
        fig4 = px.bar(
            adx_df, x="ADX", y="Name", orientation="h",
            color="Category", title="Top 20 Stocks by ADX (Trend Strength)",
            color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"},
        )
        fig4.add_vline(x=25, line_dash="dash", line_color="orange", annotation_text="Strong Trend")
        fig4.update_layout(height=550, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)

    with col4:
        st.markdown("#### Stochastic Signal Breakdown")
        df["Stoch Zone"] = df["Stoch K"].apply(
            lambda v: "Overbought" if (not pd.isna(v) and v > 80)
                      else ("Oversold" if (not pd.isna(v) and v < 20) else "Neutral")
        )
        stoch_pie = df["Stoch Zone"].value_counts().reset_index()
        stoch_pie.columns = ["Zone", "Count"]
        fig5 = px.pie(stoch_pie, values="Count", names="Zone",
                      color="Zone", title="Stochastic Zone Breakdown",
                      color_discrete_map={"Overbought":"#ff6b6b","Oversold":"#51cf66","Neutral":"#aaa"})
        st.plotly_chart(fig5, use_container_width=True)

    # Bollinger Band position
    st.markdown("### Bollinger Band Position")
    df_bb = df[["Name", "Close", "BB Upper", "BB Lower", "BB Mid", "Category"]].dropna()
    df_bb["BB Position"] = (df_bb["Close"] - df_bb["BB Lower"]) / (df_bb["BB Upper"] - df_bb["BB Lower"]) * 100
    fig6 = px.histogram(df_bb, x="BB Position", color="Category", nbins=20, opacity=0.75,
                        title="Bollinger Band % Position (0=Lower, 100=Upper)",
                        color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"})
    fig6.add_vline(x=80, line_dash="dash", line_color="red")
    fig6.add_vline(x=20, line_dash="dash", line_color="green")
    fig6.update_layout(height=350)
    st.plotly_chart(fig6, use_container_width=True)


# ─── Tab 3: Fundamentals ─────────────────────────────────────────────────────
def tab_fundamentals(df: pd.DataFrame):
    st.markdown("### Fundamental Metrics")

    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    pe_df = df["PE Ratio"].dropna()
    col1.metric("Avg PE Ratio", f"{pe_df.mean():.1f}" if not pe_df.empty else "N/A",
                f"Median: {pe_df.median():.1f}" if not pe_df.empty else "")
    pb_df = df["PB Ratio"].dropna()
    col2.metric("Avg PB Ratio", f"{pb_df.mean():.2f}" if not pb_df.empty else "N/A",
                f"Median: {pb_df.median():.2f}" if not pb_df.empty else "")
    roe_df = df["ROE"].dropna()
    col3.metric("Avg ROE", f"{roe_df.mean()*100:.1f}%" if not roe_df.empty else "N/A",
                f"Median: {roe_df.median()*100:.1f}%" if not roe_df.empty else "")
    div_df = df["Div Yield"].dropna()
    col4.metric("Avg Div Yield", f"{div_df.mean()*100:.2f}%" if not div_df.empty else "N/A",
                f"Median: {div_df.median()*100:.2f}%" if not div_df.empty else "")

    st.markdown("---")

    # PE vs PB scatter
    col5, col6 = st.columns(2)
    with col5:
        scatter_df = df.dropna(subset=["PE Ratio", "PB Ratio"]).copy()
        # Ensure marker size is always positive
        scatter_df["size_plot"] = scatter_df["Beta"].abs()
        fig1 = px.scatter(
            scatter_df,
            x="PE Ratio", y="PB Ratio", color="Category",
            hover_name="Name", title="PE Ratio vs PB Ratio",
            size="size_plot", size_max=20,
            color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"},
        )
        fig1.update_layout(height=400)
        st.plotly_chart(fig1, use_container_width=True)

    with col6:
        de_df = df.dropna(subset=["D/E Ratio"]).nsmallest(20, "D/E Ratio")
        fig2 = px.bar(
            de_df.nlargest(20, "D/E Ratio"), x="D/E Ratio", y="Name",
            orientation="h", color="Category",
            title="Top 20 Stocks by Debt/Equity Ratio",
            color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"},
        )
        fig2.update_layout(height=400, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    # Dividend yield
    st.markdown("### Dividend Yield & ROE")
    col7, col8 = st.columns(2)
    with col7:
        div_top = df.dropna(subset=["Div Yield"]).nlargest(15, "Div Yield").copy()
        div_top["Div Yield %"] = (div_top["Div Yield"] * 100).round(2)
        fig3 = px.bar(div_top, x="Div Yield %", y="Name", orientation="h",
                      color="Category", title="Top 15 Dividend Yielding Stocks (%)",
                      color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"})
        fig3.update_layout(height=450, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig3, use_container_width=True)

    with col8:
        roe_top = df.dropna(subset=["ROE"]).nlargest(15, "ROE").copy()
        roe_top["ROE %"] = (roe_top["ROE"] * 100).round(2)
        fig4 = px.bar(roe_top, x="ROE %", y="Name", orientation="h",
                      color="Category", title="Top 15 Stocks by ROE (%)",
                      color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"})
        fig4.update_layout(height=450, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig4, use_container_width=True)

    # Full fundamental table
    st.markdown("### Fundamental Data Table")
    fund_cols = ["Name", "Category", "Close", "% Change", "Market Cap",
                 "PE Ratio", "EPS", "PB Ratio", "ROE", "Div Yield",
                 "D/E Ratio", "Beta", "52W High", "52W Low", "52W Position"]
    fund_df = df[fund_cols].copy()
    fund_df["Market Cap"] = fund_df["Market Cap"].apply(fmt_crore)
    fund_df["ROE"]       = fund_df["ROE"].apply(lambda x: f"{x*100:.1f}%" if not pd.isna(x) else "N/A")
    fund_df["Div Yield"] = fund_df["Div Yield"].apply(lambda x: f"{x*100:.2f}%" if not pd.isna(x) else "N/A")
    st.dataframe(
        fund_df.style.applymap(color_pct, subset=["% Change"])
               .format({"Close": "₹{:.2f}", "% Change": "{:+.2f}%",
                        "PE Ratio": "{:.1f}", "PB Ratio": "{:.2f}",
                        "Beta": "{:.2f}", "52W Position": "{:.1f}%"},
                       na_rep="N/A"),
        use_container_width=True, hide_index=True,
    )


# ─── Tab 4: Volume Analysis ──────────────────────────────────────────────────
def tab_volume(df: pd.DataFrame):
    st.markdown("### Volume Analysis")

    # High volume movers
    st.markdown("#### Unusual Volume (Vol Ratio > 1.5×)")
    high_vol = df[df["Vol Ratio"] >= 1.5].sort_values("Vol Ratio", ascending=False).head(20)
    if high_vol.empty:
        st.info("No stocks with unusual volume found.")
    else:
        fig1 = px.bar(
            high_vol, x="Name", y="Vol Ratio", color="% Change",
            color_continuous_scale=["#ff1744", "#aaa", "#00c853"],
            title="Top 20 Unusual Volume Stocks (Volume / Avg Volume)",
            hover_data=["Volume", "Avg Volume", "% Change"],
        )
        fig1.add_hline(y=1, line_dash="dash", line_color="gray", annotation_text="Normal")
        fig1.update_layout(height=400, xaxis_tickangle=-45)
        st.plotly_chart(fig1, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### MFI Distribution")
        mfi_df = df[["Name", "MFI", "Category"]].dropna()
        fig2 = px.histogram(mfi_df, x="MFI", color="Category", nbins=20, opacity=0.8,
                            title="Money Flow Index Distribution",
                            color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"})
        fig2.add_vline(x=80, line_dash="dash", line_color="red", annotation_text="Overbought")
        fig2.add_vline(x=20, line_dash="dash", line_color="green", annotation_text="Oversold")
        fig2.update_layout(height=350)
        st.plotly_chart(fig2, use_container_width=True)

    with col2:
        st.markdown("#### OBV Trend Breakdown")
        obv_pie = df["OBV Trend"].value_counts().reset_index()
        obv_pie.columns = ["Trend", "Count"]
        fig3 = px.pie(obv_pie, values="Count", names="Trend", title="OBV Trend Breakdown",
                      color="Trend",
                      color_discrete_map={"Rising":"#00c853","Falling":"#ff1744"})
        st.plotly_chart(fig3, use_container_width=True)

    # VWAP vs Close
    st.markdown("#### VWAP vs Close Price")
    vwap_df = df[["Name", "Close", "VWAP", "Category", "% Change"]].dropna()
    vwap_df["Above VWAP"] = vwap_df["Close"] >= vwap_df["VWAP"]
    vwap_df["VWAP Delta %"] = ((vwap_df["Close"] - vwap_df["VWAP"]) / vwap_df["VWAP"] * 100).round(2)
    fig4 = px.scatter(
        vwap_df, x="VWAP Delta %", y="% Change",
        color="Above VWAP", hover_name="Name",
        title="VWAP Delta % vs Daily % Change",
        color_discrete_map={True: "#00c853", False: "#ff1744"},
        labels={"VWAP Delta %": "Close vs VWAP (%)", "Above VWAP": "Above VWAP"},
    )
    fig4.add_vline(x=0, line_dash="dash", line_color="gray")
    fig4.update_layout(height=400)
    st.plotly_chart(fig4, use_container_width=True)


# ─── Tab 5: Levels & Signals ─────────────────────────────────────────────────
def tab_levels(df: pd.DataFrame):
    st.markdown("### Support / Resistance & Action Levels")

    # Risk/Reward scatter
    st.markdown("#### Risk-Reward Overview")
    df_rr = df[["Name", "Category", "Close", "Stop Loss", "Target 1", "Target 2"]].copy()
    df_rr["Risk"]    = (df_rr["Close"] - df_rr["Stop Loss"]).round(2)
    df_rr["Reward"]  = (df_rr["Target 1"] - df_rr["Close"]).round(2)
    df_rr["R:R"]     = (df_rr["Reward"] / df_rr["Risk"].replace(0, np.nan)).round(2)
    df_rr = df_rr.dropna(subset=["R:R"])
    good_rr = df_rr[df_rr["R:R"] >= 1.5].nlargest(20, "R:R")

    if not good_rr.empty:
        fig1 = px.bar(good_rr, x="R:R", y="Name", orientation="h",
                      color="Category", title="Top 20 Stocks by Risk:Reward Ratio (Target 1)",
                      color_discrete_map={"Large Cap":"#4c9be8","Mid Cap":"#f4a261","Small Cap":"#2ec4b6"})
        fig1.add_vline(x=2, line_dash="dash", line_color="green", annotation_text="R:R 1:2")
        fig1.update_layout(height=500, yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No stocks with R:R >= 1.5 found.")

    # Fibonacci levels table
    st.markdown("#### Fibonacci & Pivot Levels")
    lev_cols = ["Name", "Category", "Close", "Pivot", "R1", "S1",
                "Fib 38.2", "Fib 50", "Fib 61.8",
                "Stop Loss", "Target 1", "Target 2"]
    st.dataframe(
        df[lev_cols].dropna().style.format({c: "₹{:.2f}" for c in lev_cols if c not in ["Name","Category"]}),
        use_container_width=True, hide_index=True,
    )


# ─── Tab 6: Raw Data ─────────────────────────────────────────────────────────
def tab_rawdata(df: pd.DataFrame):
    st.markdown("### Complete Data Table")
    show_cols = ["Name", "Category", "Close", "% Change",
                 "RSI", "RSI Signal", "MACD Signal", "ADX", "ADX Signal",
                 "Stoch K", "Williams %R", "MFI", "Vol Ratio", "OBV Trend",
                 "PE Ratio", "PB Ratio", "ROE", "Beta", "52W Position"]
    st.dataframe(
        df[show_cols].style
          .applymap(color_pct, subset=["% Change"])
          .applymap(color_rsi, subset=["RSI"])
          .format({"Close":"₹{:.2f}", "% Change":"{:+.2f}%",
                   "RSI":"{:.1f}", "ADX":"{:.1f}",
                   "Stoch K":"{:.1f}", "Williams %R":"{:.1f}",
                   "MFI":"{:.1f}", "Vol Ratio":"{:.2f}x",
                   "PE Ratio":"{:.1f}", "PB Ratio":"{:.2f}",
                   "52W Position":"{:.1f}%"}, na_rep="N/A"),
        use_container_width=True, hide_index=True,
    )

    # Download button
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download Full Data as CSV",
        data=csv,
        file_name=f"stock_analysis_{datetime.today().strftime('%Y%m%d')}.csv",
        mime="text/csv",
    )


# ─── EMA Chart ───────────────────────────────────────────────────────────────
def render_ema_chart(hist: pd.DataFrame, name: str) -> go.Figure:
    from plotly.subplots import make_subplots
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        row_heights=[0.60, 0.20, 0.20],
        vertical_spacing=0.03,
        subplot_titles=(f"{name}  —  Price · EMAs · Bollinger Bands", "Volume", "RSI (14)"),
    )
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=hist.index, open=hist["Open"], high=hist["High"],
        low=hist["Low"], close=hist["Close"], name="Price",
        increasing_line_color="#00c853", decreasing_line_color="#ff1744",
        showlegend=False,
    ), row=1, col=1)
    # EMAs / SMAs
    for col, color, lbl in [
        ("EMA_12", "#f9a825", "EMA 12"),
        ("EMA_26", "#e91e63", "EMA 26"),
        ("SMA_50", "#29b6f6", "SMA 50"),
        ("SMA_200", "#ab47bc", "SMA 200"),
    ]:
        if col in hist.columns:
            fig.add_trace(go.Scatter(x=hist.index, y=hist[col], mode="lines",
                name=lbl, line=dict(color=color, width=1.5)), row=1, col=1)
    # Bollinger Bands
    if "BB_Upper" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index, y=hist["BB_Upper"], mode="lines",
            name="BB Upper", line=dict(color="#78909c", width=1, dash="dot")), row=1, col=1)
        fig.add_trace(go.Scatter(x=hist.index, y=hist["BB_Lower"], mode="lines",
            name="BB Lower", fill="tonexty", fillcolor="rgba(120,144,156,0.12)",
            line=dict(color="#78909c", width=1, dash="dot")), row=1, col=1)
    # Volume bars (green/red)
    colors = ["#00c853" if c >= o else "#ff1744"
              for c, o in zip(hist["Close"], hist["Open"])]
    fig.add_trace(go.Bar(x=hist.index, y=hist["Volume"], name="Volume",
        marker_color=colors, showlegend=False), row=2, col=1)
    # RSI
    if "RSI" in hist.columns:
        fig.add_trace(go.Scatter(x=hist.index, y=hist["RSI"], mode="lines",
            name="RSI", line=dict(color="#ff9800", width=1.5), showlegend=False), row=3, col=1)
        fig.add_hline(y=70, line_dash="dash", line_color="rgba(255,107,107,0.7)",
                      annotation_text="OB 70", row=3, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="rgba(81,207,102,0.7)",
                      annotation_text="OS 30", row=3, col=1)
    fig.update_layout(
        height=560, xaxis_rangeslider_visible=False,
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", font_color="#1a1a2e",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
                    bgcolor="rgba(255,255,255,0.8)", bordercolor="#ddd", borderwidth=1),
        margin=dict(l=0, r=0, t=40, b=0),
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eeeeee", zeroline=False, linecolor="#cccccc")
    fig.update_yaxes(showgrid=True, gridcolor="#eeeeee", zeroline=False, linecolor="#cccccc")
    return fig


# ─── Stock Detail Panel (for NSE/BSE search result) ─────────────────────────
def _v(val, fmt=".2f", suffix=""):
    """Format a value or return N/A."""
    if pd.isna(val) if not isinstance(val, str) else val in ("N/A", ""):
        return "**N/A**"
    return f"**{val:{fmt}}{suffix}**"


def _price(val):
    return _v(val, ".2f", "")  # plain number; caller adds ₹


def render_stock_detail(ticker: str):
    """Full detail panel for a single stock picked from NSE/BSE search."""

    # ── Floating home button — position:fixed, always visible while scrolling ───
    # onclick navigates to the root URL which gives a clean fresh session.
    # (Streamlit ignores programmatic .click() on its buttons due to isTrusted=false,
    #  so a lightweight page reload is the most reliable cross-browser approach.)
    st.markdown(
        """
        <style>
        /* ─── Floating back-to-dashboard pill ─────────────────────────────── */
        .st-float-home {
            position: fixed;
            bottom: 32px;
            right: 32px;
            z-index: 999999;
            background: linear-gradient(135deg, #1a73e8 0%, #1255cc 100%);
            color: #fff !important;
            border: none;
            border-radius: 50px;
            padding: 13px 22px 13px 18px;
            font-size: 14px;
            font-weight: 700;
            cursor: pointer;
            box-shadow: 0 4px 20px rgba(26,115,232,0.50), 0 2px 8px rgba(0,0,0,0.18);
            transition: transform 0.18s ease, box-shadow 0.18s ease;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            white-space: nowrap;
            outline: none;
            user-select: none;
            text-decoration: none !important;
        }
        .st-float-home:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(26,115,232,0.65), 0 4px 12px rgba(0,0,0,0.20);
        }
        .st-float-home:active {
            transform: translateY(-1px);
            box-shadow: 0 3px 14px rgba(26,115,232,0.45);
        }
        </style>

        <a href="/" target="_self" class="st-float-home" title="Back to Dashboard">
            🏠&nbsp;&nbsp;Back to Dashboard
        </a>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.spinner(f"Fetching data for {ticker}…"):
        df   = fetch_stocks((ticker,))
        hist = fetch_stock_history(ticker)

    if df.empty:
        st.error(f"Could not fetch data for **{ticker}**. It may be delisted or unavailable.")
        return

    row   = df.iloc[0]
    exch  = "BSE" if ticker.endswith(".BO") else "NSE"
    chg_c = "#00c853" if row["% Change"] >= 0 else "#ff1744"
    arrow = "▲" if row["% Change"] >= 0 else "▼"

    # ── Header ──────────────────────────────────────────────────────────────
    st.markdown(
        f"<h3 style='margin-bottom:2px'>{row['Name']} "
        f"<span style='font-size:0.7em;color:#888'>"
        f"{ticker} · {exch} · {row['Category']}</span></h3>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<span style='font-size:1.7em;font-weight:700'>₹{row['Close']:.2f}</span>"
        f"&nbsp;&nbsp;"
        f"<span style='color:{chg_c};font-size:1.1em'>{arrow} "
        f"{abs(row['% Change']):.2f}%</span>"
        f"&nbsp;&nbsp;<span style='color:#888;font-size:0.9em'>"
        f"Prev Close ₹{row['Prev Close']:.2f}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # ── Recommendation Badge ─────────────────────────────────────────────────
    rec_data  = compute_recommendation(row)
    rec_label = rec_data["Recommendation"]
    rec_color = rec_data["Rec Color"]
    r_score   = rec_data["Score"]
    r_pct     = rec_data["Score %"]
    r_bull    = rec_data["Bull Signals"]
    r_bear    = rec_data["Bear Signals"]
    r_sigs    = rec_data["Signal Details"]

    st.markdown(
        f"<div style='display:flex;align-items:center;gap:20px;padding:14px 18px;"
        f"background:#f8f9fa;border-radius:10px;"
        f"border-left:6px solid {rec_color};margin-bottom:12px;"
        f"box-shadow:0 1px 4px rgba(0,0,0,0.08)'>"
        f"<span style='font-size:2em;font-weight:800;color:{rec_color};letter-spacing:1px'>"
        f"{rec_label}</span>"
        f"<div style='color:#555;font-size:0.92em;line-height:1.8'>"
        f"Score: <strong style='color:#1a1a2e'>{r_score:+d}</strong>&nbsp;&nbsp;"
        f"🟢 Bull signals: <strong style='color:#1e8a3e'>{r_bull}</strong>&nbsp;&nbsp;"
        f"🔴 Bear signals: <strong style='color:#d32f2f'>{r_bear}</strong>&nbsp;&nbsp;"
        f"Confidence: <strong style='color:#1a1a2e'>{r_pct}%</strong>"
        f"</div></div>",
        unsafe_allow_html=True,
    )

    with st.expander("📋 Signal Breakdown", expanded=False):
        _SC = {"bullish": "#1e8a3e", "bearish": "#d32f2f", "neutral": "#666"}
        _IC = {"bullish": "🟢", "bearish": "🔴", "neutral": "⚪"}
        for lbl, sent, detail in r_sigs:
            sc = _SC.get(sent, "#666")
            ic = _IC.get(sent, "⚪")
            st.markdown(
                f"<div style='padding:6px 0;border-bottom:1px solid #e8e8e8'>"
                f"{ic} <strong style='color:{sc}'>{lbl}</strong>"
                f"<span style='color:#666;margin-left:8px;font-size:0.88em'>— {detail}</span></div>",
                unsafe_allow_html=True,
            )

    # ── EMA Chart ───────────────────────────────────────────────────────────
    if not hist.empty:
        st.plotly_chart(render_ema_chart(hist, row["Name"]), use_container_width=True)
    else:
        st.warning("Chart data unavailable.")

    st.markdown("---")

    # ── Section Row 1: 4 metric columns ─────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown("#### 🏦 Fundamentals")
        st.markdown(f"- **Market Cap:** {fmt_crore(row['Market Cap'])}")
        pe = row['PE Ratio']
        st.markdown(f"- **P/E Ratio:** {pe:.1f}" if not pd.isna(pe) else "- **P/E Ratio:** N/A")
        eps = row['EPS']
        st.markdown(f"- **EPS:** ₹{eps:.2f}" if not pd.isna(eps) else "- **EPS:** N/A")
        pb = row['PB Ratio']
        st.markdown(f"- **P/B Ratio:** {pb:.2f}" if not pd.isna(pb) else "- **P/B Ratio:** N/A")
        roe = row['ROE']
        st.markdown(f"- **ROE:** {roe*100:.1f}%" if not pd.isna(roe) else "- **ROE:** N/A")
        dy = row['Div Yield']
        st.markdown(f"- **Div Yield:** {dy*100:.2f}%" if not pd.isna(dy) else "- **Div Yield:** N/A")
        de = row['D/E Ratio']
        st.markdown(f"- **Debt/Equity:** {de:.2f}" if not pd.isna(de) else "- **Debt/Equity:** N/A")
        beta = row['Beta']
        st.markdown(f"- **Beta:** {beta:.2f}" if not pd.isna(beta) else "- **Beta:** N/A")
        w52h, w52l = row['52W High'], row['52W Low']
        st.markdown(f"- **52W High:** ₹{w52h:.2f}" if not pd.isna(w52h) else "- **52W High:** N/A")
        st.markdown(f"- **52W Low:** ₹{w52l:.2f}" if not pd.isna(w52l) else "- **52W Low:** N/A")
        pos52 = row.get('52W Position', np.nan)
        st.markdown(f"- **52W Position:** {pos52:.1f}%" if not pd.isna(pos52) else "- **52W Position:** N/A")

    with c2:
        st.markdown("#### ⚙️ Technical Core")
        rsi = row["RSI"]
        rsi_c = "🔴" if rsi > 70 else ("🟢" if rsi < 30 else "🟡")
        st.markdown(f"- **RSI (14):** {rsi:.1f} {rsi_c} *{row['RSI Signal']}*" if not pd.isna(rsi) else "- **RSI:** N/A")
        macd, macds, macdh = row["MACD"], safe_val(row.get("MACD Signal") if False else np.nan), safe_val(row.get("MACD_Hist") if False else np.nan)
        st.markdown(f"- **MACD:** {macd:.3f}  →  {row['MACD Signal']}" if not pd.isna(macd) else "- **MACD:** N/A")
        sma50 = row["SMA 50"]
        st.markdown(f"- **50-DMA:** ₹{sma50:.2f}  ({'Above' if row['Close']>sma50 else 'Below'})" if not pd.isna(sma50) else "- **50-DMA:** N/A")
        sma200 = row["SMA 200"]
        st.markdown(f"- **200-DMA:** ₹{sma200:.2f}  ({'Above' if row['Close']>sma200 else 'Below'})" if not pd.isna(sma200) else "- **200-DMA:** N/A")
        e12 = row["EMA 12"]
        st.markdown(f"- **EMA 12:** ₹{e12:.2f}" if not pd.isna(e12) else "- **EMA 12:** N/A")
        e26 = row["EMA 26"]
        st.markdown(f"- **EMA 26:** ₹{e26:.2f}" if not pd.isna(e26) else "- **EMA 26:** N/A")
        bbu, bbm, bbl = row["BB Upper"], row["BB Mid"], row["BB Lower"]
        st.markdown(f"- **BB Upper:** ₹{bbu:.2f}" if not pd.isna(bbu) else "- **BB Upper:** N/A")
        st.markdown(f"- **BB Mid:** ₹{bbm:.2f}" if not pd.isna(bbm) else "- **BB Mid:** N/A")
        st.markdown(f"- **BB Lower:** ₹{bbl:.2f}" if not pd.isna(bbl) else "- **BB Lower:** N/A")
        if not any(pd.isna(v) for v in [bbu, bbl, bbm]) and bbm > 0:
            bw = (bbu - bbl) / bbm * 100
            st.markdown(f"- **BB Width:** {bw:.1f}%")
        else:
            st.markdown("- **BB Width:** N/A")

    with c3:
        st.markdown("#### 📡 Advanced Oscillators")
        adx = row["ADX"]
        st.markdown(f"- **ADX (14):** {adx:.1f}  *{row['ADX Signal']} trend*" if not pd.isna(adx) else "- **ADX:** N/A")
        sk, sd = row["Stoch K"], row["Stoch D"]
        sk_lbl = "🔴 OB" if not pd.isna(sk) and sk > 80 else ("🟢 OS" if not pd.isna(sk) and sk < 20 else "")
        st.markdown(f"- **Stoch %K:** {sk:.1f} {sk_lbl}" if not pd.isna(sk) else "- **Stoch %K:** N/A")
        st.markdown(f"- **Stoch %D:** {sd:.1f}" if not pd.isna(sd) else "- **Stoch %D:** N/A")
        wr = row["Williams %R"]
        wr_lbl = "🔴 OB" if not pd.isna(wr) and wr > -20 else ("🟢 OS" if not pd.isna(wr) and wr < -80 else "")
        st.markdown(f"- **Williams %R:** {wr:.1f} {wr_lbl}" if not pd.isna(wr) else "- **Williams %R:** N/A")
        mfi = row["MFI"]
        mfi_lbl = "🔴 OB" if not pd.isna(mfi) and mfi > 80 else ("🟢 OS" if not pd.isna(mfi) and mfi < 20 else "")
        st.markdown(f"- **MFI (14):** {mfi:.1f} {mfi_lbl}" if not pd.isna(mfi) else "- **MFI:** N/A")
        atr = row["ATR"]
        st.markdown(f"- **ATR (14):** ₹{atr:.2f}" if not pd.isna(atr) else "- **ATR:** N/A")
        vwap = row["VWAP"]
        vwap_lbl = "Above VWAP" if not pd.isna(vwap) and row["Close"] >= vwap else "Below VWAP"
        st.markdown(f"- **VWAP:** ₹{vwap:.2f}  *({vwap_lbl})*" if not pd.isna(vwap) else "- **VWAP:** N/A")
        vr = row["Vol Ratio"]
        vr_lbl = " 🔥" if not pd.isna(vr) and vr >= 1.5 else ""
        st.markdown(f"- **Vol Ratio:** {vr:.2f}×{vr_lbl}" if not pd.isna(vr) else "- **Vol Ratio:** N/A")
        st.markdown(f"- **OBV Trend:** {row['OBV Trend']}")

    with c4:
        st.markdown("#### 📐 Fibonacci & Pivots")
        st.markdown(f"- **Fib 38.2%:** ₹{row['Fib 38.2']:.2f}")
        st.markdown(f"- **Fib 50.0%:** ₹{row['Fib 50']:.2f}")
        st.markdown(f"- **Fib 61.8%:** ₹{row['Fib 61.8']:.2f}")
        st.markdown("---")
        st.markdown(f"- **Pivot:** ₹{row['Pivot']:.2f}")
        st.markdown(f"- **R1:** ₹{row['R1']:.2f} &nbsp;|&nbsp; **R2:** ₹{row['R2']:.2f} &nbsp;|&nbsp; **R3:** ₹{row['R3']:.2f}", unsafe_allow_html=True)
        st.markdown(f"- **S1:** ₹{row['S1']:.2f} &nbsp;|&nbsp; **S2:** ₹{row['S2']:.2f} &nbsp;|&nbsp; **S3:** ₹{row['S3']:.2f}", unsafe_allow_html=True)

    st.markdown("---")

    # ── Section Row 2: Patterns ──────────────────────────────────────────────
    pc1, pc2 = st.columns(2)

    _SENTIMENT_COLOR = {"bullish": "#1e8a3e", "bearish": "#d32f2f", "neutral": "#888888"}

    with pc1:
        st.markdown("#### 🕯️ Candlestick Patterns")
        candle_pats = row.get("Candlestick Patterns", [])
        if isinstance(candle_pats, list) and candle_pats:
            for name_p, sentiment, desc in candle_pats:
                color = _SENTIMENT_COLOR.get(sentiment, "#adb5bd")
                st.markdown(
                    f"<div style='border-left:4px solid {color};padding:6px 10px;"
                    f"margin-bottom:6px;background:#f8f9fa;border-radius:4px;"
                    f"box-shadow:0 1px 3px rgba(0,0,0,0.06)'>"
                    f"<strong style='color:{color}'>{name_p}</strong><br>"
                    f"<span style='font-size:0.88em;color:#555'>{desc}</span></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No candlestick pattern data available.")

    with pc2:
        st.markdown("#### 📊 Chart Patterns")
        chart_pats = row.get("Chart Patterns", [])
        if isinstance(chart_pats, list) and chart_pats:
            for name_p, sentiment, desc in chart_pats:
                color = _SENTIMENT_COLOR.get(sentiment, "#adb5bd")
                st.markdown(
                    f"<div style='border-left:4px solid {color};padding:6px 10px;"
                    f"margin-bottom:6px;background:#f8f9fa;border-radius:4px;"
                    f"box-shadow:0 1px 3px rgba(0,0,0,0.06)'>"
                    f"<strong style='color:{color}'>{name_p}</strong><br>"
                    f"<span style='font-size:0.88em;color:#555'>{desc}</span></div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No chart pattern data available.")

    st.markdown("---")

    # ── Section Row 3: Actionable Levels ────────────────────────────────────
    st.markdown("#### 🎯 Actionable Levels")
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.metric("Entry Zone", row.get("Entry Zone", "N/A"))
        st.metric("Stop Loss",  f"₹{row['Stop Loss']:.2f}")
    with a2:
        st.metric("Target 1", f"₹{row['Target 1']:.2f}")
        st.metric("Target 2", f"₹{row['Target 2']:.2f}")
    with a3:
        st.markdown("**Key Support**")
        st.markdown(row.get("Key Support", "N/A"))
    with a4:
        st.markdown("**Key Resistance**")
        st.markdown(row.get("Key Resistance", "N/A"))

    st.markdown("---")

    # ── Section Row 4: Analyst & Broker Recommendations ─────────────────────
    st.markdown("#### 🏦 Analyst & Broker Recommendations")
    st.caption("Source: Yahoo Finance analyst data")

    with st.spinner("Fetching analyst data…"):
        analyst = fetch_analyst_data(ticker)

    if not analyst or not analyst.get("consensus"):
        st.info("No analyst coverage data available for this stock on Yahoo Finance.")
    else:
        cons    = analyst["consensus"]
        targets = analyst["targets"]
        upgrades= analyst["upgrades"]

        # ── Consensus + Price Target summary ─────────────────────────────
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        cons_key   = cons.get("key", "N/A")
        cons_color = _analyst_consensus_color(cons_key)
        cons_score = cons.get("score", np.nan)
        cons_count = cons.get("count", 0)

        b1.markdown(
            f"<div style='text-align:center;padding:10px 4px;"
            f"background:#f8f9fa;border-radius:8px;border:1px solid #ddd'>"
            f"<div style='font-size:0.78em;color:#888'>Consensus</div>"
            f"<div style='font-size:1.15em;font-weight:800;color:{cons_color}'>{cons_key or 'N/A'}</div>"
            f"<div style='font-size:0.75em;color:#aaa'>{cons_count} analysts</div></div>",
            unsafe_allow_html=True,
        )

        score_label = f"{cons_score:.1f} / 5.0" if not (isinstance(cons_score, float) and np.isnan(cons_score)) else "N/A"
        b2.metric("Score (1=SB, 5=SS)", score_label)

        curr = targets.get("current", np.nan)
        b3.metric("Current Price", f"₹{curr:.2f}" if not (isinstance(curr, float) and np.isnan(curr)) else "N/A")

        t_mean = targets.get("mean", np.nan)
        upside = targets.get("upside_mean", np.nan)
        upside_str = f"({upside:+.1f}%)" if not (isinstance(upside, float) and np.isnan(upside)) else ""
        b4.metric("Mean Target", f"₹{t_mean:.2f} {upside_str}" if not (isinstance(t_mean, float) and np.isnan(t_mean)) else "N/A",
                  delta=f"{upside:+.1f}% upside" if not (isinstance(upside, float) and np.isnan(upside)) else None,
                  delta_color="normal" if not (isinstance(upside, float) and np.isnan(upside)) and upside >= 0 else "inverse")

        t_high = targets.get("high", np.nan)
        b5.metric("High Target",  f"₹{t_high:.2f}"   if not (isinstance(t_high, float) and np.isnan(t_high)) else "N/A")

        t_low  = targets.get("low", np.nan)
        b6.metric("Low Target",   f"₹{t_low:.2f}"    if not (isinstance(t_low, float) and np.isnan(t_low)) else "N/A")

        # ── Upgrades / Downgrades table ───────────────────────────────────
        if upgrades:
            st.markdown("##### Recent Broker Actions")
            _ACTION_COLOR = {
                "up":   "#1e8a3e",
                "down": "#d32f2f",
                "init": "#1a73e8",
                "reit": "#888",
                "main": "#888",
            }
            for rec in upgrades:
                # normalise keys (yfinance column names vary slightly)
                date_val  = rec.get("GradeDate") or rec.get("Date") or rec.get("date") or ""
                firm      = rec.get("Firm", rec.get("firm", "Unknown"))
                to_grade  = rec.get("ToGrade", rec.get("To Grade", ""))
                from_grade= rec.get("FromGrade", rec.get("From Grade", ""))
                action    = str(rec.get("Action", rec.get("action", ""))).lower()

                a_color = _ACTION_COLOR.get(action[:4], "#888")
                action_label = {
                    "up":   "⬆ Upgrade", "down": "⬇ Downgrade",
                    "init": "✦ Initiated","reit": "↔ Reiterated",
                    "main": "↔ Maintained",
                }.get(action[:4], action.title())

                from_part = f" <span style='color:#aaa'>from {from_grade}</span>" if from_grade else ""
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:12px;"
                    f"padding:7px 12px;margin-bottom:5px;background:#f8f9fa;"
                    f"border-radius:6px;border-left:4px solid {a_color}'>"
                    f"<span style='color:#888;font-size:0.82em;min-width:90px'>{date_val}</span>"
                    f"<strong style='min-width:160px'>{firm}</strong>"
                    f"<span style='color:{a_color};font-weight:600'>{action_label}</span>"
                    f"<span style='margin-left:8px'>→ <strong>{to_grade}</strong>{from_part}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No recent broker upgrade/downgrade data available.")

    st.markdown("---")

    # ── Section Row 5: Company Overview & Financials ─────────────────────────
    st.markdown("#### 🏢 Company Overview & Financials")
    with st.spinner("Fetching company data…"):
        co = fetch_company_overview(ticker)

    if not co:
        st.info("Company overview data unavailable.")
    else:
        ov  = co.get("overview",   {})
        mgmt= co.get("management", [])
        fin = co.get("financials", {})
        divs= co.get("div_hist",   [])
        news= co.get("news",       [])

        # ── About ─────────────────────────────────────────────────────────
        with st.expander("📖 About the Company", expanded=True):
            desc = ov.get("description", "")
            if desc:
                # Show first 600 chars, rest hidden to keep it tidy
                st.markdown(desc[:700] + ("…" if len(desc) > 700 else ""))
            tag1, tag2, tag3, tag4 = st.columns(4)
            tag1.markdown(f"**Sector:** {ov.get('sector') or 'N/A'}")
            tag2.markdown(f"**Industry:** {ov.get('industry') or 'N/A'}")
            emp = ov.get("employees")
            tag3.markdown(f"**Employees:** {emp:,}" if emp else "**Employees:** N/A")
            web = ov.get("website", "")
            tag4.markdown(f"**Website:** [{web}]({web})" if web else "**Website:** N/A")

        # ── Financial Highlights ──────────────────────────────────────────
        with st.expander("💰 Financial Highlights", expanded=True):
            f1, f2, f3, f4 = st.columns(4)
            f1.metric("Revenue",         _crore(fin.get("revenue")))
            f1.metric("EBITDA",          _crore(fin.get("ebitda")))
            f2.metric("Free Cash Flow",  _crore(fin.get("free_cashflow")))
            f2.metric("Total Debt",      _crore(fin.get("total_debt")))
            f3.metric("Total Cash",      _crore(fin.get("total_cash")))
            de = fin.get("total_debt"); ca = fin.get("total_cash")
            net_debt = _crore(de - ca) if de and ca else "N/A"
            f3.metric("Net Debt",        net_debt)
            roa = fin.get("roa")
            f4.metric("ROA",  f"{roa*100:.1f}%"  if roa  else "N/A")
            roe = fin.get("roe")
            f4.metric("ROE",  f"{roe*100:.1f}%"  if roe  else "N/A")

            st.markdown("##### Margins & Growth")
            m1, m2, m3, m4, m5 = st.columns(5)
            gm  = fin.get("gross_margin");  m1.metric("Gross Margin",    f"{gm*100:.1f}%"   if gm  else "N/A")
            om  = fin.get("op_margin");     m2.metric("Operating Margin", f"{om*100:.1f}%"   if om  else "N/A")
            nm  = fin.get("net_margin");    m3.metric("Net Margin",       f"{nm*100:.1f}%"   if nm  else "N/A")
            rg  = fin.get("revenue_growth");m4.metric("Revenue Growth",   f"{rg*100:+.1f}%"  if rg  else "N/A",
                                                        delta=f"{rg*100:+.1f}%" if rg else None,
                                                        delta_color="normal" if rg and rg>=0 else "inverse")
            eg  = fin.get("earnings_growth");m5.metric("Earnings Growth", f"{eg*100:+.1f}%"  if eg  else "N/A",
                                                         delta=f"{eg*100:+.1f}%" if eg else None,
                                                         delta_color="normal" if eg and eg>=0 else "inverse")

        # ── Valuation vs Sector ───────────────────────────────────────────
        with st.expander("📊 Valuation Multiples", expanded=True):
            v1, v2, v3, v4, v5, v6 = st.columns(6)
            tp  = fin.get("trailing_pe");  v1.metric("Trailing P/E",  f"{tp:.1f}"  if tp  else "N/A")
            fp  = fin.get("forward_pe");   v2.metric("Forward P/E",   f"{fp:.1f}"  if fp  else "N/A")
            peg = fin.get("peg_ratio");    v3.metric("PEG Ratio",     f"{peg:.2f}" if peg else "N/A")
            ps  = fin.get("price_to_sales");v4.metric("Price/Sales",  f"{ps:.2f}"  if ps  else "N/A")
            eve = fin.get("ev_ebitda");    v5.metric("EV/EBITDA",     f"{eve:.1f}" if eve else "N/A")
            evr = fin.get("ev_revenue");   v6.metric("EV/Revenue",    f"{evr:.2f}" if evr else "N/A")

            if tp and fp:
                diff = fp - tp
                note_color = "#1e8a3e" if diff < 0 else "#d32f2f"
                note_txt   = "Forward P/E < Trailing P/E — earnings expected to grow (positive)" \
                             if diff < 0 else \
                             "Forward P/E > Trailing P/E — earnings expected to decline (caution)"
                st.markdown(
                    f"<div style='padding:8px 12px;background:#f8f9fa;border-radius:6px;"
                    f"border-left:4px solid {note_color};margin-top:6px'>"
                    f"<span style='color:{note_color};font-size:0.9em'>ℹ️ {note_txt}</span></div>",
                    unsafe_allow_html=True,
                )
            if peg:
                peg_note = ("Undervalued relative to growth (PEG < 1)" if peg < 1
                            else "Fairly valued (PEG ≈ 1–2)" if peg <= 2
                            else "Potentially overvalued relative to growth (PEG > 2)")
                peg_color = "#1e8a3e" if peg < 1 else ("#f9a825" if peg <= 2 else "#d32f2f")
                st.markdown(
                    f"<div style='padding:8px 12px;background:#f8f9fa;border-radius:6px;"
                    f"border-left:4px solid {peg_color};margin-top:6px'>"
                    f"<span style='color:{peg_color};font-size:0.9em'>📐 PEG {peg:.2f}: {peg_note}</span></div>",
                    unsafe_allow_html=True,
                )

        # ── Management Team ───────────────────────────────────────────────
        with st.expander("👔 Management Team", expanded=False):
            if mgmt:
                mgmt_rows = []
                for o in mgmt:
                    pay = o.get("pay")
                    mgmt_rows.append({
                        "Name":  o.get("name", ""),
                        "Title": o.get("title", ""),
                        "Age":   str(o.get("age", "")) if o.get("age") else "N/A",
                        "Total Pay": f"₹{pay/1e7:.1f} Cr" if pay else "N/A",
                    })
                mgmt_df = pd.DataFrame(mgmt_rows)
                st.dataframe(mgmt_df, use_container_width=True, hide_index=True)
            else:
                st.info("Management data not available.")

        # ── Dividend History ──────────────────────────────────────────────
        with st.expander("💸 Dividend History", expanded=False):
            if divs:
                ddf = pd.DataFrame(divs)
                d1, d2 = st.columns([2, 1])
                with d1:
                    fig_div = px.bar(
                        ddf, x="Date", y="Dividend",
                        title="Dividend per Share History",
                        color_discrete_sequence=["#1a73e8"],
                    )
                    fig_div.update_layout(
                        height=280, plot_bgcolor="#ffffff",
                        paper_bgcolor="#ffffff", font_color="#1a1a2e",
                        xaxis=dict(tickangle=-45, showgrid=False),
                        yaxis=dict(gridcolor="#eeeeee"),
                        margin=dict(l=0, r=0, t=40, b=0),
                    )
                    st.plotly_chart(fig_div, use_container_width=True)
                with d2:
                    st.dataframe(
                        ddf.rename(columns={"Dividend": "₹ / Share"}),
                        use_container_width=True, hide_index=True,
                    )
            else:
                st.info("No dividend history available — company may not pay dividends.")

        # ── Recent News & Outlook (3 years) ──────────────────────────────
        with st.expander(f"📰 News & Outlook — Last 3 Years ({len(news)} articles)", expanded=True):
            if news:
                st.caption(f"Sources: Yahoo Finance · Google News  |  {len(news)} articles from last 3 years")

                # Group by year
                from itertools import groupby
                news_by_year = {}
                for n in news:
                    yr = n.get("year", "Unknown")
                    news_by_year.setdefault(yr, []).append(n)

                for year in sorted(news_by_year.keys(), reverse=True):
                    articles = news_by_year[year]
                    st.markdown(
                        f"<div style='font-size:1.05em;font-weight:700;color:#1a73e8;"
                        f"padding:6px 0 4px 0;border-bottom:2px solid #e8f0fe;"
                        f"margin:12px 0 8px 0'>📅 {year} &nbsp;"
                        f"<span style='font-size:0.8em;color:#888;font-weight:400'>"
                        f"({len(articles)} articles)</span></div>",
                        unsafe_allow_html=True,
                    )
                    for n in articles:
                        st.markdown(
                            f"<div style='padding:8px 12px;margin-bottom:6px;background:#f8f9fa;"
                            f"border-radius:6px;border-left:3px solid #1a73e8'>"
                            f"<a href='{n['link']}' target='_blank' style='color:#1a1a2e;"
                            f"font-weight:600;text-decoration:none'>{n['title']}</a><br>"
                            f"<span style='color:#888;font-size:0.82em'>"
                            f"{n['publisher']} &nbsp;·&nbsp; {n['date']}</span></div>",
                            unsafe_allow_html=True,
                        )
            else:
                st.info("No news found in the last 3 years.")


# ─── Tab 7: Recommendations ──────────────────────────────────────────────────
def tab_recommendations(df: pd.DataFrame):
    st.markdown("### 🤖 Buy / Hold / Sell Recommendations")

    if "Recommendation" not in df.columns:
        st.warning("Recommendation data not available. Please refresh data.")
        return

    _ORDER = ["STRONG BUY", "BUY", "HOLD", "SELL", "STRONG SELL"]
    _CMAP  = {
        "STRONG BUY":  "#00c853",
        "BUY":         "#69f0ae",
        "HOLD":        "#ffd740",
        "SELL":        "#ff6b6b",
        "STRONG SELL": "#ff1744",
    }

    # ── KPI row ─────────────────────────────────────────────────────────────
    kk1, kk2, kk3, kk4, kk5 = st.columns(5)
    for col_k, label, rk in [
        (kk1, "🟢 Strong Buy",  "STRONG BUY"),
        (kk2, "🟩 Buy",         "BUY"),
        (kk3, "🟡 Hold",        "HOLD"),
        (kk4, "🟥 Sell",        "SELL"),
        (kk5, "🔴 Strong Sell", "STRONG SELL"),
    ]:
        col_k.metric(label, int((df["Recommendation"] == rk).sum()))

    st.markdown("---")

    # ── Distribution charts ──────────────────────────────────────────────────
    rec_counts = df["Recommendation"].value_counts().reindex(_ORDER).dropna().reset_index()
    rec_counts.columns = ["Recommendation", "Count"]

    ch1, ch2 = st.columns([1, 2])
    with ch1:
        fig_pie = px.pie(
            rec_counts, values="Count", names="Recommendation",
            title="Recommendation Distribution",
            color="Recommendation", color_discrete_map=_CMAP,
            category_orders={"Recommendation": _ORDER},
            hole=0.4,
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        fig_pie.update_layout(height=350, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with ch2:
        rec_cat = (
            df.groupby(["Category", "Recommendation"])
            .size().reset_index(name="Count")
        )
        fig_bar = px.bar(
            rec_cat, x="Category", y="Count", color="Recommendation",
            title="Recommendations by Market Cap Category",
            color_discrete_map=_CMAP,
            category_orders={"Recommendation": _ORDER},
            barmode="group",
        )
        fig_bar.update_layout(height=350, legend_title_text="")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("---")

    # ── Score distribution histogram ─────────────────────────────────────────
    st.markdown("#### Score Distribution")
    fig_hist = px.histogram(
        df, x="Score", color="Recommendation",
        nbins=20, opacity=0.85,
        title="Signal Score Distribution across All Stocks",
        color_discrete_map=_CMAP,
        category_orders={"Recommendation": _ORDER},
    )
    fig_hist.add_vline(x=0,  line_dash="dash", line_color="gray",  annotation_text="0")
    fig_hist.add_vline(x=3,  line_dash="dot",  line_color="#69f0ae", annotation_text="BUY")
    fig_hist.add_vline(x=-2, line_dash="dot",  line_color="#ff6b6b", annotation_text="SELL")
    fig_hist.update_layout(height=300)
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("---")

    # ── BUY / SELL tables side by side ───────────────────────────────────────
    tb1, tb2 = st.columns(2)
    _disp_cols = ["Name", "Category", "Close", "% Change",
                  "Recommendation", "Score", "Score %", "Bull Signals", "Bear Signals"]

    with tb1:
        st.markdown("#### 🟢 Top BUY Picks")
        buys = (
            df[df["Recommendation"].isin(["STRONG BUY", "BUY"])]
            .sort_values("Score", ascending=False)
            .head(15)
        )
        if buys.empty:
            st.info("No BUY recommendations currently.")
        else:
            st.dataframe(
                buys[_disp_cols].style
                    .applymap(color_pct, subset=["% Change"])
                    .format({"Close": "₹{:.2f}", "% Change": "{:+.2f}%",
                             "Score %": "{:.0f}%"}, na_rep="N/A"),
                use_container_width=True, hide_index=True,
            )

    with tb2:
        st.markdown("#### 🔴 Top SELL Picks")
        sells = (
            df[df["Recommendation"].isin(["STRONG SELL", "SELL"])]
            .sort_values("Score")
            .head(15)
        )
        if sells.empty:
            st.info("No SELL recommendations currently.")
        else:
            st.dataframe(
                sells[_disp_cols].style
                    .applymap(color_pct, subset=["% Change"])
                    .format({"Close": "₹{:.2f}", "% Change": "{:+.2f}%",
                             "Score %": "{:.0f}%"}, na_rep="N/A"),
                use_container_width=True, hide_index=True,
            )

    st.markdown("---")

    # ── Full recommendation table ────────────────────────────────────────────
    st.markdown("#### 📋 All Stocks — Full Recommendation Summary")
    st.caption("💡 Click any row to open the full fundamental & technical analysis below.")

    # Include Ticker for lookup (hidden via column_config)
    _full_cols = [
        "Ticker", "Name", "Category", "Close", "% Change",
        "Recommendation", "Score", "Score %", "Bull Signals", "Bear Signals",
        "RSI",
        "MACD", "MACD Signal",
        "R1", "R2", "R3",
        "S1", "S2", "S3",
        "Target 1", "Target 2",
    ]
    all_rec = (
        df[_full_cols]
        .sort_values("Score", ascending=False)
        .reset_index(drop=True)
    )

    def _color_rec(val):
        return f"color: {_CMAP.get(val, '#333')}; font-weight: bold"

    def _color_rsi_rec(val):
        if pd.isna(val):
            return ""
        if val > 70:
            return "background-color: #ffcdd2; color: #b71c1c; font-weight:600"
        if val < 30:
            return "background-color: #c8e6c9; color: #1b5e20; font-weight:600"
        return ""

    def _color_macd_sig(val):
        if val == "Bullish":
            return "color: #1e8a3e; font-weight:600"
        if val == "Bearish":
            return "color: #d32f2f; font-weight:600"
        return ""

    price_cols = ["Close", "R1", "R2", "R3", "S1", "S2", "S3", "Target 1", "Target 2"]
    fmt = {c: "₹{:.2f}" for c in price_cols}
    fmt.update({"% Change": "{:+.2f}%", "Score %": "{:.0f}%",
                "RSI": "{:.1f}", "MACD": "{:.3f}"})

    selection = st.dataframe(
        all_rec.style
            .applymap(color_pct,       subset=["% Change"])
            .applymap(_color_rec,      subset=["Recommendation"])
            .applymap(_color_rsi_rec,  subset=["RSI"])
            .applymap(_color_macd_sig, subset=["MACD Signal"])
            .format(fmt, na_rep="N/A"),
        use_container_width=True,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="rec_full_table",
        column_config={"Ticker": None},   # hide Ticker column visually
    )

    # ── Detail panel for selected row ────────────────────────────────────────
    selected_rows = selection.selection.rows if selection and selection.selection else []
    if selected_rows:
        selected_ticker = all_rec.iloc[selected_rows[0]]["Ticker"]
        selected_name   = all_rec.iloc[selected_rows[0]]["Name"]
        st.markdown("---")
        st.markdown(
            f"<div style='background:#e8f4fd;border-left:5px solid #1a73e8;"
            f"padding:10px 16px;border-radius:6px;margin-bottom:8px'>"
            f"📊 Showing full analysis for <strong>{selected_name}</strong> "
            f"<span style='color:#888;font-size:0.9em'>({selected_ticker})</span></div>",
            unsafe_allow_html=True,
        )
        render_stock_detail(selected_ticker)


# ─── Main App ────────────────────────────────────────────────────────────────
def main():
    # ── PWA meta tags (iOS "Add to Home Screen" + Android Chrome install hint) ─
    st.markdown(
        """
        <link rel="manifest"                    href="/app/static/manifest.json">
        <link rel="apple-touch-icon"            href="/app/static/icon.svg">
        <meta name="mobile-web-app-capable"     content="yes">
        <meta name="apple-mobile-web-app-capable"          content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title"            content="Stock Dashboard">
        <meta name="theme-color"                content="#0d1b2a">
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
        """,
        unsafe_allow_html=True,
    )

    # ── Global CSS ────────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    .block-container { padding-top: 0.5rem; }
    [data-testid="stMetricDelta"] span { font-weight: 600; }

    /* Index metric cards */
    [data-testid="stMetric"] {
        background: #f7f9ff;
        border-radius: 10px;
        padding: 14px 16px;
        border: 1px solid #dce3f5;
    }

    /* Gradient dashboard header */
    .dash-header {
        background: linear-gradient(135deg, #0d1b2a 0%, #1a3a5c 60%, #0d2840 100%);
        border-radius: 14px;
        padding: 20px 28px;
        margin-bottom: 18px;
        box-shadow: 0 4px 24px rgba(13,27,42,0.22);
    }
    .dash-header h1 { color: #fff; margin: 0; font-size: 1.75em; line-height: 1.2; }
    .dash-header .sub { color: #93b4d0; font-size: 0.85em; margin-top: 5px; }
    .dash-header .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-size: 0.78em;
        font-weight: 700;
        letter-spacing: 0.4px;
        color: #fff;
    }

    /* Colored KPI cards */
    .kpi-grid { display: flex; gap: 12px; flex-wrap: wrap; margin: 4px 0 16px; }
    .kpi-card {
        flex: 1; min-width: 130px;
        background: #fff;
        border-radius: 10px;
        padding: 14px 18px;
        border-left: 5px solid #aaa;
        box-shadow: 0 1px 8px rgba(0,0,0,0.07);
    }
    .kpi-card .lbl { color: #777; font-size: 0.75em; font-weight: 600;
                     text-transform: uppercase; letter-spacing: 0.5px; }
    .kpi-card .val { font-size: 2em; font-weight: 800; color: #1a1a2e;
                     line-height: 1.1; margin-top: 4px; }
    .kpi-card .sub2 { color: #999; font-size: 0.75em; margin-top: 3px; }
    .kpi-neutral  { border-left-color: #1a73e8; }
    .kpi-change   { border-left-color: #888; }
    .kpi-buy      { border-left-color: #00c853; background: #f0fff4; }
    .kpi-hold     { border-left-color: #f9a825; background: #fffde7; }
    .kpi-sell     { border-left-color: #e53935; background: #fff5f5; }

    /* Breadth bar */
    .breadth-wrap {
        background: #f7f9ff;
        border-radius: 12px;
        padding: 14px 20px;
        margin-bottom: 8px;
        border: 1px solid #dce3f5;
    }

    /* ── Mobile / PWA responsive ──────────────────────────────────────────── */
    @media screen and (max-width: 768px) {
        /* Tighter container padding */
        .block-container { padding: 0.3rem 0.6rem 2rem !important; }

        /* Header scales down */
        .dash-header { padding: 14px 16px !important; }
        .dash-header h1 { font-size: 1.25em !important; }
        .dash-header .sub { font-size: 0.78em !important; }
        .dash-header .badge { font-size: 0.7em !important; padding: 3px 10px !important; }

        /* Stack all columns to full width on phone */
        [data-testid="column"] {
            min-width: 100% !important;
            width:     100% !important;
        }

        /* KPI cards: 2-per-row grid */
        .kpi-grid { gap: 8px !important; }
        .kpi-card {
            min-width: calc(50% - 4px) !important;
            max-width: calc(50% - 4px) !important;
            padding: 10px 12px !important;
        }
        .kpi-card .val { font-size: 1.6em !important; }
        .kpi-card .lbl { font-size: 0.68em !important; }

        /* Breadth bar */
        .breadth-wrap { padding: 10px 12px !important; }

        /* Plotly charts: cap height on phone */
        .js-plotly-plot { max-height: 320px !important; }

        /* Tabs: smaller text */
        button[role="tab"] {
            font-size: 0.78em !important;
            padding: 6px 8px !important;
        }

        /* Gainers/Losers table: hide Volume column */
        table td:last-child, table th:last-child { display: none !important; }

        /* Sidebar toggle: bigger tap target */
        [data-testid="collapsedControl"] {
            width: 44px !important;
            height: 44px !important;
        }
    }

    /* ── Standalone (installed PWA) chrome ───────────────────────────────── */
    @media (display-mode: standalone) {
        /* Account for iOS notch / home indicator */
        .block-container {
            padding-top:    env(safe-area-inset-top,    0.5rem) !important;
            padding-bottom: env(safe-area-inset-bottom, 1.5rem) !important;
        }
        /* Hide Streamlit footer in standalone mode */
        footer { display: none !important; }
    }

    /* Minimum 44px touch targets on all interactive elements */
    .stButton > button          { min-height: 44px !important; }
    .stSelectbox select         { min-height: 44px !important; }
    .stTextInput > div > input  { min-height: 44px !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── Gradient header ───────────────────────────────────────────────────────
    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p")
    market_open  = is_market_open()
    badge_bg     = "#00c853" if market_open else "#e53935"
    badge_label  = "MARKET OPEN" if market_open else "MARKET CLOSED"
    st.markdown(
        f"""
        <div class="dash-header">
          <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px">
            <div>
              <h1>📊 NSE/BSE Stock Analysis Dashboard</h1>
              <div class="sub">🕐 {now_str} &nbsp;·&nbsp; Data via Yahoo Finance (yfinance)</div>
            </div>
            <div style="text-align:right;padding-top:4px">
              <span class="badge" style="background:{badge_bg}">● {badge_label}</span>
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    selected_tickers, searched_ticker, quick_filter = build_sidebar()

    # Market index
    with st.spinner("Fetching index data…"):
        idx_data = fetch_index_data()
    render_market_overview(idx_data)

    st.markdown("---")

    # NSE/BSE search result detail panel
    if searched_ticker:
        with st.expander(f"🔍 Search Result: {searched_ticker}", expanded=True):
            render_stock_detail(searched_ticker)
        st.markdown("---")

    # Stock data
    with st.spinner(f"Fetching data for {len(selected_tickers)} stocks…"):
        df = fetch_stocks(selected_tickers)

    # ── Market breadth progress bar ───────────────────────────────────────────
    total_stocks = len(df)
    gainers_n = int((df["% Change"] > 0).sum())
    losers_n  = int((df["% Change"] < 0).sum())
    flat_n    = total_stocks - gainers_n - losers_n
    g_pct = gainers_n / total_stocks * 100 if total_stocks else 0
    l_pct = losers_n  / total_stocks * 100 if total_stocks else 0
    f_pct = flat_n    / total_stocks * 100 if total_stocks else 0
    avg_chg = df["% Change"].mean()
    sentiment = "Bullish 🟢" if avg_chg > 0.3 else ("Bearish 🔴" if avg_chg < -0.3 else "Neutral 🟡")
    st.markdown(
        f"""
        <div class="breadth-wrap">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
            <span style="font-weight:700;font-size:0.95em">📊 Market Breadth
              <span style="color:#888;font-size:0.82em;font-weight:400;margin-left:8px">
                {total_stocks} stocks tracked &nbsp;·&nbsp; Avg {avg_chg:+.2f}%
              </span>
            </span>
            <span style="font-weight:700;font-size:0.88em">Sentiment: {sentiment}</span>
          </div>
          <div style="background:#e9ecef;border-radius:8px;height:20px;overflow:hidden;display:flex">
            <div style="background:#00c853;width:{g_pct:.1f}%;height:100%"></div>
            <div style="background:#ddd;width:{f_pct:.1f}%;height:100%"></div>
            <div style="background:#e53935;width:{l_pct:.1f}%;height:100%"></div>
          </div>
          <div style="display:flex;justify-content:space-between;margin-top:6px;font-size:0.8em;color:#555">
            <span>🟢 <b>{gainers_n}</b> Gainers ({g_pct:.0f}%)</span>
            <span>⚪ <b>{flat_n}</b> Flat</span>
            <span>🔴 <b>{losers_n}</b> Losers ({l_pct:.0f}%)</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── Colored KPI cards ─────────────────────────────────────────────────────
    if "Recommendation" in df.columns:
        buy_n  = int(df["Recommendation"].isin(["STRONG BUY",  "BUY"]).sum())
        hold_n = int((df["Recommendation"] == "HOLD").sum())
        sell_n = int(df["Recommendation"].isin(["STRONG SELL", "SELL"]).sum())
    else:
        buy_n = hold_n = sell_n = 0
    rsi_ob = int((df["RSI"] > 70).sum())
    rsi_os = int((df["RSI"] < 30).sum())
    hi_vol = int((df["Vol Ratio"] >= 1.5).sum())

    st.markdown(
        f"""
        <div class="kpi-grid">
          <div class="kpi-card kpi-neutral">
            <div class="lbl">Stocks Tracked</div>
            <div class="val">{total_stocks}</div>
            <div class="sub2">All selected caps</div>
          </div>
          <div class="kpi-card kpi-change">
            <div class="lbl">Avg % Change</div>
            <div class="val" style="color:{'#00c853' if avg_chg>=0 else '#e53935'}">{avg_chg:+.2f}%</div>
            <div class="sub2">Today vs prev close</div>
          </div>
          <div class="kpi-card kpi-buy">
            <div class="lbl">🟢 Buy Signals</div>
            <div class="val" style="color:#00873a">{buy_n}</div>
            <div class="sub2">BUY + STRONG BUY</div>
          </div>
          <div class="kpi-card kpi-hold">
            <div class="lbl">🟡 Hold</div>
            <div class="val" style="color:#e65100">{hold_n}</div>
            <div class="sub2">Neutral stance</div>
          </div>
          <div class="kpi-card kpi-sell">
            <div class="lbl">🔴 Sell Signals</div>
            <div class="val" style="color:#c62828">{sell_n}</div>
            <div class="sub2">SELL + STRONG SELL</div>
          </div>
          <div class="kpi-card kpi-neutral">
            <div class="lbl">RSI Overbought</div>
            <div class="val" style="color:#c62828">{rsi_ob}</div>
            <div class="sub2">RSI &gt; 70</div>
          </div>
          <div class="kpi-card kpi-neutral">
            <div class="lbl">RSI Oversold</div>
            <div class="val" style="color:#00873a">{rsi_os}</div>
            <div class="sub2">RSI &lt; 30</div>
          </div>
          <div class="kpi-card kpi-neutral">
            <div class="lbl">High Volume</div>
            <div class="val" style="color:#1a73e8">{hi_vol}</div>
            <div class="sub2">Vol &gt; 1.5× avg</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    # ── Apply quick-filter for tab display ───────────────────────────────────
    if quick_filter == "Only BUY":
        df_display = df[df["Recommendation"].isin(["BUY", "STRONG BUY"])].copy()
    elif quick_filter == "Only Oversold (RSI < 30)":
        df_display = df[df["RSI"] < 30].copy()
    elif quick_filter == "High Volume (>1.5× avg)":
        df_display = df[df["Vol Ratio"] >= 1.5].copy()
    else:
        df_display = df

    if quick_filter != "All Stocks":
        st.info(
            f"🔍 Quick filter active: **{quick_filter}** — showing {len(df_display)} of {len(df)} stocks. "
            f"Remove via the sidebar to see all.",
            icon="ℹ️",
        )

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📈 Overview",      # same — short enough
        "⚙️ Technical",     # same
        "🏦 Funds",         # Fundamentals → Funds
        "📊 Volume",        # same
        "🎯 Levels",        # Levels & Signals → Levels
        "🗃️ Data",          # Raw Data → Data
        "🤖 Signals",       # Recommendations → Signals
    ])

    with tab1:
        tab_overview(df_display)
    with tab2:
        tab_technical(df_display)
    with tab3:
        tab_fundamentals(df_display)
    with tab4:
        tab_volume(df_display)
    with tab5:
        tab_levels(df_display)
    with tab6:
        tab_rawdata(df_display)
    with tab7:
        tab_recommendations(df_display)


if __name__ == "__main__":
    main()
