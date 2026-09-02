"""
Praxis Design System
====================
Single source of truth for all visual tokens, CSS, and HTML component builders.
No styling exists in any other file — all components import from here.

Design principles:
- Clean white/light-neutral canvas (enterprise, not AI-gimmick)
- Deep navy primary text (#0F1117)
- Praxis purple accent (#6B21A8) used sparingly
- Inter font — strong typographic hierarchy
- Thin 1px borders, subtle shadows
- Information density before decoration
"""

# ─── Full CSS design system ──────────────────────────────────────────────────

PRAXIS_CSS = """
<style>
/* ─── Google Fonts ─────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ─── Reset & Base ─────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.stApp {
    background-color: #F8F9FB !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #0F1117 !important;
    -webkit-font-smoothing: antialiased;
}

/* ─── Hide Streamlit chrome ─────────────────────────────────────── */
[data-testid="stHeader"]  { display: none !important; }
.stDeployButton           { display: none !important; }
#MainMenu                 { visibility: hidden !important; }
footer                    { visibility: hidden !important; }

/* ─── Main content area ─────────────────────────────────────────── */
.main .block-container {
    max-width: 1280px !important;
    padding: 0 2rem 4rem !important;
    margin: 0 auto !important;
    background: transparent !important;
}

/* ─── Sidebar ───────────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
    width: 240px !important;
}
[data-testid="stSidebarNav"]          { display: none !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] .block-container  { padding: 0 !important; }
[data-testid="stSidebar"] section > div     { padding: 0 !important; }

/* ─── Radio buttons (sidebar nav) ───────────────────────────────── */
.stRadio > label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin: 0 !important;
    padding: 0.875rem 1.25rem 0.375rem !important;
    display: block !important;
}
div[data-testid="stRadio"] [data-testid="stMarkdownContainer"] p {
    font-size: 0.875rem !important;
    color: #374151 !important;
    font-weight: 400 !important;
}
div[data-testid="stRadio"] > div > label {
    padding: 0.5rem 1.25rem !important;
    cursor: pointer !important;
    border-radius: 0 !important;
    transition: background 0.1s !important;
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
}
div[data-testid="stRadio"] > div > label:hover {
    background: #F3F4F6 !important;
}

/* ─── Tabs ──────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #E5E7EB !important;
    gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #6B7280 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.625rem 1.125rem !important;
    margin-bottom: -1px !important;
    transition: color 0.15s, border-color 0.15s !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em !important;
}
.stTabs [aria-selected="true"] {
    color: #0F1117 !important;
    border-bottom-color: #6B21A8 !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #374151 !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0 !important; }

/* ─── Buttons ───────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border-radius: 6px !important;
    padding: 0.5rem 1rem !important;
    height: auto !important;
    border: 1px solid #D1D5DB !important;
    background: #FFFFFF !important;
    color: #374151 !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
    letter-spacing: -0.01em !important;
}
.stButton > button:hover {
    background: #F9FAFB !important;
    border-color: #9CA3AF !important;
}
.stButton > button[kind="primary"] {
    background: #6B21A8 !important;
    border-color: #6B21A8 !important;
    color: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(107,33,168,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #581C87 !important;
    border-color: #581C87 !important;
}

/* ─── Selectbox / Radio ─────────────────────────────────────────── */
.stSelectbox > div > div {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: 6px !important;
    border-color: #D1D5DB !important;
}

/* ─── Metrics ───────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    padding: 1rem 1.25rem !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.6875rem !important;
    font-weight: 600 !important;
    color: #6B7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #0F1117 !important;
    letter-spacing: -0.02em !important;
}

/* ─── Expander ──────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
    margin-bottom: 0.75rem !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    padding: 0.875rem 1rem !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary:hover { background: #F9FAFB !important; }
[data-testid="stExpander"] > div > div   { padding: 0 1rem 1rem !important; }

/* ─── Info/warning/error states ─────────────────────────────────── */
.stAlert {
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    font-family: 'Inter', sans-serif !important;
}

/* ─── Code blocks ───────────────────────────────────────────────── */
code, .stCode {
    font-size: 0.8125rem !important;
    border-radius: 4px !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace !important;
}

/* ─── Horizontal rule ───────────────────────────────────────────── */
hr { border-color: #E5E7EB !important; margin: 1.5rem 0 !important; }

/* ─── Spinner ───────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #6B21A8 !important; }

/* ================================================================ */
/* PRAXIS COMPONENT CLASSES                                         */
/* ================================================================ */

/* ─── Application shell ─────────────────────────────────────────── */
.prx-app-header {
    position: sticky; top: 0; z-index: 100;
    background: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    padding: 0 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    margin: 0 -2rem 1.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.prx-wordmark {
    font-size: 1.125rem; font-weight: 700;
    color: #0F1117; letter-spacing: -0.03em;
    display: flex; align-items: center; gap: 0.375rem;
}
.prx-wordmark span { color: #6B21A8; }
.prx-wordmark-sub {
    font-size: 0.6875rem; font-weight: 400;
    color: #9CA3AF; letter-spacing: 0.01em;
    margin-left: 0.5rem; padding-left: 0.5rem;
    border-left: 1px solid #E5E7EB;
}
.prx-header-ctx {
    display: flex; align-items: center; gap: 1rem;
}
.prx-ctx-item {
    font-size: 0.75rem; color: #6B7280;
    display: flex; align-items: center; gap: 0.25rem;
}
.prx-ctx-item b { color: #374151; font-weight: 600; }
.prx-status-dot {
    width: 7px; height: 7px; border-radius: 50%;
    display: inline-block; flex-shrink: 0;
}
.prx-status-dot.green  { background: #16A34A; }
.prx-status-dot.amber  { background: #D97706; }
.prx-status-dot.red    { background: #DC2626; }
.prx-status-dot.purple { background: #6B21A8; }

/* ─── Sidebar logo ──────────────────────────────────────────────── */
.prx-sidebar-logo {
    font-size: 1rem; font-weight: 700; color: #0F1117;
    letter-spacing: -0.025em; padding: 1.125rem 1.25rem 0.875rem;
    border-bottom: 1px solid #F3F4F6;
}
.prx-sidebar-logo span { color: #6B21A8; }
.prx-sidebar-logo-sub {
    font-size: 0.625rem; font-weight: 400;
    color: #9CA3AF; letter-spacing: 0.01em;
    display: block; margin-top: 0.125rem;
}

.prx-sidebar-group {
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.07em;
    padding: 1rem 1.25rem 0.25rem;
}
.prx-sidebar-divider { height: 1px; background: #F3F4F6; margin: 0.75rem 0; }

/* ─── Page heading ──────────────────────────────────────────────── */
.prx-page-title {
    font-size: 1.25rem; font-weight: 600; color: #0F1117;
    letter-spacing: -0.025em; margin-bottom: 0.25rem;
}
.prx-page-sub {
    font-size: 0.8125rem; color: #6B7280; margin-bottom: 1.5rem;
    line-height: 1.5;
}
.prx-section-label {
    font-size: 0.6875rem; font-weight: 700; color: #6B7280;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin: 1.75rem 0 0.875rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F3F4F6;
}

/* ─── Cards ─────────────────────────────────────────────────────── */
.prx-card {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 1.25rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    margin-bottom: 0.75rem;
}
.prx-card-sm {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 6px; padding: 0.875rem 1rem;
    margin-bottom: 0.5rem;
}
.prx-card-header {
    font-size: 0.6875rem; font-weight: 700; color: #6B7280;
    text-transform: uppercase; letter-spacing: 0.05em;
    margin-bottom: 0.875rem;
}

/* ─── KPI Priority Queue ────────────────────────────────────────── */
.prx-queue-wrap {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04); margin-bottom: 1.5rem;
}
.prx-queue-header {
    display: grid;
    grid-template-columns: 2.25rem 2rem 1fr 6.5rem 4.5rem 5rem 6rem 5.5rem;
    gap: 0.5rem;
    padding: 0.625rem 1.25rem;
    background: #F9FAFB; border-bottom: 1px solid #E5E7EB;
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.prx-queue-row {
    display: grid;
    grid-template-columns: 2.25rem 2rem 1fr 6.5rem 4.5rem 5rem 6rem 5.5rem;
    gap: 0.5rem;
    padding: 0.875rem 1.25rem;
    border-bottom: 1px solid #F3F4F6;
    align-items: center;
    cursor: pointer;
    transition: background 0.1s;
}
.prx-queue-row:last-child { border-bottom: none; }
.prx-queue-row:hover { background: #F9FAFB; }
.prx-queue-priority {
    font-size: 0.75rem; font-weight: 700; color: #9CA3AF;
    font-variant-numeric: tabular-nums;
}
.prx-queue-icon { font-size: 1rem; line-height: 1; }
.prx-queue-name { font-size: 0.875rem; font-weight: 600; color: #0F1117; }
.prx-queue-meta { font-size: 0.6875rem; color: #9CA3AF; margin-top: 0.125rem; }
.prx-queue-values { font-variant-numeric: tabular-nums; }
.prx-queue-actual { font-size: 0.875rem; font-weight: 600; color: #0F1117; }
.prx-queue-vs { font-size: 0.6875rem; color: #9CA3AF; }
.prx-queue-delta { font-size: 0.875rem; font-weight: 600; font-variant-numeric: tabular-nums; }
.prx-queue-delta.neg   { color: #DC2626; }
.prx-queue-delta.pos   { color: #16A34A; }
.prx-queue-delta.zero  { color: #6B7280; }
.prx-queue-z { font-size: 0.8125rem; color: #6B7280; font-variant-numeric: tabular-nums; }
.prx-badge {
    display: inline-flex; align-items: center;
    font-size: 0.625rem; font-weight: 700;
    padding: 0.1875rem 0.5rem; border-radius: 3px;
    text-transform: uppercase; letter-spacing: 0.04em;
    white-space: nowrap;
}
.prx-badge.critical    { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.prx-badge.warning     { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.prx-badge.ok          { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.prx-badge.pending     { background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; }
.prx-badge.muted       { background: #F9FAFB; color: #6B7280; border: 1px solid #E5E7EB; }
.prx-badge.info        { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.prx-badge.purple      { background: #F5F3FF; color: #6B21A8; border: 1px solid #E9D5FF; }
.prx-freshness {
    display: inline-flex; align-items: center; gap: 0.25rem;
    font-size: 0.6875rem; font-weight: 500;
}
.prx-freshness.fresh { color: #16A34A; }
.prx-freshness.stale { color: #D97706; }
.prx-freshness.missing { color: #DC2626; }
.prx-cta-link {
    font-size: 0.75rem; font-weight: 600; color: #6B21A8;
    text-decoration: none; white-space: nowrap;
    display: inline-flex; align-items: center; gap: 0.25rem;
}

/* ─── Morning briefing scan bar ─────────────────────────────────── */
.prx-scan-bar {
    background: #F5F3FF; border: 1px solid #E9D5FF;
    border-radius: 6px; padding: 0.75rem 1.25rem;
    margin-bottom: 1.25rem;
    display: flex; align-items: center; justify-content: space-between;
}
.prx-scan-label { font-size: 0.875rem; font-weight: 600; color: #5B21B6; }
.prx-scan-meta { font-size: 0.75rem; color: #7C3AED; }

/* ─── Investigation workspace panels ────────────────────────────── */
.prx-inv-panel {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04); margin-bottom: 1.25rem;
}
.prx-inv-panel-head {
    background: #F9FAFB; border-bottom: 1px solid #E5E7EB;
    padding: 0.875rem 1.25rem;
    display: flex; align-items: center; justify-content: space-between;
}
.prx-inv-panel-title {
    font-size: 0.8125rem; font-weight: 700; color: #374151;
    display: flex; align-items: center; gap: 0.5rem;
}
.prx-inv-panel-body { padding: 1.25rem; }

/* ─── Metric tiles ──────────────────────────────────────────────── */
.prx-metric-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem; margin-bottom: 1.25rem;
}
.prx-metric {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 1rem 1.125rem;
    position: relative; overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.prx-metric::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: 8px 0 0 8px;
}
.prx-metric.alert::before { background: #DC2626; }
.prx-metric.warn::before  { background: #D97706; }
.prx-metric.ok::before    { background: #16A34A; }
.prx-metric.neutral::before { background: #E5E7EB; }
.prx-metric-label {
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.375rem;
}
.prx-metric-value {
    font-size: 1.375rem; font-weight: 600; color: #0F1117;
    letter-spacing: -0.02em; line-height: 1.2; margin-bottom: 0.25rem;
}
.prx-metric-delta { font-size: 0.75rem; margin-bottom: 0.5rem; }
.prx-metric-delta.neg { color: #DC2626; }
.prx-metric-delta.pos { color: #16A34A; }

/* ─── Bar chart (contribution) ──────────────────────────────────── */
.prx-bar-chart { padding: 0.25rem 0; }
.prx-bar-row {
    display: flex; align-items: center; gap: 0.75rem;
    padding: 0.5rem 0; border-bottom: 1px solid #F9FAFB;
}
.prx-bar-row:last-child { border-bottom: none; }
.prx-bar-rank {
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    width: 1.25rem; flex-shrink: 0; text-align: center;
}
.prx-bar-label {
    font-size: 0.8125rem; font-weight: 500; color: #374151;
    width: 9rem; flex-shrink: 0; line-height: 1.3;
}
.prx-bar-track {
    flex: 1; height: 10px; background: #F3F4F6;
    border-radius: 999px; overflow: hidden;
}
.prx-bar-fill { height: 100%; border-radius: 999px; }
.prx-bar-fill.c1 { background: #6B21A8; }
.prx-bar-fill.c2 { background: #9333EA; }
.prx-bar-fill.c3 { background: #A855F7; }
.prx-bar-fill.c4 { background: #C084FC; }
.prx-bar-fill.residual { background: #D1D5DB; }
.prx-bar-pct {
    font-size: 0.8125rem; font-weight: 700; color: #374151;
    width: 2.75rem; text-align: right; font-variant-numeric: tabular-nums;
}
.prx-bar-amt {
    font-size: 0.75rem; color: #6B7280;
    width: 4.5rem; text-align: right; font-variant-numeric: tabular-nums;
}
.prx-bar-method {
    font-size: 0.625rem; font-weight: 600;
    padding: 0.1rem 0.375rem; border-radius: 3px;
    white-space: nowrap;
}
.prx-bar-method.det { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.prx-bar-method.llm { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }
.prx-bar-method.ret { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.prx-bar-method.rule { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }

/* ─── Audit trail ───────────────────────────────────────────────── */
.prx-audit-row {
    display: flex; align-items: flex-start; gap: 0.875rem;
    padding: 0.875rem 0; border-bottom: 1px solid #F9FAFB;
}
.prx-audit-row:last-child { border-bottom: none; }
.prx-audit-method-badge {
    flex-shrink: 0; font-size: 0.5625rem; font-weight: 800;
    padding: 0.1875rem 0.4375rem; border-radius: 3px;
    text-transform: uppercase; letter-spacing: 0.05em;
    margin-top: 0.125rem; white-space: nowrap;
    min-width: 5rem; text-align: center;
}
.prx-audit-method-badge.det  { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.prx-audit-method-badge.llm  { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }
.prx-audit-method-badge.ret  { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.prx-audit-method-badge.rule { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.prx-audit-content { flex: 1; }
.prx-audit-title { font-size: 0.875rem; font-weight: 600; color: #0F1117; margin-bottom: 0.25rem; }
.prx-audit-detail { font-size: 0.75rem; color: #6B7280; line-height: 1.6; }
.prx-audit-formula {
    font-size: 0.75rem; color: #374151; background: #F9FAFB;
    border: 1px solid #F3F4F6; border-radius: 4px;
    padding: 0.5rem 0.75rem; margin-top: 0.375rem;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.8;
}

/* ─── Confidence panel ──────────────────────────────────────────── */
.prx-conf-wrap {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 1.25rem; margin-bottom: 1.25rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.prx-conf-score {
    font-size: 2.5rem; font-weight: 700; letter-spacing: -0.04em;
    line-height: 1;
}
.prx-conf-score.HIGH   { color: #16A34A; }
.prx-conf-score.MEDIUM { color: #D97706; }
.prx-conf-score.LOW    { color: #DC2626; }
.prx-conf-band {
    font-size: 0.8125rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.04em;
    margin-top: 0.125rem;
}
.prx-conf-band.HIGH   { color: #16A34A; }
.prx-conf-band.MEDIUM { color: #D97706; }
.prx-conf-band.LOW    { color: #DC2626; }
.prx-conf-track {
    height: 6px; background: #F3F4F6;
    border-radius: 999px; margin: 0.75rem 0; overflow: hidden;
}
.prx-conf-fill { height: 100%; border-radius: 999px; transition: width 0.4s ease; }
.prx-conf-fill.HIGH   { background: #16A34A; }
.prx-conf-fill.MEDIUM { background: #D97706; }
.prx-conf-fill.LOW    { background: #DC2626; }
.prx-conf-component-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.3125rem 0; border-bottom: 1px solid #F9FAFB;
    font-size: 0.8125rem;
}
.prx-conf-component-row:last-child { border-bottom: none; }
.prx-conf-comp-name { color: #6B7280; }
.prx-conf-comp-val { font-weight: 600; font-variant-numeric: tabular-nums; }
.prx-conf-comp-val.pos { color: #16A34A; }
.prx-conf-comp-val.neg { color: #DC2626; }
.prx-conf-comp-val.neu { color: #374151; }

/* ─── Outcome pill ──────────────────────────────────────────────── */
.prx-outcome-pill {
    display: inline-flex; align-items: center; gap: 0.375rem;
    font-size: 0.75rem; font-weight: 700;
    padding: 0.25rem 0.75rem; border-radius: 4px;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.prx-outcome-pill.ANSWER  { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.prx-outcome-pill.QUALIFY { background: #FFFBEB; color: #92400E; border: 1px solid #FDE68A; }
.prx-outcome-pill.CLARIFY { background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; }
.prx-outcome-pill.ABSTAIN { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }

/* ─── Action card ───────────────────────────────────────────────── */
.prx-action-card {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; overflow: hidden; margin-bottom: 1.25rem;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.prx-action-card-head {
    background: #1E1B4B; color: #FFFFFF;
    padding: 0.75rem 1.25rem;
    font-size: 0.6875rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.07em;
    display: flex; align-items: center; justify-content: space-between;
}
.prx-action-row {
    display: grid; grid-template-columns: 9rem 1fr;
    border-bottom: 1px solid #F9FAFB;
}
.prx-action-row:last-child { border-bottom: none; }
.prx-action-key {
    font-size: 0.6875rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.04em;
    padding: 0.625rem 1.25rem; background: #FAFAFA;
    border-right: 1px solid #F3F4F6;
    display: flex; align-items: flex-start; padding-top: 0.75rem;
}
.prx-action-val {
    font-size: 0.875rem; color: #0F1117;
    padding: 0.625rem 1.25rem; line-height: 1.5;
}
.prx-action-val b { font-weight: 600; }
.prx-action-val.success { color: #166534; font-weight: 600; }
.prx-action-val.warn    { color: #92400E; font-weight: 600; }
.prx-action-val.purple  { color: #6B21A8; font-weight: 600; }

/* ─── Evidence cards ────────────────────────────────────────────── */
.prx-evidence-row {
    display: flex; align-items: flex-start; gap: 0.875rem;
    padding: 0.875rem; border-bottom: 1px solid #F9FAFB;
}
.prx-evidence-row:last-child { border-bottom: none; }
.prx-ev-status-icon { font-size: 1rem; flex-shrink: 0; margin-top: 0.1rem; }
.prx-ev-content { flex: 1; }
.prx-ev-source {
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.1875rem;
}
.prx-ev-statement { font-size: 0.875rem; color: #0F1117; line-height: 1.5; margin-bottom: 0.25rem; }
.prx-ev-meta { font-size: 0.6875rem; color: #9CA3AF; }
.prx-ev-badge {
    flex-shrink: 0; font-size: 0.625rem; font-weight: 700;
    padding: 0.1875rem 0.4375rem; border-radius: 3px;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.prx-ev-badge.supporting   { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.prx-ev-badge.contradicting { background: #FEF2F2; color: #991B1B; border: 1px solid #FECACA; }
.prx-ev-badge.neutral       { background: #F9FAFB; color: #6B7280; border: 1px solid #E5E7EB; }

/* ─── Memory cards ──────────────────────────────────────────────── */
.prx-mem-type-badge {
    display: inline-flex; align-items: center;
    font-size: 0.5625rem; font-weight: 800;
    padding: 0.125rem 0.4rem; border-radius: 3px;
    text-transform: uppercase; letter-spacing: 0.06em;
}
.prx-mem-type-badge.outcome     { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.prx-mem-type-badge.decision    { background: #F5F3FF; color: #5B21B6; border: 1px solid #DDD6FE; }
.prx-mem-type-badge.learning    { background: #F0FDF4; color: #166534; border: 1px solid #BBF7D0; }
.prx-mem-type-badge.superseded  { background: #F9FAFB; color: #9CA3AF; border: 1px solid #E5E7EB; }

.prx-mem-status-badge {
    font-size: 0.625rem; font-weight: 700;
    padding: 0.1875rem 0.5rem; border-radius: 3px;
    text-transform: uppercase; letter-spacing: 0.04em;
}
.prx-mem-status-badge.confirmed  { background: #F0FDF4; color: #166534; }
.prx-mem-status-badge.pending    { background: #FFFBEB; color: #92400E; }
.prx-mem-status-badge.rejected   { background: #FEF2F2; color: #991B1B; }
.prx-mem-status-badge.superseded { background: #F9FAFB; color: #9CA3AF; }

/* ─── Learning loop diagram ─────────────────────────────────────── */
.prx-loop {
    display: flex; align-items: center; gap: 0; overflow-x: auto;
    padding: 1.25rem 0; margin-bottom: 1.25rem;
}
.prx-loop-node {
    flex-shrink: 0; text-align: center;
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 0.875rem 0.75rem;
    min-width: 100px;
}
.prx-loop-node.active {
    border-color: #6B21A8; background: #F5F3FF;
}
.prx-loop-node.memory-node {
    border-color: #1D4ED8; background: #EFF6FF;
}
.prx-loop-icon { font-size: 1.25rem; margin-bottom: 0.375rem; }
.prx-loop-label { font-size: 0.75rem; font-weight: 600; color: #0F1117; }
.prx-loop-sub { font-size: 0.625rem; color: #6B7280; margin-top: 0.125rem; }
.prx-loop-arrow {
    flex-shrink: 0; font-size: 1rem; color: #D1D5DB; padding: 0 0.25rem;
}

/* ─── Timeline ──────────────────────────────────────────────────── */
.prx-timeline { display: flex; align-items: flex-start; gap: 0; overflow-x: auto; padding-bottom: 0.5rem; }
.prx-tl-node {
    flex-shrink: 0; width: 168px; background: #FFFFFF;
    border: 1px solid #E5E7EB; border-radius: 6px; padding: 0.875rem;
}
.prx-tl-node.highlighted { border-color: #6B21A8; background: #F5F3FF; }
.prx-tl-connector { flex: 1; min-width: 2rem; height: 1px; background: #D1D5DB; margin-top: 1.625rem; flex-shrink: 0; }
.prx-tl-date { font-size: 0.5625rem; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.25rem; }
.prx-tl-label { font-size: 0.875rem; font-weight: 600; color: #0F1117; margin-bottom: 0.25rem; }
.prx-tl-sub { font-size: 0.6875rem; color: #6B7280; line-height: 1.4; }

/* ─── Counterfactual + risk boxes ───────────────────────────────── */
.prx-counterfactual {
    background: #F0FDF4; border: 1px solid #BBF7D0;
    border-radius: 6px; padding: 1rem 1.25rem;
    margin-bottom: 1rem; font-size: 0.875rem;
    color: #166534; line-height: 1.7;
}
.prx-risk-box {
    background: #FFFBEB; border: 1px solid #FDE68A;
    border-radius: 6px; padding: 1rem 1.25rem;
    margin-bottom: 1rem; font-size: 0.875rem;
    color: #78350F; line-height: 1.7;
}
.prx-risk-box b, .prx-counterfactual b { font-weight: 700; }
.prx-abstain-box {
    background: #FEF2F2; border: 1px solid #FECACA;
    border-radius: 8px; padding: 1.25rem;
    margin-bottom: 1rem;
}
.prx-abstain-title { font-size: 1rem; font-weight: 700; color: #991B1B; margin-bottom: 0.375rem; }
.prx-abstain-body { font-size: 0.875rem; color: #7F1D1D; line-height: 1.6; }

/* ─── Source health grid ────────────────────────────────────────── */
.prx-source-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; margin-bottom: 1.5rem; }
.prx-source-card {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 0.875rem 1rem;
    position: relative; overflow: hidden;
}
.prx-source-card::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: 8px 0 0 8px;
}
.prx-source-card.fresh::before  { background: #16A34A; }
.prx-source-card.stale::before  { background: #D97706; }
.prx-source-card.missing::before { background: #DC2626; }
.prx-source-name { font-size: 0.6875rem; font-weight: 700; color: #374151; margin-bottom: 0.375rem; }
.prx-source-status { font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 0.3rem; margin-bottom: 0.125rem; }
.prx-source-status.fresh  { color: #16A34A; }
.prx-source-status.stale  { color: #D97706; }
.prx-source-status.missing { color: #DC2626; }
.prx-source-meta { font-size: 0.6875rem; color: #9CA3AF; line-height: 1.4; }

/* ─── Decision comparison ───────────────────────────────────────── */
.prx-dec-cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1.25rem; }
.prx-dec-card {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 1.25rem; position: relative; overflow: hidden;
}
.prx-dec-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.prx-dec-card.baseline::before { background: #E5E7EB; }
.prx-dec-card.memory::before   { background: #6B21A8; }
.prx-dec-card-label {
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.875rem;
}

/* ─── Entitlement table ─────────────────────────────────────────── */
.prx-table-wrap {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; overflow: hidden;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04); margin-bottom: 1.25rem;
}
.prx-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.prx-table thead tr { border-bottom: 1px solid #E5E7EB; }
.prx-table th {
    font-size: 0.625rem; font-weight: 700; color: #9CA3AF;
    text-transform: uppercase; letter-spacing: 0.05em;
    padding: 0.625rem 1rem; text-align: left; background: #F9FAFB;
}
.prx-table td {
    padding: 0.625rem 1rem; color: #374151;
    border-bottom: 1px solid #F9FAFB; vertical-align: top;
}
.prx-table tr:last-child td { border-bottom: none; }
.prx-table .dim    { color: #9CA3AF; }
.prx-table .accent { color: #6B21A8; font-weight: 600; }
.prx-table .ok     { color: #16A34A; font-weight: 600; }
.prx-table .warn   { color: #D97706; font-weight: 600; }
.prx-table .crit   { color: #DC2626; font-weight: 600; }
.prx-table .mono   { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }

/* ─── Telemetry ─────────────────────────────────────────────────── */
.prx-tel-grid {
    display: flex; gap: 1.25rem; flex-wrap: wrap;
    margin-bottom: 0.75rem; align-items: center;
}
.prx-tel-item { font-size: 0.8125rem; color: #6B7280; }
.prx-tel-item b { color: #0F1117; font-weight: 600; }

/* ─── Narrative / prose ─────────────────────────────────────────── */
.prx-narrative {
    background: #FAFAFA; border: 1px solid #F3F4F6;
    border-radius: 6px; padding: 1rem 1.25rem;
    font-size: 0.875rem; line-height: 1.75; color: #374151;
    white-space: pre-wrap; margin-bottom: 0.75rem;
}
.prx-restricted-notice {
    background: #F9FAFB; border: 1px dashed #D1D5DB;
    border-radius: 6px; padding: 0.875rem 1.25rem;
    font-size: 0.8125rem; color: #9CA3AF; font-style: italic;
    margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 0.5rem;
}

/* ─── Empty state ───────────────────────────────────────────────── */
.prx-empty {
    padding: 3rem 1rem; text-align: center;
}
.prx-empty-icon { font-size: 2rem; margin-bottom: 0.75rem; }
.prx-empty-title { font-size: 0.9375rem; font-weight: 600; color: #374151; margin-bottom: 0.375rem; }
.prx-empty-sub   { font-size: 0.8125rem; color: #9CA3AF; line-height: 1.6; max-width: 320px; margin: 0 auto; }

/* ─── Scenario launcher ─────────────────────────────────────────── */
.prx-scenario-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.25rem; }
.prx-scenario-card {
    background: #FFFFFF; border: 1px solid #E5E7EB;
    border-radius: 8px; padding: 1.125rem;
    cursor: pointer; transition: border-color 0.15s, box-shadow 0.15s;
}
.prx-scenario-card:hover {
    border-color: #6B21A8;
    box-shadow: 0 0 0 3px rgba(107,33,168,0.08);
}
.prx-scenario-num {
    font-size: 0.625rem; font-weight: 700; color: #6B21A8;
    text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 0.375rem;
}
.prx-scenario-title { font-size: 0.9375rem; font-weight: 600; color: #0F1117; margin-bottom: 0.375rem; }
.prx-scenario-desc { font-size: 0.8125rem; color: #6B7280; line-height: 1.5; margin-bottom: 0.75rem; }

/* ─── Feedback ──────────────────────────────────────────────────── */
.prx-feedback-ok  { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 6px; padding: 0.875rem 1.25rem; margin-bottom: 0.75rem; font-size: 0.875rem; color: #166534; }
.prx-feedback-err { background: #FEF2F2; border: 1px solid #FECACA; border-radius: 6px; padding: 0.875rem 1.25rem; margin-bottom: 0.75rem; font-size: 0.875rem; color: #991B1B; }

/* ─── Callout boxes ─────────────────────────────────────────────── */
.prx-callout {
    border-radius: 6px; padding: 0.875rem 1.25rem;
    font-size: 0.875rem; line-height: 1.6; margin-bottom: 1rem;
    display: flex; align-items: flex-start; gap: 0.75rem;
}
.prx-callout.info   { background: #EFF6FF; border: 1px solid #BFDBFE; color: #1D4ED8; }
.prx-callout.warn   { background: #FFFBEB; border: 1px solid #FDE68A; color: #92400E; }
.prx-callout.ok     { background: #F0FDF4; border: 1px solid #BBF7D0; color: #166534; }
.prx-callout.purple { background: #F5F3FF; border: 1px solid #E9D5FF; color: #5B21B6; }
.prx-callout-icon { flex-shrink: 0; font-size: 1rem; margin-top: 0.125rem; }
.prx-callout-body b { font-weight: 700; }

</style>
"""


