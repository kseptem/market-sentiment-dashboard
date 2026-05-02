import json
import re
from datetime import datetime, timezone
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from streamlit_autorefresh import st_autorefresh


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Daily Market Pulse",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# -----------------------------
# CSS
# -----------------------------
st.markdown(
    """
<style>
:root {
    --ink: #111827;
    --muted: #6b7280;
    --line: #d7dde8;
    --green: #10b981;
    --yellow: #eab308;
    --orange: #f97316;
    --red: #ef4444;
    --blue: #3b82f6;
    --pink: #ec4899;
    --card: #ffffff;
    --soft: #f8fafc;
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Arial, sans-serif;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 2rem;
    max-width: 1280px;
}

.main-title {
    font-size: 48px;
    line-height: 1.05;
    font-weight: 900;
    color: var(--ink);
    letter-spacing: -1px;
    margin-bottom: 8px;
}

.pill {
    display:inline-flex;
    align-items:center;
    gap:8px;
    background:#111827;
    color:#fff;
    padding:9px 22px;
    border-radius:999px;
    font-weight:800;
    letter-spacing:.5px;
    margin-bottom: 16px;
}

.date-pill {
    display:inline-flex;
    float:right;
    border:1px solid var(--line);
    padding:8px 22px;
    border-radius:999px;
    color:#374151;
    background:#f8fafc;
    font-weight:600;
    margin-top:2px;
}

.sub-title {
    color: var(--muted);
    font-size: 17px;
    margin-top: 4px;
    margin-bottom: 24px;
}

.green-accent {
    display:inline-block;
    width:58px;
    height:7px;
    background:var(--green);
    margin-right:14px;
    vertical-align:middle;
}

.yellow-accent {
    display:inline-block;
    width:58px;
    height:7px;
    background:var(--yellow);
    margin-right:14px;
    vertical-align:middle;
}

.metric-card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 24px 26px 18px 26px;
    margin-bottom: 22px;
    box-shadow: 0 2px 12px rgba(17,24,39,0.035);
}

.metric-card h3 {
    margin: 0;
    font-size: 20px;
    font-weight: 900;
    color: var(--ink);
}

.metric-card .desc {
    color: var(--muted);
    font-size: 15px;
    margin-top: 3px;
}

.big-number {
    text-align:center;
    font-size: 76px;
    line-height: .95;
    font-weight: 950;
    letter-spacing: -2px;
}

.badge {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    border-radius:999px;
    font-weight:900;
    font-size:16px;
    padding:10px 20px;
    border:2px solid currentColor;
    min-width: 150px;
    background: rgba(255,255,255,.72);
}

.segment-wrap {
    margin-top: 20px;
}

.segment-bar {
    position:relative;
    display:grid;
    grid-template-columns: repeat(7, 1fr);
    gap:2px;
    height:25px;
    margin: 8px 24px 8px 24px;
}

.segment {
    height:25px;
    border-radius:0;
    opacity:.95;
}

.pointer {
    position:absolute;
    top:-22px;
    width:0;
    height:0;
    border-left:11px solid transparent;
    border-right:11px solid transparent;
    transform:translateX(-50%);
}

.segment-labels {
    display:grid;
    grid-template-columns: repeat(7, 1fr);
    gap:2px;
    margin:0 24px;
    text-align:center;
    font-size:13px;
    color:#64748b;
    font-weight:800;
}

.playbook-title {
    margin: 18px 0 10px 0;
    font-size: 21px;
    font-weight: 950;
    color: var(--ink);
}

.playbook-card {
    background:#fff;
    border:1px solid var(--line);
    border-radius:18px;
    padding:14px 20px 12px 20px;
    margin-bottom:24px;
    box-shadow:0 2px 12px rgba(17,24,39,0.035);
}

.playbook-table {
    width:100%;
    border-collapse:collapse;
    font-size:17px;
}

.playbook-table th {
    color:#64748b;
    text-align:left;
    padding:9px 10px;
    font-weight:900;
    border-bottom:1px solid #e5e7eb;
}

.playbook-table td {
    padding:10px;
    border-bottom:1px solid #eef2f7;
    font-weight:650;
}

.playbook-table tr.now-row {
    background: #ecfdf5;
}

.playbook-table tr.now-row-yellow {
    background: #fefce8;
}

.now-badge {
    background:#10b981;
    color:#fff;
    padding:5px 11px;
    border-radius:999px;
    font-size:13px;
    font-weight:900;
}

.now-badge-yellow {
    background:#eab308;
    color:#fff;
    padding:5px 11px;
    border-radius:999px;
    font-size:13px;
    font-weight:900;
}

.strategy-box {
    background:#ecfdf5;
    border:2px solid #10b981;
    border-radius:18px;
    padding:18px 24px;
    margin: 16px 0 28px 0;
}

.strategy-title {
    color:#059669;
    font-size:17px;
    font-weight:900;
    margin-bottom:5px;
}

.strategy-main {
    font-size:28px;
    font-weight:950;
    color:#111827;
}

.small-note {
    color:#6b7280;
    font-size:13px;
}

.source-chip {
    display:inline-flex;
    background:#f1f5f9;
    border:1px solid #e2e8f0;
    color:#475569;
    padding:4px 10px;
    border-radius:999px;
    font-size:12px;
    font-weight:700;
}

div[data-testid="stMetricValue"] {
    font-weight: 900;
}


/* --- Compact dashboard override --- */
.block-container {
    padding-top: .6rem;
    max-width: 1180px;
}
.main-title {
    font-size: 34px;
    margin-bottom: 4px;
}
.pill {
    padding: 6px 16px;
    font-size: 13px;
    margin-bottom: 8px;
}
.date-pill {
    padding: 6px 16px;
    font-size: 13px;
}
.sub-title {
    font-size: 14px;
    margin-bottom: 14px;
}
.green-accent {
    width: 44px;
    height: 5px;
}
.metric-card {
    padding: 16px 18px 14px 18px;
    margin-bottom: 14px;
    border-radius: 16px;
}
.metric-card h3 {
    font-size: 17px;
}
.metric-card .desc {
    font-size: 13px;
}
.big-number {
    font-size: 52px;
}
.badge {
    font-size: 14px;
    padding: 7px 14px;
    min-width: 110px;
}
.segment-wrap {
    margin-top: 10px;
}
.segment-bar {
    height: 18px;
    margin: 6px 14px 6px 14px;
}
.segment {
    height: 18px;
}
.pointer {
    top: -15px;
    border-left-width: 8px !important;
    border-right-width: 8px !important;
}
.segment-labels {
    margin: 0 14px;
    font-size: 11px;
}
.strategy-box {
    padding: 14px 18px;
    margin: 0 0 14px 0;
    border-radius: 16px;
}
.strategy-title {
    font-size: 14px;
}
.strategy-main {
    font-size: 25px;
}
.source-chip {
    font-size: 11px;
    padding: 3px 8px;
}
.compact-summary-card {
    background:#fff;
    border:1px solid #d7dde8;
    border-radius:16px;
    padding:14px 16px;
    box-shadow:0 2px 12px rgba(17,24,39,0.035);
    height:100%;
}
.compact-summary-title {
    color:#64748b;
    font-weight:900;
    font-size:13px;
    margin-bottom:6px;
}
.compact-summary-value {
    font-size:26px;
    color:#111827;
    font-weight:950;
    line-height:1.1;
}
.compact-summary-note {
    color:#64748b;
    font-size:12px;
    margin-top:6px;
}


.signal-card {
    background: linear-gradient(135deg, #ecfdf5 0%, #ffffff 70%);
    border: 1px solid #a7f3d0;
    border-radius: 16px;
    padding: 14px 16px;
    margin-bottom: 12px;
}
.signal-score {
    font-size: 38px;
    font-weight: 950;
    color: #059669;
    line-height: 1;
}
.signal-label {
    font-size: 16px;
    font-weight: 950;
    color: #111827;
}
.annotation-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 5px solid #10b981;
    border-radius: 14px;
    padding: 12px 14px;
    margin: 10px 0 14px 0;
    color: #334155;
    font-size: 14px;
    line-height: 1.55;
}
.annotation-box.warning {
    border-left-color: #eab308;
    background: #fffbeb;
}
.annotation-box.danger {
    border-left-color: #ef4444;
    background: #fef2f2;
}
.data-dict {
    background:#ffffff;
    border:1px solid #e2e8f0;
    border-radius:14px;
    padding:12px 14px;
    margin:8px 0;
    font-size:13px;
    color:#475569;
}
.data-dict b {
    color:#111827;
}
@media (max-width: 900px) {
    .main-title {
        font-size: 28px;
    }
    .big-number {
        font-size: 42px;
    }
    .metric-card {
        padding: 13px 14px;
    }
    .strategy-main {
        font-size: 22px;
    }
    .badge {
        min-width: 88px;
        font-size: 12px;
        padding: 6px 10px;
    }
}

</style>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Constants
# -----------------------------
INDEX_MAP = {
    "S&P 500 (^GSPC)": "^GSPC",
    "Nasdaq 100 (^NDX)": "^NDX",
    "Dow Jones (^DJI)": "^DJI",
    "SPY ETF": "SPY",
    "QQQ ETF": "QQQ",
}

PERIOD_OPTIONS = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
INTERVAL_OPTIONS = ["1m", "5m", "15m", "30m", "60m", "1d"]

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


# -----------------------------
# Helpers
# -----------------------------
def safe_float(x, default=None):
    try:
        if x is None:
            return default
        if isinstance(x, str) and x.strip() == "":
            return default
        return float(x)
    except Exception:
        return default


@st.cache_data(ttl=45, show_spinner=False)
def fetch_yahoo(symbol: str, period: str, interval: str) -> pd.DataFrame:
    try:
        df = yf.download(
            symbol,
            period=period,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False,
        )
        if df is None or df.empty:
            return pd.DataFrame()

        # Flatten MultiIndex columns if yfinance returns them
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]

        df = df.reset_index()
        time_col = "Datetime" if "Datetime" in df.columns else "Date"
        df = df.rename(columns={time_col: "time"})

        needed = ["time", "Open", "High", "Low", "Close", "Volume"]
        for col in needed:
            if col not in df.columns:
                if col == "Volume":
                    df[col] = 0
                else:
                    df[col] = np.nan

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
        df["Close"] = pd.to_numeric(df["Close"], errors="coerce")
        df = df.dropna(subset=["time", "Close"])
        return df[needed].copy()
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=120, show_spinner=False)
def fetch_cnn_fear_greed(manual_value: float) -> Tuple[float, str, str, pd.DataFrame]:
    """
    CNN has no stable official public API.
    This tries the commonly used CNN dataviz endpoint and falls back to manual value.
    """
    urls = [
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2020-01-01",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2021-01-01",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
    ]

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://edition.cnn.com/markets/fear-and-greed",
    }

    last_error = None

    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()

            fg = data.get("fear_and_greed", {}) or {}
            score = safe_float(fg.get("score"), None)
            rating = fg.get("rating") or fg.get("status") or "CNN"

            hist = pd.DataFrame()

            # Common format: fear_and_greed_historical.data = [{x: timestamp_ms, y: score}, ...]
            historical = data.get("fear_and_greed_historical", {}) or {}
            points = historical.get("data", []) if isinstance(historical, dict) else []

            rows = []
            for p in points:
                if not isinstance(p, dict):
                    continue
                x = p.get("x") or p.get("timestamp") or p.get("date")
                y = p.get("y") or p.get("score") or p.get("value")
                y = safe_float(y, None)
                if x is None or y is None:
                    continue

                try:
                    # CNN usually uses milliseconds
                    ts = pd.to_datetime(x, unit="ms", utc=True, errors="coerce")
                    if pd.isna(ts):
                        ts = pd.to_datetime(x, utc=True, errors="coerce")
                except Exception:
                    ts = pd.to_datetime(x, utc=True, errors="coerce")

                if not pd.isna(ts):
                    rows.append({"time": ts, "FearGreed": y})

            if rows:
                hist = pd.DataFrame(rows).dropna().sort_values("time")

            if score is not None:
                return float(score), str(rating).title(), "CNN live endpoint", hist

        except Exception as e:
            last_error = str(e)

    fallback_hist = pd.DataFrame(
        [{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": float(manual_value)}]
    )
    return float(manual_value), "Manual fallback", "Manual fallback · CNN blocked/unavailable", fallback_hist


@st.cache_data(ttl=300, show_spinner=False)
def fetch_finhacker_fear_greed() -> Tuple[Optional[float], Optional[str], str, pd.DataFrame]:
    """
    Finhacker is used as a non-official fallback when CNN blocks Streamlit Cloud.
    The page is currently public and contains the latest CNN Fear & Greed value in HTML text.
    """
    url = "https://www.finhacker.cz/en/fear-and-greed-index-historical-data-and-chart/"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }

    try:
        r = requests.get(url, headers=headers, timeout=12)
        r.raise_for_status()
        html = r.text

        patterns = [
            r"The current value of the Fear\s*&\s*Greed Index as of .*? is\s+(\d+(?:\.\d+)?)\s*-\s*([a-zA-Z ]+)",
            r"current value of the Fear\s*&\s*Greed Index.*?is\s+(\d+(?:\.\d+)?)\s*-\s*([a-zA-Z ]+)",
            r"Fear\s*&\s*Greed Index.*?current value.*?(\d+(?:\.\d+)?)\s*-\s*([a-zA-Z ]+)",
        ]

        value = None
        label = None

        for pat in patterns:
            m = re.search(pat, html, re.I | re.S)
            if m:
                value = safe_float(m.group(1), None)
                label = m.group(2).strip().title()
                break

        # Backup: search JSON-LD / visible text around "current value"
        if value is None:
            compact = re.sub(r"\s+", " ", html)
            m = re.search(r"current value.{0,180}?(\d{1,3})(?:\s|&nbsp;)*-(?:\s|&nbsp;)*([A-Za-z ]{3,30})", compact, re.I)
            if m:
                value = safe_float(m.group(1), None)
                label = m.group(2).strip().title()

        if value is None:
            return None, None, "Finhacker parse failed", pd.DataFrame()

        value = max(0.0, min(100.0, float(value)))
        if not label:
            label = "Finhacker"

        hist = pd.DataFrame(
            [{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": value}]
        )

        return value, label, "Finhacker fallback", hist

    except Exception as e:
        return None, None, f"Finhacker unavailable: {e}", pd.DataFrame()


def fetch_fear_greed_with_fallback(manual_value: float) -> Tuple[float, str, str, pd.DataFrame]:
    """
    Priority:
    1. CNN dataviz endpoint
    2. Finhacker public page fallback
    3. Manual fallback
    """
    cnn_value, cnn_rating, cnn_source, cnn_hist = fetch_cnn_fear_greed(manual_value)

    if "CNN live endpoint" in cnn_source:
        return cnn_value, cnn_rating, cnn_source, cnn_hist

    fh_value, fh_rating, fh_source, fh_hist = fetch_finhacker_fear_greed()
    if fh_value is not None:
        return fh_value, fh_rating or "Finhacker", fh_source, fh_hist

    manual_hist = pd.DataFrame(
        [{"time": pd.Timestamp.now(tz="UTC"), "FearGreed": float(manual_value)}]
    )
    return float(manual_value), "Manual fallback", f"Manual fallback · CNN and Finhacker unavailable", manual_hist



def vix_level(v: float):
    if v < 11:
        return "压波动", "停止追高，保留现金", "#10b981", 0
    if v < 14:
        return "Risk-On", "正常配置，顺势持有", "#10b981", 1
    if v < 18:
        return "健康中性", "常规定投，保持节奏", "#10b981", 2
    if v < 25:
        return "早期压力", "放慢加仓，观察波动", "#eab308", 3
    if v < 35:
        return "Risk-Off", "分批加仓，逢低布局", "#f97316", 4
    if v < 50:
        return "恐慌", "强力加仓，但保留现金", "#ef4444", 5
    return "流动性踩踏", "分批抄底，严控节奏", "#991b1b", 6


def fear_greed_level(v: float):
    if v <= 15:
        return "投降", "激进加仓", "#ef4444", 0
    if v <= 30:
        return "深度恐惧", "加仓，分批买入", "#f97316", 1
    if v <= 45:
        return "恐惧", "正常定投，等待修复", "#eab308", 2
    if v <= 60:
        return "中性", "保持节奏，观察趋势", "#3b82f6", 3
    if v <= 75:
        return "贪婪", "控制仓位，不追高", "#eab308", 4
    if v <= 85:
        return "亢奋", "减速买入，部分止盈", "#f97316", 5
    return "泡沫区", "明确止盈，降低风险", "#ec4899", 6


def vix_pointer_pct(v: float) -> float:
    # visual scale for <11, 11-14, 14-18, 18-25, 25-35, 35-50, >50
    bounds = [0, 11, 14, 18, 25, 35, 50, 80]
    seg = 100 / 7
    if v < 11:
        return max(2, min(seg - 1, (v / 11) * seg))
    if v < 14:
        return seg * 1 + (v - 11) / 3 * seg
    if v < 18:
        return seg * 2 + (v - 14) / 4 * seg
    if v < 25:
        return seg * 3 + (v - 18) / 7 * seg
    if v < 35:
        return seg * 4 + (v - 25) / 10 * seg
    if v < 50:
        return seg * 5 + (v - 35) / 15 * seg
    return min(98, seg * 6 + (min(v, 80) - 50) / 30 * seg)


def fg_pointer_pct(v: float) -> float:
    # visual scale for 0-15, 15-30, 30-45, 45-60, 60-75, 75-85, 85-100
    seg = 100 / 7
    if v <= 15:
        return max(2, v / 15 * seg)
    if v <= 30:
        return seg * 1 + (v - 15) / 15 * seg
    if v <= 45:
        return seg * 2 + (v - 30) / 15 * seg
    if v <= 60:
        return seg * 3 + (v - 45) / 15 * seg
    if v <= 75:
        return seg * 4 + (v - 60) / 15 * seg
    if v <= 85:
        return seg * 5 + (v - 75) / 10 * seg
    return min(98, seg * 6 + (v - 85) / 15 * seg)


def render_meter_card(kind: str, value: float, label: str, strategy: str, color: str, pointer_pct: float, source: str = ""):
    if kind == "vix":
        title = "VIX · S&P 500"
        desc = "波动率指数"
        labels = ["<11", "11-14", "14-18", "18-25", "25-35", "35-50", ">50"]
        seg_colors = ["#d1fae5", "#10b981", "#86efac", "#fde68a", "#fdba74", "#fca5a5", "#f8b4c2"]
        accent = "#10b981"
    else:
        title = "FEAR & GREED · CNN"
        desc = "恐惧与贪婪指数"
        labels = ["0-15", "15-30", "30-45", "45-60", "60-75", "75-85", "85-100"]
        seg_colors = ["#f8b4c2", "#fdba74", "#fde68a", "#bfd3ff", "#eab308", "#fb923c", "#f472b6"]
        accent = "#eab308"

    seg_html = "".join([f'<div class="segment" style="background:{c};"></div>' for c in seg_colors])
    label_html = "".join([f"<div>{x}</div>" for x in labels])

    st.markdown(
        f"""
<div class="metric-card">
  <div style="display:grid; grid-template-columns: 1.2fr 1fr 1.1fr; gap: 10px; align-items:center;">
    <div>
      <div style="width:54px;height:6px;background:{accent};border-radius:999px;margin-bottom:10px;"></div>
      <h3>{title}</h3>
      <div class="desc">{desc}</div>
      {f'<div style="margin-top:8px;"><span class="source-chip">{source}</span></div>' if source else ''}
    </div>
    <div class="big-number" style="color:{accent};">{value:.0f}</div>
    <div style="text-align:right;">
      <span class="badge" style="color:{color};">{label}</span>
    </div>
  </div>
  <div class="segment-wrap">
    <div class="segment-bar">
      {seg_html}
      <div class="pointer" style="left:{pointer_pct:.2f}%; border-top:18px solid {accent};"></div>
    </div>
    <div class="segment-labels">{label_html}</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_playbook(title: str, accent_color: str, rows, current_idx: int, yellow=False):
    trs = ""
    for i, (rng, emotion, strategy) in enumerate(rows):
        bg = "#fefce8" if yellow and i == current_idx else ("#ecfdf5" if i == current_idx else "#ffffff")
        badge_bg = "#eab308" if yellow else "#10b981"
        now = f'<span style="background:{badge_bg};color:#fff;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:900;">NOW</span>' if i == current_idx else ""
        trs += f"""
        <tr style="background:{bg};">
            <td style="color:{accent_color};font-weight:950;padding:7px 8px;border-bottom:1px solid #eef2f7;white-space:nowrap;">{rng}</td>
            <td style="font-weight:800;padding:7px 8px;border-bottom:1px solid #eef2f7;white-space:nowrap;">{emotion}</td>
            <td style="font-weight:700;padding:7px 8px;border-bottom:1px solid #eef2f7;">{strategy}</td>
            <td style="text-align:right;padding:7px 8px;border-bottom:1px solid #eef2f7;">{now}</td>
        </tr>
        """

    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif;">
      <div style="margin:4px 0 8px 0;font-size:17px;font-weight:950;color:#111827;">
        <span style="display:inline-block;width:34px;height:5px;background:{accent_color};border-radius:999px;margin-right:10px;vertical-align:middle;"></span>
        {title}
      </div>
      <div style="background:#fff;border:1px solid #d7dde8;border-radius:16px;padding:10px 12px;margin-bottom:8px;box-shadow:0 2px 12px rgba(17,24,39,0.035);">
        <table style="width:100%;border-collapse:collapse;font-size:13px;">
          <thead>
            <tr>
              <th style="color:#64748b;text-align:left;padding:6px 8px;font-weight:900;border-bottom:1px solid #e5e7eb;">区间</th>
              <th style="color:#64748b;text-align:left;padding:6px 8px;font-weight:900;border-bottom:1px solid #e5e7eb;">情绪</th>
              <th style="color:#64748b;text-align:left;padding:6px 8px;font-weight:900;border-bottom:1px solid #e5e7eb;">策略</th>
              <th style="border-bottom:1px solid #e5e7eb;"></th>
            </tr>
          </thead>
          <tbody>{trs}</tbody>
        </table>
      </div>
    </div>
    """
    components.html(html, height=250, scrolling=False)


def build_price_chart(index_df: pd.DataFrame, vix_df: pd.DataFrame, index_name: str):
    fig = go.Figure()

    if not index_df.empty:
        fig.add_trace(
            go.Scatter(
                x=index_df["time"],
                y=index_df["Close"],
                mode="lines",
                name=index_name,
                line=dict(width=3),
            )
        )

    if not vix_df.empty:
        fig.add_trace(
            go.Scatter(
                x=vix_df["time"],
                y=vix_df["Close"],
                mode="lines",
                name="VIX",
                yaxis="y2",
                line=dict(width=2, dash="dot"),
            )
        )

    fig.update_layout(
        height=320,
        margin=dict(l=10, r=10, t=24, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title=index_name, showgrid=True, gridcolor="#eef2f7"),
        yaxis2=dict(title="VIX", overlaying="y", side="right", showgrid=False),
        xaxis=dict(showgrid=False),
        hovermode="x unified",
    )
    return fig


def compute_correlations(index_df, vix_df, fg_hist, rolling_window):
    """
    Stable daily join version.
    Avoids pandas.merge_asof because Streamlit Cloud + pandas versions may raise MergeError
    when duplicate/suffixed columns exist.
    """
    if index_df is None or vix_df is None or index_df.empty or vix_df.empty:
        return pd.DataFrame(), None, None

    def prep(df, value_col_name):
        x = df.copy()

        if "time" not in x.columns or "Close" not in x.columns:
            return pd.DataFrame()

        x["date"] = pd.to_datetime(x["time"], errors="coerce").dt.date
        x[value_col_name] = pd.to_numeric(x["Close"], errors="coerce")

        x = x.dropna(subset=["date", value_col_name])
        x = x.groupby("date", as_index=False)[value_col_name].last()
        return x

    index_daily = prep(index_df, "Index")
    vix_daily = prep(vix_df, "VIX")

    if index_daily.empty or vix_daily.empty:
        return pd.DataFrame(), None, None

    merged = pd.merge(index_daily, vix_daily, on="date", how="inner")

    merged["IndexRet"] = merged["Index"].pct_change()
    merged["VIXChg"] = merged["VIX"].pct_change()

    corr_vix = None
    if merged[["IndexRet", "VIXChg"]].dropna().shape[0] >= 5:
        corr_vix = float(merged["IndexRet"].corr(merged["VIXChg"]))
        merged["RollingCorr_Index_VIX"] = (
            merged["IndexRet"].rolling(rolling_window).corr(merged["VIXChg"])
        )

    corr_fg = None

    if fg_hist is not None and not fg_hist.empty and "FearGreed" in fg_hist.columns:
        fg = fg_hist.copy()

        if "time" in fg.columns:
            fg["date"] = pd.to_datetime(fg["time"], errors="coerce").dt.date
        elif "date" in fg.columns:
            fg["date"] = pd.to_datetime(fg["date"], errors="coerce").dt.date
        else:
            fg = pd.DataFrame()

        if not fg.empty:
            fg["FearGreed"] = pd.to_numeric(fg["FearGreed"], errors="coerce")
            fg = fg.dropna(subset=["date", "FearGreed"])
            fg = fg.groupby("date", as_index=False)["FearGreed"].last()

            merged = pd.merge(merged, fg, on="date", how="left")
            merged["FearGreed"] = merged["FearGreed"].ffill().bfill()
            merged["FGChg"] = merged["FearGreed"].diff()

            if merged[["IndexRet", "FGChg"]].dropna().shape[0] >= 5:
                corr_fg = float(merged["IndexRet"].corr(merged["FGChg"]))
                merged["RollingCorr_Index_FG"] = (
                    merged["IndexRet"].rolling(rolling_window).corr(merged["FGChg"])
                )

    merged["time"] = pd.to_datetime(merged["date"])

    return merged, corr_vix, corr_fg


def build_corr_chart(corr_df: pd.DataFrame):
    fig = go.Figure()

    if corr_df is None or corr_df.empty:
        return fig

    if "RollingCorr_Index_VIX" in corr_df.columns:
        fig.add_trace(
            go.Scatter(
                x=corr_df["time"],
                y=corr_df["RollingCorr_Index_VIX"],
                mode="lines",
                name="Index vs VIX rolling corr",
                line=dict(width=3),
            )
        )

    if "RollingCorr_Index_FG" in corr_df.columns:
        fig.add_trace(
            go.Scatter(
                x=corr_df["time"],
                y=corr_df["RollingCorr_Index_FG"],
                mode="lines",
                name="Index vs Fear&Greed rolling corr",
                line=dict(width=3, dash="dot"),
            )
        )

    fig.add_hline(y=0, line_dash="dash", line_width=1)

    fig.update_layout(
        height=260,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[-1, 1], title="Correlation", showgrid=True, gridcolor="#eef2f7"),
        xaxis=dict(showgrid=False),
        hovermode="x unified",
    )
    return fig


def pct_change_text(df: pd.DataFrame):
    if df is None or df.empty or len(df) < 2:
        return None
    first = safe_float(df["Close"].iloc[0])
    last = safe_float(df["Close"].iloc[-1])
    if first in (None, 0) or last is None:
        return None
    return (last / first - 1) * 100



def market_signal_engine(vix_value: float, fg_value: float, corr_vix: Optional[float] = None, index_return: Optional[float] = None, vix_return: Optional[float] = None):
    """
    Professional signal engine.
    Score range: 0-100. Higher means better risk/reward for incremental buying.
    Also returns suggested equity exposure range.
    """
    score = 50
    notes = []
    tags = []

    # VIX regime
    if vix_value < 11:
        score -= 14
        notes.append("VIX < 11：波动被压得很低，常见于强牛市后段或过度平静期，追高性价比下降。")
    elif vix_value < 14:
        score -= 4
        notes.append("VIX 11-14：Risk-On 环境，适合持有，但新增仓位不宜太激进。")
    elif vix_value < 18:
        score += 6
        notes.append("VIX 14-18：健康中性波动区，市场结构较稳定，适合常规定投。")
    elif vix_value < 25:
        score += 8
        notes.append("VIX 18-25：早期压力区，波动开始抬头，适合放慢节奏、等待更好价格。")
    elif vix_value < 35:
        score += 18
        notes.append("VIX 25-35：Risk-Off，恐惧释放中，长期资金可以分批加仓。")
    elif vix_value < 50:
        score += 26
        notes.append("VIX 35-50：市场恐慌，机会开始变大，但需要分批执行、保留现金。")
    else:
        score += 30
        notes.append("VIX > 50：可能是流动性踩踏，不适合 All-in，但通常进入长期赔率较高区域。")

    # Fear & Greed regime
    if fg_value <= 15:
        score += 26
        notes.append("Fear & Greed 0-15：投降区，反向配置价值很高。")
    elif fg_value <= 30:
        score += 18
        notes.append("Fear & Greed 15-30：深度恐惧，适合加仓但要分批。")
    elif fg_value <= 45:
        score += 8
        notes.append("Fear & Greed 30-45：恐惧区，适合正常定投等待情绪修复。")
    elif fg_value <= 60:
        score += 2
        notes.append("Fear & Greed 45-60：中性区，按计划执行，不需要大幅调整。")
    elif fg_value <= 75:
        score -= 8
        notes.append("Fear & Greed 60-75：贪婪区，上涨趋势可能延续，但新增仓位要克制。")
    elif fg_value <= 85:
        score -= 18
        notes.append("Fear & Greed 75-85：亢奋区，FOMO 风险升高，适合减速买入或小幅止盈。")
    else:
        score -= 28
        notes.append("Fear & Greed > 85：泡沫区，短期回撤风险显著上升。")

    # Combo signals
    if vix_value < 14 and fg_value > 80:
        score -= 18
        tags.append("顶部风险")
        notes.append("组合信号：VIX 很低 + 情绪极度贪婪，属于典型顶部风险结构。")
    if vix_value > 30 and fg_value < 25:
        score += 20
        tags.append("抄底窗口")
        notes.append("组合信号：VIX > 30 + Fear & Greed < 25，恐慌充分释放，适合分批抄底。")
    if vix_value > 25 and fg_value > 60:
        score -= 10
        tags.append("风险背离")
        notes.append("组合信号：VIX 偏高但情绪仍贪婪，说明市场可能低估风险。")
    if 14 <= vix_value < 20 and 45 <= fg_value <= 70:
        tags.append("健康风险偏好")
        notes.append("组合信号：波动正常、情绪中性偏积极，属于相对健康的 Risk-On 环境。")

    # Correlation
    if corr_vix is not None and not np.isnan(corr_vix):
        if corr_vix > -0.3:
            score -= 16
            tags.append("价格-波动背离")
            notes.append("相关性信号：指数与 VIX 负相关明显减弱，可能出现上涨但风险同步上升的假行情。")
        elif corr_vix > -0.6:
            score -= 7
            notes.append("相关性信号：指数与 VIX 负相关偏弱，建议观察是否出现波动结构变化。")
        elif corr_vix < -0.95:
            score -= 4
            notes.append("相关性信号：指数与 VIX 负相关极强，交易拥挤，短期可能出现反向波动。")
        else:
            score += 5
            notes.append("相关性信号：指数与 VIX 保持正常强负相关，市场结构较健康。")
    else:
        notes.append("相关性样本不足，当前信号主要基于 VIX 与 Fear & Greed。")

    # Fake rally condition
    if index_return is not None and vix_return is not None:
        if index_return > 0 and vix_return > 0:
            score -= 10
            tags.append("假上涨警报")
            notes.append("当期指数上涨但 VIX 同时上升，说明上涨质量可能不好，需要谨慎追高。")
        elif index_return > 0 and vix_return < 0:
            score += 3
            notes.append("当期指数上涨且 VIX 下降，上涨质量较健康。")

    score = int(max(0, min(100, score)))

    # Position sizing suggestion for equity exposure
    if score >= 82:
        signal = "强机会区"
        level = "opportunity"
        action = "强力分批加仓 · 但避免一次性 All-in"
        position = "75% — 90%"
    elif score >= 68:
        signal = "偏进攻"
        level = "constructive"
        action = "加大定投 · 分批买入 · 保留现金"
        position = "60% — 75%"
    elif score >= 50:
        signal = "中性健康"
        level = "normal"
        action = "常规定投 · 保持节奏 · 不追高"
        position = "45% — 60%"
    elif score >= 35:
        signal = "偏防守"
        level = "caution"
        action = "减速买入 · 控制仓位 · 等回调"
        position = "30% — 45%"
    else:
        signal = "高风险"
        level = "risk"
        action = "暂停追高 · 部分止盈 · 提高现金"
        position = "15% — 30%"

    if not tags:
        tags = [signal]

    return score, signal, level, action, position, tags, notes


def annotation_class(level: str):
    if level in ("risk",):
        return "danger"
    if level in ("caution",):
        return "warning"
    return ""


def combined_strategy(vix_value: float, fg_value: float):
    vix_label, vix_strategy, _, vix_idx = vix_level(vix_value)
    fg_label, fg_strategy, _, fg_idx = fear_greed_level(fg_value)

    # conservative rule: high greed + low VIX means risk of chasing
    if fg_value >= 76:
        return "减半定投 · 警惕回调 · 部分止盈"
    if fg_value >= 56 and vix_value < 20:
        return "减半定投 · 谨慎追高 · 控制仓位"
    if vix_value >= 30 or fg_value <= 24:
        return "加大定投 · 分批买入 · 保留现金"
    if vix_value >= 20 or fg_value <= 44:
        return "小幅加仓 · 分批布局 · 等待确认"
    return "常规定投 · 保持节奏 · 不追高"


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.markdown("### Dashboard Settings")

    index_label = st.selectbox("Market index", list(INDEX_MAP.keys()), index=0)
    period = st.selectbox("History window", PERIOD_OPTIONS, index=4)
    interval = st.selectbox("Interval", INTERVAL_OPTIONS, index=5)
    rolling_window = st.slider("Rolling correlation window", min_value=5, max_value=120, value=30, step=5)
    refresh = st.slider("Auto refresh seconds", min_value=0, max_value=600, value=120, step=15)
    manual_fg = st.number_input("Manual Fear & Greed fallback", min_value=0, max_value=100, value=50, step=1)
    st.caption("If CNN endpoint fails, this manual value will be used and clearly marked.")

if refresh and refresh > 0:
    st_autorefresh(interval=refresh * 1000, key="market-refresh")


# -----------------------------
# Data
# -----------------------------
symbol = INDEX_MAP[index_label]
index_df = fetch_yahoo(symbol, period, interval)
vix_df = fetch_yahoo("^VIX", period, interval)

vix_value = safe_float(vix_df["Close"].iloc[-1], 0) if not vix_df.empty else 0
fg_value, fg_rating, fg_source, fg_hist = fetch_fear_greed_with_fallback(float(manual_fg))

vix_label, vix_strategy, vix_color, vix_idx = vix_level(vix_value)
fg_label, fg_strategy, fg_color, fg_idx = fear_greed_level(fg_value)

today = datetime.now().strftime("%Y · %m · %d / %a")


# -----------------------------
# Header
# -----------------------------
st.markdown(f'<div class="date-pill">{today}</div>', unsafe_allow_html=True)
st.markdown('<div class="pill">◆ DAILY MARKET PULSE</div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">今日美股情绪观察</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-title"><span class="green-accent"></span><b style="color:#059669;">US INDEX · VIX & CNN FEAR & GREED</b>'
    '　标普500 / 纳指 · 波动率指数 · 恐惧与贪婪指数</div>',
    unsafe_allow_html=True,
)


# Preliminary correlation for signal engine
corr_df, corr_vix, corr_fg = compute_correlations(index_df, vix_df, fg_hist, rolling_window)

# -----------------------------
# Executive dashboard
# -----------------------------
index_return = pct_change_text(index_df)
vix_return = pct_change_text(vix_df)
score, signal, signal_level, strategy, position_suggestion, signal_tags, signal_notes = market_signal_engine(float(vix_value), float(fg_value), corr_vix, index_return, vix_return)

top_left, top_right = st.columns([2.2, 1], gap="large")

with top_left:
    c_vix, c_fg = st.columns(2, gap="medium")
    with c_vix:
        render_meter_card(
            "vix",
            float(vix_value),
            vix_label,
            vix_strategy,
            vix_color,
            vix_pointer_pct(float(vix_value)),
            source="Yahoo Finance / CBOE VIX",
        )
    with c_fg:
        render_meter_card(
            "fg",
            float(fg_value),
            fg_label,
            fg_strategy,
            fg_color,
            fg_pointer_pct(float(fg_value)),
            source=fg_source,
        )

with top_right:
    st.markdown(
        f"""
<div class="signal-card">
  <div class="compact-summary-title">MARKET SIGNAL · 市场信号</div>
  <div style="display:flex;align-items:end;gap:12px;">
    <div class="signal-score">{score}</div>
    <div>
      <div class="signal-label">{signal}</div>
      <div class="compact-summary-note">0-100 越高代表越适合增量买入</div>
      <div class="compact-summary-note">建议权益仓位：<b>{position_suggestion}</b></div>
    </div>
  </div>
</div>
<div class="strategy-box">
  <div class="strategy-title">◆ TODAY'S STRATEGY · 今日策略</div>
  <div class="strategy-main">{strategy}</div>
  <div class="compact-summary-note" style="margin-top:8px;">信号标签：{" · ".join(signal_tags)}</div>
</div>
""",
        unsafe_allow_html=True,
    )

    last_index = f"{index_df['Close'].iloc[-1]:,.2f}" if not index_df.empty else "N/A"
    idx_ret = f"{index_return:+.2f}%" if index_return is not None else "N/A"
    vix_ret = f"{vix_return:+.2f}%" if vix_return is not None else "N/A"

    st.markdown(
        f"""
<div class="compact-summary-card">
  <div class="compact-summary-title">核心数据</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
    <div>
      <div class="compact-summary-note">{index_label}</div>
      <div class="compact-summary-value" style="font-size:21px;">{last_index}</div>
      <div class="compact-summary-note">{idx_ret}</div>
    </div>
    <div>
      <div class="compact-summary-note">VIX / F&G</div>
      <div class="compact-summary-value" style="font-size:21px;">{vix_value:.1f} / {fg_value:.0f}</div>
      <div class="compact-summary-note">VIX {vix_ret} · {fg_rating}</div>
    </div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )

    note_html = "<br>".join([f"• {x}" for x in signal_notes[:4]])
    st.markdown(
        f"""
<div class="annotation-box {annotation_class(signal_level)}">
  <b>信号注释：</b><br>{note_html}
</div>
""",
        unsafe_allow_html=True,
    )

