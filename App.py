import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="Daily Stock Signal", page_icon="📈")
st.title("📈 Daily Stock Signal AI")

MY_KEY = st.secrets.get("GEMINI_KEY", "")
if not MY_KEY:
    MY_KEY = st.text_input("Apni Gemini API Key dalo:", type="password")

client = genai.Client(api_key=MY_KEY) if MY_KEY else None
ticker = st.text_input("Stock Symbol:", "AAPL").upper()

if st.button("Aaj ka Signal Lo"):
    if not client:
        st.error("Key dalo!")
    else:
        with st.spinner("Loading..."):
            data = yf.download(ticker, period="1mo")
            prices = data['Close'].tail(10).values.flatten().tolist()
            prompt = f"Stock {ticker} prices {prices}. Give BUY/SELL/HOLD signal in 3 lines Urdu Roman."
            resp = client.models.generate_content(model="gemini-3-flash-preview", contents=prompt)
            st.success(resp.text)
