import streamlit as st
import requests
import google.generativeai as genai
from datetime import datetime

st.set_page_config(page_title="Tauric + Gemini - Live", page_icon="🐂", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #fff0f5; }
.ai-card { background: white; padding: 15px; border-radius: 15px; border-left: 5px solid #ff1493; margin: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
.ai-card * { color: black!important; }
.final-card { background: #ff1493; color: white; padding: 20px; border-radius: 20px; text-align: center; margin-top: 15px; }
.final-card * { color: white!important; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔑 Settings")
api_key = st.sidebar.text_input("Gemini API Key Yahan Paste Karo:", type="password")
st.sidebar.markdown("[API Key Free me yahan se lo](https://aistudio.google.com/app/apikey)")

st.markdown("<h1 style='text-align:center;color:#ff1493;'>🐂 TAURIC x GEMINI</h1><h3 style='text-align:center;color:black;'>Real AI Council - Unlimited Signals</h3>", unsafe_allow_html=True)

symbol = st.selectbox("Pair Select Karo:", ["BTC-USD", "EURUSD=X", "GBPUSD=X", "GC=F", "SI=F"], index=0)

def get_live_price(sym):
    if sym == "BTC-USD":
        try:
            r = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", timeout=6).json()
            return float(r['data']['amount'])
        except: pass
        try:
            r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=6).json()
            return float(r['bitcoin']['usd'])
        except: return 84013.0
    if sym in ["EURUSD=X", "GBPUSD=X"]:
        try:
            base = "EUR" if "EUR" in sym else "GBP"
            r = requests.get(f"https://api.frankfurter.app/latest?from={base}&to=USD", timeout=6).json()
            return float(r['rates']['USD'])
        except: return 1.1186 if "EUR" in sym else 1.2635
    if sym == "GC=F":
        try:
            r = requests.get("https://api.gold-api.com/price/XAU", timeout=6).json()
            return float(r['price'])
        except: return 2655.20
    if sym == "SI=F":
        try:
            r = requests.get("https://api.gold-api.com/price/XAG", timeout=6).json()
            return float(r['price'])
        except: return 32.15

price = get_live_price(symbol)

if symbol in ["EURUSD=X", "GBPUSD=X"]:
    st.metric(f"{symbol} LIVE", f"{price:.5f}")
else:
    st.metric(f"{symbol} LIVE", f"${price:,.2f}")

def get_gemini_analysis(pair, live_price, role):
    if not api_key:
        return "API Key Dalna Zaroori Hai", "HOLD"
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"You are {role} expert trader. Pair {pair} price {live_price}. Give ONLY ONE WORD: BUY or SELL or HOLD. Then give 1 short reason in 10 words. Format: WORD | Reason"
        res = model.generate_content(prompt)
        text = res.text.strip()
        if "BUY" in text.upper(): vote = "BUY"
        elif "SELL" in text.upper(): vote = "SELL"
        else: vote = "HOLD"
        return text, vote
    except Exception as e:
        return f"Error: {e}", "HOLD"

st.markdown("---")
st.subheader("🔴 LIVE GEMINI COUNCIL MEETING")

if st.button("🔄 Naya Signal Generate Karo - Gemini Se"):
    st.rerun()

if api_key:
    with st.spinner("Gemini AI Council soch raha hai..."):
        t1, v1 = get_gemini_analysis(symbol, price, "Technical Analysis RSI MACD")
        t2, v2 = get_gemini_analysis(symbol, price, "Fundamental News Analysis")
        t3, v3 = get_gemini_analysis(symbol, price, "Market Sentiment Analysis")
        t4, v4 = get_gemini_analysis(symbol, price, "Risk Management")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='ai-card'><b>🤖 AI-1 TECHNICAL</b><br>Vote: <b>{v1}</b><br><small>{t1}</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-card'><b>🤖 AI-3 SENTIMENT</b><br>Vote: <b>{v3}</b><br><small>{t3}</small></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='ai-card'><b>🤖 AI-2 NEWS</b><br>Vote: <b>{v2}</b><br><small>{t2}</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-card'><b>🤖 AI-4 RISK</b><br>Vote: <b>{v4}</b><br><small>{t4}</small></div>", unsafe_allow_html=True)

    votes = [v1, v2, v3, v4]
    buy_c = votes.count("BUY")
    sell_c = votes.count("SELL")
    final = "BUY" if buy_c >= 3 else "SELL" if sell_c >= 2 else "HOLD"
    conf = 90 if votes.count(final)>=3 else 70

    # R:R 1:2 Fixed
    if final == "BUY":
        sl = price * 0.99
        tp = price * 1.02
    elif final == "SELL":
        sl = price * 1.01
        tp = price * 0.98
    else:
        sl = price * 0.99
        tp = price * 1.01

    def fmt(p): return f"${p:,.2f}" if p>100 else f"{p:.5f}"

    st.markdown(f"<div class='final-card'><h2>FINAL VERDICT: {final}</h2><p>Confidence: {conf}% | Gemini Powered</p><p>Entry: {fmt(price)} | SL: {fmt(sl)} | TP: {fmt(tp)} | R:R 1:2</p></div>", unsafe_allow_html=True)
else:
    st.warning("👈 Sidebar me Gemini API Key dalo, phir Gemini live analysis dega! Key free hai.")
        
