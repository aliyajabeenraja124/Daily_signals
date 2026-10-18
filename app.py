import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TAURIC - Multi Signals", page_icon="📈", layout="wide")
st.title("TAURIC - Live Multi-Pair Signals")
st.caption("Final Fixed Version - TP/SL Corrected")

PAIRS = {
    "GOLD (XAUUSD)": "XAUUSD=X",
    "SILVER (XAGUSD)": "XAGUSD=X",
    "BTC-USD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X"
}

def safe_price(data):
    try:
        if isinstance(data, pd.DataFrame):
            s = data.squeeze()
            if isinstance(s, pd.DataFrame):
                s = s.iloc[:, 0]
            return float(s.dropna().iloc[-1])
        else:
            return float(data.dropna().iloc[-1])
    except:
        return float(pd.Series(data).dropna().values[-1])

@st.cache_data(ttl=300)
def get_data(symbol):
    for interval in ["1h", "1d"]:
        try:
            df = yf.download(symbol, period="1mo", interval=interval, progress=False, auto_adjust=True)
            if df is not None and not df.empty and len(df) > 10:
                return df, interval
        except:
            continue
    return None, None

selected = st.selectbox("Pair Select Karo:", list(PAIRS.keys()))
symbol = PAIRS[selected]

df, used_interval = get_data(symbol)

if df is None:
    st.error(f"{selected} - Market Closed (Sunday)")
    st.stop()

close = df['Close']
last_price = safe_price(close)

ema9 = safe_price(close.ewm(span=9).mean())
ema20 = safe_price(close.ewm(span=20).mean())

col1, col2 = st.columns([1,2])

with col1:
    st.metric(f"{selected} ({used_interval})", f"{last_price:.4f}")

    if ema9 > ema20:
        st.success("SIGNAL: BUY 📈")
        tp = last_price * 1.005
        sl = last_price * 0.997
        st.write(f"**TP (upar):** {tp:.4f}")
        st.write(f"**SL (neeche):** {sl:.4f}")
    else:
        st.error("SIGNAL: SELL 📉")
        tp = last_price * 0.995
        sl = last_price * 1.003
        st.write(f"**TP (neeche):** {tp:.4f}")
        st.write(f"**SL (upar):** {sl:.4f}")

    st.write(f"9 EMA: {ema9:.2f} | 20 EMA: {ema20:.2f}")

with col2:
    # Chart ka scale fix
    st.line_chart(close.tail(150))

st.divider()
st.subheader("Quick Overview - All Pairs")
for name, sym in PAIRS.items():
    d, _ = get_data(sym)
    if d is not None:
        try:
            lp = safe_price(d['Close'])
            e9 = safe_price(d['Close'].ewm(span=9).mean())
            e20 = safe_price(d['Close'].ewm(span=20).mean())
            sig = "BUY 📈" if e9 > e20 else "SELL 📉"
            st.write(f"**{name}**: {lp:.2f} -> {sig}")
        except:
            pass
