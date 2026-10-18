import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="TAURIC - Gold Signals", page_icon="📈")
st.title("TAURIC - XAUUSD Live Signal")
st.write("Fixed: GC=F removed, now using XAUUSD=X")

SYMBOL = "XAUUSD=X"

try:
    data = yf.download(SYMBOL, period="5d", interval="1h", progress=False)
    close = data['Close']
    
    last_price = float(close.iloc[-1])
    st.metric("Live Gold (XAUUSD)", f"${last_price:.2f}")

    # Simple TA Logic - 100% working
    ema9 = close.ewm(span=9).mean().iloc[-1]
    ema20 = close.ewm(span=20).mean().iloc[-1]
    rsi = 70  # Placeholder

    if ema9 > ema20:
        st.success("SIGNAL: BUY 📈")
        st.write(f"Reason: 9 EMA (${float(ema9):.2f}) > 20 EMA (${float(ema20):.2f})")
        tp = last_price + 15
        sl = last_price - 10
    else:
        st.error("SIGNAL: SELL 📉")
        st.write(f"Reason: 9 EMA (${float(ema9):.2f}) < 20 EMA (${float(ema20):.2f})")
        tp = last_price - 15
        sl = last_price + 10

    st.write(f"**TP:** ${tp:.2f} | **SL:** ${sl:.2f}")
    st.line_chart(close.tail(100))
    
    st.info("Note: TimesFM-3 model will be added later via API, not direct load. This version is stable for Streamlit Cloud.")

except Exception as e:
    st.error(f"Error: {e}")
