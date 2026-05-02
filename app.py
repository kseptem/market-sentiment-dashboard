from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
import yfinance as yf
from streamlit_autorefresh import st_autorefresh


# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Daily Market Pulse",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================
# CSS / UI theme
# =========================
st.markdown(
    """
<style>
:root {
    --ink: #111827;
    --muted: #667085;
    --line: #D8DEE9;
    --green: #10B981;
    --yellow: #EAB308;
    --orange: #F97316;
    --red: #E11D48;
    --blue: #3B82F6;
    --card: #FFFFFF;
    --soft: #F8FAFC;
}

.block-container {
    padding-top: 2.0rem;
    padding-bottom: 3rem;
    max-width: 1200px;
}

[data-testid="stSidebar"] {
    background: #F1F5F9;
}

.pill {
    display:inline-flex;
    align-items:center;
    gap:10px;
    background:#0F172A;
    color:white;
    padding:10px 22px;
    border-radius:999px;
    font-weight:900;
    letter-spacing:.04em;
    font-size:18px;
}

.date-pill {
    display:inline-flex;
    justify-content:center;
    align-items:center;
    border:2px solid #CBD5E1;
    background:#F8FAFC;
    color:#1F2937;
    padding:9px 22px;
    border-radius:999px;
    font-weight:700;
    font-size:18px;
    min-width:220px;
}

.hero-title {
    color:#0F172A;
    font-size:48px;
    line-height:1.08;
    font-weight:1000;
    margin:18px 0 6px 0;
}

.hero-subtitle {
    display:flex;
    align-items:center;
    gap:12px;
    color:#64748B;
    font-size:18px;
    margin-bottom:26px;
}

.accent-line {
    width:56px;
    height:7px;
    background:#10B981;
    border-radius:999px;
    display:inline-block;
}

.section-title {
    display:flex;
    align-items:center;
    gap:12px;
    color:#0F172A;
    font-size:25px;
    font-weight:1000;
    margin:24px 0 10px 0;
}

.section-line-green {width:48px;height:6px;background:#10B981;border-radius:999px;display:inline-block;}
.section-line-yellow {width:48px;height:6px;background:#EAB308;border-radius:999px;display:inline-block;}

.metric-card {
    border:2px solid #CBD5E1;
    background:#FFFFFF;
    border-radius:16px;
    padding:24px 28px 22px 28px;
    margin-bottom:22px;
    box-shadow:0 6px 20px rgba(15,23,42,.04);
}

.metric-card-top {
    display:grid;
    grid-template-columns: 1.2fr 1fr 1.1fr;
    align-items:center;
    gap:12px;
}

.metric-name {
    color:#0F172A;
    font-size:20px;
    font-weight:1000;
    letter-spacing:.03em;
}

.metric-desc {
    color:#64748B;
    font-size:15px;
    margin-top:4px;
}

.big-number {
    text-align:center;
    font-size:76px;
    line-height:1;
    font-weight:1000;
}

.status-pill {
    justify-self:end;
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:10px 18px;
    border-radius:999px;
    font-size:18px;
    font-weight:1000;
    border:2px solid currentColor;
    min-width:178px;
}

.bar-wrap {
    margin-top:22px;
}

.segment-bar {
    height:24px;
    display:grid;
    overflow:hidden;
    border-radius:4px;
    border:1px solid #E2E8F0;
    position:relative;
}

.pointer {
    position:absolute;
    top:-19px;
    width:0;
    height:0;
    border-left:11px solid transparent;
    border-right:11px solid transparent;
    border-top:18px solid var(--pointer-color);
    transform:translateX(-11px);
}

.axis-labels {
    display:grid;
    color:#64748B;
    font-size:15px;
    font-weight:800;
    margin-top:8px;
    text-align:center;
}

.playbook-card {
    border:2px solid #CBD5E1;
    background:#FFFFFF;
    border-radius:16px;
    padding:16px 22px;
    margin-bottom:24px;
    box-shadow:0 6px 20px rgba(15,23,42,.04);
}

.playbook-table {
    width:100%;
    border-collapse:collapse;
    font-size:18px;
}

.playbook-table th {
    text-align:left;
    color:#64748B;
    padding:9px 10px;
    border-bottom:1px solid #E5E7EB;
}

.playbook-table td {
    padding:10px 10px;
    border-bottom:1px solid #EEF2F7;
    color:#0F172A;
    font-weight:700;
}

.playbook-table tr.active {
    background:#ECFDF5;
}

.playbook-table tr.active-yellow {
    background:#FEF9C3;
}

.now-pill {
    float:right;
    background:#10B981;
    color:white;
    border-radius:999px;
    padding:5px 10px;
    font-size:13px;
    font-weight:1000;
}

.now-pill-yellow {
    float:right;
    background:#EAB308;
    color:white;
    border-radius:999px;
    padding:5px 10px;
    font-size:13px;
    font-weight:1000;
}

.strategy-box {
    border:2px solid #10B981;
    background:#ECFDF5;
    color:#0F172A;
    border-radius:16px;
    padding:18px 22px;
    margin:18px 0 26px 0;
}

.strategy-title {
    color:#059669;
    font-weight:1000;
    font-size:17px;
    letter-spacing:.04em;
}

.strategy-main {
    font-size:28px;
    font-weight:1000;
    margin-top:8px;
}

.small-note {
    color:#64748B;
    font-size:13px;
    margin-top:8px;
}

.kpi-grid {
    display:grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap:14px;
    margin: 12px 0 24px 0;
}

.kpi-box {
    background:#FFFFFF;
    border:1px solid #E2E8F0;
    border-radius:14px;
    padding:14px 16px;
    box-shadow:0 6px 18px rgba(15,23,42,.04);
}

.kpi-label {color:#64748B;font-size:13px;font-weight:800;}
.kpi-value {color:#0F172A;font-size:25px;font-weight:1000;margin-top:2px;}
.kpi-sub {color:#64748B;font-size:12px;margin-top:4px;}

@media (max-width: 900px) {
    .hero-title {font-size:36px;}
    .metric-card-top {grid-template-columns:1fr;}
    .big-number {text-align:left;font-size:64px;}
    .status-pill {justify-self:start;}
    .kpi-grid {grid-template-columns:1fr 1fr;}
}
</style>
""",
    unsafe_allow_html=True,
)