# ─── HTML builder helpers ────────────────────────────────────────────────────

def badge(text: str, variant: str = "muted") -> str:
    """Render a <span> badge. variant: critical|warning|ok|pending|muted|info|purple"""
    return f'<span class="prx-badge {variant}">{text}</span>'


def freshness_dot(status: str, ago: str = "") -> str:
    """status: fresh|stale|missing"""
    label = ago or status.capitalize()
    return (f'<span class="prx-freshness {status}">'
            f'<span class="prx-status-dot {("green" if status=="fresh" else "amber" if status=="stale" else "red")}"></span>'
            f' {label}</span>')


def method_badge(kind: str, label: str = None) -> str:
    """kind: det|llm|ret|rule"""
    labels = {"det": "Deterministic", "llm": "LLM", "ret": "Retrieval", "rule": "Business Rule"}
    text = label or labels.get(kind, kind.upper())
    return f'<span class="prx-bar-method {kind}">{text}</span>'


def audit_badge(kind: str) -> str:
    labels = {"det": "Deterministic", "llm": "LLM", "ret": "Retrieval", "rule": "Business Rule"}
    return f'<span class="prx-audit-method-badge {kind}">{labels.get(kind, kind)}</span>'


def outcome_pill(outcome: str) -> str:
    icons = {"ANSWER": "✓", "QUALIFY": "~", "CLARIFY": "?", "ABSTAIN": "⊘"}
    icon = icons.get(outcome, "")
    return f'<span class="prx-outcome-pill {outcome}">{icon} {outcome}</span>'


