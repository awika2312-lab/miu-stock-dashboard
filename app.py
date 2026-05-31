import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide"
)

st.title(" Miu Stock Dashboard")

symbols = ["NVDA", "RKLB"]

rows = []

for symbol in symbols:

    stock = yf.Ticker(symbol)

    info = stock.info

    rows.append({
        "Ticker": symbol,
        "Company": info.get("longName", "N/A"),
        "Price": info.get("currentPrice", "N/A"),
        "Market Cap": info.get("marketCap", "N/A"),
        "P/E": info.get("trailingPE", "N/A")
    })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
