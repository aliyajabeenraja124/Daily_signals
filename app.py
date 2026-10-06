
            
    
import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="Daily Stock Signal AI")
st.title("📈 Daily Stock Signal AI")

symbol = st.text_input("Stock Symbol:", "BTC-USD").strip().upper()
if not symbol:
    symbol = "BTC-USD"

# BTC ko BTC-USD me auto convert
if symbol == "BTC":
    symbol = "BTC-USD"
if symbol == "GOLD":
    symbol = "GC=F"
if symbol == "OIL":
    symbol = "CL=F"

if st.button("Aaj ka Signal Lo"):
    try:
        # API Key
        GEMINI_KEY = st.secrets["GEMINI_KEY"]
        client = genai.Client(api_key=GEMINI_KEY)
        
        # Stock data
        st.write(f"Data la raha hu {symbol} ka...")
        data = yf.Ticker(symbol).history(period="5d")
        
        if data.empty:
            st.error(f"{symbol} ka data nahi mila. Sahi symbol likho jaise BTC-USD, GC=F, RELIANCE.NS")
        else:
            last_price = data['Close'].iloc[-1]
            st.success(f"{symbol} Price: ${last_price:.2f}")
            
            prompt = f"Stock {symbol} ka price {last_price} hai, last 5 din ka data {data['Close'].tolist()} hai. Is pe BUY, SELL ya HOLD ka signal do with short reason."
            
            resp = client.models.generate_content(
                model="gemini-1.5-flash", 
                contents=prompt
            )
            st.markdown("### 🤖 AI Signal:")
            st.write(resp.text)
            
    except Exception as e:
        st.error(f"Error: {e}")
        st.info("Check karo: 1) Secrets me GEMINI_KEY sahi hai? 2) Symbol sahi hai?")