def section_label(text: str) -> str:
    return f'<div class="prx-section-label">{text}</div>'


def callout(text: str, kind: str = "info", icon: str = "ℹ") -> str:
    return (f'<div class="prx-callout {kind}">'
            f'<span class="prx-callout-icon">{icon}</span>'
            f'<div class="prx-callout-body">{text}</div>'
            f'</div>')


def empty_state(title: str, sub: str = "", icon: str = "○") -> str:
    return (f'<div class="prx-empty">'
            f'<div class="prx-empty-icon">{icon}</div>'
            f'<div class="prx-empty-title">{title}</div>'
            f'<div class="prx-empty-sub">{sub}</div>'
            f'</div>')


def conf_bar(score: float, band: str) -> str:
    w = min(100, max(0, score))
    return (f'<div class="prx-conf-track">'
            f'<div class="prx-conf-fill {band}" style="width:{w}%"></div>'
            f'</div>')


def bar_row(rank: int, label: str, pct: float, amt_inr: float, color_cls: str, method_kind: str = "det") -> str:
    amt_L = amt_inr / 100_000 if amt_inr else 0
    return (f'<div class="prx-bar-row">'
            f'<div class="prx-bar-rank">#{rank}</div>'
            f'<div class="prx-bar-label">{label}</div>'
            f'<div class="prx-bar-track"><div class="prx-bar-fill {color_cls}" style="width:{min(pct,100):.1f}%"></div></div>'
            f'<div class="prx-bar-pct">{pct:.0f}%</div>'
            f'<div class="prx-bar-amt">₹{amt_L:.1f}L</div>'
            f'{method_badge(method_kind)}'
            f'</div>')


