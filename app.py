import streamlit as st
import pandas as pd
import yfinance as yf
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
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

/* ── Dark theme ── */
.stApp { background-color: #0D0D0D; color: #E8E4DC; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem; max-width: 1700px; }

.dashboard-header {
    display: flex; align-items: baseline; gap: 14px;
    margin-bottom: 1.5rem; padding-bottom: 1rem;
    border-bottom: 1px solid #2A2A2A;
}
.dashboard-title {
    font-size: 1.35rem; font-weight: 600; letter-spacing: -0.02em;
    color: #F0EDE6; margin: 0;
}
.dashboard-subtitle { font-size: 0.78rem; color: #4A4A4A; font-weight: 400; letter-spacing: 0.04em; }

.section-label {
    font-size: 0.65rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #444;
    margin-bottom: 0.6rem; margin-top: 1.25rem;
}

/* ── Input ── */
.stTextInput > div > div > input {
    background: #161616 !important; border: 1px solid #2A2A2A !important;
    border-radius: 8px !important; font-family: 'DM Mono', monospace;
    font-size: 0.85rem; color: #E8E4DC !important; padding: 0.5rem 0.75rem; box-shadow: none !important;
}
.stTextInput > div > div > input::placeholder { color: #3A3A3A !important; }
.stTextInput > div > div > input:focus { border-color: #555 !important; box-shadow: none !important; }
.stTextInput label { color: #444 !important; }

/* ── Button ── */
.stButton > button {
    background: #1E1E1E; color: #C8C4BC; border: 1px solid #2A2A2A; border-radius: 8px;
    font-family: 'DM Sans', sans-serif; font-size: 0.85rem; font-weight: 500;
    padding: 0.52rem 1.25rem; width: 100%; margin-top: 1.75rem; transition: all 0.15s;
}
.stButton > button:hover { background: #2A2A2A; color: #F0EDE6; border-color: #444; }

/* ── Dataframe ── */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 1px solid #1E1E1E !important; }
[data-testid="stDataFrame"] > div { background: #111111 !important; border-radius: 10px; }
.stDataFrame th {
    background: #161616 !important; color: #444 !important; font-size: 0.67rem !important;
    font-weight: 600 !important; letter-spacing: 0.07em !important; text-transform: uppercase !important;
    border-bottom: 1px solid #1E1E1E !important; padding: 9px 12px !important;
}
.stDataFrame td {
    font-family: 'DM Mono', monospace; font-size: 0.8rem !important;
    padding: 8px 12px !important; border-bottom: 1px solid #1A1A1A !important;
    background: #111111 !important; color: #C8C4BC !important;
}
.stDataFrame tr:hover td { background: #161616 !important; }

/* ── Clock bar ── */
.clock-bar {
    display: flex; gap: 24px; align-items: center;
    background: #111111; border: 1px solid #1E1E1E; border-radius: 8px;
    padding: 10px 18px; margin-bottom: 12px;
    font-family: 'DM Mono', monospace;
}
.clock-item { display: flex; flex-direction: column; gap: 1px; }
.clock-label { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.09em; text-transform: uppercase; color: #3A3A3A; }
.clock-time  { font-size: 1.05rem; font-weight: 500; color: #E8E4DC; letter-spacing: 0.03em; }
.clock-date  { font-size: 0.68rem; color: #3A3A3A; }
.clock-open  { font-size: 0.6rem; color: #4A7A4A; font-weight: 600; letter-spacing: 0.05em; margin-top: 1px; }
.clock-divider { width: 1px; height: 38px; background: #1E1E1E; }

/* ── News panel ── */
.news-panel {
    background: #111111; border: 1px solid #1E1E1E;
    border-radius: 10px; overflow: hidden; margin-top: 6px;
}
.news-item {
    padding: 0; border-bottom: 1px solid #1A1A1A;
    transition: background 0.1s;
}
.news-item:last-child { border-bottom: none; }
.news-item:hover { background: #161616; }
.news-item-link {
    display: block; text-decoration: none; padding: 12px 14px;
}
.news-thumb {
    width: 100%; aspect-ratio: 16/9; object-fit: cover;
    border-radius: 6px; margin-bottom: 8px;
    background: #1A1A1A;
    display: block;
}
.news-source {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: #3A3A3A; margin-bottom: 4px;
}
.news-title {
    font-size: 0.8rem; font-weight: 500; color: #C8C4BC;
    line-height: 1.4; margin-bottom: 4px; display: block;
}
.news-item:hover .news-title { color: #F0EDE6; }
.news-time { font-size: 0.65rem; color: #2E2E2E; font-family: 'DM Mono', monospace; }
.no-news { padding: 28px 14px; color: #333; font-size: 0.82rem; text-align: center; }

.news-ticker-badge {
    display: inline-block; font-family: 'DM Mono', monospace;
    font-size: 0.7rem; font-weight: 600;
    background: #1E1E1E; color: #888; border: 1px solid #2A2A2A;
    padding: 2px 10px; border-radius: 4px; margin-bottom: 8px; letter-spacing: 0.05em;
}
</style>

<div class="dashboard-header">
    <span class="dashboard-title">Miu Stock Dashboard</span>
    <span class="dashboard-subtitle">Real-Time Market Data &nbsp;·&nbsp; Technical Analysis &nbsp;·&nbsp; Portfolio Tracking</span>
</div>
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

# ── Fetch news via yfinance (with thumbnail) ──
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

            # thumbnail
            thumb = ""
            try:
                tm = content.get("thumbnail", n.get("thumbnail", {}))
                if isinstance(tm, dict):
                    resolutions = tm.get("resolutions", [])
                    if resolutions:
                        # เลือก resolution กลางๆ ไม่เล็กเกิน
                        best = sorted(resolutions, key=lambda x: x.get("width", 0))
                        for r in best:
                            if r.get("width", 0) >= 200:
                                thumb = r.get("url", "")
                                break
                        if not thumb:
                            thumb = best[-1].get("url", "")
            except: pass

            if title:
                items.append({
                    "title": title, "link": link or "#",
                    "source": provider, "time": time_str,
                    "thumb": thumb,
                })
        return items
    except:
        return []

# ── Build rows ──
rows = [fetch_stock_data(s) for s in symbols]
rows = [r for r in rows if r]
df = pd.DataFrame(rows)

# ── Layout ──
main_col, news_col = st.columns([3, 1], gap="large")

with main_col:
    st.markdown('<p class="section-label">Watchlist</p>', unsafe_allow_html=True)

    # Clock bar
    tz_th = ZoneInfo("Asia/Bangkok")
    tz_ny = ZoneInfo("America/New_York")
    now_th = datetime.now(tz_th)
    now_ny = datetime.now(tz_ny)
    is_market_open = (now_ny.weekday() < 5 and 9*60+30 <= now_ny.hour*60+now_ny.minute <= 16*60)
    market_tag = '<span class="clock-open">● MARKET OPEN</span>' if is_market_open else ""

    st.markdown(f"""
    <div class="clock-bar">
        <div class="clock-item">
            <span class="clock-label">🇹🇭 Thailand</span>
            <span class="clock-time">{now_th.strftime("%H:%M:%S")}</span>
            <span class="clock-date">{now_th.strftime("%a %d %b %Y")}</span>
        </div>
        <div class="clock-divider"></div>
        <div class="clock-item">
            <span class="clock-label">🇺🇸 New York</span>
            <span class="clock-time">{now_ny.strftime("%H:%M:%S")}</span>
            <span class="clock-date">{now_ny.strftime("%a %d %b %Y")}</span>
            {market_tag}
        </div>
    </div>
    """, unsafe_allow_html=True)

    def color_pct(val):
        try:
            v = float(val)
            if v > 0: return "color:#4A8C5C; font-weight:500;"
            if v < 0: return "color:#8C4A4A; font-weight:500;"
        except: pass
        return "color:#444;"

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
        st.markdown('<p style="color:#333;font-size:0.875rem;margin-top:1rem;">No data — add a symbol above.</p>', unsafe_allow_html=True)

with news_col:
    st.markdown('<p class="section-label">Market News</p>', unsafe_allow_html=True)

    news_query = st.text_input(
        "news_search",
        placeholder="Search ticker  e.g. TSLA",
        label_visibility="collapsed",
        key="news_search_input"
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
    <div class="news-source">{source} &nbsp;·&nbsp; {item['time']}</div>
    <span class="news-title">{title}</span>
  </a>
</div>"""
            html += "</div>"
            st.markdown(html, unsafe_allow_html=True)
        else:
            st.markdown('<div class="news-panel"><div class="no-news">ไม่พบข่าวสำหรับ ticker นี้</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="news-panel"><div class="no-news">พิมพ์ชื่อหุ้นด้านบนเพื่อค้นหาข่าว</div></div>', unsafe_allow_html=True)
