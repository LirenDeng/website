import yfinance as yf
import pandas as pd
import datetime

# Define timeframe
  # set today as end date
  # set 2 years PLUS a buffer of 250 days as start date
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=(730 + 250))

# Fetch SPY data from yfinance
  # skips weekends and holidays
  # flatten column name
df = yf.download('SPY', start=start_date, end=end_date, auto_adjust=True, progress=False)['Close']
df = df.dropna()
df.columns = ['Price']

# Calculate 125-day moving average
df['125MA'] = df['Price'].rolling(window=125).mean()

# Calculate difference between Price and 125MA
df['Diff'] = df['Price'] - df['125MA']

# Find percentile rank of difference in 1 year window
df['Score'] = df['Diff'].rolling(window=365).rank(pct=True) * 100

# Define the sentiment score
def get_sentiment(score):
    if score >= 75: return "Extreme Greed"
    if score >= 55: return "Greed"
    if score >= 45: return "Neutral"
    if score >= 25: return "Fear"
    return "Extreme Fear"

# Add sentiment column to df BEFORE defining 'latest'
df['Sentiment'] = df['Score'].apply(get_sentiment)

print(f"Date: {df.index[-1].date()}")

latest = df.iloc[-1]
print(f"SPY Price: {latest['Price']:.2f}")
print(f"125-Day MA: {latest['125MA']:.2f}")
print(f"Score (0-100): {latest['Score']:.2f}")
print(f"Sentiment: {latest['Sentiment']}")

# To see the full table:
  # with pd.option_context('display.max_rows', None):
  #   print(plot_data[['Price', '125MA', 'Score', 'Sentiment']])
