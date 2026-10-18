import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TAURIC - 5 AI Meeting", page_icon="🤖", layout="wide")
st.title("TAURIC - 5 AI Meeting Decision")

PAIRS = {
    "GOLD (XAUUSD)": "XAUUSD=X",
    "SILVER (XAGUSD)": "XAGUSD=X",
    "BTC-USD": "BTC-USD",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X"
}

TIMEFRAMES = {
    "15 Minute": "15m",
    "1 Hour": "1h",
    "4 Hour": "4h",
    "1 Day": "1d",
    "1 Week": "1wk"
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
def get_data(symbol, interval):
    try:
        period = "5d" if interval in ["15m", "1h"] else "1mo" if interval in ["4h", "1d"] else "1y"
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if df is not None and not df.empty and len(df) > 10:
            return df
    except:
        pass
    return None

# --- SELECTORS ---
col_a, col_b = st.columns(2)
with col_a:
    selected = st.selectbox("Pair Select Karo:", list(PAIRS.keys()))
with col_b:
    tf_name = st.selectbox("Timeframe Select Karo:", list(TIMEFRAMES.keys()), index=1)

symbol = PAIRS[selected]
interval = TIMEFRAMES[tf_name]

df = get_data(symbol, interval)
if df is None:
    st.error(f"{selected} - {tf_name} pe data nahi mila (Market closed ho sakta hai). Dusra timeframe try karo.")
    st.stop()

close = df['Close']
last_price = safe_price(close)

# 5 AI Logic
ema9 = safe_price(close.ewm(span=9).mean())
ema20 = safe_price(close.ewm(span=20).mean())
ai1 = "BUY" if ema9 > ema20 else "SELL"

delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi_series = 100 - (100 / (1 + rs))
rsi = safe_price(rsi_series)
ai2 = "BUY" if rsi < 70 and rsi > 40 else "SELL" if rsi > 70 else "BUY"

ema12 = close.ewm(span=12).mean()
ema26 = close.ewm(span=26).mean()
macd = ema12 - ema26
macd_signal = macd.ewm(span=9).mean()
ai3 = "BUY" if safe_price(macd) > safe_price(macd_signal) else "SELL"

sma50 = safe_price(close.rolling(50).mean())
ai4 = "BUY" if last_price > sma50 else "SELL"

future_trend = close.tail(5).mean() - close.tail(10).mean()
ft_val = safe_price(future_trend) if not isinstance(future_trend, (float, int)) else float(future_trend)
ai5 = "BUY" if ft_val > 0 else "SELL"

# Display
col1, col2 = st.columns([1,2])
with col1:
    st.metric(f"{selected} ({tf_name})", f"{last_price:.4f}")
    votes = [ai1, ai2, ai3, ai4, ai5]
    buy_votes = votes.count("BUY")
    
    if buy_votes >= 3:
        st.success(f"FINAL: BUY 📈 ({buy_votes}/5)")
        tp = last_price * 1.005
        sl = last_price * 0.997
        st.write(f"TP: {tp:.4f} (upar) | SL: {sl:.4f} (neeche)")
    else:
        st.error(f"FINAL: SELL 📉 ({5-buy_votes}/5)")
        tp = last_price * 0.995
        sl = last_price * 1.003
        st.write(f"TP: {tp:.4f} (neeche) | SL: {sl:.4f} (upar)")
    
    st.write(f"RSI: {rsi:.1f}")

with col2:
    plot_data = close.squeeze() if isinstance(close, pd.DataFrame) else close
    if isinstance(plot_data, pd.DataFrame):
        plot_data = plot_data.iloc[:, 0]
    st.line_chart(plot_data.dropna().tail(150))

st.divider()
st.subheader(f"🤖 5 AI Meeting - {tf_name} Voting")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("EMA", ai1)
c2.metric("RSI", ai2, f"{rsi:.0f}")
c3.metric("MACD", ai3)
c4.metric("TREND", ai4)
c5.metric("TimesFM", ai5)
