import yfinance as yf
import pandas as pd

# 1. Define Tickers
baseline = 'SPY'
tickers = ['IVW', 'IVE']
all_tickers = [baseline] + tickers

# 2. Download Data (Last 5 years for meaningful rolling windows)
data = yf.download(all_tickers, period='5y', auto_adjust=True, progress=False)['Close']

# 3. Calculate Rolling 1-Year (252 Trading Days) Return
# We use 252 as it represents the number of trading days in 365 calendar days
rolling_window = 252
rolling_returns = data.pct_change(periods=rolling_window)

# 4. Calculate Percentage Deviation from SPY
# Deviation = (Ticker_Return - SPY_Return) * 100
deviations = pd.DataFrame()
for ticker in tickers:
    deviations[f'{ticker}_dev'] = (rolling_returns[ticker] - rolling_returns[baseline]) * 100

# 5. Clean up data (remove the initial NaNs from the rolling window)
df = deviations.dropna().copy()

df['Diff'] = df['IVW_dev'] - df['IVE_dev']

df['Score'] = df['Diff'].rolling(window=252).rank(pct=True) * 100

def get_sentiment(Score):
    if Score >= 90: return "Extreme Greed"
    if Score >= 70: return "Greed"
    if Score >= 40: return "Neutral"
    if Score >= 20: return "Fear"
    return "Extreme Fear"

# Add Sentiment column to df BEFORE defining 'latest'
df['Sentiment'] = df['Score'].apply(get_sentiment)

print(f"Date: {df.index[-1].date()}")

latest = df.iloc[-1]
print(f"Relative strength of Growth versus Value stocks: {latest['Diff']:.2f}%")
print(f"Percentile Rank: {latest['Score']:.2f}")
print(f"Sentiment: {latest['Sentiment']}")
