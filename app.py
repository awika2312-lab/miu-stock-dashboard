import streamlit as st
import pandas as pd
import requests

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide"
)

st.title("📊 Miu Stock Dashboard")

API_KEY = st.secrets["ALPHA_VANTAGE_KEY"]


def get_overview(symbol):
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=OVERVIEW"
        f"&symbol={symbol}"
        f"&apikey={API_KEY}"
    )
    return requests.get(url).json()


def get_daily(symbol):
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={symbol}"
        f"&outputsize=compact"
        f"&apikey={API_KEY}"
    )
    return requests.get(url).json()


symbols = ["NVDA", "RKLB"]

rows = []

for symbol in symbols:

    data = get_overview(symbol)
    daily = get_daily(symbol)

    st.write(symbol)
    st.write(daily)

    rows.append({
        "Ticker": symbol,
        "Company": data.get("Name", "N/A"),
        "Market Cap": data.get("MarketCapitalization", "N/A"),
        "P/E": data.get("PERatio", "N/A"),
        "P/S": data.get("PriceToSalesRatioTTM", "N/A")
    })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
