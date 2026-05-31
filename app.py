import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide"
)

st.title("🚀 Miu Stock Dashboard")

symbols = ["NVDA", "RKLB"]

rows = []

for symbol in symbols:

    try:
        stock = yf.Ticker(symbol)

        hist = stock.history(period="1y")

        if len(hist) > 0:

            current_price = round(hist["Close"].iloc[-1], 2)

            sma20 = round(hist["Close"].rolling(20).mean().iloc[-1], 2)
            sma50 = round(hist["Close"].rolling(50).mean().iloc[-1], 2)
            sma200 = round(hist["Close"].rolling(200).mean().iloc[-1], 2)

            one_year_return = round(
                (
                    (hist["Close"].iloc[-1] - hist["Close"].iloc[0])
                    / hist["Close"].iloc[0]
                ) * 100,
                2,
            )

            rows.append({
                "Ticker": symbol,
                "Price": current_price,
                "% 1Y": one_year_return,
                "20SMA": sma20,
                "50SMA": sma50,
                "200SMA": sma200,
            })

    except Exception as e:

        rows.append({
            "Ticker": symbol,
            "Price": f"ERROR: {e}",
            "% 1Y": "",
            "20SMA": "",
            "50SMA": "",
            "200SMA": "",
        })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
