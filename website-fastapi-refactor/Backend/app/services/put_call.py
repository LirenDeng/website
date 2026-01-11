import yfinance as yf
import pandas as pd
from datetime import datetime


def get_put_call_data():
    ticker = yf.Ticker("SPY")

    option_dates = ticker.options[:10]  # 10 nearest expirations

    results = []

    for exp_date in option_dates:
        try:
            chain = ticker.option_chain(exp_date)

            calls = chain.calls
            puts = chain.puts

            call_volume = calls["volume"].fillna(0).sum()
            put_volume = puts["volume"].fillna(0).sum()

            # Avoid division by zero
            put_call_ratio = (
                put_volume / call_volume if call_volume > 0 else None
            )

            # Days to expiration (DTE)
            dte = (
                datetime.strptime(exp_date, "%Y-%m-%d") - datetime.utcnow()
            ).days

            results.append({
                "expiration": exp_date,
                "dte": dte,
                "put_call_ratio": round(put_call_ratio, 3) if put_call_ratio else None
            })

        except Exception as e:
            # skip problematic expiration dates
            continue

    # Sort by DTE ascending
    results.sort(key=lambda x: x["dte"])

    return results
