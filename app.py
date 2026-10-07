import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="TAURIC x GEMINI PRO", page_icon="🐂", layout="centered")

# ===== KEY YAHAN NAHI, STREAMLIT SECRETS ME JAYEGI =====
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
# =======================================================

# --- PINK DESIGN - AAPKE SCREENSHOT JAISA ---
st.markdown("""
<style>
.stApp { background-color: #FFEAEC !important; }
header { visibility: hidden; }
h1, h2, h3, p, div, span, label { color: #0D3B3B !important; }
.block {
    background: #0A4D4D;
    width: 72px;
    height: 72px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 36px;
    box-shadow: 0 8px 18px rgba(0,0,0,0.25);
}
.bull-block {
    background: #0A4D4D;
    width: 110px;
    height: 110px;
    border-radius: 18px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 58px;
    box-shadow: 0 12px 24px rgba(0,0,0,0.3);
    margin: 20px auto;
}
.agent-row {
    display: flex;
    align-items: center;
    gap: 16px;
    margin: 22px 10px;
}
.agent-row.right { justify-content: flex-end; }
.agent-text { line-height: 1.2; }
.agent-text b { font-size: 16px; }
.agent-text span { font-size: 13px; color: #234F4F !important; }
.price-card {
    background: white;
    padding: 15px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    margin: 15px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="bull-block">🐂</div>', unsafe_allow_html=True)
st.markdown("<h2 style='text-align:center;'>TAURIC x GEMINI PRO</h2>", unsafe_allow_html=True)

symbol = st.radio("Pair:", ["BTC-USD", "EURUSD=X", "GBPUSD=X", "GC=F (Gold)", "SI=F (Silver)"], horizontal=True)

def get_price():
    try:
        r = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", timeout=5).json()
        return float(r['data']['amount'])
    except:
        return 83615.0

price = get_price()
st.markdown(f'<div class="price-card"><b>{symbol} LIVE</b><br><span style="font-size:28px; font-weight:800; color:#ff1493 !important;">${price:,.2f}</span><br><small>{datetime.now().strftime("%H:%M:%S")}</small></div>', unsafe_allow_html=True)

# 5 AI DISPLAY
st.markdown("""
<div class="agent-row">
    <div class="block">📈</div>
    <div class="agent-text"><b>Trade Scout:</b><br><span>Finds the best possible<br>trade setup.</span></div>
</div>
<div class="agent-row right">
    <div class="agent-text" style="text-align:right;"><b>News Analyst:</b><br><span>Checks news and market<br>sentiment before entry.</span></div>
    <div class="block">📊</div>
</div>
<div class="agent-row">
    <div class="block">🏛️</div>
    <div class="agent-text"><b>Market Analyst:</b><br><span>Analyzes volume, indicators,<br>and market strength.</span></div>
</div>
<div class="agent-row right">
    <div class="agent-text" style="text-align:right;"><b>Validator:</b><br><span>Rechecks the research<br>and validates the setup.</span></div>
    <div class="block">🕯️</div>
</div>
<div class="agent-row">
    <div class="block">💹</div>
    <div class="agent-text"><b>Profit Checker:</b><br><span>Confirms whether the<br>trade is worth taking.</span></div>
</div>
""", unsafe_allow_html=True)

def call_gemini(role_detail, pair, live_price):
    models = ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash-lite"]
    prompt = f"You are {role_detail}. Pair {pair} price {live_price}. Reply strictly: BUY or SELL or HOLD | 10 word reason"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    for m in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent?key={GEMINI_API_KEY}"
            r = requests.post(url, json=payload, timeout=15)
            d = r.json()
            if "candidates" in d:
                txt = d['candidates'][0]['content']['parts'][0]['text']
                vote = "BUY" if "BUY" in txt.upper() else "SELL" if "SELL" in txt.upper() else "HOLD"
                return txt, vote
        except:
            continue
    return "AI busy, retry", "HOLD"

st.markdown("---")

if not GEMINI_API_KEY:
    st.warning("⚠️ Streamlit > Settings > Secrets me jaake GEMINI_API_KEY paste karo, phir Reboot karo.")
    st.code('GEMINI_API_KEY = "AQAb8... tumhari puri key"')
else:
    if st.button("🚀 5-AI COUNCIL SE SIGNAL LO", use_container_width=True, type="primary"):
        with st.spinner("5 AI soch rahe hain..."):
            t1, v1 = call_gemini("Trade Scout - find best trade setup", symbol, price)
            t2, v2 = call_gemini("News Analyst - check news sentiment", symbol, price)
            t3, v3 = call_gemini("Market Analyst - analyze volume and indicators", symbol, price)
            t4, v4 = call_gemini("Validator - recheck and validate setup", symbol, price)
            t5, v5 = call_gemini("Profit Checker - confirm if trade worth taking", symbol, price)

        st.markdown("### 🔴 LIVE COUNCIL RESULT")
        st.info(f"📈 **Trade Scout [{v1}]**: {t1}")
        st.info(f"📊 **News Analyst [{v2}]**: {t2}")
        st.info(f"🏛️ **Market Analyst [{v3}]**: {t3}")
        st.info(f"🕯️ **Validator [{v4}]**: {t4}")
        st.info(f"💹 **Profit Checker [{v5}]**: {t5}")

        votes = [v1,v2,v3,v4,v5]
        final = "BUY" if votes.count("BUY")>=3 else "SELL" if votes.count("SELL")>=3 else "HOLD"
        
        if final=="BUY":
            st.success(f"## FINAL: {final} 🟢 | Entry ${price:,.2f} | SL ${price*0.985:,.2f} | TP ${price*1.03:,.2f}")
        elif final=="SELL":
            st.error(f"## FINAL: {final} 🔴 | Entry ${price:,.2f} | SL ${price*1.015:,.2f} | TP ${price*0.97:,.2f}")
        else:
            st.warning(f"## FINAL: {final} 🟡 | Wait")
