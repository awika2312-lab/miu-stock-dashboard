import streamlit as st
import pandas as pd
import yfinance as yf
from pathlib import Path

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #F7F7F5;
    color: #1A1A1A;
}

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 2.5rem 3rem 2rem 3rem;
    max-width: 1400px;
}

/* ── Header ── */
.dashboard-header {
    display: flex;
    align-items: baseline;
    gap: 12px;
    margin-bottom: 2rem;
    padding-bottom: 1.25rem;
    border-bottom: 1px solid #E0DDD8;
}
.dashboard-title {
    font-size: 1.5rem;
    font-weight: 600;
    letter-spacing: -0.02em;
    color: #1A1A1A;
    margin: 0;
}
.dashboard-subtitle {
    font-size: 0.8rem;
    color: #9E9B95;
    font-weight: 400;
    letter-spacing: 0.03em;
}

/* ── Add Symbol bar ── */
.stTextInput > div > div > input {
    background: #FFFFFF;
    border: 1px solid #E0DDD8 !important;
    border-radius: 8px !important;
    font-family: 'DM Mono', monospace;
    font-size: 0.85rem;
    color: #1A1A1A;
    padding: 0.5rem 0.75rem;
    box-shadow: none !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1A1A1A !important;
    box-shadow: none !important;
}
.stTextInput label {
    font-size: 0.75rem;
    font-weight: 500;
    color: #9E9B95;
    letter-spacing: 0.05em;
    text-transform: uppercase;
}

/* ── Button ── */
.stButton > button {
    background: #1A1A1A;
    color: #F7F7F5;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.52rem 1.25rem;
    cursor: pointer;
    transition: background 0.15s ease;
    width: 100%;
    margin-top: 1.75rem;
}
.stButton > button:hover {
    background: #333333;
}

/* ── Dataframe ── */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid #E0DDD8;
    background: #FFFFFF;
}
[data-testid="stDataFrame"] > div {
    border-radius: 12px;
}

/* Table header */
.stDataFrame th {
    background: #F0EDE8 !important;
    color: #6B6860 !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid #E0DDD8 !important;
    padding: 10px 14px !important;
}

/* Table rows */
.stDataFrame td {
    font-family: 'DM Mono', monospace;
    font-size: 0.82rem !important;
    padding: 9px 14px !important;
    border-bottom: 1px solid #F0EDE8 !important;
    background: #FFFFFF !important;
}
.stDataFrame tr:hover td {
    background: #FAFAF8 !important;
}

/* Section label */
.section-label {
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #9E9B95;
    margin-bottom: 0.75rem;
    margin-top: 1.75rem;
}

/* Ticker badge */
.ticker-mono {
    font-family: 'DM Mono', monospace;
    font-weight: 500;
}
</style>

<div class="dashboard-header">
    <span class="dashboard-title">Miu Stock Dashboard</span>
    <span class="dashboard-subtitle">Real-Time Market Data · Technical Analysis · Portfolio Tracking</span>
