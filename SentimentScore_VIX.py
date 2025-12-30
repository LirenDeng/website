import yfinance as yf
import pandas as pd
import datetime

# Define timeframe
  # set today as end date
  # set 1 years PLUS a buffer of 100 days as start date
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=365 + 100) 


# Fetch VIX data from yfinance
  # flatten column name
vix_data = yf.download('^VIX', start=start_date, end=end_date, auto_adjust=True, progress=False)
df = vix_data[['Close']].copy()
df.columns = ['VIX']

# Calculate 50-day moving average
df['50MA'] = df['VIX'].rolling(window=50).mean()

# Calculate difference (VIX - 50MA)
df['Diff'] = df['VIX'] - df['50MA']

# Find percentile rank of difference in 1 year window
df['Percentile'] = df['Diff'].rolling(window=252).rank(pct=True) * 100

# Calculate sentiment score (Inverted)
  # High VIX Diff = High Percentile = High Fear = LOW Score
  # Low VIX Diff = Low Percentile = High Greed = HIGH Score
df['Score'] = 100 - df['Percentile']

# Define sentiment score
def get_sentiment(score):
    if score >= 95: return "Extreme Greed"
    if score >= 80: return "Greed"
    if score >= 20: return "Neutral"
    if score >= 5: return "Fear"
    return "Extreme Fear"

df = df.dropna().copy()
df['Sentiment'] = df['Score'].apply(get_sentiment)

latest = df.iloc[-1]
print(f"Date: {df.index[-1].date()}")
print(f"VIX Price: {latest['VIX']:.2f}")
print(f"50-Day MA: {latest['50MA']:.2f}")
print(f"Score (0-100): {latest['Score']:.2f}")
print(f"Sentiment: {latest['Sentiment']}")
