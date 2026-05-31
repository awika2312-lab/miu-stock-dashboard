import streamlit as st
import pandas as pd
import yfinance as yf
from pathlib import Path

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
}
</style>
""", unsafe_allow_html=True)

st.title("Miu Stock Dashboard")
st.caption(
    "Real-Time Market Data • Technical Analysis • Portfolio Tracking"
)

WATCHLIST_FILE = "watchlist.csv"

# =====================
# LOAD WATCHLIST
# =====================

if not Path(WATCHLIST_FILE).exists():

    pd.DataFrame({
        "Ticker": ["NVDA", "RKLB"]
    }).to_csv(
        WATCHLIST_FILE,
        index=False
    )

watchlist_df = pd.read_csv(
    WATCHLIST_FILE
)

symbols = (
    watchlist_df["Ticker"]
    .dropna()
    .astype(str)
    .str.upper()
    .tolist()
)

# =====================
# ADD SYMBOL
# =====================

col1, col2 = st.columns([3,1])

with col1:

    new_symbol = st.text_input(
        "Add Symbol",
        placeholder="AAPL"
    )

with col2:

    add_clicked = st.button(
        "Add"
    )

if add_clicked and new_symbol:

    new_symbol = new_symbol.upper()

    if new_symbol not in symbols:

        symbols.append(
            new_symbol
        )

        pd.DataFrame({
            "Ticker": symbols
        }).to_csv(
            WATCHLIST_FILE,
            index=False
        )

        st.rerun()

# =====================
# STOCK TABLE
# =====================

rows = []

for symbol in symbols:

    try:

        stock = yf.Ticker(symbol)

        hist = stock.history(
            period="1y"
        )

        if len(hist) < 200:
            continue

        current_price = round(
            hist["Close"].iloc[-1],
            2
        )

        previous_price = round(
            hist["Close"].iloc[-2],
            2
        )

        daily_return = round(
            (
                current_price
                - previous_price
            )
            /
            previous_price
            * 100,
            2
        )

        one_year_return = round(
            (
                hist["Close"].iloc[-1]
                - hist["Close"].iloc[0]
            )
            /
            hist["Close"].iloc[0]
            * 100,
            2
        )

        current_year = hist[
            hist.index.year
            ==
            pd.Timestamp.now().year
        ]

        if len(current_year):

            ytd_return = round(
                (
                    current_price
                    -
                    current_year["Close"].iloc[0]
                )
                /
                current_year["Close"].iloc[0]
                * 100,
                2
            )

        else:

            ytd_return = 0

        sma20 = round(
            hist["Close"]
            .rolling(20)
            .mean()
            .iloc[-1],
            2
        )

        sma50 = round(
            hist["Close"]
            .rolling(50)
            .mean()
            .iloc[-1],
            2
        )

        sma200 = round(
            hist["Close"]
            .rolling(200)
            .mean()
            .iloc[-1],
            2
        )

        high_52w = round(
            hist["High"].max(),
            2
        )

        from_high = round(
            (
                current_price
                - high_52w
            )
            /
            high_52w
            * 100,
            2
        )

        monthly_return = round(
            (
                hist["Close"].iloc[-1]
                -
                hist["Close"].iloc[-22]
            )
            /
            hist["Close"].iloc[-22]
            * 100,
            2
        )

        rs_rank = int(
            min(
                99,
                max(
                    1,
                    50 + monthly_return * 2
                )
            )
        )

        trend = (
            hist["Close"]
            .tail(60)
            .tolist()
        )

        company = symbol
        market_cap = "N/A"
        pe_ratio = "N/A"

        try:

            info = stock.info

            company = info.get(
                "longName",
                symbol
            )

            market_cap = info.get(
                "marketCap",
                "N/A"
            )

            pe_ratio = info.get(
                "trailingPE",
                "N/A"
            )

        except:
            pass

        rows.append({

            "Ticker": symbol,
            "Company": company,
            "Price": current_price,
            "Change %": daily_return,
            "Market Cap": market_cap,
            "P/E": pe_ratio,
            "YTD %": ytd_return,
            "Trend": trend,
            "1Y %": one_year_return,
            "52W High": high_52w,
            "From High %": from_high,
            "RS Rank": rs_rank,
            "20 SMA": sma20,
            "50 SMA": sma50,
            "200 SMA": sma200

        })

    except:
        pass

df = pd.DataFrame(rows)

def color_change(val):

    try:

        val = float(val)

        if val > 0:
            return (
                "color:#22C55E;"
                "font-weight:bold;"
            )

        if val < 0:
            return (
                "color:#EF4444;"
                "font-weight:bold;"
            )

    except:
        pass

    return ""

styled_df = df.style.map(
    color_change,
    subset=[
        "Change %",
        "YTD %",
        "1Y %",
        "From High %"
    ]
)

st.dataframe(
    styled_df,
    column_config={
        "Trend":
        st.column_config.LineChartColumn(
            "Trend",
            width="medium"
        )
    },
    use_container_width=True,
    hide_index=True
)