def action_row(key: str, value: str, val_class: str = "") -> str:
    return (f'<div class="prx-action-row">'
            f'<div class="prx-action-key">{key}</div>'
            f'<div class="prx-action-val {val_class}">{value}</div>'
            f'</div>')


def evidence_row(source: str, statement: str, freshness: str, ago: str, ev_type: str = "supporting") -> str:
    icon = {"supporting": "✓", "contradicting": "✗", "neutral": "·"}.get(ev_type, "·")
    return (f'<div class="prx-evidence-row">'
            f'<div class="prx-ev-status-icon" style="color:{"#16A34A" if ev_type=="supporting" else "#DC2626" if ev_type=="contradicting" else "#9CA3AF"}">{icon}</div>'
            f'<div class="prx-ev-content">'
            f'<div class="prx-ev-source">{source}</div>'
            f'<div class="prx-ev-statement">{statement}</div>'
            f'<div class="prx-ev-meta">{freshness_dot(freshness, ago)}</div>'
            f'</div>'
            f'<span class="prx-ev-badge {ev_type}">{ev_type.title()}</span>'
            f'</div>')


def audit_row(kind: str, title: str, detail: str, formula: str = "") -> str:
    formula_html = f'<div class="prx-audit-formula">{formula}</div>' if formula else ""
    return (f'<div class="prx-audit-row">'
            f'{audit_badge(kind)}'
            f'<div class="prx-audit-content">'
            f'<div class="prx-audit-title">{title}</div>'
            f'<div class="prx-audit-detail">{detail}</div>'
            f'{formula_html}'
            f'</div>'
            f'</div>')


