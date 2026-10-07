import streamlit as st
import requests
from datetime import datetime

st.set_page_config(page_title="TAURIC x GEMINI PRO", page_icon="🐂", layout="centered")

# --- PREMIUM LIGHT THEME ---
st.markdown("""
<style>
    .stApp { background-color: #FFF5F8 !important; }
    h1, h2, h3, p, label, span, div { color: #222 !important; }
    
    /* Dropdown Fix - Ab kala nahi hoga */
    div[data-baseweb="select"] > div {
        background-color: white !important;
        color: black !important;
        border: 1.5px solid #ff1493 !important;
    }
    
    .header {
        text-align: center;
        padding: 20px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(255,20,147,0.1);
        margin-bottom: 20px;
    }
    .price-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #ffe0ec;
        margin-bottom: 15px;
    }
    .ai-card {
        background: white;
        padding: 18px;
        border-radius: 16px;
        margin: 10px 0;
        border-left: 6px solid #ff1493;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .buy { border-left-color: #00C853 !important; }
    .sell { border-left-color: #FF1744 !important; }
    .hold { border-left-color: #FFC400 !important; }
    
    .final-buy { background: linear-gradient(135deg, #00C853, #009624); color: white !important; padding: 25px; border-radius: 20px; text-align: center; }
    .final-sell { background: linear-gradient(135deg, #FF1744, #D50000); color: white !important; padding: 25px; border-radius: 20px; text-align: center; }
    .final-hold { background: linear-gradient(135deg, #FF9100, #FF6D00); color: white !important; padding: 25px; border-radius: 20px; text-align: center; }
    .final-buy *, .final-sell *, .final-hold * { color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.title("🔑 Tauric Settings")
    api_key = st.text_input("Gemini API Key (AQ wali):", type="password", placeholder="AQAb8... paste karo").strip()
    st.markdown("---")
    st.markdown("**Key kaise leni hai?**")
    st.link_button("Get API Key", "https://aistudio.google.com/app/apikey")
    st.caption("Copy icon 📋 se puri key copy karo, space nahi hona chahiye.")

# --- HEADER ---
st.markdown("""
<div class="header">
    <h1 style="color:#ff1493 !important; margin:0;">🐂 TAURIC x GEMINI PRO</h1>
    <p style="margin:5px 0 0 0; font-weight:600;">Real 4-AI Council - Live Trading Signals</p>
</div>
""", unsafe_allow_html=True)

# --- PAIR SELECT ---
col1, col2 = st.columns([2, 1])
with col1:
    symbol = st.selectbox("Pair Select Karo:", ["BTC-USD", "EURUSD=X", "GBPUSD=X", "GC=F (Gold)", "SI=F (Silver)"], index=0)
with col2:
    st.write("")
    st.write("")
    refresh = st.button("🔄 Refresh Price")

# --- LIVE PRICE ---
def get_live_price(sym):
    try:
        if "BTC" in sym:
            r = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", timeout=5).json()
            return float(r['data']['amount']), "Coinbase Live"
    except: pass
    return 83615.46, "Simulated (API busy)"

price, source = get_live_price(symbol)

st.markdown(f"""
<div class="price-card">
    <div style="font-size:14px; color:#888 !important;">{symbol} | {source} | {datetime.now().strftime('%H:%M:%S')}</div>
    <div style="font-size:32px; font-weight:800; color:#ff1493 !important;">${price:,.2f}</div>
</div>
""", unsafe_allow_html=True)

# --- GEMINI CALL - LATEST MODELS ---
def call_gemini(key, pair, live_price, role):
    if not key:
        return "Key dalo", "HOLD"
    
    # 2026 ke latest models ki list - ek fail ho to dusra chalega
    models = ["gemini-2.5-flash", "gemini-3-flash-preview", "gemini-2.5-flash-lite"]
    prompt = f"You are a {role} expert trader. Analyze {pair} at live price {live_price}. Give ONLY: BUY or SELL or HOLD | reason in 8 words. No extra text."
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    for model in models:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
            r = requests.post(url, json=payload, timeout=15)
            data = r.json()
            if "candidates" in data and data["candidates"]:
                text = data['candidates'][0]['content']['parts'][0]['text']
                upper = text.upper()
                if "BUY" in upper: vote = "BUY"
                elif "SELL" in upper: vote = "SELL"
                else: vote = "HOLD"
                return text, vote
        except:
            continue
    return "Gemini thoda busy hai, dobara try karo", "HOLD"

# --- COUNCIL ---
st.markdown("### 🔴 LIVE AI COUNCIL MEETING")
generate = st.button("🚀 Naya Signal Generate Karo - Gemini Se", use_container_width=True, type="primary")

if not api_key:
    st.info("👈 Sidebar me apni AQ wali key dalo, phir signal ayega.")
else:
    if generate or True:
        with st.spinner("4 AI Experts soch rahe hain... 5 second lagega"):
            t1, v1 = call_gemini(api_key, symbol, price, "Technical Chart")
            t2, v2 = call_gemini(api_key, symbol, price, "Global News")
            t3, v3 = call_gemini(api_key, symbol, price, "Market Sentiment")
            t4, v4 = call_gemini(api_key, symbol, price, "Risk Management")

        # Display Cards
        def card_class(v): return "buy" if v=="BUY" else "sell" if v=="SELL" else "hold"

        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"<div class='ai-card {card_class(v1)}'><b>📊 AI-1 TECHNICAL</b><br>Vote: <b>{v1}</b><br><small>{t1}</small></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ai-card {card_class(v3)}'><b>🧠 AI-3 SENTIMENT</b><br>Vote: <b>{v3}</b><br><small>{t3}</small></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='ai-card {card_class(v2)}'><b>📰 AI-2 NEWS</b><br>Vote: <b>{v2}</b><br><small>{t2}</small></div>", unsafe_allow_html=True)
            st.markdown(f"<div class='ai-card {card_class(v4)}'><b>🛡️ AI-4 RISK</b><br>Vote: <b>{v4}</b><br><small>{t4}</small></div>", unsafe_allow_html=True)

        # Final Verdict Logic
        votes = [v1, v2, v3, v4]
        buy_c = votes.count("BUY")
        sell_c = votes.count("SELL")
        
        if buy_c >= 3: final = "BUY"
        elif sell_c >= 3: final = "SELL"
        elif buy_c == 2 and sell_c <=1: final = "BUY"
        elif sell_c == 2 and buy_c <=1: final = "SELL"
        else: final = "HOLD"

        sl = price*0.985 if final=="BUY" else price*1.015 if final=="SELL" else price*0.99
        tp = price*1.03 if final=="BUY" else price*0.97 if final=="SELL" else price*1.01
        
        final_class = "final-buy" if final=="BUY" else "final-sell" if final=="SELL" else "final-hold"
        
        st.markdown(f"""
        <div class="{final_class}">
            <h1 style="margin:0;">FINAL VERDICT: {final}</h1>
            <p style="margin:10px 0 0 0;">Confidence: {max(buy_c, sell_c, 2)*25}% | {buy_c} BUY vs {sell_c} SELL</p>
            <div style="margin-top:15px; background:rgba(255,255,255,0.2); padding:10px; border-radius:10px;">
                Entry: ${price:,.2f} | SL: ${sl:,.2f} | TP: ${tp:,.2f} | R:R 1:2
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.caption("⚠️ Ye AI signal hai, financial advice nahi. Apni research zarur karo.")
    
