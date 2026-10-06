import streamlit as st
import yfinance as yf
from google import genai

st.set_page_config(page_title="Daily Signal AI", page_icon="📈")
st.title("📈 Daily Signal AI - BTC / Gold / Oil")

st.markdown("Symbol likho aur signal lo:")
symbol_input = st.text_input("Symbol:", "BTC-USD").strip().upper()

# Auto convert
if symbol_input == "BTC":
    symbol = "BTC-USD"
elif symbol_input == "GOLD":
    symbol = "GC=F"
elif symbol_input == "OIL":
    symbol = "CL=F"
else:
    symbol = symbol_input

st.info(f"Aap dekh rahe ho: **{symbol}** | Gold=GC=F, Oil=CL=F, BTC=BTC-USD")

if st.button("Aaj ka Signal Lo 🔥"):
    try:
        key = st.secrets["GEMINI_KEY"]
        client = genai.Client(api_key=key)
        
        st.write(f"⏳ {symbol} ka data la raha hu...")
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="10d")
        
        if data.empty:
            st.error("Data nahi mila! Sahi symbol likho: BTC-USD, ETH-USD, GC=F, CL=F, AAPL")
        else:
            price = data['Close'].iloc[-1]
            st.success(f"Current Price: ${price:.2f}")
            st.line_chart(data['Close'])

            prompt = f"""
            Symbol {symbol} ka current price ${price:.2f} hai.
            Last 10 days closing: {data['Close'].tolist()}.
            Is par short BUY/SELL/HOLD signal do. 
            1. Signal 2. Reason 3. Risk. Urdu/Hindi mix me jawab do.
            """

            with st.spinner("AI soch raha hai..."):
                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=prompt
                )
            st.markdown("### 🤖 AI Signal:")
            st.write(response.text)

    except Exception as e:
        st.error(f"Error: {e}")
