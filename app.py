import json
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
    grid-template-columns: repeat(5, 1fr);
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
    grid-template-columns: repeat(5, 1fr);
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
    ("< 12", "极度乐观", "谨慎追高，保持警觉"),
    ("12 — 20", "正常区间", "常规定投，保持节奏"),
    ("20 — 30", "恐惧上升", "加大定投，分批买入"),
    ("30 — 50", "市场恐慌", "加倍定投，逢低布局"),
    ("> 50", "极度恐慌", "黄金机会，大胆抄底"),
]

FG_ROWS = [
    ("0 — 24", "极度恐惧", "黄金机会，加倍买入"),
    ("25 — 44", "恐惧", "加大定投，分批布局"),
    ("45 — 55", "中性", "常规定投，保持节奏"),
    ("56 — 75", "贪婪", "谨慎追高，控制仓位"),
    ("76 — 100", "极度贪婪", "警惕回调，部分止盈"),
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


def vix_level(v: float):
    if v < 12:
        return "极度乐观", "谨慎追高，保持警觉", "#10b981", 0
    if v < 20:
        return "正常波动", "常规定投，保持节奏", "#10b981", 1
    if v < 30:
        return "恐惧上升", "加大定投，分批买入", "#eab308", 2
    if v < 50:
        return "市场恐慌", "加倍定投，逢低布局", "#f97316", 3
    return "极度恐慌", "黄金机会，大胆抄底", "#ef4444", 4


def fear_greed_level(v: float):
    if v <= 24:
        return "极度恐惧", "黄金机会，加倍买入", "#ef4444", 0
    if v <= 44:
        return "恐惧", "加大定投，分批布局", "#f97316", 1
    if v <= 55:
        return "中性", "常规定投，保持节奏", "#3b82f6", 2
    if v <= 75:
        return "贪婪", "谨慎追高，控制仓位", "#eab308", 3
    return "极度贪婪", "警惕回调，部分止盈", "#ec4899", 4


def vix_pointer_pct(v: float) -> float:
    # visual scale for <12, 12-20, 20-30, 30-50, >50
    if v <= 0:
        return 0
    if v < 12:
        return max(2, min(19, v / 12 * 20))
    if v < 20:
        return 20 + (v - 12) / 8 * 20
    if v < 30:
        return 40 + (v - 20) / 10 * 20
    if v < 50:
        return 60 + (v - 30) / 20 * 20
    return min(98, 80 + (min(v, 80) - 50) / 30 * 20)


def fg_pointer_pct(v: float) -> float:
    return max(1, min(99, v))


def render_meter_card(kind: str, value: float, label: str, strategy: str, color: str, pointer_pct: float, source: str = ""):
    if kind == "vix":
        title = "VIX · S&P 500"
        desc = "波动率指数"
        labels = ["< 12", "12-20", "20-30", "30-50", "> 50"]
        seg_colors = ["#fde7b3", "#10b981", "#fde7b3", "#fde7b3", "#f8b4c2"]
        accent = "#10b981"
    else:
        title = "FEAR & GREED · CNN"
        desc = "恐惧与贪婪指数"
        labels = ["0-24", "25-44", "45-55", "56-75", "76-100"]
        seg_colors = ["#f8b4c2", "#fde7b3", "#bfd3ff", "#eab308", "#f8b4c2"]
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
        now = f'<span style="background:{badge_bg};color:#fff;padding:5px 11px;border-radius:999px;font-size:13px;font-weight:900;">NOW</span>' if i == current_idx else ""
        trs += f"""
        <tr style="background:{bg};">
            <td style="color:{accent_color};font-weight:950;padding:10px;border-bottom:1px solid #eef2f7;">{rng}</td>
            <td style="font-weight:800;padding:10px;border-bottom:1px solid #eef2f7;">{emotion}</td>
            <td style="font-weight:700;padding:10px;border-bottom:1px solid #eef2f7;">{strategy}</td>
            <td style="text-align:right;padding:10px;border-bottom:1px solid #eef2f7;">{now}</td>
        </tr>
        """

    html = f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Helvetica Neue',Arial,sans-serif;">
      <div style="margin:18px 0 10px 0;font-size:21px;font-weight:950;color:#111827;">
        <span style="display:inline-block;width:52px;height:6px;background:{accent_color};border-radius:999px;margin-right:14px;vertical-align:middle;"></span>
        {title}
        <span style="color:#94a3b8;font-size:16px;margin-left:10px;">指数区间 · 市场情绪 · 定投策略</span>
      </div>
      <div style="background:#fff;border:1px solid #d7dde8;border-radius:18px;padding:14px 20px 12px 20px;margin-bottom:24px;box-shadow:0 2px 12px rgba(17,24,39,0.035);">
        <table style="width:100%;border-collapse:collapse;font-size:17px;">
          <thead>
            <tr>
              <th style="color:#64748b;text-align:left;padding:9px 10px;font-weight:900;border-bottom:1px solid #e5e7eb;">指数区间</th>
              <th style="color:#64748b;text-align:left;padding:9px 10px;font-weight:900;border-bottom:1px solid #e5e7eb;">市场情绪</th>
              <th style="color:#64748b;text-align:left;padding:9px 10px;font-weight:900;border-bottom:1px solid #e5e7eb;">定投策略</th>
              <th style="border-bottom:1px solid #e5e7eb;"></th>
            </tr>
          </thead>
          <tbody>{trs}</tbody>
        </table>
      </div>
    </div>
    """
    components.html(html, height=300, scrolling=False)


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
        height=420,
        margin=dict(l=10, r=10, t=30, b=10),
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
        height=330,
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
fg_value, fg_rating, fg_source, fg_hist = fetch_cnn_fear_greed(float(manual_fg))

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


# -----------------------------
# Top Metrics
# -----------------------------
render_meter_card(
    "vix",
    float(vix_value),
    vix_label,
    vix_strategy,
    vix_color,
    vix_pointer_pct(float(vix_value)),
    source="Yahoo Finance / CBOE VIX",
)

render_meter_card(
    "fg",
    float(fg_value),
    fg_label,
    fg_strategy,
    fg_color,
    fg_pointer_pct(float(fg_value)),
    source=fg_source,
)

strategy = combined_strategy(float(vix_value), float(fg_value))
st.markdown(
    f"""
<div class="strategy-box">
  <div class="strategy-title">◆ TODAY'S STRATEGY · 今日策略</div>
  <div class="strategy-main">{strategy}</div>
</div>
""",
    unsafe_allow_html=True,
)


# -----------------------------
# Playbooks
# -----------------------------
render_playbook("VIX PLAYBOOK", "#10b981", VIX_ROWS, vix_idx, yellow=False)
render_playbook("FEAR & GREED PLAYBOOK", "#eab308", FG_ROWS, fg_idx, yellow=True)


# -----------------------------
# Charts and correlations
# -----------------------------
st.markdown("### 市场走势与波动率")
index_return = pct_change_text(index_df)
vix_return = pct_change_text(vix_df)

c1, c2, c3, c4 = st.columns(4)
c1.metric(index_label, f"{index_df['Close'].iloc[-1]:,.2f}" if not index_df.empty else "N/A",
          f"{index_return:.2f}%" if index_return is not None else None)
c2.metric("VIX", f"{vix_value:.2f}" if vix_value else "N/A",
          f"{vix_return:.2f}%" if vix_return is not None else None)
c3.metric("CNN Fear & Greed", f"{fg_value:.0f}", fg_rating)
c4.metric("Auto refresh", f"{refresh}s" if refresh else "Off")

st.plotly_chart(build_price_chart(index_df, vix_df, index_label), use_container_width=True)

corr_df, corr_vix, corr_fg = compute_correlations(index_df, vix_df, fg_hist, rolling_window)

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

if corr_df is not None and not corr_df.empty:
    st.plotly_chart(build_corr_chart(corr_df), use_container_width=True)

with st.expander("查看原始相关性数据"):
    if corr_df is None or corr_df.empty:
        st.write("No correlation data available.")
    else:
        st.dataframe(corr_df.tail(120), use_container_width=True)


# -----------------------------
# Footer
# -----------------------------
st.markdown(
    """
<div class="small-note">
Data: Yahoo Finance via yfinance · CBOE VIX · CNN Fear & Greed unofficial endpoint/fallback manual input.
<br>
仅供参考，不构成投资建议。CNN Fear & Greed 没有稳定官方公开 API，如接口不可用会自动使用左侧手动 fallback 数值。
</div>
""",
    unsafe_allow_html=True,
)
