import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="VOO / SPY Macro Risk Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root{--ink:#111827;--muted:#64748b;--line:#d7dde8;--green:#10b981;--yellow:#eab308;--orange:#f97316;--red:#ef4444;--blue:#3b82f6;--pink:#ec4899;--soft:#f8fafc}
html,body,[class*="css"]{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Helvetica Neue",Arial,sans-serif}
.block-container{padding-top:.7rem;padding-bottom:2rem;max-width:1220px}
.pill{display:inline-flex;background:#111827;color:#fff;padding:7px 18px;border-radius:999px;font-weight:900;letter-spacing:.5px;margin-bottom:8px;font-size:13px}
.date-pill{display:inline-flex;float:right;border:1px solid var(--line);padding:6px 16px;border-radius:999px;color:#374151;background:#f8fafc;font-weight:700;font-size:13px}
.main-title{font-size:34px;line-height:1.05;font-weight:950;color:var(--ink);letter-spacing:-.7px;margin-bottom:4px}
.sub-title{color:var(--muted);font-size:14px;margin-bottom:14px}
.green-accent{display:inline-block;width:42px;height:5px;background:var(--green);margin-right:10px;vertical-align:middle;border-radius:999px}
.metric-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:14px 16px 12px;margin-bottom:12px;box-shadow:0 2px 12px rgba(17,24,39,.035);min-height:248px}
.metric-card h3{margin:0;font-size:16px;font-weight:950;color:var(--ink)}
.metric-card .desc{color:var(--muted);font-size:12px;margin-top:3px}
.big-number{text-align:center;font-size:48px;line-height:.95;font-weight:950;letter-spacing:-1.5px}
.badge{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;font-weight:950;font-size:13px;padding:7px 13px;border:2px solid currentColor;min-width:105px;background:rgba(255,255,255,.72)}
.segment-wrap{margin-top:8px}
.segment-bar{position:relative;display:grid;grid-template-columns:repeat(7,1fr);gap:2px;height:17px;margin:6px 10px 5px}
.segment{height:17px;opacity:.95}
.pointer{position:absolute;top:-14px;width:0;height:0;border-left:8px solid transparent;border-right:8px solid transparent;transform:translateX(-50%)}
.segment-labels{display:grid;grid-template-columns:repeat(7,1fr);gap:1px;margin:0 8px;text-align:center;font-size:10px;color:#64748b;font-weight:800}
.source-chip{display:inline-flex;background:#f1f5f9;border:1px solid #e2e8f0;color:#475569;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:800}
.strategy-grid{display:grid;grid-template-columns:1.05fr 1.35fr 1fr;gap:14px;align-items:stretch;margin:6px 0 14px}
.strategy-panel{background:#ecfdf5;border:2px solid #10b981;border-radius:16px;padding:16px 18px;height:100%}
.strategy-panel .title{color:#059669;font-size:13px;font-weight:950;margin-bottom:7px}
.strategy-panel .main{color:#111827;font-size:25px;font-weight:950;line-height:1.2}
.signal-card{background:linear-gradient(135deg,#ecfdf5 0%,#fff 72%);border:1px solid #a7f3d0;border-radius:16px;padding:14px 16px;height:100%}
.signal-score{font-size:38px;font-weight:950;color:#059669;line-height:1}
.signal-label{font-size:16px;font-weight:950;color:#111827}
.position-panel{background:#fff;border:1px solid #d7dde8;border-radius:16px;padding:16px 18px;height:100%;box-shadow:0 2px 12px rgba(17,24,39,.035)}
.position-panel .k{color:#64748b;font-size:13px;font-weight:950}
.position-panel .v{color:#111827;font-size:25px;font-weight:950;margin-top:4px}
.note-panel{background:#f8fafc;border:1px solid #e2e8f0;border-left:5px solid #10b981;border-radius:16px;padding:14px 16px;height:100%;color:#334155;font-size:13px;line-height:1.5}
.note-panel.warning{border-left-color:#eab308;background:#fffbeb}.note-panel.danger{border-left-color:#ef4444;background:#fef2f2}
.compact-summary-title{color:#64748b;font-weight:950;font-size:12px;margin-bottom:5px}.compact-summary-value{font-size:20px;color:#111827;font-weight:950;line-height:1.1}.compact-summary-note{color:#64748b;font-size:11px;margin-top:4px}
.macro-card{background:#fff;border:1px solid #d7dde8;border-radius:16px;padding:13px 14px;box-shadow:0 2px 12px rgba(17,24,39,.035);min-height:132px}
.macro-title{font-size:12px;font-weight:950;color:#64748b;text-transform:uppercase}.macro-value{font-size:27px;font-weight:950;color:#111827;margin-top:4px}.macro-label{display:inline-flex;border-radius:999px;padding:4px 9px;font-size:11px;font-weight:950;margin-top:7px}.macro-note{color:#64748b;font-size:11px;margin-top:6px;line-height:1.35}
.responsive-playbook{margin-bottom:12px}.pb-title{font-size:17px;font-weight:950;color:#111827;margin:6px 0 8px}.pb-card{background:#fff;border:1px solid #d7dde8;border-radius:16px;padding:10px 12px;box-shadow:0 2px 12px rgba(17,24,39,.035)}
.pb-header,.pb-row{display:grid;grid-template-columns:90px 1fr 1.6fr 56px;gap:10px;align-items:center}.pb-header{color:#64748b;font-size:13px;font-weight:900;padding:4px 6px 8px;border-bottom:1px solid #e5e7eb}.pb-row{font-size:13px;padding:8px 6px;border-bottom:1px solid #eef2f7}.pb-row:last-child{border-bottom:none}.pb-row.now-green{background:#ecfdf5;border-radius:10px}.pb-row.now-yellow{background:#fefce8;border-radius:10px}.pb-range{font-weight:950;white-space:nowrap}.pb-emotion{font-weight:900;color:#111827}.pb-strategy{font-weight:750;color:#334155}.pb-now{display:inline-block;padding:3px 8px;border-radius:999px;color:#fff;font-size:11px;font-weight:950;text-align:center}
.data-dict{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:12px 14px;margin:8px 0;font-size:13px;color:#475569}.data-dict b{color:#111827}
@media(max-width:760px){
html,body,.stApp{background:#f8fafc!important;color:#111827!important}.block-container{padding-left:.65rem;padding-right:.65rem;padding-top:.25rem;max-width:100%}.pill,.date-pill{display:none}.main-title{font-size:24px;line-height:1.12;margin:0 0 4px;color:#111827!important}.sub-title{font-size:12px;margin-bottom:8px;line-height:1.25;color:#64748b!important}.green-accent{width:28px;height:4px;margin-right:8px}.metric-card{min-height:0!important;padding:10px;margin-bottom:8px;border-radius:14px}.metric-card h3{font-size:14px;line-height:1.1}.metric-card .desc,.source-chip{display:none}.big-number{font-size:38px;letter-spacing:-1px}.badge{font-size:12px;padding:5px 9px;min-width:72px;border-width:1.5px}.segment-wrap{margin-top:4px}.segment-bar{height:12px;margin:4px}.segment{height:12px}.pointer{top:-12px;border-left-width:7px!important;border-right-width:7px!important;border-top-width:12px!important}.segment-labels{margin:0 2px;font-size:8px;gap:1px}.strategy-grid{display:block;margin:4px 0 8px}.strategy-panel,.position-panel,.note-panel,.signal-card{padding:10px 12px;border-radius:14px;margin-bottom:8px;min-height:0!important}.strategy-panel .title,.compact-summary-title{font-size:12px;margin-bottom:4px}.strategy-panel .main{font-size:21px;line-height:1.18}.signal-score{font-size:32px}.signal-label{font-size:14px}.compact-summary-note{font-size:11px}.compact-summary-value{font-size:18px!important}.position-panel .v{font-size:22px}.note-panel{font-size:12px;line-height:1.42;max-height:135px;overflow:auto}.macro-card{min-height:auto;margin-bottom:8px;padding:10px 12px}.macro-value{font-size:22px}.pb-title{font-size:16px!important;margin:10px 0 7px!important;color:#111827!important}.pb-card{padding:7px 8px;border-radius:14px;background:#fff!important;color:#111827!important}.pb-header{display:none}.pb-row{grid-template-columns:62px 1fr 92px;gap:8px;padding:8px;font-size:12px;border-bottom:1px solid #eef2f7}.pb-row .pb-strategy{text-align:right;line-height:1.25}.pb-row .pb-now-wrap{display:none}.pb-range{font-size:13px}.pb-emotion{font-size:13px;color:#111827!important}.pb-strategy{font-size:12px;color:#334155!important}.pb-now{font-size:9px;padding:2px 6px;margin-left:4px}
}

/* --- Macro heat cards --- */
.macro-card.heat-green {
    background: linear-gradient(135deg,#ecfdf5 0%,#ffffff 75%);
    border-color:#a7f3d0;
}
.macro-card.heat-yellow {
    background: linear-gradient(135deg,#fffbeb 0%,#ffffff 75%);
    border-color:#fde68a;
}
.macro-card.heat-red {
    background: linear-gradient(135deg,#fef2f2 0%,#ffffff 75%);
    border-color:#fecaca;
}
.macro-risk-summary {
    border-radius:16px;
    padding:12px 16px;
    margin: 4px 0 14px 0;
    font-size:13px;
    line-height:1.5;
    border:1px solid #e2e8f0;
}
.macro-risk-summary.green {
    background:#ecfdf5;
    border-color:#a7f3d0;
    color:#065f46;
}
.macro-risk-summary.yellow {
    background:#fffbeb;
    border-color:#fde68a;
    color:#92400e;
}
.macro-risk-summary.red {
    background:#fef2f2;
    border-color:#fecaca;
    color:#991b1b;
}


/* --- Pro clean v3 cards --- */
.macro-card.heat-green{background:linear-gradient(135deg,#ecfdf5 0%,#fff 78%);border-color:#a7f3d0}
.macro-card.heat-yellow{background:linear-gradient(135deg,#fffbeb 0%,#fff 78%);border-color:#fde68a}
.macro-card.heat-red{background:linear-gradient(135deg,#fef2f2 0%,#fff 78%);border-color:#fecaca}
.decision-summary{border-radius:18px;padding:16px 18px;margin:10px 0 16px;border:1px solid #d7dde8;box-shadow:0 2px 12px rgba(17,24,39,.035);font-size:13px;line-height:1.55}
.decision-summary.green{background:linear-gradient(135deg,#ecfdf5 0%,#fff 78%);border-color:#a7f3d0;color:#065f46}
.decision-summary.yellow{background:linear-gradient(135deg,#fffbeb 0%,#fff 78%);border-color:#fde68a;color:#92400e}
.decision-summary.red{background:linear-gradient(135deg,#fef2f2 0%,#fff 78%);border-color:#fecaca;color:#991b1b}
.decision-grid{display:grid;grid-template-columns:1fr 1fr 1.1fr;gap:14px;align-items:start}
.decision-title{font-size:16px;font-weight:950;margin-bottom:6px}
.decision-k{font-size:12px;font-weight:950;opacity:.8}
.decision-v{font-size:20px;font-weight:950;margin-top:2px}
.pro-title{font-size:20px;font-weight:950;color:#111827;margin:16px 0 10px}
@media(max-width:760px){.decision-grid{grid-template-columns:1fr;gap:8px}.decision-v{font-size:17px}.decision-summary{padding:12px 14px}.pro-title{font-size:17px;margin:10px 0 8px}}


/* --- Pro summary visual upgrade --- */
.pro-composite-box{
    border-radius:18px;
    padding:15px 18px;
    margin:14px 0 20px 0;
    border:1px solid #d7dde8;
    box-shadow:0 2px 12px rgba(17,24,39,.035);
    font-size:13px;
    line-height:1.55;
}
.pro-composite-box.green{
    background:linear-gradient(135deg,#ecfdf5 0%,#ffffff 78%);
    border-color:#a7f3d0;
    color:#065f46;
}
.pro-composite-box.yellow{
    background:linear-gradient(135deg,#fffbeb 0%,#ffffff 78%);
    border-color:#fde68a;
    color:#92400e;
}
.pro-composite-box.red{
    background:linear-gradient(135deg,#fef2f2 0%,#ffffff 78%);
    border-color:#fecaca;
    color:#991b1b;
}
.pro-composite-title{
    font-size:16px;
    font-weight:950;
    margin-bottom:6px;
}
.pro-card-spacer{
    margin-bottom:18px;
}
@media(max-width:760px){
    .pro-composite-box{padding:12px 14px;margin:10px 0 14px 0}
    .pro-composite-title{font-size:15px}
    .pro-card-spacer{margin-bottom:10px}
}


/* --- Unified decision summary --- */
.unified-summary {
    border-radius:20px;
    padding:18px 20px;
    margin:12px 0 20px 0;
    border:1px solid #d7dde8;
    box-shadow:0 3px 16px rgba(17,24,39,.045);
    font-size:13px;
    line-height:1.55;
}
.unified-summary.green {
    background:linear-gradient(135deg,#ecfdf5 0%,#ffffff 78%);
    border-color:#a7f3d0;
    color:#065f46;
}
.unified-summary.yellow {
    background:linear-gradient(135deg,#fffbeb 0%,#ffffff 78%);
    border-color:#fde68a;
    color:#92400e;
}
.unified-summary.red {
    background:linear-gradient(135deg,#fef2f2 0%,#ffffff 78%);
    border-color:#fecaca;
    color:#991b1b;
}
.unified-title {
    font-size:18px;
    font-weight:950;
    margin-bottom:8px;
}
.unified-grid {
    display:grid;
    grid-template-columns:1fr 1fr 1fr;
    gap:14px;
    margin-top:10px;
}
.unified-k {
    font-size:12px;
    font-weight:950;
    opacity:.8;
}
.unified-v {
    font-size:18px;
    font-weight:950;
    margin-top:2px;
}
.unified-note {
    font-size:12px;
    margin-top:8px;
    opacity:.92;
}
@media(max-width:760px){
    .unified-summary{padding:13px 14px;margin:10px 0 14px 0}
    .unified-title{font-size:16px}
    .unified-grid{grid-template-columns:1fr;gap:8px}
    .unified-v{font-size:16px}
}


/* --- Decision window guidance --- */
.mode-chip {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    border-radius:14px;
    padding:10px 14px;
    margin:4px 0 14px 0;
    border:1px solid #d7dde8;
    font-size:13px;
    font-weight:850;
}
.mode-chip.green {
    background:linear-gradient(135deg,#ecfdf5 0%,#ffffff 80%);
    border-color:#a7f3d0;
    color:#065f46;
}
.mode-chip.yellow {
    background:linear-gradient(135deg,#fffbeb 0%,#ffffff 80%);
    border-color:#fde68a;
    color:#92400e;
}
.mode-chip.gray {
    background:linear-gradient(135deg,#f8fafc 0%,#ffffff 80%);
    border-color:#cbd5e1;
    color:#475569;
}
.mode-chip .mode-main {
    font-size:14px;
    font-weight:950;
}
.mode-chip .mode-sub {
    font-size:12px;
    opacity:.85;
}
@media(max-width:760px){
    .mode-chip{display:block;padding:9px 11px;margin:2px 0 10px 0}
    .mode-chip .mode-main{font-size:13px}
    .mode-chip .mode-sub{font-size:11px;margin-top:3px}
}

</style>
""",
    unsafe_allow_html=True,
)

INDEX_MAP = {
    "S&P 500 (^GSPC)": "^GSPC",
    "SPY ETF": "SPY",
    "VOO ETF": "VOO",
    "Nasdaq 100 (^NDX)": "^NDX",
    "QQQ ETF": "QQQ",
    "Dow Jones (^DJI)": "^DJI",
}
MACRO_SYMBOLS = {"10Y Yield": "^TNX", "DXY": "DX-Y.NYB", "HYG": "HYG", "LQD": "LQD"}
PRO_SYMBOLS = {"MOVE": "^MOVE", "VIX3M": "^VIX3M", "RSP": "RSP", "SPY": "SPY"}
MACRO_DISPLAY_NAMES = {
    "10Y Yield": "10Y Yield · 美国10年期国债收益率",
    "DXY": "DXY · 美元指数",
    "HYG": "HYG · 高收益债信用风险",
    "LQD": "LQD · 投资级债/利率压力",
    "MOVE": "MOVE · 债券波动率",
    "VIX3M/VIX": "VIX3M/VIX · 波动率期限结构",
    "Real Yield": "Real Yield · 10年期真实利率",
    "RSP/SPY": "RSP/SPY · 市场宽度 Proxy",
    "Trend": "Trend · 200日均线趋势",
    "Put/Call": "Put/Call Proxy · SPY期权看跌/看涨成交量比",
}
MACRO_DISPLAY_NAMES = {
    "10Y Yield": "10Y Yield · 美国10年期国债收益率",
    "DXY": "DXY · 美元指数",
    "HYG": "HYG · 高收益债信用风险",
    "LQD": "LQD · 投资级债/利率压力",
    "MOVE": "MOVE · 债券波动率",
    "VIX3M/VIX": "VIX3M/VIX · 波动率期限结构",
    "Real Yield": "Real Yield · 10年期真实利率",
    "RSP/SPY": "RSP/SPY · 市场宽度 Proxy",
    "Trend": "Trend · 200日均线趋势",
    "Put/Call": "Put/Call Proxy · SPY期权看跌/看涨成交量比",
}
PERIOD_OPTIONS = ["实时盘中", "3d", "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
INTERVAL_OPTIONS = ["1d", "60m", "30m", "15m", "5m", "1m"]
FG_HISTORY_PATH = Path("fg_history.csv")

VIX_ROWS = [
    ("< 11", "Vol Suppression", "停止追高，保留现金"),
    ("11 — 14", "Risk-On", "正常配置，顺势持有"),
    ("14 — 18", "Neutral", "常规定投，保持节奏"),
    ("18 — 25", "Early Stress", "放慢加仓，观察波动"),
    ("25 — 35", "Risk-Off", "分批加仓，逢低布局"),
    ("35 — 50", "Panic", "强力加仓，但保留现金"),
    ("> 50", "Liquidation", "分批抄底，严控节奏"),
]
FG_ROWS = [
    ("0 — 15", "Capitulation", "激进加仓"),
    ("15 — 30", "Deep Fear", "加仓，分批买入"),
    ("30 — 45", "Fear", "正常定投，等待修复"),
    ("45 — 60", "Neutral", "保持节奏，观察趋势"),
    ("60 — 75", "Greed", "控制仓位，不追高"),
    ("75 — 85", "Euphoria", "减速买入，部分止盈"),
    ("85 — 100", "Bubble Zone", "明确止盈，降低风险"),
]


def safe_float(x, default=None):
    try:
        if x is None or pd.isna(x):
            return default
        return float(x)
    except Exception:
        return default


@st.cache_data(ttl=45, show_spinner=False)
def fetch_yahoo(symbol: str, period: str, interval: str) -> pd.DataFrame:
    try:
        query_period = "5d" if period == "3d" else period

        df = yf.download(
            symbol,
            period=query_period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False,
        )
        if df is None or df.empty:
            return pd.DataFrame()

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        df = df.reset_index()
        time_col = "Datetime" if "Datetime" in df.columns else "Date"
        df = df.rename(columns={time_col: "time"})

        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col not in df.columns:
                df[col] = 0 if col == "Volume" else np.nan

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["time", "Close"])

        if period == "3d" and not df.empty:
            cutoff = df["time"].max() - pd.Timedelta(days=3)
            df = df[df["time"] >= cutoff]

        return df[["time", "Open", "High", "Low", "Close", "Volume"]].copy()

    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=120, show_spinner=False)
def fetch_cnn_fear_greed(manual_value: float) -> Tuple[float, str, str, pd.DataFrame]:
    urls = [
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2020-01-01",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
    ]
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json,text/plain,*/*", "Referer": "https://edition.cnn.com/markets/fear-and-greed"}
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            fg = data.get("fear_and_greed", {}) or {}
            score = safe_float(fg.get("score"), None)
            rating = fg.get("rating") or fg.get("status") or "CNN"
            hist = pd.DataFrame()
            points = (data.get("fear_and_greed_historical", {}) or {}).get("data", [])
            rows = []
            for p in points:
                if not isinstance(p, dict):
                    continue
                x = p.get("x") or p.get("timestamp") or p.get("date")
                y = safe_float(p.get("y") or p.get("score") or p.get("value"), None)
                if x is None or y is None:
                    continue
                ts = pd.to_datetime(x, unit="ms", utc=True, errors="coerce")
                if pd.isna(ts):
                    ts = pd.to_datetime(x, utc=True, errors="coerce")
                if not pd.isna(ts):
                    rows.append({"time": ts, "FearGreed": y})
            if rows:
                hist = pd.DataFrame(rows).dropna().sort_values("time")
            if score is not None:
                return float(score), str(rating).title(), "CNN live endpoint", hist
        except Exception:
            pass
    return float(manual_value), "Manual fallback", "Manual fallback · CNN unavailable", pd.DataFrame([{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": float(manual_value)}])


@st.cache_data(ttl=300, show_spinner=False)
def fetch_finhacker_fear_greed() -> Tuple[Optional[float], Optional[str], str, pd.DataFrame]:
    """
    Finhacker tracks the CNN Fear & Greed Index historical/current value.
    Used only as a CNN-mouthpiece fallback when CNN's own dataviz endpoint is blocked.
    """
    urls = [
        "https://www.finhacker.cz/en/fear-and-greed-index-historical-data-and-chart/",
        "https://www.finhacker.cz/fear-and-greed-index-historical-data-and-chart/",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Cache-Control": "no-cache",
    }

    last_error = ""
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            html = re.sub(r"\s+", " ", r.text)

            patterns = [
                r"current value of the Fear\s*&\s*Greed Index as of .*? is\s+(\d+(?:\.\d+)?)\s*\(([a-zA-Z ]+)\)",
                r"current value of the Fear\s*&\s*Greed Index.*? is\s+(\d+(?:\.\d+)?)\s*\(([a-zA-Z ]+)\)",
                r"The current value.*?Fear\s*&\s*Greed.*?is\s+(\d+(?:\.\d+)?)\s*[-–]\s*([a-zA-Z ]+)",
                r"current value.{0,240}?(\d{1,3})(?:\s|&nbsp;)*(?:\(|-|–)([A-Za-z ]{3,30})(?:\)|\.|,)",
            ]

            for pat in patterns:
                match = re.search(pat, html, re.I | re.S)
                if match:
                    value = max(0.0, min(100.0, float(match.group(1))))
                    label = match.group(2).strip().title()
                    hist = pd.DataFrame([{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": value}])
                    return value, label, "Finhacker CNN mirror", hist

            nearby = re.search(r"Fear\s*&\s*Greed Index.{0,600}", html, re.I | re.S)
            if nearby:
                nums = re.findall(r"\b([0-9]{1,3})(?:\.\d+)?\b", nearby.group(0))
                candidates = [int(x) for x in nums if 0 <= int(x) <= 100]
                if candidates:
                    value = float(candidates[0])
                    label = "Greed" if value >= 56 else ("Fear" if value <= 44 else "Neutral")
                    hist = pd.DataFrame([{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": value}])
                    return value, label, "Finhacker CNN mirror · loose parse", hist

            last_error = "parse failed"

        except Exception as e:
            last_error = str(e)

    return None, None, f"Finhacker CNN mirror unavailable: {last_error}", pd.DataFrame()


def fetch_fear_greed_with_fallback(manual_value: float) -> Tuple[float, str, str, pd.DataFrame]:
    # 1) CNN official endpoint
    cnn_value, cnn_rating, cnn_source, cnn_hist = fetch_cnn_fear_greed(manual_value)
    if "CNN live endpoint" in cnn_source:
        return cnn_value, cnn_rating, cnn_source, cnn_hist

    # 2) Finhacker mirror of CNN Fear & Greed
    fh_value, fh_rating, fh_source, fh_hist = fetch_finhacker_fear_greed()
    if fh_value is not None:
        return fh_value, fh_rating or "CNN Mirror", fh_source, fh_hist

    # 3) Local GitHub history last value to avoid jumping back to 50 when web sources are temporarily blocked.
    try:
        local_hist = load_fg_history()
        if local_hist is not None and not local_hist.empty:
            last_row = local_hist.sort_values("date").iloc[-1]
            value = float(last_row["FearGreed"])
            label = str(last_row.get("label", "")) or ("Greed" if value >= 56 else ("Fear" if value <= 44 else "Neutral"))
            hist = fg_history_for_correlation(local_hist)
            return value, label, "Local fg_history.csv fallback", hist
    except Exception:
        pass

    # 4) Manual fallback as final safety net.
    manual_hist = pd.DataFrame([{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": float(manual_value)}])
    return float(manual_value), "Manual fallback", "Manual fallback · CNN sources unavailable", manual_hist


def load_fg_history() -> pd.DataFrame:
    cols = ["date", "FearGreed", "label", "source", "updated_at"]
    if not FG_HISTORY_PATH.exists():
        return pd.DataFrame(columns=cols)
    try:
        hist = pd.read_csv(FG_HISTORY_PATH)
        if hist.empty or "date" not in hist.columns or "FearGreed" not in hist.columns:
            return pd.DataFrame(columns=cols)
        for col in cols:
            if col not in hist.columns:
                hist[col] = ""
        hist["date"] = pd.to_datetime(hist["date"], errors="coerce").dt.date.astype(str)
        hist["FearGreed"] = pd.to_numeric(hist["FearGreed"], errors="coerce")
        hist = hist.dropna(subset=["date", "FearGreed"]).drop_duplicates(subset=["date"], keep="last").sort_values("date")
        return hist[cols]
    except Exception:
        return pd.DataFrame(columns=cols)


def build_fg_history_for_app(current_value: float, current_label: str, current_source: str) -> pd.DataFrame:
    hist = load_fg_history()
    today = datetime.now().date().isoformat()
    row = pd.DataFrame([{"date": today, "FearGreed": float(current_value), "label": str(current_label), "source": str(current_source), "updated_at": datetime.now(timezone.utc).isoformat()}])
    if hist.empty:
        hist = row
    elif today not in set(hist["date"].astype(str)):
        hist = pd.concat([hist, row], ignore_index=True)
    hist["date"] = pd.to_datetime(hist["date"], errors="coerce").dt.date.astype(str)
    hist["FearGreed"] = pd.to_numeric(hist["FearGreed"], errors="coerce")
    return hist.dropna(subset=["date", "FearGreed"]).drop_duplicates(subset=["date"], keep="last").sort_values("date")



def save_fg_history_file(hist: pd.DataFrame) -> bool:
    try:
        if hist is None or hist.empty:
            return False
        out = hist.copy()
        out["date"] = pd.to_datetime(out["date"], errors="coerce").dt.date.astype(str)
        out["FearGreed"] = pd.to_numeric(out["FearGreed"], errors="coerce")
        out = out.dropna(subset=["date", "FearGreed"])
        out = out.drop_duplicates(subset=["date"], keep="last").sort_values("date")
        out.to_csv(FG_HISTORY_PATH, index=False)
        return True
    except Exception:
        return False


def fg_history_for_correlation(hist: pd.DataFrame) -> pd.DataFrame:
    if hist is None or hist.empty:
        return pd.DataFrame(columns=["time", "FearGreed"])
    x = hist.copy()
    x["time"] = pd.to_datetime(x["date"], errors="coerce")
    x["FearGreed"] = pd.to_numeric(x["FearGreed"], errors="coerce")
    return x.dropna(subset=["time", "FearGreed"])[["time", "FearGreed"]].sort_values("time")


def vix_level(v: float):
    if v < 11: return "压波动", "停止追高，保留现金", "#10b981", 0
    if v < 14: return "Risk-On", "正常配置，顺势持有", "#10b981", 1
    if v < 18: return "健康中性", "常规定投，保持节奏", "#10b981", 2
    if v < 25: return "早期压力", "放慢加仓，观察波动", "#eab308", 3
    if v < 35: return "Risk-Off", "分批加仓，逢低布局", "#f97316", 4
    if v < 50: return "恐慌", "强力加仓，但保留现金", "#ef4444", 5
    return "流动性踩踏", "分批抄底，严控节奏", "#991b1b", 6


def fear_greed_level(v: float):
    if v <= 15: return "投降", "激进加仓", "#ef4444", 0
    if v <= 30: return "深度恐惧", "加仓，分批买入", "#f97316", 1
    if v <= 45: return "恐惧", "正常定投，等待修复", "#eab308", 2
    if v <= 60: return "中性", "保持节奏，观察趋势", "#3b82f6", 3
    if v <= 75: return "贪婪", "控制仓位，不追高", "#eab308", 4
    if v <= 85: return "亢奋", "减速买入，部分止盈", "#f97316", 5
    return "泡沫区", "明确止盈，降低风险", "#ec4899", 6


def classify_10y(y_raw: float):
    y = y_raw / 10 if y_raw and y_raw > 20 else y_raw
    if y < 3.5: return y, "宽松", "偏利好估值", "#10b981", 8
    if y < 4.5: return y, "中性", "利率压力可控", "#3b82f6", 2
    if y < 5.0: return y, "压估值", "估值扩张受限", "#eab308", -8
    return y, "高压区", "对 SPY/VOO 估值不友好", "#ef4444", -16


def classify_dxy(chg):
    if chg is None: return "未知", "观察美元方向", "#64748b", 0
    if chg > 2: return "美元走强", "全球流动性偏紧", "#ef4444", -9
    if chg > .5: return "美元偏强", "风险资产承压", "#eab308", -4
    if chg < -2: return "美元走弱", "流动性改善", "#10b981", 7
    if chg < -.5: return "美元偏弱", "风险偏好友好", "#10b981", 4
    return "美元稳定", "流动性中性", "#3b82f6", 1


def classify_hyg(chg):
    if chg is None: return "未知", "观察 HYG 趋势", "#64748b", 0
    if chg < -3: return "信用恶化", "高收益债承压，风险上升", "#ef4444", -14
    if chg < -1: return "信用偏弱", "大盘上涨质量需验证", "#eab308", -7
    if chg > 3: return "信用修复", "风险偏好明显改善", "#10b981", 10
    if chg > 1: return "信用改善", "支持 Risk-On", "#10b981", 6
    return "信用稳定", "系统性风险暂稳", "#3b82f6", 2


def classify_lqd(chg):
    if chg is None: return "未知", "观察 LQD", "#64748b", 0
    if chg < -3: return "债券承压", "利率/信用压力偏大", "#ef4444", -7
    if chg < -1: return "债券偏弱", "估值压力存在", "#eab308", -3
    if chg > 2: return "债券修复", "利率压力缓和", "#10b981", 5
    return "债券稳定", "宏观压力中性", "#3b82f6", 1


def vix_pointer_pct(v):
    seg = 100 / 7
    if v < 11: return max(2, min(seg - 1, (v / 11) * seg))
    if v < 14: return seg * 1 + (v - 11) / 3 * seg
    if v < 18: return seg * 2 + (v - 14) / 4 * seg
    if v < 25: return seg * 3 + (v - 18) / 7 * seg
    if v < 35: return seg * 4 + (v - 25) / 10 * seg
    if v < 50: return seg * 5 + (v - 35) / 15 * seg
    return min(98, seg * 6 + (min(v, 80) - 50) / 30 * seg)


def fg_pointer_pct(v):
    seg = 100 / 7
    if v <= 15: return max(2, v / 15 * seg)
    if v <= 30: return seg + (v - 15) / 15 * seg
    if v <= 45: return seg * 2 + (v - 30) / 15 * seg
    if v <= 60: return seg * 3 + (v - 45) / 15 * seg
    if v <= 75: return seg * 4 + (v - 60) / 15 * seg
    if v <= 85: return seg * 5 + (v - 75) / 10 * seg
    return min(98, seg * 6 + (v - 85) / 15 * seg)


def pct_change_text(df):
    if df is None or df.empty or len(df) < 2:
        return None
    first, last = safe_float(df["Close"].iloc[0]), safe_float(df["Close"].iloc[-1])
    if first in (None, 0) or last is None:
        return None
    return (last / first - 1) * 100


def annotation_class(level): return "danger" if level == "risk" else ("warning" if level == "caution" else "")


def compute_correlations(index_df, vix_df, fg_hist, macro_data, rolling_window):
    if index_df is None or index_df.empty:
        return pd.DataFrame(), {}

    def prep(df, col):
        if df is None or df.empty or "time" not in df.columns or "Close" not in df.columns:
            return pd.DataFrame()
        x = df.copy()
        x["date"] = pd.to_datetime(x["time"], errors="coerce").dt.date
        x[col] = pd.to_numeric(x["Close"], errors="coerce")
        return x.dropna(subset=["date", col]).groupby("date", as_index=False)[col].last()

    merged = prep(index_df, "Index")
    if merged.empty:
        return pd.DataFrame(), {}

    for name, df in {"VIX": vix_df, **macro_data}.items():
        d = prep(df, name)
        if not d.empty:
            merged = pd.merge(merged, d, on="date", how="left")

    if fg_hist is not None and not fg_hist.empty and "FearGreed" in fg_hist.columns:
        fg = fg_hist.copy()
        fg["date"] = pd.to_datetime(fg["time"], errors="coerce").dt.date
        fg["FearGreed"] = pd.to_numeric(fg["FearGreed"], errors="coerce")
        fg = fg.dropna(subset=["date", "FearGreed"]).groupby("date", as_index=False)["FearGreed"].last()
        merged = pd.merge(merged, fg, on="date", how="left")
        merged["FearGreed"] = merged["FearGreed"].ffill().bfill()

    merged = merged.sort_values("date")
    merged["IndexRet"] = merged["Index"].pct_change()
    corr = {}

    def add_corr(col, change_col, rolling_col, use_pct=True):
        if col not in merged.columns:
            return
        merged[change_col] = merged[col].pct_change() if use_pct else merged[col].diff()
        valid = merged[["IndexRet", change_col]].dropna()
        if valid.shape[0] >= 5:
            corr[col] = float(valid["IndexRet"].corr(valid[change_col]))
            merged[rolling_col] = merged["IndexRet"].rolling(rolling_window).corr(merged[change_col])
        else:
            corr[col] = None

    add_corr("VIX", "VIXChg", "RollingCorr_Index_VIX", True)
    add_corr("FearGreed", "FGChg", "RollingCorr_Index_FG", False)
    add_corr("10Y Yield", "YieldChg", "RollingCorr_Index_10Y", False)
    add_corr("DXY", "DXYChg", "RollingCorr_Index_DXY", True)
    add_corr("HYG", "HYGChg", "RollingCorr_Index_HYG", True)
    add_corr("LQD", "LQDChg", "RollingCorr_Index_LQD", True)
    merged["time"] = pd.to_datetime(merged["date"])
    return merged, corr



def detect_macro_divergences(index_return, vix_return, macro_summary, corr):
    """
    Detect cross-market divergences.
    A divergence means equity price action is not confirmed by risk, dollar, or credit indicators.
    """
    divergences = []
    severity = 0

    hyg_chg = macro_summary.get("HYG", {}).get("change")
    dxy_chg = macro_summary.get("DXY", {}).get("change")
    lqd_chg = macro_summary.get("LQD", {}).get("change")
    ten_y_label = macro_summary.get("10Y Yield", {}).get("label")
    ten_y_score = macro_summary.get("10Y Yield", {}).get("score", 0)
    corr_vix = corr.get("VIX")

    if index_return is not None and index_return > 0:
        if vix_return is not None and vix_return > 0:
            divergences.append("指数上涨但 VIX 同步上升：上涨质量偏弱")
            severity += 1
        if dxy_chg is not None and dxy_chg > 1:
            divergences.append("指数上涨但 DXY 走强：美元流动性边际收紧")
            severity += 1
        if hyg_chg is not None and hyg_chg < -1:
            divergences.append("指数上涨但 HYG 走弱：信用市场不确认上涨")
            severity += 2
        if lqd_chg is not None and lqd_chg < -1.5:
            divergences.append("指数上涨但 LQD 走弱：利率/债券端压力仍在")
            severity += 1

    if ten_y_score <= -8:
        divergences.append(f"10Y Yield 处于「{ten_y_label}」：估值端存在压力")
        severity += 1

    if corr_vix is not None and not np.isnan(corr_vix) and corr_vix > -0.3:
        divergences.append("指数与 VIX 负相关明显减弱：价格-波动结构异常")
        severity += 2

    if severity >= 4:
        level = "high"
        title = "多指标背离 · 高风险警报"
        penalty = -18
    elif severity >= 2:
        level = "medium"
        title = "多指标背离 · 风险上升"
        penalty = -10
    elif severity >= 1:
        level = "low"
        title = "轻微信号背离"
        penalty = -4
    else:
        level = "none"
        title = "未发现明显多指标背离"
        penalty = 0

    return {
        "level": level,
        "title": title,
        "items": divergences,
        "severity": severity,
        "penalty": penalty,
    }



def market_signal_engine(vix_value, fg_value, corr, index_return, vix_return, macro_summary, divergence_info=None):
    score, notes, tags = 50, [], []
    if vix_value < 11: score -= 14; notes.append("VIX < 11：波动被压低，追高性价比下降。")
    elif vix_value < 14: score -= 4; notes.append("VIX 11-14：Risk-On，适合持有，但新增仓位别太激进。")
    elif vix_value < 18: score += 6; notes.append("VIX 14-18：健康波动区，适合常规定投。")
    elif vix_value < 25: score += 8; notes.append("VIX 18-25：早期压力，放慢加仓。")
    elif vix_value < 35: score += 18; notes.append("VIX 25-35：Risk-Off，长期资金可分批加仓。")
    elif vix_value < 50: score += 26; notes.append("VIX 35-50：恐慌区，机会变大但要保留现金。")
    else: score += 30; notes.append("VIX > 50：流动性踩踏区，赔率高但不 All-in。")

    if fg_value <= 15: score += 26; notes.append("Fear & Greed 0-15：投降区，反向配置价值高。")
    elif fg_value <= 30: score += 18; notes.append("Fear & Greed 15-30：深度恐惧，适合分批买入。")
    elif fg_value <= 45: score += 8; notes.append("Fear & Greed 30-45：恐惧区，适合正常定投。")
    elif fg_value <= 60: score += 2; notes.append("Fear & Greed 45-60：中性，按计划执行。")
    elif fg_value <= 75: score -= 8; notes.append("Fear & Greed 60-75：贪婪区，不宜追高。")
    elif fg_value <= 85: score -= 18; notes.append("Fear & Greed 75-85：亢奋区，减速买入或部分止盈。")
    else: score -= 28; notes.append("Fear & Greed > 85：泡沫区，回撤风险上升。")

    for key in ["10Y Yield", "DXY", "HYG", "LQD", "MOVE", "VIX3M/VIX", "Real Yield", "RSP/SPY", "Trend", "Put/Call"]:
        item = macro_summary.get(key)
        if item:
            score += item.get("score", 0)
            notes.append(f"{key}：{item.get('label')}，{item.get('note')}。")

    corr_vix = corr.get("VIX")
    if corr_vix is not None and not np.isnan(corr_vix):
        if corr_vix > -0.3: score -= 16; tags.append("价格-波动背离"); notes.append("指数与 VIX 负相关明显减弱，可能是上涨但风险同步上升。")
        elif corr_vix > -0.6: score -= 7; notes.append("指数与 VIX 负相关偏弱，需观察波动结构。")
        elif corr_vix < -0.95: score -= 4; notes.append("指数与 VIX 负相关极强，交易较拥挤。")
        else: score += 5; notes.append("指数与 VIX 保持正常强负相关，结构健康。")

    if vix_value < 14 and fg_value > 80: score -= 18; tags.append("顶部风险"); notes.append("组合信号：低 VIX + 极度贪婪，顶部风险结构。")
    if vix_value > 30 and fg_value < 25: score += 20; tags.append("抄底窗口"); notes.append("组合信号：高 VIX + 低情绪，恐慌充分释放。")
    if index_return is not None and vix_return is not None:
        if index_return > 0 and vix_return > 0: score -= 10; tags.append("假上涨警报"); notes.append("窗口内指数上涨但 VIX 同时上升，上涨质量偏弱。")
        elif index_return > 0 and vix_return < 0: score += 3; notes.append("窗口内指数上涨且 VIX 下降，上涨质量较健康。")

    hyg_chg = macro_summary.get("HYG", {}).get("change")
    dxy_chg = macro_summary.get("DXY", {}).get("change")
    if index_return is not None and index_return > 0:
        if hyg_chg is not None and hyg_chg < -1: score -= 12; tags.append("信用背离"); notes.append("指数上涨但 HYG 走弱，信用市场不确认上涨。")
        if dxy_chg is not None and dxy_chg > 1: score -= 8; tags.append("美元背离"); notes.append("指数上涨但 DXY 走强，全球流动性边际收紧。")

    if divergence_info and divergence_info.get("penalty", 0) < 0:
        score += divergence_info.get("penalty", 0)
        if divergence_info.get("level") in ("medium", "high"):
            tags.append("多指标背离")
            notes.append(divergence_info.get("title", "多指标背离风险上升") + "。")

    score = int(max(0, min(100, score)))
    if score >= 82: signal, level, action, position = "强机会区", "opportunity", "强力分批加仓 · 避免一次性 All-in", "75% — 90%"
    elif score >= 68: signal, level, action, position = "偏进攻", "constructive", "加大定投 · 分批买入 · 保留现金", "60% — 75%"
    elif score >= 50: signal, level, action, position = "中性健康", "normal", "常规定投 · 保持节奏 · 不追高", "45% — 60%"
    elif score >= 35: signal, level, action, position = "偏防守", "caution", "减速买入 · 控制仓位 · 等回调", "30% — 45%"
    else: signal, level, action, position = "高风险", "risk", "暂停追高 · 部分止盈 · 提高现金", "15% — 30%"
    return score, signal, level, action, position, (tags or [signal]), notes



def build_macro_risk_summary(macro_summary):
    levels = {}
    for name, item in macro_summary.items():
        levels[name] = macro_heat_level(name, item)

    red_items = [name for name, level in levels.items() if level == "red"]
    yellow_items = [name for name, level in levels.items() if level == "yellow"]

    if len(red_items) >= 2 or (len(red_items) >= 1 and len(yellow_items) >= 2):
        level = "red"
        title = "宏观风险偏高"
        msg = "多个宏观/信用指标同时承压，建议降低追高动作，提高现金与分批节奏。"
    elif len(red_items) >= 1 or len(yellow_items) >= 2:
        level = "yellow"
        title = "宏观环境开始走弱"
        msg = "部分利率、美元或信用指标出现压力，建议保持定投但控制新增仓位。"
    else:
        level = "green"
        title = "宏观环境健康"
        msg = "利率、美元与信用指标整体未出现明显系统性压力。"

    detail = []
    for name in ["10Y Yield", "DXY", "HYG", "LQD"]:
        if name in macro_summary:
            item = macro_summary[name]
            detail.append(f"{MACRO_DISPLAY_NAMES.get(name, name)}：{item.get('label')}")

    return {
        "level": level,
        "title": title,
        "msg": msg,
        "detail": detail,
        "levels": levels,
    }




@st.cache_data(ttl=3600, show_spinner=False)
def fetch_fred_series(series_id: str, lookback_days: int = 900) -> pd.DataFrame:
    try:
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
        r = requests.get(url, timeout=12)
        r.raise_for_status()
        from io import StringIO
        df = pd.read_csv(StringIO(r.text))
        if df.empty or "observation_date" not in df.columns or series_id not in df.columns:
            return pd.DataFrame()
        df = df.rename(columns={"observation_date": "time", series_id: "Close"})
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["Close"] = pd.to_numeric(df["Close"].replace(".", np.nan), errors="coerce")
        df = df.dropna(subset=["time", "Close"]).sort_values("time")
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=lookback_days)
        df = df[df["time"] >= cutoff]
        df["Open"] = df["High"] = df["Low"] = df["Close"]
        df["Volume"] = 0
        return df[["time", "Open", "High", "Low", "Close", "Volume"]].copy()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_put_call_ratio():
    """
    SPY options Put/Call proxy via yfinance.
    Not official CBOE total PCR.
    """
    try:
        spy = yf.Ticker("SPY")
        expiries = list(spy.options or [])
        if not expiries:
            return None, "No SPY option expiries from yfinance"

        tried = []
        for expiry in expiries[:8]:
            try:
                chain = spy.option_chain(expiry)
                puts, calls = chain.puts, chain.calls
                if puts is None or calls is None or puts.empty or calls.empty:
                    tried.append(f"{expiry}: empty")
                    continue
                put_vol = pd.to_numeric(puts.get("volume"), errors="coerce").fillna(0).sum()
                call_vol = pd.to_numeric(calls.get("volume"), errors="coerce").fillna(0).sum()
                tried.append(f"{expiry}: put={int(put_vol)}, call={int(call_vol)}")
                if put_vol > 0 and call_vol > 0:
                    return float(put_vol / call_vol), f"SPY options proxy · expiry {expiry} · put {int(put_vol):,} / call {int(call_vol):,}"
            except Exception as inner_e:
                tried.append(f"{expiry}: {inner_e}")
        return None, "No non-zero SPY option volume found · " + " | ".join(tried[:3])
    except Exception as e:
        return None, f"SPY options proxy failed: {e}"


def latest_close(df):
    if isinstance(df, pd.DataFrame) and not df.empty and "Close" in df.columns:
        return safe_float(df["Close"].iloc[-1], None)
    return None


def classify_move(value):
    if value is None:
        return "N/A", "债券波动率数据不可用", "#64748b", 0
    if value > 150:
        return "债市高压", "MOVE > 150，债市波动极高，风险资产承压", "#ef4444", -16
    if value > 120:
        return "债市紧张", "MOVE 120-150，系统性波动压力偏高", "#eab308", -8
    if value > 100:
        return "偏高", "MOVE 100-120，债市波动略高", "#eab308", -4
    return "稳定", "债市波动处于相对稳定区", "#10b981", 5


def classify_vix_term(vix3m, vix):
    if vix3m is None or vix is None or vix <= 0:
        return None, "N/A", "期限结构数据不可用", "#64748b", 0
    ratio = vix3m / vix
    if ratio < 0.95:
        return ratio, "倒挂", "近端恐慌高于远端，风险临近", "#ef4444", -14
    if ratio < 1.05:
        return ratio, "偏紧", "期限结构接近平坦，市场压力上升", "#eab308", -7
    return ratio, "健康", "远期波动高于近端，期限结构正常", "#10b981", 5


def classify_rsp_spy(ratio_change):
    if ratio_change is None:
        return "N/A", "市场宽度数据不可用", "#64748b", 0
    if ratio_change < -2:
        return "宽度恶化", "RSP/SPY 明显下行，指数可能由少数权重股拉动", "#ef4444", -12
    if ratio_change < -0.5:
        return "宽度偏弱", "等权指数相对走弱，需警惕假牛", "#eab308", -6
    if ratio_change > 1:
        return "宽度改善", "等权指数相对走强，市场参与度改善", "#10b981", 8
    return "宽度稳定", "市场宽度未明显恶化", "#10b981", 3


def classify_trend(index_df_long):
    if index_df_long is None or index_df_long.empty or len(index_df_long) < 210:
        return None, "N/A", "趋势样本不足", "#64748b", 0
    x = index_df_long.copy()
    x["MA200"] = x["Close"].rolling(200).mean()
    last = safe_float(x["Close"].iloc[-1], None)
    ma200 = safe_float(x["MA200"].iloc[-1], None)
    if last is None or ma200 is None or ma200 == 0:
        return None, "N/A", "趋势数据不可用", "#64748b", 0
    distance = (last / ma200 - 1) * 100
    if distance < -5:
        return distance, "熊市/弱趋势", "价格低于200MA较多，趋势偏弱", "#ef4444", -16
    if distance < 0:
        return distance, "趋势承压", "价格低于200MA，适合更保守", "#eab308", -8
    if distance > 12:
        return distance, "趋势过热", "价格显著高于200MA，需防追高", "#eab308", -4
    return distance, "牛市趋势", "价格位于200MA上方，趋势健康", "#10b981", 10


def classify_real_yield(value):
    if value is None:
        return "N/A", "真实利率数据不可用", "#64748b", 0
    if value > 2.5:
        return "高压", "真实利率偏高，估值压力明显", "#ef4444", -16
    if value > 1.8:
        return "偏高", "真实利率较高，压制估值扩张", "#eab308", -8
    if value < 0.8:
        return "宽松", "真实利率偏低，利好风险资产估值", "#10b981", 8
    return "中性", "真实利率处于中性区", "#3b82f6", 2


def classify_put_call(value):
    if value is None:
        return "N/A", "SPY期权 Put/Call Proxy 暂无有效成交量，不参与评分", "#64748b", 0
    if value > 1.30:
        return "明显恐慌", "看跌成交量显著高于看涨，反向机会增加", "#10b981", 5
    if value > 1.05:
        return "偏恐慌", "保护性需求偏高", "#10b981", 3
    if value < 0.55:
        return "明显贪婪", "看涨成交过热，追涨风险上升", "#ef4444", -5
    if value < 0.75:
        return "偏贪婪", "风险偏好偏强", "#eab308", -3
    return "中性", "SPY Put/Call Proxy 处于中性区", "#3b82f6", 1


def build_pro_summary(pro_summary):
    levels = {k: macro_heat_level(k, v) for k, v in pro_summary.items()}
    red = [k for k, v in levels.items() if v == "red"]
    yellow = [k for k, v in levels.items() if v == "yellow"]
    if len(red) >= 2 or (len(red) >= 1 and len(yellow) >= 3):
        level, title, msg = "red", "Pro Risk · 高风险复合信号", "趋势、流动性、波动或信用多个维度同时承压，建议显著降低追高动作。"
    elif len(red) >= 1 or len(yellow) >= 3:
        level, title, msg = "yellow", "Pro Risk · 风险升温", "部分专业指标开始走弱，建议定投降速、提高现金缓冲。"
    else:
        level, title, msg = "green", "Pro Risk · 结构健康", "趋势、流动性、信用与波动结构整体未出现明显系统性压力。"
    detail = [f"{MACRO_DISPLAY_NAMES.get(k, k)}：{v.get('label')}" for k, v in pro_summary.items()]
    return {"level": level, "title": title, "msg": msg, "detail": detail, "levels": levels}


def build_semi_quant_regime(score, macro_risk_summary, pro_risk_summary, divergence_info, pro_summary):
    danger_count = 0
    warn_count = 0
    for obj in [macro_risk_summary, pro_risk_summary]:
        if obj.get("level") == "red":
            danger_count += 1
        elif obj.get("level") == "yellow":
            warn_count += 1

    if divergence_info.get("level") == "high":
        danger_count += 1
    elif divergence_info.get("level") == "medium":
        warn_count += 1

    if score >= 75 and danger_count == 0:
        regime, cn, action, color = "Risk-On Accumulation", "风险偏好健康 · 可进攻", "维持或小幅提高VOO/SPY仓位，分批执行，不追单日大阳线。", "green"
    elif score >= 55 and danger_count == 0:
        regime, cn, action, color = "Neutral Uptrend", "中性偏多 · 定投优先", "维持常规定投；若出现回调，可分批补仓。", "green"
    elif score >= 40 and danger_count <= 1:
        regime, cn, action, color = "Caution / Late Risk-On", "谨慎区 · 降低追高", "降低新增买入力度，等待VIX/信用/美元信号改善。", "yellow"
    elif score >= 25:
        regime, cn, action, color = "Risk-Off Defense", "防守区 · 控制仓位", "减少追高，保留现金，优先等待恐慌释放后的分批机会。", "red"
    else:
        regime, cn, action, color = "Stress / De-risk", "压力区 · 去风险", "暂停追高，控制权益暴露；仅在极端恐慌且信用稳定时分批低吸。", "red"

    detail = [
        f"Trend趋势：{pro_summary.get('Trend', {}).get('label', 'N/A')}",
        f"Real Yield真实利率：{pro_summary.get('Real Yield', {}).get('label', 'N/A')}",
        f"MOVE债券波动：{pro_summary.get('MOVE', {}).get('label', 'N/A')}",
        f"VIX期限结构：{pro_summary.get('VIX3M/VIX', {}).get('label', 'N/A')}",
        f"市场宽度RSP/SPY：{pro_summary.get('RSP/SPY', {}).get('label', 'N/A')}",
        f"SPY Put/Call Proxy：{pro_summary.get('Put/Call', {}).get('label', 'N/A')}",
    ]
    return {"regime": regime, "cn": cn, "action": action, "color": color, "detail": detail}


def combined_decision_level(macro_risk_summary, pro_risk_summary, semi_quant_regime, divergence_info):
    levels = [macro_risk_summary.get("level", "green"), pro_risk_summary.get("level", "green"), semi_quant_regime.get("color", "green")]
    if divergence_info.get("level") == "high":
        levels.append("red")
    elif divergence_info.get("level") == "medium":
        levels.append("yellow")
    if "red" in levels:
        return "red"
    if "yellow" in levels:
        return "yellow"
    return "green"



def render_meter_card(kind, value, label, strategy, color, pointer_pct, source=""):
    if kind == "vix":
        title, desc, labels, seg_colors, accent = "VIX · S&P 500", "波动率指数", ["<11", "11-14", "14-18", "18-25", "25-35", "35-50", ">50"], ["#d1fae5", "#10b981", "#86efac", "#fde68a", "#fdba74", "#fca5a5", "#f8b4c2"], "#10b981"
    else:
        title, desc, labels, seg_colors, accent = "FEAR & GREED · CNN", "恐惧与贪婪指数", ["0-15", "15-30", "30-45", "45-60", "60-75", "75-85", "85-100"], ["#f8b4c2", "#fdba74", "#fde68a", "#bfd3ff", "#eab308", "#fb923c", "#f472b6"], "#eab308"
    seg_html = "".join([f'<div class="segment" style="background:{c};"></div>' for c in seg_colors])
    label_html = "".join([f"<div>{x}</div>" for x in labels])
    st.markdown(f"""
<div class="metric-card">
  <div style="display:grid;grid-template-columns:1.15fr .9fr 1fr;gap:8px;align-items:center;">
    <div><div style="width:42px;height:5px;background:{accent};border-radius:999px;margin-bottom:8px;"></div><h3>{title}</h3><div class="desc">{desc}</div>{f'<div style="margin-top:7px;"><span class="source-chip">{source}</span></div>' if source else ''}</div>
    <div class="big-number" style="color:{accent};">{value:.0f}</div>
    <div style="text-align:right;"><span class="badge" style="color:{color};">{label}</span></div>
  </div>
  <div class="segment-wrap"><div class="segment-bar">{seg_html}<div class="pointer" style="left:{pointer_pct:.2f}%;border-top:14px solid {accent};"></div></div><div class="segment-labels">{label_html}</div></div>
</div>""", unsafe_allow_html=True)


def render_playbook(title, accent_color, rows, current_idx, yellow=False):
    row_html = ""
    for i, (rng, emotion, strategy) in enumerate(rows):
        cls = "now-yellow" if yellow and i == current_idx else ("now-green" if i == current_idx else "")
        now_bg = "#eab308" if yellow else "#10b981"
        now = f'<span class="pb-now" style="background:{now_bg};">NOW</span>' if i == current_idx else ""
        row_html += f'<div class="pb-row {cls}"><div class="pb-range" style="color:{accent_color};">{rng}</div><div class="pb-emotion">{emotion} {now}</div><div class="pb-strategy">{strategy}</div><div class="pb-now-wrap">{now}</div></div>'
    st.markdown(f'<div class="responsive-playbook"><div class="pb-title"><span style="display:inline-block;width:34px;height:5px;background:{accent_color};border-radius:999px;margin-right:10px;vertical-align:middle;"></span>{title}</div><div class="pb-card"><div class="pb-header"><div>区间</div><div>情绪</div><div>策略</div><div></div></div>{row_html}</div></div>', unsafe_allow_html=True)


def macro_heat_level(name, item):
    label = item.get("label", "")
    score = item.get("score", 0)
    change = item.get("change")

    if name == "10Y Yield":
        if score <= -12:
            return "red"
        if score < 0:
            return "yellow"
        return "green"

    if name == "DXY":
        if score <= -7:
            return "red"
        if score < 0:
            return "yellow"
        return "green"

    if name == "HYG":
        if score <= -10:
            return "red"
        if score < 0:
            return "yellow"
        return "green"

    if name == "LQD":
        if score <= -6:
            return "red"
        if score < 0:
            return "yellow"
        return "green"

    return "green"


def heat_badge_text(level):
    if level == "red":
        return "高风险"
    if level == "yellow":
        return "警惕"
    return "健康"


def macro_heat_level(name, item):
    score = item.get("score", 0)
    if score <= -10:
        return "red"
    if score < 0:
        return "yellow"
    return "green"


def heat_badge_text(level):
    if level == "red":
        return "高风险"
    if level == "yellow":
        return "警惕"
    return "健康"


def render_macro_card(title, value_text, label, note, color, change_text, heat_level="green"):
    st.markdown(
        f"""
<div class="macro-card heat-{heat_level}">
  <div class="macro-title">{title}</div>
  <div class="macro-value">{value_text}</div>
  <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
    <div class="macro-label" style="color:{color};background:{color}18;border:1px solid {color}55;">{label}</div>
    <div class="macro-label" style="color:{color};background:{color}10;border:1px solid {color}33;">{heat_badge_text(heat_level)}</div>
  </div>
  <div class="macro-note">{note}</div>
  <div class="macro-note">窗口变化：{change_text}</div>
</div>
""",
        unsafe_allow_html=True,
    )


def build_price_chart(index_df, vix_df, index_name):
    fig = go.Figure()
    if not index_df.empty:
        fig.add_trace(go.Scatter(x=index_df["time"], y=index_df["Close"], mode="lines", name=index_name, line=dict(width=3)))
    if not vix_df.empty:
        fig.add_trace(go.Scatter(x=vix_df["time"], y=vix_df["Close"], mode="lines", name="VIX", yaxis="y2", line=dict(width=2, dash="dot")))
    fig.update_layout(height=320, margin=dict(l=10, r=10, t=24, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(title=index_name, gridcolor="#eef2f7"), yaxis2=dict(title="VIX", overlaying="y", side="right", showgrid=False), xaxis=dict(showgrid=False), hovermode="x unified")
    return fig


def build_macro_trend_chart(macro_data):
    fig = go.Figure()
    for name, df in macro_data.items():
        if df is None or df.empty:
            continue
        y = df["Close"].astype(float)
        norm = y / y.iloc[0] * 100 if len(y) > 1 and y.iloc[0] != 0 else y
        fig.add_trace(go.Scatter(x=df["time"], y=norm, mode="lines", name=name, line=dict(width=2)))
    fig.update_layout(height=310, margin=dict(l=10, r=10, t=24, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(title="Normalized to 100", gridcolor="#eef2f7"), xaxis=dict(showgrid=False), hovermode="x unified")
    return fig


def build_corr_chart(corr_df):
    fig = go.Figure()
    if corr_df is None or corr_df.empty:
        return fig
    for col, name in [("RollingCorr_Index_VIX", "Index vs VIX"), ("RollingCorr_Index_FG", "Index vs Fear&Greed"), ("RollingCorr_Index_10Y", "Index vs 10Y"), ("RollingCorr_Index_DXY", "Index vs DXY"), ("RollingCorr_Index_HYG", "Index vs HYG"), ("RollingCorr_Index_LQD", "Index vs LQD")]:
        if col in corr_df.columns:
            fig.add_trace(go.Scatter(x=corr_df["time"], y=corr_df[col], mode="lines", name=name, line=dict(width=2)))
    fig.add_hline(y=0, line_dash="dash", line_width=1)
    fig.update_layout(height=300, margin=dict(l=10, r=10, t=24, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis=dict(range=[-1, 1], title="Correlation", gridcolor="#eef2f7"), xaxis=dict(showgrid=False), hovermode="x unified")
    return fig


with st.sidebar:
    st.markdown("### Dashboard Settings")
    index_label = st.selectbox("Market index", list(INDEX_MAP.keys()), index=0)
    period = st.selectbox("History window", PERIOD_OPTIONS, index=1)
    if period == "3d":
        st.success("推荐决策周期：3d · 用于日常仓位调整")
    elif period == "实时盘中":
        st.warning("实时盘中仅用于观察，不建议直接改变策略")
    elif period in ["5d", "1mo"]:
        st.info("辅助确认周期：用于风控/趋势确认，不作为主决策")
    else:
        st.caption("当前周期偏观察用途，主决策建议回到 3d")

    st.markdown("""
**周期使用建议**
- **3d**：主决策周期，日常加仓/控仓
- **5d / 1mo**：风控确认，看短中期是否转弱
- **实时盘中**：只看盘中异动，不直接改策略
""")
    interval = st.selectbox("Interval", INTERVAL_OPTIONS, index=0)
    rolling_window = st.slider("Rolling correlation window", 5, 120, 30, 5)
    refresh = st.slider("Auto refresh seconds", 0, 600, 120, 15)
    manual_fg = st.number_input("Manual Fear & Greed fallback", 0, 100, 50, 1)
    collect_fg_now = st.button("立即写入 Fear & Greed 当前值到历史CSV", use_container_width=True)
    st.caption("选择「实时盘中」可分钟级查看盘中最新值；相关性/宏观趋势仍使用日线。FG历史来自 repo 中的 fg_history.csv，本地 collector 每晚更新并 push。")

if refresh:
    st_autorefresh(interval=refresh * 1000, key="market-refresh")

symbol = INDEX_MAP[index_label]

# Display mode:
# - "实时盘中": use intraday 1m data for top cards and the main price chart.
# - Analytics mode: always use daily bars for correlation, macro trends, and signal structure.
is_live_mode = period == "实时盘中"
display_period = "1d" if is_live_mode else period
display_interval = "1m" if is_live_mode else interval

analytics_period = "3d" if is_live_mode else period
analytics_interval = "1d"

if period == "3d":
    decision_mode_label = "主决策模式"
    decision_mode_color = "green"
    decision_mode_note = "用于日常仓位调整，系统默认推荐。"
elif period == "实时盘中":
    decision_mode_label = "实时观察模式"
    decision_mode_color = "yellow"
    decision_mode_note = "分钟级看盘中异动；相关性和趋势仍使用日线，不建议直接改变策略。"
elif period in ["5d", "1mo"]:
    decision_mode_label = "风控确认模式"
    decision_mode_color = "yellow"
    decision_mode_note = "用于确认短期/中期风险是否转弱，辅助主决策。"
else:
    decision_mode_label = "趋势观察模式"
    decision_mode_color = "gray"
    decision_mode_note = "用于观察更长周期结构，不作为日常加仓/减仓主信号。"

index_df_display = fetch_yahoo(symbol, display_period, display_interval)
vix_df_display = fetch_yahoo("^VIX", display_period, display_interval)
macro_data_display = {name: fetch_yahoo(sym, display_period, display_interval) for name, sym in MACRO_SYMBOLS.items()}
pro_data_display = {name: fetch_yahoo(sym, display_period, display_interval) for name, sym in PRO_SYMBOLS.items()}

index_df = fetch_yahoo(symbol, analytics_period, analytics_interval)
vix_df = fetch_yahoo("^VIX", analytics_period, analytics_interval)
macro_data = {name: fetch_yahoo(sym, analytics_period, analytics_interval) for name, sym in MACRO_SYMBOLS.items()}
pro_data = {name: fetch_yahoo(sym, analytics_period, analytics_interval) for name, sym in PRO_SYMBOLS.items()}
index_df_long = fetch_yahoo(symbol, "1y", "1d")
real_yield_df = fetch_fred_series("DFII10", lookback_days=900)

vix_value = safe_float(vix_df_display["Close"].iloc[-1], 0) if not vix_df_display.empty else (safe_float(vix_df["Close"].iloc[-1], 0) if not vix_df.empty else 0)
fg_value, fg_rating, fg_source, _fg_live = fetch_fear_greed_with_fallback(float(manual_fg))
fg_history_table = build_fg_history_for_app(float(fg_value), str(fg_rating), str(fg_source))

if collect_fg_now:
    saved_ok = save_fg_history_file(fg_history_table)
    if saved_ok:
        st.sidebar.success(f"已采集并写入 fg_history.csv：{fg_value:.0f} · {fg_rating}")
    else:
        st.sidebar.error("采集成功，但写入 fg_history.csv 失败")

fg_hist = fg_history_for_correlation(fg_history_table)

index_return, vix_return = pct_change_text(index_df_display), pct_change_text(vix_df_display)
macro_changes = {name: pct_change_text(df) for name, df in macro_data_display.items()}

corr_df, corr = compute_correlations(index_df, vix_df, fg_hist, macro_data, rolling_window)

macro_summary = {}
for name, df_daily in macro_data.items():
    df_live = macro_data_display.get(name, pd.DataFrame())
    df_for_latest = df_live if df_live is not None and not df_live.empty else df_daily
    if df_for_latest.empty:
        continue
    last = safe_float(df_for_latest["Close"].iloc[-1], 0)
    chg = macro_changes.get(name)
    if name == "10Y Yield":
        y, label, note, color, score = classify_10y(last)
        macro_summary[name] = {"value": y, "label": label, "note": note, "color": color, "score": score, "change": chg, "display": f"{y:.2f}%"}
    elif name == "DXY":
        label, note, color, score = classify_dxy(chg)
        macro_summary[name] = {"value": last, "label": label, "note": note, "color": color, "score": score, "change": chg, "display": f"{last:.2f}"}
    elif name == "HYG":
        label, note, color, score = classify_hyg(chg)
        macro_summary[name] = {"value": last, "label": label, "note": note, "color": color, "score": score, "change": chg, "display": f"{last:.2f}"}
    elif name == "LQD":
        label, note, color, score = classify_lqd(chg)
        macro_summary[name] = {"value": last, "label": label, "note": note, "color": color, "score": score, "change": chg, "display": f"{last:.2f}"}

vix_label, vix_strategy, vix_color, vix_idx = vix_level(float(vix_value))
fg_label, fg_strategy, fg_color, fg_idx = fear_greed_level(float(fg_value))
pro_summary = {}

move_val = latest_close(pro_data_display.get("MOVE", pd.DataFrame())) or latest_close(pro_data.get("MOVE", pd.DataFrame()))
move_label, move_note, move_color, move_score = classify_move(move_val)
pro_summary["MOVE"] = {"value": move_val, "display": f"{move_val:.1f}" if move_val is not None else "N/A", "label": move_label, "note": move_note, "color": move_color, "score": move_score, "change": pct_change_text(pro_data_display.get("MOVE", pd.DataFrame()))}

vix3m_val = latest_close(pro_data_display.get("VIX3M", pd.DataFrame())) or latest_close(pro_data.get("VIX3M", pd.DataFrame()))
vix_term_ratio, term_label, term_note, term_color, term_score = classify_vix_term(vix3m_val, vix_value)
pro_summary["VIX3M/VIX"] = {"value": vix_term_ratio, "display": f"{vix_term_ratio:.2f}" if vix_term_ratio is not None else "N/A", "label": term_label, "note": term_note, "color": term_color, "score": term_score, "change": None}

rsp_df = pro_data_display.get("RSP", pd.DataFrame())
spy_df = pro_data_display.get("SPY", pd.DataFrame())
rsp_spy_val, rsp_spy_change = None, None
try:
    if not rsp_df.empty and not spy_df.empty:
        merged_ratio = pd.merge(
            rsp_df[["time", "Close"]].rename(columns={"Close": "RSP"}),
            spy_df[["time", "Close"]].rename(columns={"Close": "SPY"}),
            on="time",
            how="inner",
        )
        if len(merged_ratio) >= 2:
            ratio = merged_ratio["RSP"] / merged_ratio["SPY"]
            rsp_spy_val = ratio.iloc[-1]
            rsp_spy_change = (ratio.iloc[-1] / ratio.iloc[0] - 1) * 100
except Exception:
    pass
breadth_label, breadth_note, breadth_color, breadth_score = classify_rsp_spy(rsp_spy_change)
pro_summary["RSP/SPY"] = {"value": rsp_spy_val, "display": f"{rsp_spy_val:.3f}" if rsp_spy_val is not None else "N/A", "label": breadth_label, "note": breadth_note, "color": breadth_color, "score": breadth_score, "change": rsp_spy_change}

trend_distance, trend_label, trend_note, trend_color, trend_score = classify_trend(index_df_long)
pro_summary["Trend"] = {"value": trend_distance, "display": f"{trend_distance:+.1f}% vs 200MA" if trend_distance is not None else "N/A", "label": trend_label, "note": trend_note, "color": trend_color, "score": trend_score, "change": None}

real_yield_val = latest_close(real_yield_df)
real_yield_label, real_yield_note, real_yield_color, real_yield_score = classify_real_yield(real_yield_val)
pro_summary["Real Yield"] = {"value": real_yield_val, "display": f"{real_yield_val:.2f}%" if real_yield_val is not None else "N/A", "label": real_yield_label, "note": real_yield_note, "color": real_yield_color, "score": real_yield_score, "change": pct_change_text(real_yield_df)}

put_call_val, put_call_source = fetch_put_call_ratio()
pc_label, pc_note, pc_color, pc_score = classify_put_call(put_call_val)
pro_summary["Put/Call"] = {"value": put_call_val, "display": f"{put_call_val:.2f}" if put_call_val is not None else "N/A", "label": pc_label, "note": pc_note + f" · {put_call_source}", "color": pc_color, "score": pc_score, "change": None}

divergence_info = detect_macro_divergences(index_return, vix_return, macro_summary, corr)
macro_risk_summary = build_macro_risk_summary(macro_summary)
pro_risk_summary = build_pro_summary(pro_summary)

extended_summary = dict(macro_summary)
extended_summary.update({k: {"label": v.get("label"), "note": v.get("note"), "score": v.get("score", 0), "change": v.get("change")} for k, v in pro_summary.items()})
score, signal, signal_level, strategy, position_suggestion, signal_tags, signal_notes = market_signal_engine(float(vix_value), float(fg_value), corr, index_return, vix_return, extended_summary, divergence_info)
semi_quant_regime = build_semi_quant_regime(score, macro_risk_summary, pro_risk_summary, divergence_info, pro_summary)
combined_level = combined_decision_level(macro_risk_summary, pro_risk_summary, semi_quant_regime, divergence_info)

today = datetime.now().strftime("%Y · %m · %d / %a")
st.markdown(f'<div class="date-pill">{today}</div>', unsafe_allow_html=True)
st.markdown('<div class="pill">◆ VOO / SPY MACRO RISK DASHBOARD</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">大盘 ETF 投资观测系统</div>', unsafe_allow_html=True)
mode_text = "实时盘中 · 分钟级展示 / 日线计算" if is_live_mode else f"{period} · 日线计算"
st.markdown(f'<div class="sub-title"><span class="green-accent"></span><b style="color:#059669;">Price · VIX · Fear & Greed · Rates · USD · Credit</b>　价格 / 波动 / 情绪 / 利率 / 美元 / 信用　<span class="source-chip">{mode_text}</span></div>', unsafe_allow_html=True)

st.markdown(
    f"""
<div class="mode-chip {decision_mode_color}">
  <div>
    <div class="mode-main">当前模式：{decision_mode_label} · Window = {period}</div>
    <div class="mode-sub">{decision_mode_note}</div>
  </div>
  <div class="mode-sub">推荐主决策：3d + 1d interval</div>
</div>
""",
    unsafe_allow_html=True,
)

last_index = f"{index_df_display['Close'].iloc[-1]:,.2f}" if not index_df_display.empty else (f"{index_df['Close'].iloc[-1]:,.2f}" if not index_df.empty else "N/A")
idx_ret = f"{index_return:+.2f}% window" if index_return is not None else "N/A"
vix_ret = f"{vix_return:+.2f}% window" if vix_return is not None else "N/A"
note_html = "<br>".join([f"• {x}" for x in signal_notes[:5]])

card1, card2, card3 = st.columns([1.05, 1.05, 0.95], gap="medium")
with card1:
    render_meter_card("vix", float(vix_value), vix_label, vix_strategy, vix_color, vix_pointer_pct(float(vix_value)), "Yahoo Finance / CBOE VIX")
with card2:
    render_meter_card("fg", float(fg_value), fg_label, fg_strategy, fg_color, fg_pointer_pct(float(fg_value)), fg_source)
with card3:
    st.markdown(f"""
<div class="note-panel {annotation_class(signal_level)}" style="min-height:248px;">
  <div class="compact-summary-title">SIGNAL NOTES · 信号注释</div>
  <b>{signal}</b><br>{note_html}
</div>""", unsafe_allow_html=True)

decision_period_warning = "" if period == "3d" else "当前非主决策周期，建议只作为辅助观察。"

st.markdown(f"""
<div class="strategy-grid">
  <div class="strategy-panel">
    <div class="title">◆ TODAY'S STRATEGY · 今日策略</div>
    <div class="main">{strategy}</div>
    <div class="compact-summary-note" style="margin-top:10px;"><b>决策周期：</b>{period} · {decision_mode_label}</div><div class="compact-summary-note"><b>半量化状态：</b>{semi_quant_regime.get("cn")} ({semi_quant_regime.get("regime")})</div>
    <div class="compact-summary-note"><b>核心风险：</b>{pro_risk_summary.get("title")} · {divergence_info.get("title")}</div>
    <div class="compact-summary-note"><b>信号标签：</b>{" · ".join(signal_tags)}</div>
  </div>
  <div class="signal-card">
    <div class="compact-summary-title">MARKET SIGNAL · 市场信号</div>
    <div style="display:flex;align-items:end;gap:12px;margin-bottom:12px;"><div class="signal-score">{score}</div><div><div class="signal-label">{signal}</div><div class="compact-summary-note">0-100 越高越适合增量买入</div></div></div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:8px;">
      <div><div class="compact-summary-note">{index_label}</div><div class="compact-summary-value">{last_index}</div><div class="compact-summary-note">{period} change: {idx_ret}</div></div>
      <div><div class="compact-summary-note">VIX / F&G</div><div class="compact-summary-value">{vix_value:.1f} / {fg_value:.0f}</div><div class="compact-summary-note">VIX {period}: {vix_ret}</div><div class="compact-summary-note">FG历史：{len(fg_history_table)} 天</div></div>
    </div>
  </div>
  <div class="position-panel">
    <div class="k">POSITION SIZING · 仓位建议</div>
    <div class="v">{position_suggestion}</div>
    <div class="compact-summary-note"><b>执行原则：</b>{semi_quant_regime.get("action")}</div>
    <div class="compact-summary-note" style="margin-top:8px;"><b>宏观：</b>{macro_risk_summary.get("title")} · <b>专业：</b>{pro_risk_summary.get("title")}</div>
    <div class="compact-summary-note">指权益类资产目标仓位，不是单只股票仓位。</div><div class="compact-summary-note"><b>{decision_period_warning}</b></div>
  </div>
</div>
""", unsafe_allow_html=True)

if divergence_info.get("items"):
    div_items = "<br>".join([f"• {x}" for x in divergence_info.get("items", [])[:5]])
    div_color = "#ef4444" if divergence_info.get("level") == "high" else ("#eab308" if divergence_info.get("level") == "medium" else "#3b82f6")
    st.markdown(
        f"""
<div class="note-panel {'danger' if divergence_info.get('level') == 'high' else 'warning' if divergence_info.get('level') == 'medium' else ''}" style="margin-bottom:14px;">
  <b>背离检测 · {divergence_info.get("title")}</b><br>
  {div_items}
</div>
""",
        unsafe_allow_html=True,
    )


st.markdown("### Macro & Credit · 宏观信用指标")
cols = st.columns(4, gap="medium")
for i, name in enumerate(["10Y Yield", "DXY", "HYG", "LQD"]):
    item = macro_summary.get(name, {})
    with cols[i]:
        render_macro_card(
            MACRO_DISPLAY_NAMES.get(name, name),
            item.get("display", "N/A"),
            item.get("label", "N/A"),
            item.get("note", "No data"),
            item.get("color", "#64748b"),
            f"{item.get('change'):+.2f}%" if item.get("change") is not None else "N/A",
            macro_risk_summary.get("levels", {}).get(name, "green"),
        )


st.markdown('<div class="pro-title">Professional Signals · 专业增强指标</div>', unsafe_allow_html=True)
pro_cols = st.columns(3, gap="medium")
for idx, name in enumerate(["Real Yield", "MOVE", "VIX3M/VIX", "RSP/SPY", "Trend", "Put/Call"]):
    item = pro_summary.get(name, {})
    with pro_cols[idx % 3]:
        st.markdown('<div class="pro-card-spacer">', unsafe_allow_html=True)
        render_macro_card(
            MACRO_DISPLAY_NAMES.get(name, name),
            item.get("display", "N/A"),
            item.get("label", "N/A"),
            item.get("note", "No data"),
            item.get("color", "#64748b"),
            f"{item.get('change'):+.2f}%" if item.get("change") is not None else "N/A",
            pro_risk_summary.get("levels", {}).get(name, macro_heat_level(name, item)),
        )
        st.markdown('</div>', unsafe_allow_html=True)


st.markdown("### 策略区间")
pb1, pb2 = st.columns(2, gap="medium")
with pb1:
    render_playbook("VIX PLAYBOOK", "#10b981", VIX_ROWS, vix_idx, yellow=False)
with pb2:
    render_playbook("FEAR & GREED PLAYBOOK", "#eab308", FG_ROWS, fg_idx, yellow=True)

st.markdown("### 市场走势与波动率")
m1, m2, m3, m4 = st.columns(4)
m1.metric(index_label, last_index, f"{period} change: {idx_ret}")
m2.metric("VIX", f"{vix_value:.2f}", f"{period} change: {vix_ret}")
m3.metric("CNN Fear & Greed", f"{fg_value:.0f}", fg_rating)
m4.metric("Auto refresh", f"{refresh}s" if refresh else "Off")
st.caption(f"顶部百分比为当前展示窗口（{period}）内累计变化；实时盘中模式使用分钟级数据展示最新值，但相关性与宏观趋势仍使用日线历史数据计算。")
st.plotly_chart(build_price_chart(index_df_display if not index_df_display.empty else index_df, vix_df_display if not vix_df_display.empty else vix_df, index_label), use_container_width=True)

st.markdown("### Macro Trends · 宏观趋势")
st.plotly_chart(build_macro_trend_chart(macro_data), use_container_width=True)

st.markdown("### Pro Trends · 专业指标趋势")
pro_trend_data = {
    "MOVE": pro_data.get("MOVE", pd.DataFrame()),
    "VIX3M": pro_data.get("VIX3M", pd.DataFrame()),
    "RSP": pro_data.get("RSP", pd.DataFrame()),
    "SPY": pro_data.get("SPY", pd.DataFrame()),
    "Real Yield": real_yield_df,
}
st.plotly_chart(build_macro_trend_chart(pro_trend_data), use_container_width=True)
st.caption("宏观趋势图将每个指标窗口起点标准化为 100，方便看方向，不代表绝对数值大小。")

st.markdown("### 相关性分析")
corr_cols = st.columns(3)
corr_cols[0].metric(f"{index_label} vs VIX", f"{corr.get('VIX'):.3f}" if corr.get("VIX") is not None and not np.isnan(corr.get("VIX")) else "N/A")
corr_cols[1].metric(f"{index_label} vs Fear & Greed", f"{corr.get('FearGreed'):.3f}" if corr.get("FearGreed") is not None and not np.isnan(corr.get("FearGreed")) else "N/A · need 5+ days")
corr_cols[2].metric(f"{index_label} vs HYG", f"{corr.get('HYG'):.3f}" if corr.get("HYG") is not None and not np.isnan(corr.get("HYG")) else "N/A")
st.plotly_chart(build_corr_chart(corr_df), use_container_width=True)

with st.expander("查看 Fear & Greed 历史数据"):
    st.caption("数据来自 repo 中的 fg_history.csv。你本地 collector 每晚 23:00 更新并 push 后，Streamlit Cloud 会读取最新历史。")
    if fg_history_table.empty:
        st.write("No Fear & Greed history yet.")
    else:
        show_hist = fg_history_table.sort_values("date", ascending=False).copy()
        show_hist["FearGreed"] = pd.to_numeric(show_hist["FearGreed"], errors="coerce").round(2)
        st.dataframe(show_hist, use_container_width=True)
        st.download_button("下载 fg_history.csv", data=fg_history_table.to_csv(index=False).encode("utf-8"), file_name="fg_history.csv", mime="text/csv")

with st.expander("查看原始相关性数据 · 字段说明"):
    st.markdown("""
<div class="data-dict">
<b>Index</b>：指数/ETF价格。<br>
<b>VIX</b>：波动率指数，越高代表市场恐慌越强。<br>
<b>FearGreed</b>：来自 fg_history.csv，每天一条，累计 5 天以上后可计算相关性。<br>
<b>10Y Yield / 美国10年期国债收益率</b>：估值锚，越高越压制估值。<br>
<b>DXY / 美元指数</b>：美元流动性指标，走强通常压制风险资产。<br>
<b>HYG / 高收益债ETF</b>：信用风险 proxy，走弱代表信用端压力。<br>
<b>LQD / 投资级债ETF</b>：利率/高等级信用压力 proxy。<br>
<b>MOVE</b>：债券市场波动率，常领先股市风险。<br><b>VIX3M/VIX</b>：波动率期限结构，倒挂代表近端风险高。<br><b>Real Yield</b>：真实利率，越高越压制估值。<br><b>RSP/SPY</b>：等权/市值权重比值，衡量市场宽度。<br><b>Trend</b>：价格相对200日均线的趋势过滤器。<br><b>Put/Call Proxy</b>：用 yfinance 读取 SPY 期权链，按 Put成交量/Call成交量估算；不是官方CBOE总Put/Call，因此权重较低。<br><b>RollingCorr</b>：滚动相关性，判断价格与风险因子是否出现背离。
</div>
""", unsafe_allow_html=True)
    if corr_df.empty:
        st.write("No correlation data available.")
    else:
        display_df = corr_df.copy()
        if "time" in display_df.columns:
            display_df = display_df.sort_values("time", ascending=False)
        display_df = display_df.head(150)
        numeric_cols = display_df.select_dtypes(include=["float", "float64", "float32"]).columns
        display_df[numeric_cols] = display_df[numeric_cols].round(4)
        st.dataframe(display_df, use_container_width=True)

st.markdown(
    """
<div style="color:#64748b;font-size:12px;margin-top:18px;">
Data: Yahoo Finance via yfinance · CNN/Finhacker Fear & Greed · Local/GitHub fg_history.csv.
<br>仅供参考，不构成投资建议。仓位建议为权益类资产目标区间，不代表任何单只股票建议。
</div>
""",
    unsafe_allow_html=True,
)
