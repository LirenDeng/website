import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime

# Find current price of SPY
ticker_symbol = "SPY"
spy = yf.Ticker(ticker_symbol)
current_price = spy.history(period="1d")['Close'].iloc[-1]

# Get the nearest 10 expiration dates
expirations = spy.options[:10]  # Take the first 10 expirations

all_calls_data = []  # To store (calls_df, expiry_date) tuples
all_puts_data = []   # To store (puts_df, expiry_date) tuples
all_filtered_ivs_for_y_axis = []  # For global dynamic y-axis calculation

# Set x-axis range to focus on relevant strikes (+-10% from spot)
x_min = current_price * 0.95
x_max = current_price * 1.05

# Get today's date for DTE calculation
today = datetime.now().date()

for expiry_date in expirations:
    # Calculate Days to Expiration (DTE)
    expiry_datetime = datetime.strptime(expiry_date, '%Y-%m-%d').date()
    dte = (expiry_datetime - today).days

    # Fetch option chain for each expiration date
    opt = spy.option_chain(expiry_date)
    calls = opt.calls
    puts = opt.puts

    # 3. Data Cleaning and Smoothing
    # Filter for reasonable liquidity and remove zero IV values
    calls = calls[calls['impliedVolatility'] > 0.001].copy()
    puts = puts[puts['impliedVolatility'] > 0.001].copy()

    # Sort by strike for proper rolling mean calculation
    calls = calls.sort_values(by='strike')
    puts = puts.sort_values(by='strike')

    # Apply a rolling mean to smooth the implied volatility
    window_size = 5 # Can be adjusted
    calls['impliedVolatility_smoothed'] = calls['impliedVolatility'].rolling(window=window_size, min_periods=1, center=True).mean()
    puts['impliedVolatility_smoothed'] = puts['impliedVolatility'].rolling(window=window_size, min_periods=1, center=True).mean()

    all_calls_data.append((calls, expiry_date, dte))
    all_puts_data.append((puts, expiry_date, dte))

    # Collect implied volatilities from *filtered* data within x-axis range for dynamic y-axis calculation
    filtered_calls_for_y = calls[(calls['strike'] >= x_min) & (calls['strike'] <= x_max)]
    filtered_puts_for_y = puts[(puts['strike'] >= x_min) & (puts['strike'] <= x_max)]

    if not filtered_calls_for_y.empty:
        all_filtered_ivs_for_y_axis.extend((filtered_calls_for_y['impliedVolatility_smoothed'] * 100).tolist())
    if not filtered_puts_for_y.empty:
        all_filtered_ivs_for_y_axis.extend((filtered_puts_for_y['impliedVolatility_smoothed'] * 100).tolist())

# Calculate global min/max for y-axis from all collected filtered IVs
if all_filtered_ivs_for_y_axis:
    min_iv_filtered = min(all_filtered_ivs_for_y_axis)
    max_iv_filtered = max(all_filtered_ivs_for_y_axis)
    # Add a small buffer to the y-axis range
    ymin = min_iv_filtered * 0.95 if min_iv_filtered > 0 else 0  # Ensure ymin doesn't go below 0
    ymax = max_iv_filtered * 1.05
else:
    # Fallback if no data points are within the x-axis range across all expirations
    ymin = 0
    ymax = 100  # Default to a reasonable range

# 4. Plotting with Plotly
fig = go.Figure()

# Add dummy traces for concise legend entries 'Calls' and 'Puts'
fig.add_trace(go.Scatter(
    x=[None], y=[None],
    mode='lines',
    line=dict(color='green', width=1),
    name='Calls',
    showlegend=True,
    legendgroup='calls_legend'
))
fig.add_trace(go.Scatter(
    x=[None], y=[None],
    mode='lines',
    line=dict(color='red', width=1),
    name='Puts',
    showlegend=True,
    legendgroup='puts_legend'
))

# Plot all Call IV curves (with gradient)
for i, (calls_df, expiry_date, dte) in enumerate(all_calls_data):
    alpha_val = 1.0 - (i / len(all_calls_data)) * 0.9
    color_calls = f'rgba(0, 128, 0, {alpha_val})' # Green
    fig.add_trace(go.Scatter(
        x=calls_df['strike'],
        y=calls_df['impliedVolatility_smoothed'] * 100,
        mode='lines',
        name=f'Call (DTE: {dte})', # Name for hover header
        line=dict(color=color_calls, width=1),
        showlegend=False, # Don't show individual expiries in legend
        legendgroup='calls', # Group for hover toggle behavior (if needed)
        hovertemplate=f'<b>{dte} DTE</b>: %{{y:.2f}}%<extra></extra>' # DTE now in hovertemplate
    ))

# Plot all Put IV curves (with gradient)
for i, (puts_df, expiry_date, dte) in enumerate(all_puts_data):
    alpha_val = 1.0 - (i / len(all_puts_data)) * 0.9
    color_puts = f'rgba(255, 0, 0, {alpha_val})' # Red
    fig.add_trace(go.Scatter(
        x=puts_df['strike'],
        y=puts_df['impliedVolatility_smoothed'] * 100,
        mode='lines',
        name=f'Put (DTE: {dte})', # Name for hover header
        line=dict(color=color_puts, width=1),
        showlegend=False, # Don't show individual expiries in legend
        legendgroup='puts', # Group for hover toggle behavior (if needed)
        hovertemplate=f'<b>{dte} DTE</b>: %{{y:.2f}}%<extra></extra>' # DTE now in hovertemplate
    ))

# Add vertical line for Current Price
fig.add_vline(
    x=current_price,
    line_dash="dash",
    line_color="grey",
    line_width=1,
    name=f'Current Price: {current_price:.2f}'
)

# Add a dummy trace for the gradient explanation in the legend
fig.add_trace(go.Scatter(
    x=[None],
    y=[None],
    mode='lines',
    line=dict(color='grey', width=0),
    name='Lighter line = further expiration date',
    showlegend=True
))

# Formatting
fig.update_layout(
    title=f"Volatility Skew - {ticker_symbol} (Smoothed)",
    xaxis_title="Strikes",
    yaxis_title="Implied Volatility (IV)",
    xaxis_range=[x_min, x_max],
    yaxis_range=[ymin, ymax],
    hovermode="x unified",
    title_x=0.5,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    ),
    height=800,
    width=1300
)

fig.update_yaxes(gridcolor='lightgray', showgrid=True)
fig.show()