def memory_card_html(record: dict) -> str:
    vs = record.get("validation_status", "pending")
    status_cls = ("confirmed" if vs in ("demo_preapproved",) else
                  "rejected" if vs == "rejected" else "pending")
    status_label = {"demo_preapproved": "Confirmed", "pending": "Pending", "rejected": "Rejected"}.get(vs, vs)
    driver = record.get("driver_type", "?").replace("_", " ").title()
    grain = record.get("grain_key", "?")
    band = record.get("original_confidence_band", "?")
    action = record.get("action_taken", "?")
    created = record.get("created_at", "?")[:10]
    fixture = " · demo fixture" if record.get("demo_fixture") else ""
    return (f'<div class="prx-card-sm">'
            f'<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:.375rem;">'
            f'<span style="font-size:.875rem;font-weight:600;color:#0F1117;">{driver} · {grain}</span>'
            f'<span class="prx-mem-status-badge {status_cls}">{status_label}</span>'
            f'</div>'
            f'<div style="font-size:.75rem;color:#6B7280;line-height:1.6;">'
            f'<b>Band at decision:</b> {band} &nbsp;·&nbsp; <b>Admitted:</b> {created}{fixture}<br>'
            f'<b>Action:</b> {action}'
            f'</div>'
            f'</div>')


def tel_html(t: dict) -> str:
    t = t or {}
    items = [
        ("Total latency", f"{t.get('total_latency_ms', 0):.0f} ms"),
        ("LLM calls", str(t.get("total_llm_calls", 0))),
        ("Tokens", str(t.get("total_tokens", 0))),
        ("Est. cost", f"${t.get('total_cost_usd', 0):.5f}"),
    ]
    chips = " &nbsp;·&nbsp; ".join(f'<b>{k}</b> {v}' for k, v in items)
    return f'<div class="prx-tel-grid"><span class="prx-tel-item">{chips}</span></div>'
