import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Define ticker and timeframe
  # find option chains in the 14 nearest expiration dates
sp500 = yf.Ticker('SPY')
option_dates = sp500.options[:14]
results = []

# Loop to find Put/Call ratio across all chains
  # calculate Put/Call ratio by dividing volume and OI of Puts by Calls
  # assign quadrant based on Put/Call ratios
for date in option_dates:
    opt = sp500.option_chain(date)
    
    v_pcr = opt.puts['volume'].sum() / opt.calls['volume'].sum()
    oi_pcr = opt.puts['openInterest'].sum() / opt.calls['openInterest'].sum()
    
    v_score = 'High Vol PCR' if v_pcr > 1.0 else 'Low Vol PCR'
    oi_score = 'High OI PCR' if oi_pcr > 1.0 else 'Low OI PCR'
    
    results.append({'v_score': v_score, 'oi_score': oi_score})

# Build 2x2 matrix for heatmap
df = pd.DataFrame(results)
matrix = pd.crosstab(df['oi_score'], df['v_score']).reindex(
    index=['High OI PCR', 'Low OI PCR'], 
    columns=['Low Vol PCR', 'High Vol PCR'], 
    fill_value=0
)

# Define sentiment labels
  # matrix order: [High OI, Low OI] x [Low Vol, High Vol]
labels = [
    ["Short Covering<br>(Bearish Setup)", "Extreme Fear<br>(Capitulation)"],
    ["Extreme Greed<br>(Bullish Setup)", "Tactical Hedging<br>(Panic Buying)"]
]

# Generate heatmap with Plotly
fig = go.Figure(data=go.Heatmap(
    z=matrix.values,
    x=['Low Volume PCR (<1.0)', 'High Volume PCR (>1.0)'],
    y=['High OI PCR (>1.0)', 'Low OI PCR (<1.0)'],
    text=labels,
    texttemplate="%{text}<br><br>Count: %{z}",
    hoverinfo='none',
    reversescale=True,
    showscale=True
))

fig.update_layout(
    title='Options Sentiment Distribution: 14 Nearest Expirations',
    xaxis_title='Volume Activity (Market Momentum)',
    yaxis_title='Open Interest (Structural Positioning)',
    xaxis=dict(side='top')
)

fig.show()

# Find quadrant with the highest count
max_count = matrix.max().max()
max_loc = matrix.stack().idxmax()

# Extract row and column names
oi_score_max = max_loc[0]
v_score_max = max_loc[1]

# Find corresponding indices in the labels list
if oi_score_max == 'High OI PCR':
    row_idx = 0
else:
    row_idx = 1

if v_score_max == 'Low Vol PCR':
    col_idx = 0
else:
    col_idx = 1

highest_sentiment = labels[row_idx][col_idx].replace('<br>', ' ')

print(f"Sentiment: {highest_sentiment}")