st.markdown("### 策略区间")
pb1, pb2 = st.columns(2, gap="medium")
with pb1:
    render_playbook("VIX PLAYBOOK", "#10b981", VIX_ROWS, vix_idx, yellow=False)
with pb2:
    render_playbook("FEAR & GREED PLAYBOOK", "#eab308", FG_ROWS, fg_idx, yellow=True)


# -----------------------------
# Charts and correlations
# -----------------------------
st.markdown("### 市场走势与波动率")
c1, c2, c3, c4 = st.columns(4)
c1.metric(index_label, f"{index_df['Close'].iloc[-1]:,.2f}" if not index_df.empty else "N/A",
          f"{index_return:.2f}%" if index_return is not None else None)
c2.metric("VIX", f"{vix_value:.2f}" if vix_value else "N/A",
          f"{vix_return:.2f}%" if vix_return is not None else None)
c3.metric("CNN Fear & Greed", f"{fg_value:.0f}", fg_rating)
c4.metric("Auto refresh", f"{refresh}s" if refresh else "Off")

st.plotly_chart(build_price_chart(index_df, vix_df, index_label), use_container_width=True)

st.markdown("### 相关性分析")
m1, m2 = st.columns(2)
m1.metric(
    f"{index_label} vs VIX",
    f"{corr_vix:.3f}" if corr_vix is not None and not np.isnan(corr_vix) else "N/A",
    help="使用同日收益率/变化率计算，通常大盘与 VIX 为负相关。",
)
m2.metric(
    f"{index_label} vs Fear & Greed",
    f"{corr_fg:.3f}" if corr_fg is not None and not np.isnan(corr_fg) else "N/A",
    help="使用同日收益率与 Fear & Greed 日变化计算。CNN 历史数据不可用时可能无法计算。",
)

