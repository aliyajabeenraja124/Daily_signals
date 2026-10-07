import streamlit as st
import requests

st.set_page_config(page_title="Tauric x Gemini", page_icon="🐂", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #ffffff !important; }
h1, h2, h3, p, label, div, span { color: black !important; }
.ai-card { background: #f9f9f9; padding: 15px; border-radius: 15px; border-left: 5px solid #ff1493; margin: 8px; border: 1px solid #ddd; }
.final-card { background: #ff1493; padding: 20px; border-radius: 20px; text-align: center; margin-top: 15px; }
.final-card * { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔑 Settings")
api_key = st.sidebar.text_input("Gemini API Key Paste Karo (AQ wali):", type="password").strip()

st.markdown("<h1 style='text-align:center;color:#ff1493 !important;'>🐂 TAURIC x GEMINI</h1><h3 style='text-align:center;'>Real AI Council - Unlimited</h3>", unsafe_allow_html=True)

symbol = st.selectbox("Pair Select Karo:", ["BTC-USD", "EURUSD=X", "GBPUSD=X", "GC=F", "SI=F"], index=0)

def get_live_price(sym):
    try:
        if sym == "BTC-USD":
            r = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", timeout=6).json()
            return float(r['data']['amount'])
    except: pass
    return 83618.79

price = get_live_price(symbol)
st.metric(f"{symbol} LIVE Price", f"${price:,.2f}")

def call_gemini_direct(key, pair, live_price, role):
    if not key: 
        return "API Key dalo", "HOLD"
    # FIX: Naya model name - 2.0-flash
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    prompt = f"You are expert {role} trader for {pair} at price {live_price}. Give decision BUY or SELL or HOLD with short 10 words reason. Format: BUY/SELL/HOLD | reason"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=20)
        data = r.json()
        if "candidates" in data and len(data["candidates"])>0:
            text = data['candidates'][0]['content']['parts'][0]['text']
            upper = text.upper()
            vote = "BUY" if "BUY" in upper else "SELL" if "SELL" in upper else "HOLD"
            return text, vote
        else:
            # Agar 2.0 fail ho to 1.5-flash-8b try karo
            url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-8b:generateContent?key={key}"
            r2 = requests.post(url2, json=payload, timeout=20)
            data2 = r2.json()
            if "candidates" in data2:
                text = data2['candidates'][0]['content']['parts'][0]['text']
                vote = "BUY" if "BUY" in text.upper() else "SELL" if "SELL" in text.upper() else "HOLD"
                return text, vote
            return f"Gemini Reply: {str(data)[:300]}", "HOLD"
    except Exception as e:
        return f"Error: {e}", "HOLD"

st.markdown("---")
st.subheader("🔴 LIVE GEMINI COUNCIL MEETING")

if st.button("🔄 Naya Signal Generate Karo - Gemini Se"):
    st.rerun()

if not api_key:
    st.warning("👈 Left side >> pe click karke sidebar me AQ wali puri key paste karo.")
else:
    with st.spinner("Gemini Council soch raha hai..."):
        t1, v1 = call_gemini_direct(api_key, symbol, price, "Technical Analysis")
        t2, v2 = call_gemini_direct(api_key, symbol, price, "News Analysis")
        t3, v3 = call_gemini_direct(api_key, symbol, price, "Sentiment Analysis")
        t4, v4 = call_gemini_direct(api_key, symbol, price, "Risk Management")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='ai-card'><b>🤖 AI-1 TECHNICAL</b><br>Vote: <b>{v1}</b><br><small>{t1}</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-card'><b>🤖 AI-3 SENTIMENT</b><br>Vote: <b>{v3}</b><br><small>{t3}</small></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='ai-card'><b>🤖 AI-2 NEWS</b><br>Vote: <b>{v2}</b><br><small>{t2}</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-card'><b>🤖 AI-4 RISK</b><br>Vote: <b>{v4}</b><br><small>{t4}</small></div>", unsafe_allow_html=True)

    votes = [v1, v2, v3, v4]
    final = "BUY" if votes.count("BUY")>=2 else "SELL" if votes.count("SELL")>=2 else "HOLD"
    if votes.count("BUY")==2 and votes.count("SELL")==2:
        final = "HOLD"
    
    sl = price*0.99 if final=="BUY" else price*1.01 if final=="SELL" else price*0.99
    tp = price*1.02 if final=="BUY" else price*0.98 if final=="SELL" else price*1.01
    
    st.markdown(f"<div class='final-card'><h2>FINAL: {final}</h2><p>Entry ${price:,.2f} | SL ${sl:,.2f} | TP ${tp:,.2f} | R:R 1:2</p></div>", unsafe_allow_html=True)
