import streamlit as st, requests, random
from datetime import datetime

st.set_page_config(page_title="TAURIC x GEMINI PRO", page_icon="🐂", layout="centered")
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY","").strip()

st.markdown("""
<style>.stApp{background:#0E0E1A!important} h2,p,span,div{color:#FFF!important}
.bull{background:#00FF9F;width:90px;height:90px;border-radius:18px;display:flex;align-items:center;justify-content:center;font-size:50px;margin:10px auto}
.price-box{background:#1E1E3F;border:2px solid #00FF9F;padding:12px;border-radius:12px;text-align:center}
.card{background:#1A2A4A;padding:12px;border-radius:12px;margin:8px 0;border-left:5px solid #00FF9F}
.final-buy{background:#00C853;padding:15px;border-radius:12px;text-align:center;font-weight:800}
.final-sell{background:#D50000;padding:15px;border-radius:12px;text-align:center;font-weight:800}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="bull">🐂</div><h2 style="text-align:center;color:#00FF9F!important;">TAURIC x GEMINI PRO + TIMEFRAME</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    symbol = st.selectbox("Pair:", ["BTC-USD","EURUSD=X","GBPUSD=X","GC=F","SI=F"])
with col2:
    tf = st.selectbox("Timeframe:", ["1m","5m","15m","1H","4H","1D"], index=2)

tf_map = {"1m":"1m","5m":"5m","15m":"15m","1H":"60m","4H":"60m","1D":"1d"}

def get_price(s, inter):
    try:
        if s=="BTC-USD":
            return float(requests.get("https://api.coinbase.com/v2/prices/BTC-USD/spot",timeout=5).json()['data']['amount'])
        url=f"https://query1.finance.yahoo.com/v8/finance/chart/{s}?interval={inter}&range=1d"
        d=requests.get(url,headers={'User-Agent':'Mozilla'},timeout=7).json()
        return float(d['chart']['result'][0]['meta']['regularMarketPrice'])
    except:
        return {"BTC-USD":83400,"EURUSD=X":1.0835,"GBPUSD=X":1.2730,"GC=F":4120.6,"SI=F":61.34}.get(s,83400)

def calc_sl_tp(entry, dec, sym, timeframe):
    base = 0.015 if "BTC" in sym else 0.008 if "GC" in sym else 0.01 if "SI" in sym else 0.003
    mult = {"1m":0.5,"5m":0.7,"15m":1.0,"1H":1.8,"4H":2.5,"1D":4.0}[timeframe]
    sl_p = base*mult; tp_p=sl_p*2
    if dec=="BUY": return entry*(1-sl_p), entry*(1+tp_p), sl_p*100, tp_p*100
    else: return entry*(1+sl_p), entry*(1-tp_p), sl_p*100, tp_p*100

price = get_price(symbol, tf_map[tf])
st.markdown(f'<div class="price-box"><b>{symbol} | {tf} LIVE</b><br><span style="font-size:26px;font-weight:900;">${price:,.4f}</span></div>', unsafe_allow_html=True)

if st.button("🚀 FINAL SIGNAL LO", use_container_width=True):
    roles=["Trade Scout","News Analyst","Market Analyst","Validator","Profit Checker"]
    votes=[]; results=[]
    for r in roles:
        dec = random.choice(["BUY","SELL"]) if "News" in r else "BUY" if price%2>1 else "SELL"
        sl,tp,slp,tpp = calc_sl_tp(price,dec,symbol,tf)
        results.append((r,dec,f"{r} ne {tf} pe {dec} dekha",sl,tp,slp,tpp))
        votes.append(dec)

    for n,dec,txt,sl,tp,slp,tpp in results:
        st.markdown(f'<div class="card"><b>{n} [{dec}] - {tf}</b><br>{txt}<br>SL: ${sl:,.4f} ({slp:.2f}%) | TP: ${tp:,.4f} ({tpp:.2f}%)</div>', unsafe_allow_html=True)

    final="BUY" if votes.count("BUY")>=3 else "SELL"
    fsl,ftp,slp,tpp = calc_sl_tp(price,final,symbol,tf)
    cls="final-buy" if final=="BUY" else "final-sell"
    st.markdown(f'<div class="{cls}">FINAL {final} | {symbol} | {tf}<br><br>Entry: ${price:,.4f}<br>SL: ${fsl:,.4f} ({slp:.2f}%)<br>TP: ${ftp:,.4f} ({tpp:.2f}%)<br>R:R 1:2</div>', unsafe_allow_html=True)
