import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

st.set_page_config(
    page_title="Miu Stock Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── TradingView-style: light bg, dark table ── */
.stApp { background-color: #F0F3FA; color: #131722; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0; max-width: 100%; }

/* ── Top nav bar ── */
.tv-navbar {
    background: #FFFFFF;
    border-bottom: 1px solid #E0E3EB;
    padding: 0 24px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky; top: 0; z-index: 100;
}
.tv-logo {
    font-size: 1rem; font-weight: 700; letter-spacing: -0.03em;
    color: #131722;
}
.tv-logo span { color: #2962FF; }
.tv-clock-bar {
    display: flex; gap: 24px; align-items: center;
    font-family: 'JetBrains Mono', monospace;
}
.tv-clock-item { display: flex; flex-direction: column; align-items: flex-end; }
.tv-clock-label { font-size: 0.58rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #868993; }
.tv-clock-val { font-size: 0.82rem; font-weight: 500; color: #131722; }
.tv-clock-date { font-size: 0.62rem; color: #B2B5BE; }
.tv-market-open { font-size: 0.58rem; color: #089981; font-weight: 700; letter-spacing: 0.05em; }
.tv-divider { width: 1px; height: 28px; background: #E0E3EB; }

/* ── Main content padding ── */
.tv-body { padding: 16px 20px; }

/* ── Section label ── */
.section-label {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #868993;
    margin-bottom: 8px; margin-top: 16px;
}

/* ── Add symbol input ── */
.stTextInput > div > div > input {
    background: #FFFFFF !important; border: 1px solid #E0E3EB !important;
    border-radius: 6px !important; font-family: 'JetBrains Mono', monospace;
    font-size: 0.82rem; color: #131722 !important; padding: 0.45rem 0.75rem;
    box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder { color: #B2B5BE !important; }
.stTextInput > div > div > input:focus { border-color: #2962FF !important; box-shadow: 0 0 0 2px rgba(41,98,255,0.12) !important; }
.stTextInput label { color: #868993 !important; font-size: 0.7rem !important; }

/* ── Add button ── */
.stButton > button {
    background: #2962FF; color: #FFFFFF; border: none; border-radius: 6px;
    font-family: 'Inter', sans-serif; font-size: 0.82rem; font-weight: 600;
    padding: 0.48rem 1rem; width: 100%; margin-top: 1.7rem; transition: background 0.15s;
}
.stButton > button:hover { background: #1E4FCC; }

/* ── Dataframe: dark table on light bg ── */
.stDataFrame { border-radius: 8px; overflow: hidden; border: 1px solid #2A2E39 !important; }
[data-testid="stDataFrame"] > div { background: #1E222D !important; border-radius: 8px; }
.stDataFrame th {
    background: #131722 !important; color: #4C525E !important;
    font-size: 0.62rem !important; font-weight: 600 !important;
    letter-spacing: 0.08em !important; text-transform: uppercase !important;
    border-bottom: 1px solid #2A2E39 !important; padding: 8px 10px !important;
}
.stDataFrame td {
    font-family: 'JetBrains Mono', monospace; font-size: 0.78rem !important;
    padding: 7px 10px !important; border-bottom: 1px solid #2A2E39 !important;
    background: #1E222D !important; color: #B2B5BE !important;
}
.stDataFrame tr:hover td { background: #262B3A !important; }

/* ── News panel ── */
.news-panel {
    background: #FFFFFF; border: 1px solid #E0E3EB;
    border-radius: 8px; overflow: hidden; margin-top: 6px;
}
.news-item { border-bottom: 1px solid #F0F3FA; transition: background 0.1s; }
.news-item:last-child { border-bottom: none; }
.news-item:hover { background: #F8F9FD; }
.news-item-link { display: block; text-decoration: none; padding: 10px 12px; }
.news-thumb {
    width: 100%; height: 90px; object-fit: cover;
    border-radius: 4px; margin-bottom: 7px;
    background: #F0F3FA; display: block;
}
.news-meta {
    font-size: 0.58rem; font-weight: 600; letter-spacing: 0.07em;
    text-transform: uppercase; color: #B2B5BE; margin-bottom: 4px;
}
.news-title {
    font-size: 0.77rem; font-weight: 500; color: #131722;
    line-height: 1.4; display: block;
}
.news-item:hover .news-title { color: #2962FF; }
.no-news { padding: 28px 14px; color: #B2B5BE; font-size: 0.8rem; text-align: center; }
.news-ticker-badge {
    display: inline-block; font-family: 'JetBrains Mono', monospace;
    font-size: 0.68rem; font-weight: 600;
    background: #EEF2FF; color: #2962FF; border: 1px solid #C7D7FF;
    padding: 2px 10px; border-radius: 4px; margin-bottom: 8px; letter-spacing: 0.04em;
}
.news-search-wrap input {
    border-radius: 20px !important;
    background: #F0F3FA !important;
    border: 1px solid #E0E3EB !important;
}
</style>
""", unsafe_allow_html=True)

# ── Nav bar ──
tz_th = ZoneInfo("Asia/Bangkok")
tz_ny = ZoneInfo("America/New_York")
now_th = datetime.now(tz_th)
now_ny = datetime.now(tz_ny)
is_open = now_ny.weekday() < 5 and 9*60+30 <= now_ny.hour*60+now_ny.minute <= 16*60
market_tag = '<span class="tv-market-open">● OPEN</span>' if is_open else '<span style="font-size:0.58rem;color:#868993;">CLOSED</span>'

st.markdown(f"""
<div class="tv-navbar">
  <div class="tv-logo">Miu <span>Stock</span></div>
  <div class="tv-clock-bar">
    <div class="tv-clock-item">
      <span class="tv-clock-label">🇹🇭 Thailand</span>
      <span class="tv-clock-val">{now_th.strftime("%H:%M:%S")}</span>
      <span class="tv-clock-date">{now_th.strftime("%a %d %b %Y")}</span>
    </div>
    <div class="tv-divider"></div>
    <div class="tv-clock-item">
      <span class="tv-clock-label">🇺🇸 New York &nbsp; {market_tag}</span>
      <span class="tv-clock-val">{now_ny.strftime("%H:%M:%S")}</span>
      <span class="tv-clock-date">{now_ny.strftime("%a %d %b %Y")}</span>
    </div>
  </div>
</div>
<div class="tv-body">
""", unsafe_allow_html=True)

WATCHLIST_FILE = "watchlist.csv"
if not Path(WATCHLIST_FILE).exists():
    pd.DataFrame({"Ticker": ["NVDA", "RKLB"]}).to_csv(WATCHLIST_FILE, index=False)

watchlist_df = pd.read_csv(WATCHLIST_FILE)
symbols = watchlist_df["Ticker"].dropna().astype(str).str.upper().tolist()

# ── Add symbol ──
st.markdown('<p class="section-label">Add to Watchlist</p>', unsafe_allow_html=True)
c1, c2 = st.columns([4, 1])
with c1:
    new_symbol = st.text_input("Ticker", placeholder="e.g. AAPL", label_visibility="collapsed", key="add_input")
with c2:
    if st.button("＋ Add") and new_symbol:
        ns = new_symbol.strip().upper()
        if ns not in symbols:
            symbols.append(ns)
            pd.DataFrame({"Ticker": symbols}).to_csv(WATCHLIST_FILE, index=False)
            st.rerun()

# ── Fetch stock data ──
@st.cache_data(ttl=300)
def fetch_stock_data(symbol):
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        if len(hist) < 200:
            return None
        cp  = round(hist["Close"].iloc[-1], 2)
        pp  = round(hist["Close"].iloc[-2], 2)
        daily  = round((cp - pp) / pp * 100, 2)
        yr1    = round((hist["Close"].iloc[-1] - hist["Close"].iloc[0]) / hist["Close"].iloc[0] * 100, 2)
        cy     = hist[hist.index.year == pd.Timestamp.now().year]
        ytd    = round((cp - cy["Close"].iloc[0]) / cy["Close"].iloc[0] * 100, 2) if len(cy) else 0
        sma20  = round(hist["Close"].rolling(20).mean().iloc[-1], 2)
        sma50  = round(hist["Close"].rolling(50).mean().iloc[-1], 2)
        sma200 = round(hist["Close"].rolling(200).mean().iloc[-1], 2)
        h52    = round(hist["High"].max(), 2)
        fh     = round((cp - h52) / h52 * 100, 2)
        mr     = round((hist["Close"].iloc[-1] - hist["Close"].iloc[-22]) / hist["Close"].iloc[-22] * 100, 2)
        rs     = int(min(99, max(1, 50 + mr * 2)))
        trend  = hist["Close"].tail(60).tolist()
        company = symbol; mcap = "N/A"; pe = "N/A"
        try:
            info    = stock.info
            company = info.get("longName", symbol)
            mcap    = info.get("marketCap", "N/A")
            pe      = info.get("trailingPE", "N/A")
        except: pass
        return {
            "Ticker": symbol, "Company": company, "Price": cp,
            "Change %": daily, "Market Cap": mcap, "P/E": pe,
            "YTD %": ytd, "Trend": trend, "1Y %": yr1,
            "52W High": h52, "From High %": fh, "RS Rank": rs,
            "SMA 20": sma20, "SMA 50": sma50, "SMA 200": sma200,
        }
    except:
        return None

# ── Fetch news ──
@st.cache_data(ttl=600)
def fetch_news(ticker):
    try:
        stock = yf.Ticker(ticker.upper())
        raw = stock.news
        items = []
        for n in raw[:12]:
            content  = n.get("content", n)
            title    = content.get("title", n.get("title", ""))
            cl       = content.get("canonicalUrl", {})
            link     = cl.get("url", "") if isinstance(cl, dict) else ""
            if not link:
                link = content.get("url", n.get("link", "#"))
            prov     = content.get("provider", {})
            provider = prov.get("displayName", "Yahoo Finance") if isinstance(prov, dict) else n.get("publisher", "Yahoo Finance")
            pub_ts   = content.get("pubDate", n.get("providerPublishTime", None))
            time_str = ""
            if pub_ts:
                try:
                    dt = datetime.strptime(pub_ts[:19], "%Y-%m-%dT%H:%M:%S") if isinstance(pub_ts, str) else datetime.utcfromtimestamp(int(pub_ts))
                    diff = datetime.utcnow() - dt
                    time_str = f"{diff.days}d ago" if diff.days > 0 else (f"{diff.seconds//3600}h ago" if diff.seconds >= 3600 else f"{diff.seconds//60}m ago")
                except: pass
            thumb = ""
            try:
                tm = content.get("thumbnail", n.get("thumbnail", {}))
                if isinstance(tm, dict):
                    resolutions = tm.get("resolutions", [])
                    if resolutions:
                        best = sorted(resolutions, key=lambda x: x.get("width", 0))
                        for r in best:
                            if r.get("width", 0) >= 200:
                                thumb = r.get("url", "")
                                break
                        if not thumb:
                            thumb = best[-1].get("url", "")
            except: pass
            if title:
                items.append({"title": title, "link": link or "#", "source": provider, "time": time_str, "thumb": thumb})
        return items
    except:
        return []

# ── Build rows ──
rows = [fetch_stock_data(s) for s in symbols]
rows = [r for r in rows if r]
df = pd.DataFrame(rows)
# KPI DATA
portfolio_value = df["Price"].sum() if not df.empty else 0
today_gain = df["Change %"].mean() if not df.empty else 0
ytd_return = df["YTD %"].mean() if not df.empty else 0
holdings = len(df)
# ── Layout ──
k1, k2, k3, k4 = st.columns(4)

k1.metric(
    "Portfolio Value",
    f"${portfolio_value:,.2f}"
)

k2.metric(
    "Today's Gain",
    f"{today_gain:+.2f}%"
)

k3.metric(
    "YTD Return",
    f"{ytd_return:+.2f}%"
)

k4.metric(
    "Holdings",
    holdings
)
# Portfolio Analytics
if not df.empty:
# Top Movers
best_stock = df.loc[df["Change %"].idxmax()]
worst_stock = df.loc[df["Change %"].idxmin()]

st.subheader("Top Movers")

m1, m2 = st.columns(2)

with m1:
    st.success(
        f"🚀 Best Performer\n\n"
        f"{best_stock['Ticker']}  ({best_stock['Change %']:+.2f}%)"
    )

with m2:
    st.error(
        f"📉 Worst Performer\n\n"
        f"{worst_stock['Ticker']}  ({worst_stock['Change %']:+.2f}%)"
    )
    chart_df = df[["Ticker", "Price"]].copy()

    fig = px.pie(
        chart_df,
        names="Ticker",
        values="Price",
        hole=0.65
    )

    fig.update_layout(
        height=350,
        margin=dict(l=10, r=10, t=20, b=10)
    )

    st.subheader("Portfolio Allocation")
    st.plotly_chart(
        fig,
        use_container_width=True
    )
main_col, news_col = st.columns([3, 1], gap="medium")

with main_col:
    st.markdown('<p class="section-label">Watchlist</p>', unsafe_allow_html=True)

    def color_pct(val):
        try:
            v = float(val)
            if v > 0: return "color:#089981; font-weight:500;"
            if v < 0: return "color:#F23645; font-weight:500;"
        except: pass
        return "color:#4C525E;"

    def fmt_mcap(val):
        try:
            v = float(val)
            if v >= 1e12: return f"${v/1e12:.2f}T"
            if v >= 1e9:  return f"${v/1e9:.1f}B"
            if v >= 1e6:  return f"${v/1e6:.0f}M"
        except: pass
        return str(val)

    if not df.empty:
        d = df.copy()
        d["Market Cap"] = d["Market Cap"].apply(fmt_mcap)
        d["P/E"] = d["P/E"].apply(lambda v: f"{float(v):.1f}x" if str(v).replace('.','').replace('-','').isdigit() else str(v))
        styled = d.style.map(color_pct, subset=["Change %","YTD %","1Y %","From High %"]).format({
            "Price": "${:.2f}", "Change %": "{:+.2f}%", "YTD %": "{:+.2f}%",
            "1Y %": "{:+.2f}%", "From High %": "{:+.2f}%",
            "52W High": "${:.2f}", "SMA 20": "${:.2f}", "SMA 50": "${:.2f}", "SMA 200": "${:.2f}",
        })
        st.dataframe(
            styled,
            column_config={
                "Trend":   st.column_config.LineChartColumn("60d Trend", width="medium"),
                "RS Rank": st.column_config.ProgressColumn("RS Rank", min_value=1, max_value=99, format="%d"),
            },
            use_container_width=True, hide_index=True,
            height=min(60 + len(df) * 38, 600)
        )
    else:
        st.markdown('<p style="color:#868993;font-size:0.875rem;margin-top:1rem;">No data — add a symbol above.</p>', unsafe_allow_html=True)

with news_col:
    st.markdown('<p class="section-label">Market News</p>', unsafe_allow_html=True)

    news_query = st.text_input(
        "news_search", placeholder="Search ticker  e.g. TSLA",
        label_visibility="collapsed", key="news_search_input"
    )
    search_ticker = news_query.strip().upper() if news_query.strip() else (symbols[0] if symbols else None)

    if search_ticker:
        st.markdown(f'<div class="news-ticker-badge">{search_ticker}</div>', unsafe_allow_html=True)
        news_items = fetch_news(search_ticker)
        if news_items:
            html = '<div class="news-panel">'
            for item in news_items:
                title  = item["title"].replace("<","&lt;").replace(">","&gt;")
                source = item["source"].replace("<","&lt;").replace(">","&gt;")
                thumb_html = ""
                if item.get("thumb"):
                    thumb_html = f'<img class="news-thumb" src="{item["thumb"]}" alt="" loading="lazy" onerror="this.style.display=\'none\'">'
                html += f"""<div class="news-item">
  <a class="news-item-link" href="{item['link']}" target="_blank">
    {thumb_html}
    <div class="news-meta">{source} &nbsp;·&nbsp; {item['time']}</div>
    <span class="news-title">{title}</span>
  </a>
</div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="news-panel"><div class="no-news">ไม่พบข่าวสำหรับ ticker นี้</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="news-panel"><div class="no-news">พิมพ์ชื่อหุ้นด้านบนเพื่อค้นหาข่าว</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