# =========================
# Data models / rules
# =========================
@dataclass
class Level:
    key: str
    cn: str
    en: str
    strategy: str
    color: str
    active_class: str = "active"


VIX_LEVELS = [
    (0, 12, Level("vix_lt12", "极度乐观", "EUPHORIA", "谨慎追高，保持警觉", "#F59E0B")),
    (12, 20, Level("vix_12_20", "正常波动", "NORMAL", "常规定投，保持节奏", "#10B981")),
    (20, 30, Level("vix_20_30", "恐惧上升", "FEAR RISING", "加大定投，分批买入", "#EAB308", "active-yellow")),
    (30, 50, Level("vix_30_50", "市场恐慌", "PANIC", "加倍定投，逢低布局", "#F97316", "active-yellow")),
    (50, 999, Level("vix_gt50", "极度恐慌", "EXTREME PANIC", "黄金机会，大胆抄底", "#E11D48", "active-yellow")),
]

FG_LEVELS = [
    (0, 25, Level("fg_0_24", "极度恐惧", "EXTREME FEAR", "黄金机会，加倍买入", "#E11D48", "active-yellow")),
    (25, 45, Level("fg_25_44", "恐惧", "FEAR", "加大定投，分批布局", "#F97316", "active-yellow")),
    (45, 56, Level("fg_45_55", "中性", "NEUTRAL", "常规定投，保持节奏", "#3B82F6")),
    (56, 76, Level("fg_56_75", "贪婪", "GREED", "谨慎追高，控制仓位", "#EAB308", "active-yellow")),
    (76, 101, Level("fg_76_100", "极度贪婪", "EXTREME GREED", "警惕回调，部分止盈", "#E11D48", "active-yellow")),
]

