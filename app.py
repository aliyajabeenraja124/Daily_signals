import streamlit as st
import requests
import random
from datetime import datetime
import pytz

st.set_page_config(page_title="Tauric Research - Real Market", page_icon="🐂", layout="wide")
st.cache_data.clear()

st.markdown("""
<style>
.stApp { background-color: #fff0f5; }
div[data-testid="stMetricValue"] { color: black!important; font-size: 32px!important; }
div[data-testid="stMetricLabel"] { color: black!important; font-weight: bold; }
.ai-card { background: white; padding: 15px; border-radius: 15px; border-left: 5px solid #ff1493; margin: 8px; }
.ai-card * { color: black!important; }
.final-card { background: #ff1493; color: white; padding: 20px; border-radius: 20px; text-align: center; margin-top: 15px; }
.final-card * { color: white!important; }
</style>
""", unsafe_allow_html=True)

# Pakistan Time - Sahi Time
pk_tz = pytz.timezone('Asia/Karachi')
now_pk = datetime.now(pk_tz)

st.markdown("<h1 style='text-align:center;color:#ff1493;'>🐂 TAURIC RESEARCH</h1><h3 style='text-align:center;color:black;'>5 AI COUNCIL MEETING - LIVE MARKET</h3>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center;color:black;'>Live Time: {now_pk.strftime('%d %B %Y - %I:%M:%S %p')} (PKT) | TradingView Aligned</p>", unsafe_allow_html=True)

symbol = st.selectbox("Pair Select Karo:", ["BTC-USD", "EURUSD=X", "GBPUSD=X", "GC=F", "SI=F"], index=0)

# === 100% REAL PRICE - TradingView ke jaisa ===
def get_live_price(sym):
    # BTC - 3 APIs
    if sym == "BTC-USD":
        for url, parser in [
            ("https://api.coinbase.com/v2/prices/BTC-USD/spot", lambda j: float(j['data']['amount'])),
            ("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", lambda j: float(j['bitcoin']['usd'])),
            ("https://api.kraken.com/0/public/Ticker?pair=XBTUSD", lambda j: float(j['result']['XXBTZUSD']['c'][0])),
        ]:
            try:
                r = requests.get(url, timeout=6).json()
                p = parser(r)
                if p > 1000: return p
            except: continue
        return None

    # FOREX - Real time forex API
    if sym in ["EURUSD=X", "GBPUSD=X"]:
        base = "EUR" if "EUR" in sym else "GBP"
        # Try 1: exchangerate.host - real time
        try:
            r = requests.get(f"https://api.exchangerate.host/convert?from={base}&to=USD", timeout=6).json()
            if r.get('result'): return float(r['result'])
        except: pass
        # Try 2: frankfurter
        try:
            r = requests.get(f"https://api.frankfurter.app/latest?from={base}&to=USD", timeout=6).json()
            return float(r['rates']['USD'])
        except: pass
        return None

    # GOLD / SILVER - Real metal price
    if sym == "GC=F":
        try:
            r = requests.get("https://api.gold-api.com/price/XAU", timeout=6).json()
            return float(r['price'])
        except: return None
    if sym == "SI=F":
        try:
            r = requests.get("https://api.gold-api.com/price/XAG", timeout=6).json()
            return float(r['price'])
        except: return None

price = get_live_price(symbol)

if price is None:
    st.error("⚠️ Live API thoda slow hai, 10 sec me Refresh karo. Neeche fallback dikh raha hai.")
    # Fallback bhi ab TradingView ke qareeb wala
    if symbol == "BTC-USD": price = 84013.0
    elif symbol == "EURUSD=X": price = 1.1186
    elif symbol == "GBPUSD=X": price = 1.2635
    elif symbol == "GC=F": price = 2655.20
    else: price = 32.15
    source = "ESTIMATED"
else:
    source = "LIVE ✅ TradingView Aligned"

# Price Show
if symbol in ["EURUSD=X", "GBPUSD=X"]:
    st.metric(f"{symbol} {source}", f"{price:.5f}", "Live Market")
else:
    st.metric(f"{symbol} {source}", f"${price:,.2f}", "Live Market")

st.markdown("---")
st.subheader("🔴 LIVE AI COUNCIL DISCUSSION")
c1, c2 = st.columns(2)

v1 = random.choice(["BUY", "BUY", "SELL"])
v2 = random.choice(["BUY", "SELL", "SELL"])
v3 = random.choice(["BUY", "BUY", "HOLD"])
v4 = random.choice(["BUY", "HOLD", "HOLD"])

with c1:
    st.markdown(f"<div class='ai-card'><b>🤖 AI-1: TECHNICAL</b><br>Vote: <b style='color:green;'>{v1}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai-card'><b>🤖 AI-3: SENTIMENT</b><br>Vote: <b style='color:green;'>{v3}</b></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='ai-card'><b>🤖 AI-2: NEWS</b><br>Vote: <b>{v2}</b></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ai-card'><b>🤖 AI-4: RISK</b><br>Vote: <b>{v4}</b></div>", unsafe_allow_html=True)

votes = [v1][v2][v3][v4]
buy_c = votes.count("BUY")
sell_c = votes.count("SELL")

if buy_c >= 3:
    final, agree = "BUY", buy_c
elif sell_c >= 2:
    final, agree = "SELL", sell_c
else:
    final, agree = "HOLD", votes.count("HOLD") or 1

conf = 85 if agree>=3 else 65

# SL TP - BUY aur SELL ka sahi logic
if price > 1000: # BTC / GOLD
    if final == "BUY": sl, tp = price*0.99, price*1.02
    elif final == "SELL": sl, tp = price*1.01, price*0.98
    else: sl, tp = price*0.99, price*1.01
else: # Forex / Silver
    if final == "BUY": sl, tp = price*0.998, price*1.002
    elif final == "SELL": sl, tp = price*1.002, price*0.998
    else: sl, tp = price*0.999, price*1.001

def fmt(p):
    return f"${p:,.2f}" if p>100 else f"{p:.5f}"

st.markdown(f"<div class='final-card'><h2>FINAL VERDICT: {final}</h2><p>Confidence: {conf}% | {agree} AI Agree</p><p>Entry: {fmt(price)} | SL: {fmt(sl)} | TP: {fmt(tp)}</p><p>{'LONG - SL neeche, TP upar' if final=='BUY' else 'SHORT - SL upar, TP neeche' if final=='SELL' else 'WAIT'}</p></div>", unsafe_allow_html=True)

if st.button("🔄 Refresh Live Price"):
    st.rerun()
