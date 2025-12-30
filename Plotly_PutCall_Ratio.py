import yfinance as yf
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go

# Define ticker and timeframe
  # find option chains in the 14 nearest expiration dates
  # reserve dictionary for Put/Call ratio across different chains
sp500 = yf.Ticker('SPY')
option_dates = sp500.options[:14]
put_call_ratios_by_date = {}
put_call_OI_ratios_by_date = {}

# Loop to find Put/Call ratio across all chains
  # obtain call and put volume of each expiration
  # calculate Put/Call ratio by dividing volume and OI of Puts by Calls
for date in option_dates:
    opt_chain_by_date = sp500.option_chain(date=date)

    calls_by_date = opt_chain_by_date.calls
    puts_by_date = opt_chain_by_date.puts

    total_call_volume_by_date = calls_by_date['volume'].sum()
    total_put_volume_by_date = puts_by_date['volume'].sum()

    total_call_OI_by_date = calls_by_date['openInterest'].sum()
    total_put_OI_by_date = puts_by_date['openInterest'].sum()

    if total_call_volume_by_date > 0:
        ratio = total_put_volume_by_date / total_call_volume_by_date
    else:
        ratio = float('nan')

    if total_call_OI_by_date > 0:
        OI_ratio = total_put_OI_by_date / total_call_OI_by_date
    else:
        OI_ratio = float('nan')

    put_call_ratios_by_date[date] = ratio

    put_call_OI_ratios_by_date[date] = OI_ratio

# Convert the dictionary to a DataFrame
put_call_df = pd.DataFrame(put_call_ratios_by_date.items(), columns=['Expiration Date', 'Put/Call Ratio'])
put_call_OI_df = pd.DataFrame(put_call_OI_ratios_by_date.items(), columns=['Expiration Date', 'Put/Call OI Ratio'])

# Sort DF by date
put_call_df['Expiration Date'] = pd.to_datetime(put_call_df['Expiration Date'])
put_call_df = put_call_df.sort_values(by='Expiration Date').reset_index(drop=True)
put_call_OI_df['Expiration Date'] = pd.to_datetime(put_call_OI_df['Expiration Date'])
put_call_OI_df = put_call_OI_df.sort_values(by='Expiration Date').reset_index(drop=True)

# Convert dates to days to expiration (DTE)
current_date_ts = pd.Timestamp(datetime.now().date())
put_call_df['DTE'] = (put_call_df['Expiration Date'] - current_date_ts).dt.days
put_call_OI_df['DTE'] = (put_call_OI_df['Expiration Date'] - current_date_ts).dt.days # Add DTE for OI dataframe

# Filter out rows where Put/Call Ratio is NaN
put_call_df = put_call_df.dropna(subset=['Put/Call Ratio'])
put_call_OI_df = put_call_OI_df.dropna(subset=['Put/Call OI Ratio'])

# Generate interactive bar plot using Plotly
  # Hover legend that labels x as DTE and y as Put/Call Ratio
fig = go.Figure(
    data=[
        go.Bar(
            x=put_call_df.index,
            y=put_call_df['Put/Call Ratio'],
            name='Put/Call Volume Ratio',
            customdata=put_call_df['DTE'],
            hovertemplate='<b>DTE:</b> %{customdata}<br><b>Put/Call Volume Ratio:</b> %{y:.2f}<extra></extra>'
        ),
        go.Bar(
            x=put_call_OI_df.index,
            y=put_call_OI_df['Put/Call OI Ratio'],
            name='Put/Call Open Interest Ratio',
            customdata=put_call_OI_df['DTE'],
            hovertemplate='<b>DTE:</b> %{customdata}<br><b>Put/Call OI Ratio:</b> %{y:.2f}<extra></extra>'
        )
    ],

    # Drops DTE with no Put/Call Ratios
      # convert DTE to catagory
    layout=go.Layout(
        title=go.layout.Title(text='Put/Call Ratios (Volume and Open Interests) for the 14 Nearest Expiration Dates'),
        xaxis=dict(
            title='Days To Expiration (DTE)',
            type='category',
            tickmode='array',
            tickvals=put_call_df.index,
            ticktext=put_call_df['DTE'].astype(str)
        ),
        yaxis_title='Put/Call Ratio'
    )
)

fig.show()
