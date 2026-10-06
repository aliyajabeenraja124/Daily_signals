import streamlit as st
import yfinance as yf
import pandas as pd
import random
from datetime import datetime

st.set_page_config(page_title="Tauric Research - 5 AI Council", page_icon="🐂", layout="wide")

# Custom CSS - Pink Tauric Style
st.markdown("""
<style>
.main { background-color: #fff0f5; }
.stApp { background-color: #fff0f5; }
.ai-card { background: white; padding: 15px; border-radius: 15px; border-left: 5px solid #ff1493; margin-bottom: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.final-card { background: linear-gradient(135deg, #ff1493, #ff69b4); color: white; padding: 20px; border-radius: 20px; text-align: center; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center; color: #ff1493;'>🐂 TAURIC RESEARCH</h1><h3 style='text-align: center;'>5 AI COUNCIL MEETING</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center;'>Live Meeting Time: {datetime.now().strftime('%d %B %Y - %I:%M %p')}</p>", unsafe_allow_html=True)

symbol = st.selectbox("Pair Select Karo:", ["GC=F", "EURUSD=X", "GBPUSD=X", "BTC-USD", "SI=F"], index=0)
symbol_names = {"GC=F": "GOLD / XAUUSD", "EURUSD=X": "EUR/USD", "GBPUSD=X": "GBP/USD", "BTC-USD": "BTC/USD", "SI=F": "SILVER"}

# Get Price
try:
    data = yf.download(symbol, period="1d", interval="1m")
    price = float(data['Close'].iloc[-1])
    change = float(data['Close'].iloc[-1] - data['Close'].iloc[0])
except:
    price = 2650.50
    change = 5.2

st.metric(f"{symbol_names[symbol]} Price", f"${price:.2f}", f"{change:.2f}")

st.markdown("---")
st.subheader("🔴 LIVE AI COUNCIL DISCUSSION")

# Simulate 5 AIs
col1, col2 = st.columns(2)

ai1_vote = random.choice(["BUY", "BUY", "SELL"])
ai1_reason = "RSI is 35, market Oversold hai. Upar jayega." if ai1_vote == "BUY" else "RSI 78 hai, Overbought hai."

ai2_vote = random.choice(["BUY", "SELL", "SELL"])
ai2_reason = "Fed ne interest rate kam kiya hai, Dollar weak." if ai2_vote == "BUY" else "US Dollar strong ho raha hai."

ai3_vote = random.choice(["BUY", "BUY", "HOLD"])
ai3_reason = "Market me Fear hai, log Gold khareed rahe hain."

ai4_vote = random.choice(["BUY", "HOLD", "HOLD"])
ai4_reason = "Risk zyada hai, SL chhota rakho." if ai4_vote == "HOLD" else "Risk kam hai, safe entry hai."

with col1:
    st.markdown(f"<div class='ai-card'><b>🤖 AI-1: TECHNICAL EXPERT</b><br>Vote: <b style='color: {'green' if ai1_vote=='BUY' else 'red'}'>{ai1_vote}</b><br><small>{ai1_reason}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai-card'><b>🤖 AI-2: NEWS ANALYST</b><br>Vote: <b style='color: {'green' if ai2_vote=='BUY' else 'red'}'>{ai2_vote}</b><br><small>{ai2_reason}</small></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai-card'><b>🤖 AI-3: SENTIMENT GURU</b><br>Vote: <b style='color: {'green' if ai3_vote=='BUY' else 'orange'}'>{ai3_vote}</b><br><small>{ai3_reason}</small></div>", unsafe_allow_html=True)

with col2:
    st.markdown(f"<div class='ai-card'><b>🤖 AI-4: RISK MANAGER</b><br>Vote: <b style='color: {'green' if ai4_vote=='BUY' else 'orange'}'>{ai4_vote}</b><br><small>{ai4_reason}</small></div>", unsafe_allow_html=True)
    votes = [ai1_vote, ai2_vote, ai3_vote, ai4_vote]
    buy_count = votes.count("BUY")
    sell_count = votes.count("SELL")
    final = "BUY" if buy_count >= 3 else "SELL" if sell_count >= 2 else "HOLD"
    confidence = int((max(buy_count, sell_count)/4)*100)

    st.markdown(f"<div class='ai-card'><b>🤖 AI-5: BOSS (Final Decision)</b><br>4 AI ki baat suni...<br><small>{buy_count} BUY, {sell_count} SELL votes mile</small></div>", unsafe_allow_html=True)

st.markdown("---")
st.markdown(f"<div class='final-card'><h2>FINAL VERDICT: {final}</h2><p>Confidence: {confidence}% | {buy_count} AI Agree</p><p>Entry: ${price:.2f} | SL: ${price-5:.2f} | TP: ${price+10:.2f}</p></div>", unsafe_allow_html=True)

if st.button("🔄 Nayi Meeting Shuru Karo"):
    st.rerun()

st.caption("Disclaimer: Ye AI Council educational purpose ke liye hai. Tauric Research style free clone.")
