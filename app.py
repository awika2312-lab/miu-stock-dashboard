import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide"
)

st.title("📊 Miu Stock Dashboard")

symbols = ["NVDA", "RKLB"]

rows = []

for symbol in symbols:

    try:
        stock = yf.Ticker(symbol)

        hist = stock.history(period="1y")

        if len(hist) > 0:

            current_price = round(hist["Close"].iloc[-1], 2)
            previous_price = round(hist["Close"].iloc[-2], 2)

            change_pct = round(
                ((current_price - previous_price) / previous_price) * 100,
                2
            )

            sma20 = round(
                hist["Close"].rolling(20).mean().iloc[-1],
                2
            )

            sma50 = round(
                hist["Close"].rolling(50).mean().iloc[-1],
                2
            )

            sma200 = round(
                hist["Close"].rolling(200).mean().iloc[-1],
                2
            )

            one_year_return = round(
                (
                    (hist["Close"].iloc[-1] - hist["Close"].iloc[0])
                    / hist["Close"].iloc[0]
                ) * 100,
                2
            )

            high_52w = round(
                hist["High"].max(),
                2
            )

            distance_from_high = round(
                ((current_price - high_52w) / high_52w) * 100,
                2
            )

            rows.append({
                "Ticker": symbol,
                "Price": current_price,
                "Day %": change_pct,
                "% 1Y": one_year_return,
                "52W High": high_52w,
                "From High %": distance_from_high,
                "20SMA": sma20,
                "50SMA": sma50,
                "200SMA": sma200
            })

    except Exception as e:

        rows.append({
            "Ticker": symbol,
            "Price": f"ERROR: {e}",
            "Day %": "",
            "% 1Y": "",
            "52W High": "",
            "From High %": "",
            "20SMA": "",
            "50SMA": "",
            "200SMA": ""
        })

df = pd.DataFrame(rows)

def color_change(val):
    try:
        if float(val) > 0:
            return "color: limegreen; font-weight: bold;"
        elif float(val) < 0:
            return "color: red; font-weight: bold;"
    except:
        pass
    return ""

styled_df = df.style.map(
    color_change,
    subset=["Day %", "% 1Y", "From High %"]
)

st.dataframe(
    styled_df,
    use_container_width=True,
    hide_index=True
)
