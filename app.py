import streamlit as st
import requests

st.set_page_config(page_title="Tauric x Gemini", page_icon="🐂", layout="wide")

st.markdown("""
<style>
.stApp { background-color: #ffffff !important; }
h1, h2, h3, p, label, div { color: black !important; }
.ai-card { background: #f8f8f8; padding: 15px; border-radius: 15px; border-left: 5px solid #ff1493; margin: 8px; border: 1px solid #ddd; }
.final-card { background: #ff1493; padding: 20px; border-radius: 20px; text-align: center; margin-top: 15px; }
.final-card * { color: white !important; }
</style>
""", unsafe_allow_html=True)

st.sidebar.title("🔑 Settings")
api_key = st.sidebar.text_input("Gemini API Key Paste Karo:", type="password").strip()

st.markdown("<h1 style='text-align:center;color:#ff1493;'>🐂 TAURIC x GEMINI</h1><h3 style='text-align:center;'>Real AI Council - Unlimited</h3>", unsafe_allow_html=True)

symbol = st.selectbox("Pair Select Karo:", ["BTC-USD", "EURUSD=X", "GBPUSD=X", "GC=F"], index=0)

def get_live_price(sym):
    try:
        if sym == "BTC-USD":
            r = requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot", timeout=6).json()
            return float(r['data']['amount'])
    except: return 83570.90
    return 83570.90

price = get_live_price(symbol)
st.metric(f"{symbol} LIVE Price", f"${price:,.2f}")

def call_gemini_direct(key, pair, live_price, role):
    if not key: return "API Key dalo", "HOLD"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={key}"
    prompt = f"You are {role} trader. Pair {pair} price {live_price}. Reply: BUY or SELL or HOLD | reason in 10 words"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        r = requests.post(url, json=payload, timeout=15)
        data = r.json()
        if "candidates" in data:
            text = data['candidates'][0]['content']['parts'][0]['text']
            vote = "BUY" if "BUY" in text.upper() else "SELL" if "SELL" in text.upper() else "HOLD"
            return text, vote
        else:
            return f"Error: {str(data)[:200]}", "HOLD"
    except Exception as e:
        return f"Error: {e}", "HOLD"

st.markdown("---")
st.subheader("🔴 LIVE GEMINI COUNCIL MEETING")

if st.button("🔄 Naya Signal Generate Karo - Gemini Se"):
    st.rerun()

if not api_key:
    st.warning("👈 Upar left me >> pe click karo, sidebar khulega, wahan AQ wali key dalo.")
else:
    with st.spinner("Gemini soch raha hai..."):
        t1, v1 = call_gemini_direct(api_key, symbol, price, "Technical")
        t2, v2 = call_gemini_direct(api_key, symbol, price, "News")
        t3, v3 = call_gemini_direct(api_key, symbol, price, "Sentiment")
        t4, v4 = call_gemini_direct(api_key, symbol, price, "Risk")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"<div class='ai-card'><b>🤖 AI-1 TECHNICAL</b><br>Vote: <b>{v1}</b><br><small>{t1}</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-card'><b>🤖 AI-3 SENTIMENT</b><br>Vote: <b>{v3}</b><br><small>{t3}</small></div>", unsafe_allow_html=True)
    with c2:
        st.markdown(f"<div class='ai-card'><b>🤖 AI-2 NEWS</b><br>Vote: <b>{v2}</b><br><small>{t2}</small></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='ai-card'><b>🤖 AI-4 RISK</b><br>Vote: <b>{v4}</b><br><small>{t4}</small></div>", unsafe_allow_html=True)

    votes = [v1, v2, v3, v4]
    final = "BUY" if votes.count("BUY")>=3 else "SELL" if votes.count("SELL")>=2 else "HOLD"
    sl = price*0.99 if final=="BUY" else price*1.01
    tp = price*1.02 if final=="BUY" else price*0.98
    st.markdown(f"<div class='final-card'><h2>FINAL: {final}</h2><p>Entry ${price:,.2f} | SL ${sl:,.2f} | TP ${tp:,.2f}</p></div>", unsafe_allow_html=True)
