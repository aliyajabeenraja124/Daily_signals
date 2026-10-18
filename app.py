import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TAURIC - 5 AI Meeting", page_icon="🤖", layout="wide")
st.title("TAURIC - 5 AI Meeting Decision")
st.caption("GOLD, SILVER, BTC, EURUSD, GBPUSD + 5 AI Agents")

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
    st.error("Market Closed")
    st.stop()

close = df['Close']
last_price = safe_price(close)

# --- 5 AI AGENTS LOGIC ---
# 1. EMA AI
ema9 = safe_price(close.ewm(span=9).mean())
ema20 = safe_price(close.ewm(span=20).mean())
ai1 = "BUY" if ema9 > ema20 else "SELL"

# 2. RSI AI
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi_series = 100 - (100 / (1 + rs))
rsi = safe_price(rsi_series)
ai2 = "BUY" if rsi < 70 and rsi > 40 else "SELL" if rsi > 70 else "NEUTRAL"

# 3. MACD AI
ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd = ema12 - ema26
macd_signal = macd.ewm(span=9).mean()
ai3 = "BUY" if safe_price(macd) > safe_price(macd_signal) else "SELL"

# 4. Trend AI (SMA 50)
sma50 = safe_price(close.rolling(50).mean())
ai4 = "BUY" if last_price > sma50 else "SELL"

# 5. TimesFM AI (Light - SMA forecast instead of heavy torch model)
# Heavy model hata ke light forecast
future_trend = (close.tail(5).mean() - close.tail(10).mean()).iloc[0] if isinstance(close.tail(5).mean(), pd.Series) else close.tail(5).mean() - close.tail(10).mean()
ai5 = "BUY" if future_trend > 0 else "SELL"

# --- DISPLAY ---
col1, col2 = st.columns([1,2])
with col1:
    st.metric(f"{selected} ({used_interval})", f"{last_price:.4f}")
    st.write(f"RSI: {rsi:.1f} | SMA50: {sma50:.2f}")

    # Final Decision by Voting
    votes = [ai1, ai2, ai3, ai4, ai5]
    buy_votes = votes.count("BUY")
    sell_votes = votes.count("SELL")
    
    if buy_votes >= 3:
        st.success(f"FINAL SIGNAL: BUY 📈 ({buy_votes}/5 AI Agree)")
        tp = last_price * 1.005
        sl = last_price * 0.997
    else:
        st.error(f"FINAL SIGNAL: SELL 📉 ({sell_votes}/5 AI Agree)")
        tp = last_price * 0.995
        sl = last_price * 1.003
    
    st.write(f"**TP:** {tp:.4f} | **SL:** {sl:.4f}")

with col2:
    st.line_chart(close.tail(150))

st.divider()
st.subheader("🤖 5 AI Meeting Room - Live Voting")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("AI-1 EMA", ai1)
c2.metric("AI-2 RSI", ai2, f"{rsi:.0f}")
c3.metric("AI-3 MACD", ai3)
c4.metric("AI-4 TREND", ai4)
c5.metric("AI-5 TimesFM-Lite", ai5)

st.write(f"Voting: {votes} -> BUY: {buy_votes} | SELL: {sell_votes}")

st.divider()
st.subheader("Quick Overview - All Pairs")
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
            pass