INDEX_MAP = {
    "S&P 500 (^GSPC)": "^GSPC",
    "Nasdaq 100 (^NDX)": "^NDX",
    "Nasdaq Composite (^IXIC)": "^IXIC",
    "Dow Jones (^DJI)": "^DJI",
    "SPY ETF": "SPY",
    "QQQ ETF": "QQQ",
}

PERIOD_OPTIONS = ["5d", "1mo", "3mo", "6mo", "1y", "2y", "5y"]
INTERVAL_OPTIONS = ["5m", "15m", "30m", "60m", "1d"]


def classify(value: float, levels: list[tuple[float, float, Level]]) -> Level:
    for lo, hi, level in levels:
        if lo <= value < hi:
            return level
    return levels[-1][2]


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# =========================
# Fetchers
# =========================
@st.cache_data(ttl=60)
def fetch_price_history(ticker: str, period: str, interval: str) -> pd.DataFrame:
    df = yf.download(ticker, period=period, interval=interval, progress=False, auto_adjust=False)
    if df.empty:
        return pd.DataFrame()
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.reset_index()
    date_col = "Datetime" if "Datetime" in df.columns else "Date"
    df = df.rename(columns={date_col: "time"})
    return df


@st.cache_data(ttl=60)
def fetch_latest_close(ticker: str) -> Optional[float]:
    df = fetch_price_history(ticker, "5d", "5m")
    if df.empty or "Close" not in df:
        df = fetch_price_history(ticker, "1mo", "1d")
    if df.empty or "Close" not in df:
        return None
    close = df["Close"].dropna()
    if close.empty:
        return None
    return float(close.iloc[-1])


@st.cache_data(ttl=300)
def fetch_cnn_fear_greed() -> Tuple[Optional[float], Optional[str], Optional[pd.DataFrame], str]:
    """Best-effort CNN Fear & Greed fetch.

    CNN does not provide a stable official public API. This endpoint may change.
    """
    urls = [
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata",
        "https://production.dataviz.cnn.io/index/fearandgreed/graphdata/2020-09-19",
    ]
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "application/json,text/plain,*/*",
        "Referer": "https://www.cnn.com/markets/fear-and-greed",
    }

    last_error = ""
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=12)
            r.raise_for_status()
            data = r.json()

            fg = data.get("fear_and_greed") or data.get("fear_and_greed_historical", {})
            score = fg.get("score") if isinstance(fg, dict) else None
            rating = fg.get("rating") if isinstance(fg, dict) else None

            hist_raw = data.get("fear_and_greed_historical", {}).get("data", [])
            hist = []
            for item in hist_raw:
                x = item.get("x")
                y = item.get("y")
                if x is None or y is None:
                    continue
                # CNN x is usually epoch milliseconds
                ts = pd.to_datetime(int(x), unit="ms", utc=True, errors="coerce")
                if pd.notna(ts):
                    hist.append({"time": ts, "FearGreed": float(y)})
            hist_df = pd.DataFrame(hist)
            if not hist_df.empty:
                hist_df = hist_df.sort_values("time")

            return (float(score) if score is not None else None), rating, hist_df, "CNN unofficial endpoint"
        except Exception as e:  # noqa: BLE001
            last_error = str(e)

    return None, None, None, f"Manual fallback: {last_error[:120]}"


# =========================
# UI helpers
# =========================
def render_header() -> None:
    today = datetime.now().strftime("%Y · %m · %d / %a")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="pill">◆ DAILY MARKET PULSE</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div style="text-align:right"><span class="date-pill">{today}</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="hero-title">今日美股情绪观察</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle"><span class="accent-line"></span>'
        '<b style="color:#059669">S&amp;P 500 · VIX &amp; CNN FEAR &amp; GREED</b>'
        '<span>标普500 · 波动率指数 · 恐惧与贪婪指数</span></div>',
        unsafe_allow_html=True,
    )