corr_comment = "正常情况下，指数和 VIX 应该强负相关。若相关性从 -0.8 附近快速升向 0，说明指数上涨时风险也在上升，属于背离信号。"
if corr_vix is not None and not np.isnan(corr_vix):
    if corr_vix > -0.3:
        corr_comment = "⚠️ 当前指数与 VIX 负相关明显减弱，说明市场价格和风险指标出现背离，建议降低追高动作。"
    elif corr_vix < -0.95:
        corr_comment = "⚠️ 当前指数与 VIX 负相关极强，说明交易非常一致，短期可能出现反向波动。"
    elif corr_vix < -0.6:
        corr_comment = "✅ 当前指数与 VIX 保持强负相关，属于较健康的市场结构。"

st.markdown(
    f"""
<div class="annotation-box">
  <b>相关性怎么用：</b>{corr_comment}
</div>
""",
    unsafe_allow_html=True,
)

if corr_df is not None and not corr_df.empty:
    st.plotly_chart(build_corr_chart(corr_df), use_container_width=True)

with st.expander("查看原始相关性数据 · 字段说明"):
    st.markdown(
        """
<div class="data-dict">
<b>Index</b>：指数收盘价。<br>
<b>VIX</b>：波动率指数，越高代表市场恐慌越强。<br>
<b>IndexRet</b>：指数日收益率。<br>
<b>VIXChg</b>：VIX 日变化率。<br>
<b>RollingCorr_Index_VIX</b>：指数收益率与 VIX 变化率的滚动相关性，通常应为负值。<br>
<b>FearGreed</b>：CNN 恐惧与贪婪指数；如果使用 Finhacker fallback，只有最新值，历史列可能为空。<br>
<b>FGChg</b>：Fear & Greed 的日变化。历史数据不足时可能为空。<br>
<b>Market Signal Score</b>：综合 VIX、Fear & Greed、相关性和价格-波动背离后的 0-100 分；越高代表越适合增量买入。<br>
<b>仓位建议</b>：这里指权益类资产目标仓位区间，不是单只股票仓位。
</div>
""",
        unsafe_allow_html=True,
    )
    if corr_df is None or corr_df.empty:
        st.write("No correlation data available.")
    else:
        display_df = corr_df.tail(120).copy()
        numeric_cols = display_df.select_dtypes(include=["float", "float64", "float32"]).columns
        display_df[numeric_cols] = display_df[numeric_cols].round(4)
        st.dataframe(display_df, use_container_width=True)


# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
<div class="small-note">
Data: Yahoo Finance via yfinance · CBOE VIX · CNN Fear & Greed unofficial endpoint/fallback manual input.
<br>
仅供参考，不构成投资建议。CNN Fear & Greed 没有稳定官方公开 API，如接口不可用会自动尝试 Finhacker fallback，仍失败才使用左侧手动 fallback 数值。
</div>
""",
    unsafe_allow_html=True,
)
