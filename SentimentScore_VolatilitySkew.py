import yfinance as yf
import numpy as np
import pandas as pd

# Find current price of SPY
ticker_symbol = "SPY"
spy = yf.Ticker(ticker_symbol)
current_price = spy.history(period="1d")['Close'].iloc[-1]

# Get the nearest 10 expiration dates
expirations = spy.options[:10]

# Set parameters for option data
  # 1% at-the-money window
  # +- 10% moneyness

ATM_WIN = 0.01   # 1% ATM window
OTM_PCT = 0.10   # +-10% OTM

results = []

# Process each expiration
for expiry_date in expirations:
    opt = spy.option_chain(expiry_date)
    calls = opt.calls.copy()
    puts = opt.puts.copy()

    calls["type"] = "call"
    puts["type"] = "put"

    df = pd.concat([calls, puts])
    df = df[df["impliedVolatility"] > 0]

    # Classify moneyness
    df["moneyness"] = df["strike"] / current_price

    atm = df[(df["moneyness"] > 1 - ATM_WIN) & (df["moneyness"] < 1 + ATM_WIN)]
    otm_calls = df[(df["type"] == "call") & (df["moneyness"] > 1 + OTM_PCT)]
    otm_puts = df[(df["type"] == "put") & (df["moneyness"] < 1 - OTM_PCT)]

    if atm.empty or otm_calls.empty or otm_puts.empty:
        continue

    metrics = {
        "expiration": expiry_date,
        "atm_iv": atm["impliedVolatility"].mean(),
        "otm_call_iv": otm_calls["impliedVolatility"].mean(),
        "otm_put_iv": otm_puts["impliedVolatility"].mean(),
    }

    metrics["tail_skew_ratio"] = metrics["otm_put_iv"] / metrics["otm_call_iv"]
    metrics["put_convexity"] = metrics["otm_put_iv"] / metrics["atm_iv"]
    metrics["call_fomo"] = metrics["otm_call_iv"] / metrics["atm_iv"]

    results.append(metrics)

df_metrics = pd.DataFrame(results)

sentiment = []

# OTM puts vs OTM calls
tail_skew = df_metrics["tail_skew_ratio"].mean()
  # The higher the tail_skew, the more biddings on crashes than on squeezes
if tail_skew > 1.3:
    sentiment.append("Strong downside tail fear")
elif tail_skew > 1.1:
    sentiment.append("Moderate downside risk awareness")
else:
    sentiment.append("Balanced tail risk")

# OTM puts vs ATM options
put_convexity = df_metrics["put_convexity"].mean()
  # The higher the put_convexity, the more biddings on crashes than price stabilizations
if put_convexity > 1.4:
    sentiment.append("Crash protection demand elevated")
elif put_convexity > 1.2:
    sentiment.append("Moderate tail hedging")
else:
    sentiment.append("Low tail hedging")

# OTM calls vs ATM options
call_fomo = df_metrics["call_fomo"].mean()
  # The higher the call_fomo, the more biddings on squeezes than price stabilizations
if call_fomo > 1.2:
    sentiment.append("Upside FOMO / squeeze risk")
elif call_fomo < 1.0:
    sentiment.append("Upside confidence")
else:
    sentiment.append("Neutral upside expectations")

# Measures the difference in tail skew between the nearest and furthest dated options
term_structure_slope = (df_metrics.iloc[-1]["tail_skew_ratio"] - df_metrics.iloc[0]["tail_skew_ratio"])
  # The higher the term_structure_slope, the more fear near-term options are relatively, vice versa
if term_structure_slope > 0.2:
    sentiment.append("Long-term risk feared")
elif term_structure_slope < -0.1:
    sentiment.append("Near-term fear dominant")
else:
    sentiment.append("Stable term-structure sentiment")

# Output
print("Raw Metrics (averaged across expirations):")
print(df_metrics.mean(numeric_only=True).round(3))

print("\nVolatility Skew Sentiment Diagnosics:")

for s in sentiment:
    print(f"- {s}")

