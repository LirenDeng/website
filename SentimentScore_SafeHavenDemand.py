import yfinance as yf
import datetime

# Define tickers and timeframe
  # fetch adjusted closing prices for both tickers
  # yfinance defaults auto_adjust=True that define closeing prices as 'Close'
tickers = ['SPY', 'IEF']
data = yf.download(tickers, period='12mo', auto_adjust=True, progress=False) ['Close']

# Calculate 20-Day Rolling Returns (Percentage Change)
returns_20d = data.pct_change(20).dropna()

# Calculate the spread
  # "Stocks return minus bonds return"
returns_20d['Spread'] = returns_20d['SPY'] - returns_20d['IEF']

# Define the sentiment score
def get_sentiment(spread):
    if spread <= -0.02:
        return "Extreme Fear"
    elif spread <= 0.015:
        return "Fear"
    elif spread <= 0.02:
        return "Neutral"
    elif spread <= 0.05:
        return "Greed"
    else:
        return "Extreme Greed"

plot_data = returns_20d.dropna().copy()
plot_data['Sentiment'] = plot_data['Spread'].apply(get_sentiment)
latest = plot_data.iloc[-1]

print(f"Date: {plot_data.index[-1].date()}")
print(f"SPY 20d Return: {latest['SPY']:.4f}")
print(f"IEF 20d Return: {latest['IEF']:.4f}")
print(f"Return Spread:   {latest['Spread']:.4f}")
print(f"Sentiment:       {latest['Sentiment']}")
