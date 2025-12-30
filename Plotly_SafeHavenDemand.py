import yfinance as yf
import plotly.graph_objects as go

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

# Generate plot
  # plot the single combined line
  # format hover menu
fig = go.Figure()
fig.add_trace(go.Scatter(x=returns_20d.index, y=returns_20d['Spread'], mode='lines', name='Momentum Spread',
hovertemplate='%{x}<br>%{y:.2f}%<extra></extra>'))

# Add zero line
fig.add_shape(
    type='line',
    x0=returns_20d.index.min(),
    y0=0,
    x1=returns_20d.index.max(),
    y1=0,
    line=dict(
        color='red',
        width=1,
        dash='dash'
    )
)

fig.update_layout(
    title='20-Day Momentum Spread: SPY (Stocks) minus IEF (Treasury Bond ETF)',
    xaxis_title='Date',
    yaxis_title='Difference in 20-Day % Change'
)

fig.show()
