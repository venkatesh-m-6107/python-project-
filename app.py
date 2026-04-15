import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import warnings

warnings.filterwarnings("ignore")

# 1. PAGE CONFIGURATION
st.set_page_config(
    page_title="Pro-Sports Data Engine",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 2. CUSTOM CSS (Glass-morphism & Dark Theme)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Sans:wght@300;400;500;600&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: linear-gradient(135deg, #0f0c29 0%, #141e30 50%, #0f0c29 100%); color: #e8e8e8; }
.metric-card {
    background: linear-gradient(145deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; padding: 20px; text-align: center; backdrop-filter: blur(10px);
}
.metric-label { font-size: 12px; letter-spacing: 2px; text-transform: uppercase; color: #9ca3c8; }
.metric-value { font-family: 'Bebas Neue', sans-serif; font-size: 42px; color: #7ee8fa; }
.section-header {
    font-family: 'Bebas Neue', sans-serif; font-size: 28px; letter-spacing: 3px; color: #7ee8fa;
    border-left: 4px solid #ee7752; padding-left: 14px; margin: 30px 0;
}
.hero {
    background: linear-gradient(90deg, #ee7752, #e73c7e, #23a6d5, #23d5ab);
    background-size: 300% 300%; animation: gradientShift 6s ease infinite;
    border-radius: 20px; padding: 40px; margin-bottom: 25px;
}
@keyframes gradientShift { 0% {background-position:0% 50%} 50% {background-position:100% 50%} 100% {background-position:0% 50%} }
</style>
""", unsafe_allow_html=True)

# ─── CHART THEME ────────────────────────────────────────────────────────────────
CHART_BG       = "rgba(15, 12, 41, 0)"          # fully transparent
PAPER_BG       = "rgba(20, 30, 48, 0.55)"        # subtle frosted panel
GRID_COLOR     = "rgba(255, 255, 255, 0.07)"
AXIS_COLOR     = "rgba(255, 255, 255, 0.25)"
FONT_COLOR     = "#d0d6f5"
FONT_FAMILY    = "DM Sans, sans-serif"
ACCENT_CYAN    = "#7ee8fa"
ACCENT_ORANGE  = "#ee7752"
ACCENT_PINK    = "#e73c7e"
ACCENT_TEAL    = "#23d5ab"
ACCENT_BLUE    = "#23a6d5"

# Gradient-style sequential palette for histogram bars
HIST_COLORSCALE = [
    [0.0,  "#1a3a5c"],
    [0.25, "#1b6ca8"],
    [0.5,  "#23a6d5"],
    [0.75, "#7ee8fa"],
    [1.0,  "#c8f6ff"],
]

def base_layout(title: str = "") -> dict:
    """Returns a shared Plotly layout dict for all charts."""
    return dict(
        title=dict(
            text=title,
            font=dict(family=FONT_FAMILY, size=17, color=ACCENT_CYAN),
            x=0.03, xanchor="left",
        ),
        plot_bgcolor=CHART_BG,
        paper_bgcolor=PAPER_BG,
        font=dict(family=FONT_FAMILY, color=FONT_COLOR, size=13),
        margin=dict(l=60, r=30, t=60, b=60),
        hoverlabel=dict(
            bgcolor="rgba(20, 30, 48, 0.92)",
            bordercolor=ACCENT_CYAN,
            font=dict(family=FONT_FAMILY, size=13, color="#ffffff"),
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=12, color=FONT_COLOR),
            title_font=dict(size=13, color=FONT_COLOR),
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=GRID_COLOR,
            linecolor=AXIS_COLOR,
            tickcolor=AXIS_COLOR,
            tickfont=dict(size=12, color=FONT_COLOR),
            title_font=dict(size=13, color=FONT_COLOR),
            zeroline=False,
        ),
        legend=dict(
            bgcolor="rgba(255,255,255,0.04)",
            bordercolor="rgba(255,255,255,0.12)",
            borderwidth=1,
            font=dict(size=12, color=FONT_COLOR),
        ),
    )

def make_histogram(df, col):
    """
    Styled histogram with per-bar color gradient and a smooth KDE overlay line.
    """
    series = df[col].dropna()

    # Build histogram manually so we can apply per-bar coloring
    counts, bin_edges = np.histogram(series, bins=30)
    bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2

    # Normalize counts → 0-1 for color mapping
    norm = counts / counts.max() if counts.max() > 0 else counts

    # Map normalized value to a cyan gradient
    def lerp_color(t):
        # Interpolate between dark-blue and bright-cyan
        r = int(26  + t * (200 - 26))
        g = int(58  + t * (246 - 58))
        b = int(92  + t * (255 - 92))
        return f"rgb({r},{g},{b})"

    bar_colors = [lerp_color(float(v)) for v in norm]

    fig = go.Figure()

    # Bars
    fig.add_trace(go.Bar(
        x=bin_centers,
        y=counts,
        width=(bin_edges[1] - bin_edges[0]) * 0.88,
        marker=dict(
            color=bar_colors,
            line=dict(width=0),
            opacity=0.90,
        ),
        hovertemplate=f"<b>{col}</b>: %{{x:.2f}}<br>Count: %{{y}}<extra></extra>",
        name=col,
    ))

    # KDE smooth curve overlay
    try:
        from scipy.stats import gaussian_kde
        kde = gaussian_kde(series, bw_method="scott")
        x_line = np.linspace(series.min(), series.max(), 300)
        kde_vals = kde(x_line) * len(series) * (bin_edges[1] - bin_edges[0])
        fig.add_trace(go.Scatter(
            x=x_line, y=kde_vals,
            mode="lines",
            line=dict(color=ACCENT_ORANGE, width=2.5, dash="solid"),
            name="Density",
            hoverinfo="skip",
        ))
    except ImportError:
        pass  # scipy not available — skip KDE

    layout = base_layout(f"Distribution of  {col}")
    layout["bargap"] = 0.06
    layout["xaxis"]["title"] = dict(text=col, font=dict(size=13, color=FONT_COLOR))
    layout["yaxis"]["title"] = dict(text="Count", font=dict(size=13, color=FONT_COLOR))
    layout["showlegend"] = True
    fig.update_layout(**layout)
    return fig


def make_scatter(df, x_col, y_col, hover_col):
    """
    Styled scatter plot with glow-effect markers, trendline, and rich tooltips.
    """
    series_x = df[x_col].dropna()
    series_y = df[y_col].dropna()
    common_idx = series_x.index.intersection(series_y.index)
    plot_df = df.loc[common_idx].copy()

    # Color-encode points by y-value magnitude
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=plot_df[x_col],
        y=plot_df[y_col],
        mode="markers",
        marker=dict(
            size=9,
            color=plot_df[y_col],
            colorscale=[
                [0.0,  "#1a3a5c"],
                [0.35, "#23a6d5"],
                [0.65, "#7ee8fa"],
                [0.85, "#ee7752"],
                [1.0,  "#e73c7e"],
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text=y_col, font=dict(size=12, color=FONT_COLOR)),
                tickfont=dict(size=11, color=FONT_COLOR),
                outlinewidth=0,
                thickness=12,
                len=0.75,
            ),
            opacity=0.85,
            line=dict(width=0.5, color="rgba(255,255,255,0.25)"),
        ),
        customdata=plot_df[[hover_col]],
        hovertemplate=(
            f"<b>%{{customdata[0]}}</b><br>"
            f"{x_col}: %{{x:.2f}}<br>"
            f"{y_col}: %{{y:.2f}}"
            "<extra></extra>"
        ),
        name="Athletes",
    ))

    # Linear trendline
    try:
        mask = plot_df[[x_col, y_col]].notna().all(axis=1)
        x_vals = plot_df.loc[mask, x_col].values
        y_vals = plot_df.loc[mask, y_col].values
        if len(x_vals) >= 2:
            coeffs = np.polyfit(x_vals, y_vals, 1)
            x_trend = np.linspace(x_vals.min(), x_vals.max(), 200)
            y_trend = np.polyval(coeffs, x_trend)
            fig.add_trace(go.Scatter(
                x=x_trend, y=y_trend,
                mode="lines",
                line=dict(color=ACCENT_TEAL, width=2, dash="dot"),
                name="Trend",
                hoverinfo="skip",
            ))
    except Exception:
        pass

    layout = base_layout(f"{x_col}  vs  {y_col}")
    layout["xaxis"]["title"] = dict(text=x_col, font=dict(size=13, color=FONT_COLOR))
    layout["yaxis"]["title"] = dict(text=y_col, font=dict(size=13, color=FONT_COLOR))
    fig.update_layout(**layout)
    return fig


# 3. AUTOMATIC DATA LOADING ENGINE
@st.cache_data
def load_local_csvs():
    """Scans the current folder for CSV files and identifies the sport type."""
    data_map = {}
    for f in os.listdir('.'):
        if f.lower().endswith('.csv'):
            try:
                df = pd.read_csv(f)
                df.columns = [c.strip() for c in df.columns]
                cols = [c.lower() for c in df.columns]
                if any(x in cols for x in ['pts', 'ppg', 'nba']):
                    data_map[f] = {"df": df, "type": "NBA"}
                elif any(x in cols for x in ['overall', 'club', 'fifa']):
                    data_map[f] = {"df": df, "type": "FIFA"}
                else:
                    data_map[f] = {"df": df, "type": "General Sports"}
            except:
                continue
    return data_map

# 4. INITIALIZE APP
found_files = load_local_csvs()

# 5. SIDEBAR CONTROLS
with st.sidebar:
    st.markdown("<h2 style='text-align:center; color:#7ee8fa;'>🏆 SPORTS ANALYTICS</h2>", unsafe_allow_html=True)
    st.write("---")

    if not found_files:
        st.warning("No CSV files found in the folder. Please add a sports dataset CSV to the directory.")
        selected_file = None
    else:
        selected_file = st.selectbox("📂 Detected Datasets", options=list(found_files.keys()))

# 6. MAIN DASHBOARD LOGIC
st.markdown("""<div class="hero"><h1>PRO-SPORTS PERFORMANCE ENGINE</h1>
<p>Automated Insight Delivery for Professional Athletics</p></div>""", unsafe_allow_html=True)

if selected_file:
    active_df = found_files[selected_file]["df"]
    sport_type = found_files[selected_file]["type"]

    st.info(f"Currently Analyzing: **{selected_file}** ({sport_type} Dataset)")

    # 7. KPI METRICS
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Data Rows</div><div class="metric-value">{len(active_df):,}</div></div>', unsafe_allow_html=True)
    with m2:
        num_cols = len(active_df.columns)
        st.markdown(f'<div class="metric-card"><div class="metric-label">Attributes</div><div class="metric-value">{num_cols}</div></div>', unsafe_allow_html=True)
    with m3:
        name_col = next((c for c in active_df.columns if 'name' in c.lower() or 'player' in c.lower()), active_df.columns[0])
        st.markdown(f'<div class="metric-card"><div class="metric-label">Unique Athletes</div><div class="metric-value">{active_df[name_col].nunique()}</div></div>', unsafe_allow_html=True)
    with m4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Missing Data</div><div class="metric-value">{active_df.isnull().sum().sum()}</div></div>', unsafe_allow_html=True)

    # 8. ANALYTICS TABS
    st.markdown('<div class="section-header">DATA VISUALIZATION INTERFACE</div>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["📊 Distribution Analysis", "📈 Correlation Explorer"])

    num_cols_only = active_df.select_dtypes(include=[np.number]).columns

    with t1:
        if not num_cols_only.empty:
            sel_col = st.selectbox("Select Metric to View Distribution", num_cols_only)
            fig1 = make_histogram(active_df, sel_col)
            st.plotly_chart(fig1, use_container_width=True)

    with t2:
        if len(num_cols_only) >= 2:
            c1, c2 = st.columns(2)
            with c1: x_axis = st.selectbox("X-Axis", num_cols_only, index=0)
            with c2: y_axis = st.selectbox("Y-Axis", num_cols_only, index=1)

            fig2 = make_scatter(active_df, x_axis, y_axis, name_col)
            st.plotly_chart(fig2, use_container_width=True)

    # 9. RAW DATA VIEW
    with st.expander("📋 Data Inspection Table"):
        st.dataframe(active_df.head(500), use_container_width=True)

else:
    st.header("Waiting for data...")
    st.write("Place your CSV files in the same directory as this script and refresh the page.")