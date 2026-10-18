import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TAURIC - Multi Signals", page_icon="📈", layout="wide")
st.title("TAURIC - Live Multi-Pair Signals")
st.caption("XAUUSD Fixed + BTC + EURUSD + GBPUSD + SILVER Added")

PAIRS = {
    "GOLD (XAUUSD)": "XAUUSD=X",
    "SILVER (XAGUSD)": "XAGUSD=X",
    "BTC-USD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X"
}

def safe_price(series_or_df):
    """Koi bhi format ho, float nikal dega"""
    try:
        # Agar DataFrame hai to Series banao
        if isinstance(series_or_df, pd.DataFrame):
            s = series_or_df.squeeze()
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            return float(s.dropna().iloc[-1])
        else:
            return float(series_or_df.dropna().iloc[-1])
    except:
        # Last option
        return float(pd.Series(series_or_df).dropna().values[-1])

@st.cache_data(ttl=300)
def get_data(symbol):
    for interval in ["1h", "1d", "1wk"]:
        try:
            df = yf.download(symbol, period="1mo", interval=interval, progress=False, auto_adjust=True)
            if df is not None and not df.empty and len(df) > 5:
                return df, interval
        except:
            continue
    return None, None

selected = st.selectbox("Pair Select Karo:", list(PAIRS.keys()))
symbol = PAIRS[selected]

df, used_interval = get_data(symbol)

if df is None:
    st.error(f"{selected} ka data nahi mila. Market closed ho sakta hai.")
    st.stop()

close = df['Close']

last_price = safe_price(close)

col1, col2 = st.columns([1,2])

with col1:
    # EMA safe
    ema9_series = close.ewm(span=9).mean()
    ema20_series = close.ewm(span=20).mean()
    ema9 = safe_price(ema9_series)
    ema20 = safe_price(ema20_series)

    st.metric(f"{selected} ({used_interval})", f"{last_price:.4f}")

    if ema9 > ema20:
        st.success("SIGNAL: BUY 📈")
    else:
        st.error("SIGNAL: SELL 📉")

    st.write(f"9 EMA: {ema9:.2f}")
    st.write(f"20 EMA: {ema20:.2f}")
    st.write(f"TP: {last_price * 1.005:.2f} | SL: {last_price * 0.997:.2f}")

with col2:
    st.line_chart(close.tail(150))

st.divider()
st.write("Quick Overview - All Pairs")
for name, sym in PAIRS.items():
    d, _ = get_data(sym)
    if d is not None:
        try:
            lp = safe_price(d['Close'])
            e9 = safe_price(d['Close'].ewm(span=9).mean())
            e20 = safe_price(d['Close'].ewm(span=20).mean())
            sig = "BUY" if e9 > e20 else "SELL"
            st.write(f"**{name}**: {lp:.2f} -> {sig}")
        except:
            st.write(f"**{name}**: Loading...")