def vix_pointer_pct(v: float) -> float:
    # Custom visual scale: 0-60 maps to 0-100, cap at 60 for display.
    return clamp(v / 60 * 100, 0, 100)


def fg_pointer_pct(v: float) -> float:
    return clamp(v, 0, 100)


def render_segment_bar(kind: str, value: float, color: str) -> None:
    if kind == "vix":
        # segments: <12, 12-20, 20-30, 30-50, >50 on display range 0-60
        widths = [20, 13.333, 16.667, 33.333, 16.667]
        colors = ["#FDE7B2", "#10B981", "#FDE7B2", "#FDE7B2", "#F7B6C2"]
        labels = ["< 12", "12-20", "20-30", "30-50", "> 50"]
        pct = vix_pointer_pct(value)
    else:
        widths = [25, 20, 11, 20, 24]
        colors = ["#F7B6C2", "#FDE7B2", "#BBD3FF", "#EAB308", "#F7B6C2"]
        labels = ["0-24", "25-44", "45-55", "56-75", "76-100"]
        pct = fg_pointer_pct(value)

    grid_cols = " ".join([f"{w}fr" for w in widths])
    segs = "".join([f'<div style="background:{c};"></div>' for c in colors])
    label_cols = grid_cols
    labs = "".join([f"<div>{x}</div>" for x in labels])
    html = f"""
    <div class="bar-wrap" style="--pointer-color:{color}; position:relative; padding-top:18px;">
        <div class="pointer" style="left:{pct}%;"></div>
        <div class="segment-bar" style="grid-template-columns:{grid_cols};">{segs}</div>
        <div class="axis-labels" style="grid-template-columns:{label_cols};">{labs}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def render_metric_card(title: str, subtitle: str, value: float, level: Level, kind: str) -> None:
    value_str = f"{value:.0f}"
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-card-top">
                <div>
                    <div style="width:48px;height:6px;background:{level.color};border-radius:999px;margin-bottom:10px;"></div>
                    <div class="metric-name">{title}</div>
                    <div class="metric-desc">{subtitle}</div>
                </div>
                <div class="big-number" style="color:{level.color};">{value_str}</div>
                <div class="status-pill" style="color:{level.color}; background:{level.color}12;">
                    {level.cn}&nbsp;&nbsp;<span style="font-size:15px;">{level.en}</span>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )
    render_segment_bar(kind, value, level.color)
    st.markdown("</div>", unsafe_allow_html=True)


def render_playbook(kind: str, current_value: float) -> None:
    if kind == "vix":
        title = '<span class="section-line-green"></span> VIX PLAYBOOK <span style="font-size:16px;color:#64748B;font-weight:500;">VIX 区间 · 市场情绪 · 定投策略</span>'
        levels = VIX_LEVELS
        rows = [
            ("< 12", "极度乐观", "谨慎追高，保持警觉"),
            ("12 — 20", "正常区间", "常规定投，保持节奏"),
            ("20 — 30", "恐惧上升", "加大定投，分批买入"),
            ("30 — 50", "市场恐慌", "加倍定投，逢低布局"),
            ("> 50", "极度恐慌", "黄金机会，大胆抄底"),
        ]
        level = classify(current_value, levels)
        active_class = level.active_class
        now_class = "now-pill" if active_class == "active" else "now-pill-yellow"
    else:
        title = '<span class="section-line-yellow"></span> FEAR &amp; GREED PLAYBOOK <span style="font-size:16px;color:#64748B;font-weight:500;">指数区间 · 市场情绪 · 定投策略</span>'
        levels = FG_LEVELS
        rows = [
            ("0 — 24", "极度恐惧", "黄金机会，加倍买入"),
            ("25 — 44", "恐惧", "加大定投，分批布局"),
            ("45 — 55", "中性", "常规定投，保持节奏"),
            ("56 — 75", "贪婪", "谨慎追高，控制仓位"),
            ("76 — 100", "极度贪婪", "警惕回调，部分止盈"),
        ]
        level = classify(current_value, levels)
        active_class = level.active_class
        now_class = "now-pill" if active_class == "active" else "now-pill-yellow"

    html_rows = ""
    for idx, (r, mood, strategy) in enumerate(rows):
        lo, hi, lv = levels[idx]
        active = lo <= current_value < hi
        tr_class = active_class if active else ""
        now = f'<span class="{now_class}">NOW</span>' if active else ""
        color = lv.color
        html_rows += f"""
        <tr class="{tr_class}">
            <td style="color:{color};font-weight:1000;">{r}</td>
            <td>{mood}</td>
            <td>{strategy}{now}</td>
        </tr>
        """

    st.markdown(
        f"""
        <div class="section-title">{title}</div>
        <div class="playbook-card">
            <table class="playbook-table">
                <thead><tr><th>指数区间</th><th>市场情绪</th><th>定投策略</th></tr></thead>
                <tbody>{html_rows}</tbody>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_strategy(vix: float, fg: float, index_return_pct: Optional[float]) -> None:
    vix_level = classify(vix, VIX_LEVELS)
    fg_level = classify(fg, FG_LEVELS)

    # Simple rule-based strategy. Conservative by design.
    if vix >= 30 or fg <= 24:
        main = "加大定投 · 分批布局 · 避免一次性梭哈"
    elif vix >= 20 or fg <= 44:
        main = "正常偏进攻 · 逢低分批 · 保留现金"
    elif fg >= 76 and vix < 20:
        main = "降低追高 · 控制仓位 · 部分止盈"
    elif fg >= 56 and vix < 20:
        main = "减半定投 · 谨慎追高 · 控制仓位"
    else:
        main = "常规定投 · 保持节奏 · 不做情绪化交易"

    if index_return_pct is not None:
        if index_return_pct > 2 and fg >= 56:
            main += " · 大涨后不追"
        elif index_return_pct < -2 and vix < 30:
            main += " · 回调可分批"

    st.markdown(
        f"""
        <div class="strategy-box">
            <div class="strategy-title">◆ TODAY'S STRATEGY · 今日策略</div>
            <div class="strategy-main">{main}</div>
            <div class="small-note">当前状态：VIX = {vix:.1f} / {vix_level.cn}；Fear &amp; Greed = {fg:.0f} / {fg_level.cn}。仅供研究，不构成投资建议。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpis(index_name: str, latest: Optional[float], idx_ret: Optional[float], vix: Optional[float], fg: float, fg_source: str) -> None:
    idx_ret_str = "N/A" if idx_ret is None else f"{idx_ret:+.2f}%"
    latest_str = "N/A" if latest is None else f"{latest:,.2f}"
    vix_str = "N/A" if vix is None else f"{vix:.2f}"
    html = f"""
    <div class="kpi-grid">
        <div class="kpi-box"><div class="kpi-label">Market Index</div><div class="kpi-value">{latest_str}</div><div class="kpi-sub">{index_name}</div></div>
        <div class="kpi-box"><div class="kpi-label">Window Return</div><div class="kpi-value">{idx_ret_str}</div><div class="kpi-sub">Selected period</div></div>
        <div class="kpi-box"><div class="kpi-label">VIX</div><div class="kpi-value">{vix_str}</div><div class="kpi-sub">Yahoo Finance / CBOE symbol</div></div>
        <div class="kpi-box"><div class="kpi-label">CNN Fear & Greed</div><div class="kpi-value">{fg:.0f}</div><div class="kpi-sub">{fg_source}</div></div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def make_price_chart(index_df: pd.DataFrame, vix_df: pd.DataFrame, index_label: str) -> go.Figure:
    fig = go.Figure()
    if not index_df.empty:
        fig.add_trace(
            go.Scatter(
                x=index_df["time"],
                y=index_df["Close"],
                mode="lines",
                name=index_label,
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
        title="Index vs VIX",
        height=430,
        margin=dict(l=20, r=20, t=55, b=20),
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title=index_label),
        yaxis2=dict(title="VIX", overlaying="y", side="right", showgrid=False),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    return fig


def compute_return_pct(df: pd.DataFrame) -> Optional[float]:
    if df.empty or "Close" not in df:
        return None
    close = df["Close"].dropna()
    if len(close) < 2:
        return None
    return float((close.iloc[-1] / close.iloc[0] - 1) * 100)


def compute_correlations(index_df: pd.DataFrame, vix_df: pd.DataFrame, fg_hist: Optional[pd.DataFrame], rolling_window: int):
    if index_df.empty or vix_df.empty:
        return pd.DataFrame(), None, None

    def clean_price(df, out_col):
        x = df[["time", "Close"]].copy()
        x["time"] = pd.to_datetime(x["time"], utc=True, errors="coerce")
        x = x.dropna(subset=["time", "Close"])
        x = x.rename(columns={"Close": out_col})
        x = x.groupby("time", as_index=False)[out_col].last()
        return x.sort_values("time")

    a = clean_price(index_df, "Index")
    b = clean_price(vix_df, "VIX")

    merged = pd.merge_asof(
        a.sort_values("time"),
        b.sort_values("time"),
        on="time",
        direction="nearest",
        suffixes=("", "_vix")
    )

    merged["IndexRet"] = merged["Index"].pct_change()
    merged["VIXChg"] = merged["VIX"].pct_change()

    corr_vix = None
    if merged[["IndexRet", "VIXChg"]].dropna().shape[0] >= 5:
        corr_vix = float(merged["IndexRet"].corr(merged["VIXChg"]))
        merged["RollingCorr_Index_VIX"] = merged["IndexRet"].rolling(rolling_window).corr(merged["VIXChg"])

    corr_fg = None
    if fg_hist is not None and not fg_hist.empty and "FearGreed" in fg_hist.columns:
        fg = fg_hist[["time", "FearGreed"]].copy()
        fg["time"] = pd.to_datetime(fg["time"], utc=True, errors="coerce")
        fg = fg.dropna(subset=["time", "FearGreed"])
        fg = fg.groupby("time", as_index=False)["FearGreed"].last()
        fg = fg.sort_values("time")

        if "FearGreed" in merged.columns:
            merged = merged.drop(columns=["FearGreed"])

        merged = pd.merge_asof(
            merged.sort_values("time"),
            fg,
            on="time",
            direction="nearest",
            suffixes=("", "_fg")
        )

        merged["FGChg"] = merged["FearGreed"].diff()

        if merged[["IndexRet", "FGChg"]].dropna().shape[0] >= 5:
            corr_fg = float(merged["IndexRet"].corr(merged["FGChg"]))
            merged["RollingCorr_Index_FG"] = merged["IndexRet"].rolling(rolling_window).corr(merged["FGChg"])

    return merged, corr_vix, corr_fg

def render_corr_chart(corr_df: pd.DataFrame) -> None:
    if corr_df.empty or "RollingCorr_Index_VIX" not in corr_df:
        st.info("Correlation data is not enough yet. Try a longer history window, such as 6mo or 1y.")
        return
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=corr_df["time"], y=corr_df["RollingCorr_Index_VIX"], mode="lines", name="Index vs VIX rolling corr"))
    if "RollingCorr_Index_FG" in corr_df.columns:
        fig.add_trace(go.Scatter(x=corr_df["time"], y=corr_df["RollingCorr_Index_FG"], mode="lines", name="Index vs Fear&Greed rolling corr"))
    fig.add_hline(y=0, line_dash="dash")
    fig.update_layout(
        title="Rolling Correlation",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified",
        yaxis=dict(range=[-1, 1]),
        paper_bgcolor="white",
        plot_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)


