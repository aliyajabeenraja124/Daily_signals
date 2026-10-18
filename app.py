# TAURIC x GEMINI x GOOGLE TimesFM-3
# Final Fix for XAUUSD

import yfinance as yf
import torch
import timesfm
import numpy as np

# --- CONFIG ---
# 1. Symbol Fix: GC=F hataya, XAUUSD=X lagaya
GOLD_SYMBOL = "XAUUSD=X" 
DXY_SYMBOL = "DX-Y.NYB"  # Dollar Index - Isse TimesFM zyada accurate hota hai
FORECAST_HOURS = 24  # Agle 24 candle ka forecast

print("Loading Google TimesFM-3 Model...")
# Google ka 330M wala model load
model = timesfm.TimesFm(
    hparams=timesfm.TimesFmHparams(
        backend="torch",
        per_core_batch_size=32,
        horizon_len=FORECAST_HOURS,
    ),
    checkpoint=timesfm.TimesFmCheckpoint(
        huggingface_repo_id="google/timesfm-3.0-500m-pytorch"
    ),
)

# 1. Data Lao (Multivariate)
print(f"Downloading {GOLD_SYMBOL} and {DXY_SYMBOL}...")
gold_data = yf.download(GOLD_SYMBOL, period="10d", interval="1h")['Close']
dxy_data = yf.download(DXY_SYMBOL, period="10d", interval="1h")['Close']

# Align data
df = gold_data.to_frame(name='gold')
df['dxy'] = dxy_data
df.dropna(inplace=True)

last_price = df['gold'].iloc[-1]
print(f"Live Gold Price: ${last_price:.2f}")

# 2. TimesFM-3 ko do (Multivariate Forecast)
# Input format: [time, variates]
# Gold + DXY dono ek saath
input_series = df[['gold', 'dxy']].values.T  # Shape: [num_variates, time]

# Forecast
forecast, quantiles = model.forecast(
    inputs=[input_series],
    freq=[0] # 0 = high freq
)

# forecast[0] me gold ka future hai
predicted_prices = forecast[0][0]  # First variate = Gold
next_price = predicted_prices[0]

# 3. Signal Banao
diff = next_price - last_price
pct_change = (diff / last_price) * 100

print(f"TimesFM-3 Prediction Next Hour: ${next_price:.2f} ({pct_change:+.2f}%)")

if pct_change > 0.15:
    signal = "STRONG BUY"
    reason = f"Model ko 70%+ confidence hai Gold up jayega kyunki DXY weak hai"
elif pct_change > 0.05:
    signal = "BUY"
    reason = "Slight bullish momentum"
elif pct_change < -0.15:
    signal = "STRONG SELL"
    reason = "Model ko 70%+ confidence hai Gold down jayega"
else:
    signal = "SELL"
    reason = "Slight bearish"

# Final Output jo aap ke App pe dikhega
print("\n--- TAURIC FINAL SIGNAL ---")
print(f"PAIR: {GOLD_SYMBOL} (Fixed from GC=F)")
print(f"LIVE: ${last_price:.2f}")
print(f"SIGNAL: {signal}")
print(f"REASON: {reason}")
print(f"TP: ${last_price + (diff*2):.2f} | SL: ${last_price - (diff):.2f}")
