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

def get_quote(symbol):
    url = (
        f"https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE"
        f"&symbol={symbol}"
        f"&apikey={API_KEY}"
    )
    return requests.get(url).json()

symbols = ["NVDA", "RKLB"]

rows = []

for symbol in symbols:

    overview = get_overview(symbol)
    quote = get_quote(symbol)

    quote_data = quote.get("Global Quote", {})

    price = quote_data.get("05. price", "N/A")
    change_pct = quote_data.get("10. change percent", "N/A")

    rows.append({
        "Ticker": symbol,
        "Company": overview.get("Name", "N/A"),
        "Price": price,
        "Change %": change_pct,
        "Market Cap": overview.get("MarketCapitalization", "N/A"),
        "P/E": overview.get("PERatio", "N/A"),
        "P/S": overview.get("PriceToSalesRatioTTM", "N/A")
    })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True
)