</div>
""", unsafe_allow_html=True)

WATCHLIST_FILE = "watchlist.csv"

# =====================
# LOAD WATCHLIST
# =====================

if not Path(WATCHLIST_FILE).exists():
    pd.DataFrame({
        "Ticker": ["NVDA", "RKLB"]
    }).to_csv(WATCHLIST_FILE, index=False)

watchlist_df = pd.read_csv(WATCHLIST_FILE)
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

st.markdown('<p class="section-label">Add to Watchlist</p>', unsafe_allow_html=True)

col1, col2 = st.columns([4, 1])

with col1:
    new_symbol = st.text_input(
        "Ticker Symbol",
        placeholder="e.g. AAPL",
        label_visibility="collapsed"
    )

with col2:
    add_clicked = st.button("＋ Add")

if add_clicked and new_symbol:
    new_symbol = new_symbol.upper()
    if new_symbol not in symbols:
        symbols.append(new_symbol)
        pd.DataFrame({"Ticker": symbols}).to_csv(WATCHLIST_FILE, index=False)
        st.rerun()

# =====================
# STOCK TABLE
# =====================

st.markdown('<p class="section-label">Watchlist</p>', unsafe_allow_html=True)

rows = []

for symbol in symbols:
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")

        if len(hist) < 200:
            continue

        current_price = round(hist["Close"].iloc[-1], 2)
        previous_price = round(hist["Close"].iloc[-2], 2)

        daily_return = round(
            (current_price - previous_price) / previous_price * 100, 2
        )

        one_year_return = round(
            (hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100, 2
        )

        current_year = hist[hist.index.year == pd.Timestamp.now().year]
        ytd_return = round(
            (current_price - current_year["Close"].iloc[0]) / current_year["Close"].iloc[0] * 100, 2
        ) if len(current_year) else 0

        sma20  = round(hist["Close"].rolling(20).mean().iloc[-1], 2)
        sma50  = round(hist["Close"].rolling(50).mean().iloc[-1], 2)
        sma200 = round(hist["Close"].rolling(200).mean().iloc[-1], 2)

        high_52w = round(hist["High"].max(), 2)
        from_high = round((current_price - high_52w) / high_52w * 100, 2)

        monthly_return = round(
            (hist["Close"].iloc[-1] - hist["Close"].iloc[-22]) / hist["Close"].iloc[-22] * 100, 2
        )
        rs_rank = int(min(99, max(1, 50 + monthly_return * 2)))

        trend = hist["Close"].tail(60).tolist()

        company = symbol
        market_cap = "N/A"
        pe_ratio = "N/A"

        try:
            info = stock.info
            company   = info.get("longName", symbol)
            market_cap = info.get("marketCap", "N/A")
            pe_ratio  = info.get("trailingPE", "N/A")
        except:
            pass

        rows.append({
            "Ticker":     symbol,
            "Company":    company,
            "Price":      current_price,
            "Change %":   daily_return,
            "Market Cap": market_cap,
            "P/E":        pe_ratio,
            "YTD %":      ytd_return,
            "Trend":      trend,
            "1Y %":       one_year_return,
            "52W High":   high_52w,
            "From High %": from_high,
            "RS Rank":    rs_rank,
            "SMA 20":     sma20,
            "SMA 50":     sma50,
            "SMA 200":    sma200,
        })

    except:
        pass

df = pd.DataFrame(rows)

# ── Colour helpers ──
def color_pct(val):
    try:
        v = float(val)
        if v > 0:  return "color:#16A34A; font-weight:500;"
        if v < 0:  return "color:#DC2626; font-weight:500;"
    except:
        pass
    return "color:#6B6860;"

def format_mcap(val):
    try:
        v = float(val)
        if v >= 1e12: return f"${v/1e12:.2f}T"
        if v >= 1e9:  return f"${v/1e9:.1f}B"
        if v >= 1e6:  return f"${v/1e6:.0f}M"
    except:
        pass
    return str(val)

def format_pe(val):
    try:
        return f"{float(val):.1f}x"
    except:
        return str(val)

if not df.empty:
    display_df = df.copy()
    display_df["Market Cap"] = display_df["Market Cap"].apply(format_mcap)
    display_df["P/E"]        = display_df["P/E"].apply(format_pe)

    styled = display_df.style.map(
        color_pct,
        subset=["Change %", "YTD %", "1Y %", "From High %"]
    ).format({
        "Price":      "${:.2f}",
        "Change %":   "{:+.2f}%",
        "YTD %":      "{:+.2f}%",
        "1Y %":       "{:+.2f}%",
        "From High %":"{:+.2f}%",
        "52W High":   "${:.2f}",
        "SMA 20":     "${:.2f}",
        "SMA 50":     "${:.2f}",
        "SMA 200":    "${:.2f}",
    })

    st.dataframe(
        styled,
        column_config={
            "Trend": st.column_config.LineChartColumn(
                "60d Trend", width="medium"
            ),
            "RS Rank": st.column_config.ProgressColumn(
                "RS Rank", min_value=1, max_value=99, format="%d"
            ),
        },
        use_container_width=True,
        hide_index=True,
        height=min(60 + len(df) * 38, 600)
    )
else:
    st.markdown(
        '<p style="color:#9E9B95; font-size:0.875rem; margin-top:1rem;">No data available. Add a symbol above to get started.</p>',
        unsafe_allow_html=True
    )
