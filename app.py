import streamlit as st
import yfinance as yf
import pandas as pd
import requests

st.set_page_config(page_title="TAURIC - 5 AI LIVE XAUUSD", page_icon="🤖", layout="wide")
st.title("TAURIC - 5 AI Meeting Decision")

PAIRS = {
    "GOLD (XAUUSD)": ["GC=F", "XAUUSD=X"], # Chart GC=F se, price live API se
    "SILVER (XAGUSD)": ["SI=F", "XAGUSD=X"],
    "BTC-USD": ["BTC-USD"],
    "EURUSD": ["EURUSD=X"],
    "GBPUSD": ["GBPUSD=X"]
}

TIMEFRAMES = {
    "15 Minute": "15m",
    "1 Hour": "1h",
    "4 Hour": "4h",
    "1 Day": "1d",
    "1 Week": "1wk"
}

def get_live_spot_price(pair_name):
    try:
        if "GOLD" in pair_name:
            r = requests.get("https://api.gold-api.com/price/XAU", timeout=5).json()
            return float(r['price'])
        if "SILVER" in pair_name:
            r = requests.get("https://api.gold-api.com/price/XAG", timeout=5).json()
            return float(r['price'])
    except:
        return None
    return None

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

@st.cache_data(ttl=60)
def get_data(symbols_list, interval):
    for sym in symbols_list:
        try:
            period = "7d" if interval in ["15m", "1h"] else "2y"
            df = yf.download(sym, period=period, interval=interval, progress=False, auto_adjust=True)
            if df is not None and not df.empty and len(df) > 20:
                return df, sym
        except:
            continue
    return None, None

col_a, col_b = st.columns(2)
with col_a:
    selected = st.selectbox("Pair Select Karo:", list(PAIRS.keys()))
with col_b:
    tf_name = st.selectbox("Timeframe Select Karo:", list(TIMEFRAMES.keys()), index=3)

symbol_list = PAIRS[selected]
interval = TIMEFRAMES[tf_name]
df, used_sym = get_data(symbol_list, interval)

if df is None:
    st.error(f"{selected} ka data nahi mila")
    st.stop()

close = df['Close']
chart_price = safe_price(close)

# LIVE XAUUSD SPOT PRICE
live_spot = get_live_spot_price(selected)
last_price = live_spot if live_spot else chart_price
is_live = live_spot is not None

# 5 AI - indicators chart se
ema9 = safe_price(close.ewm(span=9).mean())
ema20 = safe_price(close.ewm(span=20).mean())
ai1 = "BUY" if ema9 > ema20 else "SELL"

delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = safe_price(100 - (100 / (1 + rs)))
ai2 = "BUY" if rsi < 70 else "SELL"

ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd = ema12 - ema26
ai3 = "BUY" if safe_price(macd) > safe_price(macd.ewm(span=9).mean()) else "SELL"

sma50 = safe_price(close.rolling(50).mean())
ai4 = "BUY" if chart_price > sma50 else "SELL"
ai5 = "BUY" if safe_price(close.tail(5).mean() - close.tail(10).mean()) > 0 else "SELL"

c1, c2 = st.columns([1,2])
with c1:
    if is_live:
        st.metric(f"{selected} LIVE SPOT ({tf_name})", f"{last_price:.2f}", f"GC=F: {chart_price:.2f}", delta_color="off")
        st.caption(f"✅ Live XAUUSD Price | Chart: {used_sym}")
    else:
        st.metric(f"{selected} ({used_sym})", f"{last_price:.2f}")
    
    votes = [ai1, ai2, ai3, ai4, ai5]
    buy_votes = votes.count("BUY")
    if buy_votes >= 3:
        st.success(f"FINAL: BUY 📈 ({buy_votes}/5)")
        tp = last_price * 1.005
        sl = last_price * 0.997
    else:
        st.error(f"FINAL: SELL 📉 ({5-buy_votes}/5)")
        tp = last_price * 0.995
        sl = last_price * 1.003
    st.write(f"**TP:** {tp:.2f} | **SL:** {sl:.2f}")

with c2:
    plot_data = close.squeeze() if isinstance(close, pd.DataFrame) else close
    if isinstance(plot_data, pd.DataFrame):
        plot_data = plot_data.iloc[:, 0]
    st.line_chart(plot_data.dropna().tail(150))

st.divider()
st.subheader(f"🤖 5 AI Meeting - {tf_name}")
a,b,c,d,e = st.columns(5)
a.metric("EMA", ai1)
b.metric("RSI", ai2, f"{rsi:.0f}")
c.metric("MACD", ai3)
d.metric("TREND", ai4)
e.metric("TimesFM", ai5)

if st.button("🔄 Refresh Live Price"):
    st.cache_data.clear()
    st.rerun()
