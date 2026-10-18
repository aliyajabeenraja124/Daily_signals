import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TAURIC - Multi Signals", page_icon="📈", layout="wide")
st.title("TAURIC - Live Multi-Pair Signals")
st.caption("XAUUSD Fixed + BTC + EURUSD + GBPUSD + SILVER Added")

# --- Sab Pairs Yahan ---
PAIRS = {
    "GOLD (XAUUSD)": "XAUUSD=X",
    "SILVER (XAGUSD)": "XAGUSD=X",
    "BTC-USD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X"
}

@st.cache_data(ttl=300)
def get_data(symbol):
    for interval in ["1h", "1d"]:
        try:
            df = yf.download(symbol, period="1mo", interval=interval, progress=False, auto_adjust=True)
            if not df.empty and len(df) > 20:
                return df, interval
        except:
            continue
    return None, None

# --- UI ---
selected = st.selectbox("Pair Select Karo:", list(PAIRS.keys()))
symbol = PAIRS[selected]

col1, col2 = st.columns([1,2])

with col1:
    df, used_interval = get_data(symbol)
    
    if df is None:
        st.error(f"{selected} ka data nahi mil raha (Sunday Market Closed)")
        st.stop()

    close = df['Close']
    
    # Safe Price
    try:
        last_price = float(close.iloc[-1])
    except:
        last_price = float(close.values[-1])
    
    # Safe EMA
    try:
        ema9 = float(close.ewm(span=9).mean().iloc[-1])
        ema20 = float(close.ewm(span=20).mean().iloc[-1])
    except:
        ema9 = float(close.ewm(span=9).mean().values[-1])
        ema20 = float(close.ewm(span=20).mean().values[-1])

    st.metric(f"{selected} ({used_interval})", f"${last_price:.4f}" if "USD" in selected and "GOLD" not in selected and "SILVER" not in selected else f"${last_price:.2f}")

    if ema9 > ema20:
        st.success(f"SIGNAL: BUY 📈")
        reason = f"9 EMA ({ema9:.2f}) > 20 EMA ({ema20:.2f})"
        tp = last_price * 1.005
        sl = last_price * 0.997
    else:
        st.error(f"SIGNAL: SELL 📉")
        reason = f"9 EMA ({ema9:.2f}) < 20 EMA ({ema20:.2f})"
        tp = last_price * 0.995
        sl = last_price * 1.003

    st.write(f"**Reason:** {reason}")
    st.write(f"**TP:** {tp:.4f} | **SL:** {sl:.4f}")

with col2:
    st.line_chart(close.tail(150))
    st.dataframe(df.tail(10).sort_index(ascending=False))

# --- All Pairs Overview ---
st.divider()
st.subheader("All Pairs Quick Overview")
for name, sym in PAIRS.items():
    d, _ = get_data(sym)
    if d is not None:
        c = d['Close']
        try:
            lp = float(c.iloc[-1])
            e9 = float(c.ewm(span=9).mean().iloc[-1])
            e20 = float(c.ewm(span=20).mean().iloc[-1])
            sig = "BUY" if e9 > e20 else "SELL"
        except:
            lp = 0
            sig = "N/A"
        st.write(f"**{name}**: ${lp:.2f} -> {sig}")