# =========================
# Sidebar
# =========================
with st.sidebar:
    st.markdown("### Dashboard Settings")
    index_name = st.selectbox("Market index", list(INDEX_MAP.keys()), index=0)
    period = st.selectbox("History window", PERIOD_OPTIONS, index=4)
    interval = st.selectbox("Interval", INTERVAL_OPTIONS, index=4)
    rolling_window = st.slider("Rolling correlation window", 5, 120, 30)
    refresh = st.slider("Auto refresh seconds", 30, 600, 120, step=30)
    manual_fg = st.number_input("Manual Fear & Greed fallback", min_value=0, max_value=100, value=50, step=1)
    st.caption("If CNN endpoint fails, this manual value will be used and clearly marked.")

st_autorefresh(interval=refresh * 1000, key="market_pulse_refresh")


# =========================
# Main app
# =========================
render_header()

index_ticker = INDEX_MAP[index_name]
index_df = fetch_price_history(index_ticker, period, interval)
vix_df = fetch_price_history("^VIX", period, interval)
latest_index = None if index_df.empty else float(index_df["Close"].dropna().iloc[-1])
index_return_pct = compute_return_pct(index_df)
latest_vix = fetch_latest_close("^VIX")

cnn_score, cnn_rating, fg_hist, fg_source = fetch_cnn_fear_greed()
if cnn_score is None:
    fg_value = float(manual_fg)
    fg_label = "Manual fallback"
