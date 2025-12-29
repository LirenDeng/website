import yfinance as yf
import pandas as pd
import datetime
import plotly.graph_objects as go

# Define timeframe
  # set today as end date
  # set 1 year PLUS a buffer of 100 days (for 50-day moving average) as start date
end_date = datetime.datetime.now()
start_date = end_date - datetime.timedelta(days=365 + 100)

# Fetch data from yfinance
  # 'VIX' is the ticker for CBOE Volatility Index in yfinance
  # skips weekends and holidays
vix_data = yf.download('^VIX', start=start_date, end=end_date, auto_adjust=True, progress=False)
df = vix_data[['Close']].copy()
df.columns = ['VIX']

# Calculate the 50-Day moving average
df['50MA'] = df['VIX'].rolling(window=50).mean()

# Filter data to display only the last 365 days, drop buffer in plot
plot_data = df.loc[df.index > (end_date - datetime.timedelta(days=365))]

fig = go.Figure()
fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['VIX'], mode='lines', name='Cboe Volatility Index (VIX)'))
fig.add_trace(go.Scatter(x=plot_data.index, y=plot_data['50MA'], mode='lines', name='50-Day Moving Average'))

fig.update_layout(
    title='VIX vs 50-Day Moving Average (Past 1 Year)',
    xaxis_title='Date',
    yaxis_title='Index',
    hovermode='x unified'
)

fig.show()
