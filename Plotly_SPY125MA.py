import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

# Define timeframe
  # set today as end date
  # set 1 year PLUS a buffer of 250 days (for 125-day moving average) as start date
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=365 + 250)

# Fetch SPY data from yfinance
  # skips weekends and holidays
df = yf.download('SPY', start=start_date, end=end_date, auto_adjust=True, progress=False)['Close']
df = df.dropna()

# Calculate 125-day moving average
df['125MA'] = df['SPY'].rolling(window=125).mean()

# Filter data to display only the last 365 days
  # drop buffer in plot
plot_data = df.loc[df.index > (end_date - datetime.timedelta(days=365))]

# Generate Plotly chart
fig = go.Figure()
fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['SPY'], mode='lines', name='SPY (S&P 500 ETF)'))
fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['125MA'], mode='lines', name='125-Day Moving Average'))

fig.update_layout(
    title='SPY vs 125-Day Moving Average (Past 1 Year)',
    xaxis_title='Date',
    yaxis_title='Price',
    hovermode='x unified'
)

fig.show()
