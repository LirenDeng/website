import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Define tickers and timeframe
baseline = 'SPY'
tickers = ['IVW', 'IVE']
all_tickers = [baseline] + tickers

# Fetch adjusted closing prices in 5 yera window
data = yf.download(all_tickers, period='5y', auto_adjust=True, progress=False)['Close']

# Calculate Rolling 1-Year (252 Trading Days) Return
# We use 252 as it represents the number of trading days in 365 calendar days
rolling_window = 252
rolling_returns = data.pct_change(periods=rolling_window)

# Calculate Percentage Deviation from SPY
# Deviation = (Ticker_Return - SPY_Return) * 100
deviations = pd.DataFrame()
for ticker in tickers:
    deviations[f'{ticker}_dev'] = (rolling_returns[ticker] - rolling_returns[baseline]) * 100

deviations = deviations.dropna()


fig = go.Figure()
label_map = {'IVW_dev': 'Growth Stocks', 'IVE_dev': 'Value Stocks'}
for column in deviations.columns:
    fig.add_trace(go.Scatter(x=deviations.index, y=deviations[column], mode='lines', name=label_map.get(column, column)))

# Calculate the range for the last year
end_date_plot = deviations.index.max()
start_date_plot = end_date_plot - pd.DateOffset(years=1)

fig.update_layout(
    title='Growth Stocks vs Value Stocks (Past 1 Year)',
    xaxis_title='Date',
    yaxis_title='Percentage Deviation from S&P 500 (%)',
    hovermode='x unified',
    xaxis_range=[start_date_plot, end_date_plot]
)

fig.show()