else:
    fg_value = float(cnn_score)
    fg_label = cnn_rating or "CNN"

if latest_vix is None:
    st.error("Failed to fetch VIX from Yahoo Finance. Please check network access or try again later.")
    latest_vix = 20.0

render_kpis(index_name, latest_index, index_return_pct, latest_vix, fg_value, fg_source)

vix_level = classify(latest_vix, VIX_LEVELS)
fg_level = classify(fg_value, FG_LEVELS)
render_metric_card("VIX · S&P 500", "波动率指数", latest_vix, vix_level, "vix")
render_metric_card("FEAR & GREED · CNN", "恐惧与贪婪指数", fg_value, fg_level, "fg")

render_playbook("vix", latest_vix)
render_playbook("fg", fg_value)
render_strategy(latest_vix, fg_value, index_return_pct)

st.markdown("### Market Trend")
st.plotly_chart(make_price_chart(index_df, vix_df, index_name), use_container_width=True)

corr_df, corr_vix, corr_fg = compute_correlations(index_df, vix_df, fg_hist, rolling_window)

c1, c2 = st.columns(2)
with c1:
    st.metric("Correlation: Index return vs VIX change", "N/A" if corr_vix is None else f"{corr_vix:.3f}")
with c2:
    st.metric("Correlation: Index return vs Fear & Greed change", "N/A" if corr_fg is None else f"{corr_fg:.3f}")

render_corr_chart(corr_df)

with st.expander("Data status / debug"):
    st.write({
        "index": index_name,
        "index_ticker": index_ticker,
        "index_rows": int(len(index_df)),
        "vix_rows": int(len(vix_df)),
        "cnn_score": cnn_score,
        "cnn_rating": cnn_rating,
        "fear_greed_source": fg_source,
        "fear_greed_history_rows": 0 if fg_hist is None else int(len(fg_hist)),
        "last_refresh_utc": datetime.now(timezone.utc).isoformat(),
    })
    if fg_hist is not None and not fg_hist.empty:
        st.dataframe(fg_hist.tail(10), use_container_width=True)

st.caption("Data: Yahoo Finance via yfinance; VIX symbol ^VIX; CNN Fear & Greed via unofficial endpoint/fallback. For research only, not investment advice.")
