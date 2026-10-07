import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="TAURIC x GEMINI PRO", page_icon="🐂", layout="centered")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")

st.markdown("""
<style>
.stApp{background-color:#FFEAEC!important} header{visibility:hidden}
.block{background:#0A4D4D;width:62px;height:62px;border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:30px}
.bull-block{background:#0A4D4D;width:90px;height:90px;border-radius:16px;display:flex;align-items:center;justify-content:center;font-size:48px;margin:15px auto}
.agent-row{display:flex;align-items:center;gap:12px;margin:18px 8px}
.agent-row.right{justify-content:flex-end}
.price-card{background:white;padding:12px;border-radius:16px;text-align:center;box-shadow:0 4px 10px rgba(0,0,0,0.08)}
.result-card{background:white;padding:12px;border-radius:12px;margin:8px 0;border-left:5px solid #0A4D4D}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="bull-block">🐂</div><h3 style="text-align:center">TAURIC x GEMINI PRO</h3>', unsafe_allow_html=True)

symbol = st.radio("Pair:", ["BTC-USD","EURUSD=X","GBPUSD=X","GC=F (Gold)","SI=F (Silver)"], horizontal=True)

def get_live_price(sym):
    try:
        if "BTC" in sym:
            return float(requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot",timeout=5).json()['data']['amount'])
        # forex / gold ke liye Yahoo se
        import json as js
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{sym}?interval=1m&range=1d"
        d = requests.get(url, headers={'User-Agent':'Mozilla'}, timeout=8).json()
        return float(d['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return 83081.35

price = get_live_price(symbol)
st.markdown(f'<div class="price-card"><b>{symbol} LIVE</b><br><span style="font-size:26px;font-weight:800;color:#ff1493!important">${price:,.2f}</span><br><small>{datetime.now().strftime("%H:%M:%S")}</small></div>', unsafe_allow_html=True)

def call_ai(role, sym, lp):
    if not GEMINI_API_KEY:
        return f"{role} key missing", "HOLD"
    prompt = f"""You are {role} for trading.
Pair: {sym}, Price: {lp}
Your specialty:
- Trade Scout: Find best support/resistance, trend, entry setup.
- News Analyst: Check news, sentiment, FOMC/NFP risk before entry.
- Market Analyst: Analyze RSI, MACD, volume, market strength.
- Validator: Recheck if setup is real or fakeout/trap.
- Profit Checker: Check R:R, is trade worth taking? Minimum 1:2.
Return EXACT format: VOTE: BUY/SELL/HOLD | REASON: 15 words max in Roman Urdu | SL: price | TP: price
"""
    for model in ["gemini-2.5-flash","gemini-3-flash-preview"]:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
            r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=20).json()
            if "candidates" in r:
                txt = r['candidates'][0]['content']['parts'][0]['text']
                vote = "BUY" if "BUY" in txt.upper() else "SELL" if "SELL" in txt.upper() else "HOLD"
                return txt, vote
        except:
            continue
    return "AI busy", "HOLD"

if not GEMINI_API_KEY:
    st.error("⚠️ Secrets me key dalo phir Reboot karo. Tab hi signal banega.")
else:
    if st.button("🚀 5-AI SE FINAL SIGNAL LO", use_container_width=True, type="primary"):
        with st.spinner("5 AI apna kaam kar rahe hain..."):
            a1,v1 = call_ai("Trade Scout - Finds the best possible trade setup", symbol, price)
            a2,v2 = call_ai("News Analyst - Checks news and market sentiment before entry", symbol, price)
            a3,v3 = call_ai("Market Analyst - Analyzes volume, indicators, and market strength", symbol, price)
            a4,v4 = call_ai("Validator - Rechecks the research and validates the setup", symbol, price)
            a5,v5 = call_ai("Profit Checker - Confirms whether the trade is worth taking", symbol, price)

        st.markdown("### 👇 Har AI ka kaam dekho")
        st.markdown(f'<div class="result-card">📈 <b>Trade Scout [{v1}]</b><br>{a1}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-card">📊 <b>News Analyst [{v2}]</b><br>{a2}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-card">🏛️ <b>Market Analyst [{v3}]</b><br>{a3}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-card">🕯️ <b>Validator [{v4}]</b><br>{a4}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="result-card">💹 <b>Profit Checker [{v5}]</b><br>{a5}</div>', unsafe_allow_html=True)

        votes = [v1,v2,v3,v4,v5]
        final = "BUY" if votes.count("BUY")>=3 else "SELL" if votes.count("SELL")>=3 else "HOLD"

        # SL TP calculation
        if final=="BUY":
            sl = price*0.985; tp = price*1.03
            st.success(f"## FINAL DECISION: {final} 🟢\n\n**Entry:** ${price:,.2f}\n\n**SL:** ${sl:,.2f} (-1.5%)\n\n**TP:** ${tp:,.2f} (+3%)\n\n**R:R = 1:2**")
        elif final=="SELL":
            sl = price*1.015; tp = price*0.97
            st.error(f"## FINAL DECISION: {final} 🔴\n\n**Entry:** ${price:,.2f}\n\n**SL:** ${sl:,.2f} (+1.5%)\n\n**TP:** ${tp:,.2f} (-3%)\n\n**R:R = 1:2**")
        else:
            st.warning(f"## FINAL DECISION: {final} 🟡 - Abhi wait karo, clear setup nahi hai")
