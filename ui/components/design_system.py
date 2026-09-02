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
/* ─── Google Fonts ──────────────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@700;800&display=swap');

/* ─── Design tokens ─────────────────────────────────────────────── */
:root {
  --bg:           #FFFFFF;
  --bg-subtle:    #F7F8FA;
  --bg-muted:     #F0F1F4;
  --surface:      #FFFFFF;
  --border:       #E8EAED;
  --border-soft:  #F0F1F4;

  --text-primary:   #111827;
  --text-secondary: #4B5563;
  --text-tertiary:  #9CA3AF;
  --text-inverse:   #FFFFFF;

  --purple-50:  #F5F3FF;
  --purple-100: #EDE9FE;
  --purple-200: #DDD6FE;
  --purple-600: #7C3AED;
  --purple-700: #6D28D9;
  --purple-800: #5B21B6;
  --purple-900: #4C1D95;

  --green-50:  #ECFDF5;
  --green-100: #D1FAE5;
  --green-600: #059669;
  --green-700: #047857;

  --red-50:   #FEF2F2;
  --red-100:  #FEE2E2;
  --red-600:  #DC2626;
  --red-700:  #B91C1C;

  --amber-50:   #FFFBEB;
  --amber-100:  #FEF3C7;
  --amber-600:  #D97706;
  --amber-700:  #B45309;

  --blue-50:  #EFF6FF;
  --blue-100: #DBEAFE;
  --blue-600: #2563EB;
  --blue-700: #1D4ED8;

  --shadow-sm: 0 1px 3px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 8px -2px rgba(0,0,0,0.08), 0 2px 4px -1px rgba(0,0,0,0.04);
  --shadow-lg: 0 12px 20px -4px rgba(0,0,0,0.08), 0 4px 8px -2px rgba(0,0,0,0.04);
  --shadow-purple: 0 0 0 3px rgba(124,58,237,0.12);

  --radius-sm:  6px;
  --radius-md:  10px;
  --radius-lg:  14px;
  --radius-xl:  18px;

  --sidebar-w: 248px;
  --header-h:  58px;
}

/* ─── Reset & Base ──────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.stApp {
    background-color: var(--bg-subtle) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: var(--text-primary) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* ─── Hide Streamlit chrome ─────────────────────────────────────── */
[data-testid="stHeader"]  { display: none !important; }
.stDeployButton           { display: none !important; }
#MainMenu                 { visibility: hidden !important; }
footer                    { visibility: hidden !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ─── Main content area ─────────────────────────────────────────── */
.main .block-container {
    max-width: 1320px !important;
    padding: 0 2.25rem 5rem !important;
    margin: 0 auto !important;
    background: transparent !important;
}

/* ─── Custom scrollbar ──────────────────────────────────────────── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #D1D5DB; border-radius: 99px; }
::-webkit-scrollbar-thumb:hover { background: #9CA3AF; }

/* ─── Sidebar ───────────────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
    width: var(--sidebar-w) !important;
}
[data-testid="stSidebarNav"]          { display: none !important; }
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebar"] .block-container  { padding: 0 !important; }
[data-testid="stSidebar"] section > div     { padding: 0 !important; }

/* ─── Sidebar buttons (nav items) ───────────────────────────────── */
[data-testid="stSidebar"] .stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.84375rem !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 0.875rem !important;
    height: auto !important;
    border: none !important;
    background: transparent !important;
    color: var(--text-secondary) !important;
    transition: background 0.15s, color 0.15s !important;
    box-shadow: none !important;
    text-align: left !important;
    letter-spacing: -0.01em !important;
    margin: 1px 0.75rem !important;
    width: calc(100% - 1.5rem) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--bg-subtle) !important;
    color: var(--text-primary) !important;
    border: none !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: var(--purple-600) !important;
    color: var(--text-inverse) !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 3px rgba(124,58,237,0.25) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
    background: var(--purple-700) !important;
    box-shadow: 0 2px 5px rgba(124,58,237,0.3) !important;
}

/* ─── Tabs ──────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1.5px solid var(--border) !important;
    gap: 0 !important; padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: var(--text-tertiary) !important;
    font-size: 0.84375rem !important;
    font-weight: 500 !important;
    padding: 0.6875rem 1.125rem !important;
    margin-bottom: -1.5px !important;
    transition: color 0.15s, border-color 0.15s !important;
    font-family: 'Inter', sans-serif !important;
    letter-spacing: -0.01em !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom-color: var(--purple-600) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab"]:hover { color: var(--text-secondary) !important; }
.stTabs [data-baseweb="tab-panel"] { padding: 1.75rem 0 0 !important; }

/* ─── Buttons (global) ──────────────────────────────────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5625rem 1.125rem !important;
    height: auto !important;
    border: 1px solid var(--border) !important;
    background: var(--surface) !important;
    color: var(--text-secondary) !important;
    transition: all 0.15s ease !important;
    box-shadow: var(--shadow-sm) !important;
    letter-spacing: -0.01em !important;
}
.stButton > button:hover {
    background: var(--bg-subtle) !important;
    border-color: #C4C8D0 !important;
    color: var(--text-primary) !important;
    box-shadow: var(--shadow-md) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button[kind="primary"] {
    background: var(--purple-600) !important;
    border-color: transparent !important;
    color: var(--text-inverse) !important;
    box-shadow: 0 2px 4px rgba(124,58,237,0.3), 0 1px 2px rgba(0,0,0,0.1) !important;
    font-weight: 600 !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--purple-700) !important;
    box-shadow: 0 4px 8px rgba(124,58,237,0.35), 0 2px 4px rgba(0,0,0,0.08) !important;
    transform: translateY(-1px) !important;
}

/* ─── Selectbox ─────────────────────────────────────────────────── */
.stSelectbox > div > div {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    border-radius: var(--radius-sm) !important;
    border-color: var(--border) !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ─── Metrics ───────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    padding: 1.125rem 1.375rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.6875rem !important;
    font-weight: 700 !important;
    color: var(--text-tertiary) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.625rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
    letter-spacing: -0.03em !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8125rem !important; }

/* ─── Expander ──────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-md) !important;
    overflow: hidden !important;
    background: var(--surface) !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 0.75rem !important;
    transition: box-shadow 0.2s !important;
}
[data-testid="stExpander"]:hover {
    box-shadow: var(--shadow-md) !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.875rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    padding: 0.875rem 1.125rem 0.875rem 2.375rem !important;
    background: var(--surface) !important;
    list-style: none !important;
    position: relative !important;
    cursor: pointer !important;
    letter-spacing: -0.01em !important;
}
[data-testid="stExpander"] summary::-webkit-details-marker { display: none !important; }
[data-testid="stExpander"] summary::marker { display: none !important; content: '' !important; }
[data-testid="stExpander"] summary::before {
    content: '' !important;
    position: absolute !important;
    left: 0.9rem !important;
    top: 50% !important;
    transform: translateY(-50%) rotate(-90deg) !important;
    width: 0 !important; height: 0 !important;
    border-left: 4px solid transparent !important;
    border-right: 4px solid transparent !important;
    border-top: 5px solid var(--text-tertiary) !important;
    transition: transform 0.2s ease !important;
}
[data-testid="stExpander"][open] summary::before {
    transform: translateY(-50%) rotate(0deg) !important;
}
[data-testid="stExpander"] summary p {
    display: inline !important;
    margin: 0 !important;
}
[data-testid="stExpander"] summary:hover { background: var(--bg-subtle) !important; }
[data-testid="stExpander"] > div > div { padding: 0 1.125rem 1.125rem !important; }

/* ─── Info / warning / error ────────────────────────────────────── */
.stAlert {
    border-radius: var(--radius-md) !important;
    font-size: 0.875rem !important;
    font-family: 'Inter', sans-serif !important;
    border: none !important;
    box-shadow: var(--shadow-sm) !important;
}

/* ─── Code blocks ───────────────────────────────────────────────── */
code, .stCode {
    font-size: 0.8125rem !important;
    border-radius: var(--radius-sm) !important;
    font-family: 'JetBrains Mono', 'Fira Code', 'Cascadia Code', monospace !important;
}

/* ─── Horizontal rule ───────────────────────────────────────────── */
hr { border-color: var(--border) !important; margin: 1.75rem 0 !important; }

/* ─── Spinner ───────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: var(--purple-600) !important; }

/* ─── Progress bar ──────────────────────────────────────────────── */
.stProgress > div > div { background-color: var(--purple-600) !important; border-radius: 99px !important; }
.stProgress > div { border-radius: 99px !important; background: var(--bg-muted) !important; }


/* ================================================================ */
/* PRAXIS COMPONENT CLASSES                                         */
/* ================================================================ */

/* ─── Application shell / header ────────────────────────────────── */
.prx-app-header {
    position: sticky; top: 0; z-index: 100;
    background: rgba(255,255,255,0.95);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-bottom: 1px solid var(--border);
    padding: 0 2.25rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: var(--header-h);
    margin: 0 -2.25rem 2rem;
    box-shadow: 0 1px 0 rgba(0,0,0,0.04), 0 2px 8px rgba(0,0,0,0.04);
}
.prx-wordmark {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    font-size: 1.1875rem; font-weight: 800;
    color: var(--text-primary); letter-spacing: -0.04em;
    display: flex; align-items: center; gap: 0.4375rem;
}
.prx-wordmark-accent { color: var(--purple-600); }
.prx-wordmark-icon {
    width: 24px; height: 24px;
    background: var(--purple-600);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.prx-wordmark-sub {
    font-family: 'Inter', sans-serif;
    font-size: 0.6875rem; font-weight: 400;
    color: var(--text-tertiary); letter-spacing: 0.01em;
    margin-left: 0.625rem; padding-left: 0.625rem;
    border-left: 1px solid var(--border);
    line-height: 1;
}
.prx-header-ctx {
    display: flex; align-items: center; gap: 0.5rem;
}
.prx-ctx-pill {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.75rem; font-weight: 500;
    padding: 0.3125rem 0.6875rem;
    background: var(--bg-subtle);
    border: 1px solid var(--border);
    border-radius: 99px;
    color: var(--text-secondary);
    white-space: nowrap;
}
.prx-ctx-pill b { color: var(--text-primary); font-weight: 600; }
.prx-ctx-divider { width: 1px; height: 20px; background: var(--border); margin: 0 0.25rem; }
.prx-status-pill {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.6875rem; font-weight: 600;
    padding: 0.25rem 0.625rem;
    background: var(--green-50);
    border: 1px solid var(--green-100);
    border-radius: 99px;
    color: var(--green-700);
    letter-spacing: 0.02em;
}
.prx-status-dot {
    width: 6px; height: 6px; border-radius: 50%;
    display: inline-block; flex-shrink: 0;
}
.prx-status-dot.green  { background: var(--green-600); box-shadow: 0 0 0 2px rgba(5,150,105,0.2); }
.prx-status-dot.amber  { background: var(--amber-600); }
.prx-status-dot.red    { background: var(--red-600); }
.prx-status-dot.purple { background: var(--purple-600); }

/* ─── Sidebar logo ──────────────────────────────────────────────── */
.prx-sidebar-logo {
    padding: 1.25rem 1.125rem 1rem;
    border-bottom: 1px solid var(--border-soft);
    display: flex; flex-direction: column; gap: 0.125rem;
}
.prx-sidebar-logo-mark {
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
    font-size: 1.0625rem; font-weight: 800; color: var(--text-primary);
    letter-spacing: -0.04em; display: flex; align-items: center; gap: 0.4375rem;
}
.prx-sidebar-logo-mark .acc { color: var(--purple-600); }
.prx-sidebar-logo-icon {
    width: 22px; height: 22px;
    background: linear-gradient(135deg, var(--purple-600) 0%, var(--purple-800) 100%);
    border-radius: 5px;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; color: white; flex-shrink: 0;
    box-shadow: 0 2px 4px rgba(124,58,237,0.3);
}
.prx-sidebar-logo-sub {
    font-size: 0.625rem; font-weight: 500;
    color: var(--text-tertiary); letter-spacing: 0.02em;
    padding-left: 29px;
}

/* ─── Sidebar persona pill ──────────────────────────────────────── */
.prx-sidebar-persona {
    margin: 0.75rem 0.875rem 0;
    padding: 0.5rem 0.75rem;
    background: var(--purple-50);
    border: 1px solid var(--purple-200);
    border-radius: var(--radius-sm);
    font-size: 0.75rem;
    display: flex; align-items: center; gap: 0.375rem;
}
.prx-sidebar-persona-label {
    font-size: 0.5625rem; font-weight: 700; color: var(--purple-700);
    text-transform: uppercase; letter-spacing: 0.06em;
    display: block; margin-bottom: 0.125rem;
}
.prx-sidebar-persona-name { font-weight: 600; color: var(--purple-800); font-size: 0.8125rem; }

/* ─── Sidebar nav groups ────────────────────────────────────────── */
.prx-sidebar-group {
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.08em;
    padding: 1.125rem 1.125rem 0.3rem;
}
.prx-sidebar-divider { height: 1px; background: var(--border-soft); margin: 0.5rem 0; }
.prx-sidebar-footer {
    padding: 0.875rem 1.125rem;
    border-top: 1px solid var(--border-soft);
    margin-top: 1rem;
}
.prx-sidebar-footer-item {
    font-size: 0.6875rem; color: var(--text-tertiary); line-height: 1.7;
    display: flex; justify-content: space-between;
}
.prx-sidebar-footer-item b { color: var(--text-secondary); font-weight: 600; }

/* ─── Page heading ──────────────────────────────────────────────── */
.prx-page-title {
    font-size: 1.4375rem; font-weight: 700; color: var(--text-primary);
    letter-spacing: -0.03em; margin-bottom: 0.25rem;
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.prx-page-sub {
    font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 1.75rem;
    line-height: 1.5;
}
.prx-section-label {
    font-size: 0.625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.08em;
    margin: 2rem 0 0.875rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border-soft);
    display: flex; align-items: center; gap: 0.5rem;
}

/* ─── Cards ─────────────────────────────────────────────────────── */
.prx-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.375rem;
    box-shadow: var(--shadow-sm);
    margin-bottom: 0.875rem;
    transition: box-shadow 0.2s, transform 0.2s;
}
.prx-card:hover {
    box-shadow: var(--shadow-md);
}
.prx-card-sm {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 0.875rem 1.125rem;
    margin-bottom: 0.5rem;
    transition: box-shadow 0.15s;
}
.prx-card-sm:hover { box-shadow: var(--shadow-sm); }
.prx-card-header {
    font-size: 0.6875rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-bottom: 1rem;
}

/* ─── KPI Priority Queue ────────────────────────────────────────── */
.prx-queue-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden;
    box-shadow: var(--shadow-sm); margin-bottom: 1.75rem;
}
.prx-queue-header {
    display: grid;
    grid-template-columns: 2rem 2rem 1fr 7rem 5rem 5.5rem 6.5rem 6rem;
    gap: 0.5rem;
    padding: 0.625rem 1.375rem;
    background: var(--bg-subtle); border-bottom: 1px solid var(--border);
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.07em;
}
.prx-queue-row {
    display: grid;
    grid-template-columns: 2rem 2rem 1fr 7rem 5rem 5.5rem 6.5rem 6rem;
    gap: 0.5rem;
    padding: 0.9375rem 1.375rem;
    border-bottom: 1px solid var(--border-soft);
    align-items: center;
    cursor: pointer;
    transition: background 0.12s;
    position: relative;
}
.prx-queue-row:last-child { border-bottom: none; }
.prx-queue-row:hover { background: var(--bg-subtle); }
.prx-queue-row.material {
    border-left: 3px solid var(--red-600);
}
.prx-queue-row.stable {
    border-left: 3px solid var(--green-600);
}
.prx-queue-row.pending {
    border-left: 3px solid var(--border);
}
.prx-queue-priority {
    font-size: 0.6875rem; font-weight: 700; color: var(--text-tertiary);
    font-variant-numeric: tabular-nums; text-align: center;
}
.prx-queue-icon { font-size: 0.9375rem; line-height: 1; }
.prx-queue-name { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); line-height: 1.3; }
.prx-queue-meta { font-size: 0.6875rem; color: var(--text-tertiary); margin-top: 0.1875rem; }
.prx-queue-values { font-variant-numeric: tabular-nums; }
.prx-queue-actual { font-size: 0.9375rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.02em; }
.prx-queue-vs { font-size: 0.625rem; color: var(--text-tertiary); font-weight: 500; }
.prx-queue-delta { font-size: 0.875rem; font-weight: 700; font-variant-numeric: tabular-nums; }
.prx-queue-delta.neg   { color: var(--red-600); }
.prx-queue-delta.pos   { color: var(--green-600); }
.prx-queue-delta.zero  { color: var(--text-tertiary); }
.prx-queue-z { font-size: 0.75rem; color: var(--text-secondary); font-variant-numeric: tabular-nums; }

/* ─── Badges ─────────────────────────────────────────────────────── */
.prx-badge {
    display: inline-flex; align-items: center;
    font-size: 0.625rem; font-weight: 700;
    padding: 0.1875rem 0.5625rem; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.05em;
    white-space: nowrap; line-height: 1.4;
}
.prx-badge.critical    { background: var(--red-50);    color: var(--red-700);    border: 1px solid var(--red-100); }
.prx-badge.warning     { background: var(--amber-50);  color: var(--amber-700);  border: 1px solid var(--amber-100); }
.prx-badge.ok          { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-badge.pending     { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-badge.muted       { background: var(--bg-muted);  color: var(--text-tertiary); border: 1px solid var(--border); }
.prx-badge.info        { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-badge.purple      { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }

/* ─── Freshness indicators ──────────────────────────────────────── */
.prx-freshness {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.6875rem; font-weight: 500;
}
.prx-freshness.fresh  { color: var(--green-600); }
.prx-freshness.stale  { color: var(--amber-600); }
.prx-freshness.missing { color: var(--red-600); }
.prx-cta-link {
    font-size: 0.75rem; font-weight: 600; color: var(--purple-600);
    text-decoration: none; white-space: nowrap;
    display: inline-flex; align-items: center; gap: 0.25rem;
    transition: color 0.15s;
}
.prx-cta-link:hover { color: var(--purple-700); }

/* ─── Morning briefing scan / decision brief bar ─────────────────── */
.prx-scan-bar {
    background: linear-gradient(135deg, var(--purple-50) 0%, #FBF9FF 100%);
    border: 1px solid var(--purple-200);
    border-radius: var(--radius-lg); padding: 1.25rem 1.5rem;
    margin-bottom: 1.75rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 2px 8px rgba(124,58,237,0.06);
}
.prx-scan-label { font-size: 0.9375rem; font-weight: 700; color: var(--purple-800); letter-spacing: -0.02em; }
.prx-scan-meta { font-size: 0.8125rem; color: var(--purple-700); margin-top: 0.1875rem; }
.prx-scan-stat-wrap { display: flex; gap: 2rem; flex-shrink: 0; }
.prx-scan-stat { text-align: center; }
.prx-scan-stat-num { font-size: 1.625rem; font-weight: 800; letter-spacing: -0.04em; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.prx-scan-stat-label { font-size: 0.5625rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; margin-top: 0.125rem; }

/* ─── Investigation workspace panels ────────────────────────────── */
.prx-inv-panel {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-lg); overflow: hidden;
    box-shadow: var(--shadow-sm); margin-bottom: 1.375rem;
}
.prx-inv-panel-head {
    background: var(--bg-subtle); border-bottom: 1px solid var(--border);
    padding: 0.9375rem 1.375rem;
    display: flex; align-items: center; justify-content: space-between;
}
.prx-inv-panel-title {
    font-size: 0.875rem; font-weight: 700; color: var(--text-primary);
    display: flex; align-items: center; gap: 0.5rem; letter-spacing: -0.01em;
}
.prx-inv-panel-body { padding: 1.375rem; }

/* ─── Metric tiles ──────────────────────────────────────────────── */
.prx-metric-grid {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 0.875rem; margin-bottom: 1.375rem;
}
.prx-metric {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.125rem 1.25rem;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s, transform 0.2s;
}
.prx-metric:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.prx-metric::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: var(--radius-md) 0 0 var(--radius-md);
}
.prx-metric.alert::before  { background: var(--red-600); }
.prx-metric.warn::before   { background: var(--amber-600); }
.prx-metric.ok::before     { background: var(--green-600); }
.prx-metric.neutral::before { background: var(--border); }
.prx-metric-label {
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.4375rem;
}
.prx-metric-value {
    font-size: 1.5rem; font-weight: 700; color: var(--text-primary);
    letter-spacing: -0.03em; line-height: 1.2; margin-bottom: 0.25rem;
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.prx-metric-delta { font-size: 0.75rem; font-weight: 600; margin-bottom: 0.5rem; }
.prx-metric-delta.neg { color: var(--red-600); }
.prx-metric-delta.pos { color: var(--green-600); }

/* ─── Bar chart (contribution) ──────────────────────────────────── */
.prx-bar-chart { padding: 0.25rem 0; }
.prx-bar-row {
    display: flex; align-items: center; gap: 0.875rem;
    padding: 0.5625rem 0; border-bottom: 1px solid var(--border-soft);
}
.prx-bar-row:last-child { border-bottom: none; }
.prx-bar-rank {
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    width: 1.25rem; flex-shrink: 0; text-align: center;
}
.prx-bar-label {
    font-size: 0.8125rem; font-weight: 500; color: var(--text-secondary);
    width: 9rem; flex-shrink: 0; line-height: 1.3;
}
.prx-bar-track {
    flex: 1; height: 8px; background: var(--bg-muted);
    border-radius: 99px; overflow: hidden;
}
.prx-bar-fill { height: 100%; border-radius: 99px; transition: width 0.4s ease; }
.prx-bar-fill.c1 { background: linear-gradient(90deg, var(--purple-600), var(--purple-700)); }
.prx-bar-fill.c2 { background: linear-gradient(90deg, #8B5CF6, var(--purple-600)); }
.prx-bar-fill.c3 { background: linear-gradient(90deg, #A78BFA, #8B5CF6); }
.prx-bar-fill.c4 { background: linear-gradient(90deg, #C4B5FD, #A78BFA); }
.prx-bar-fill.residual { background: var(--border); }
.prx-bar-pct {
    font-size: 0.8125rem; font-weight: 700; color: var(--text-primary);
    width: 2.75rem; text-align: right; font-variant-numeric: tabular-nums;
}
.prx-bar-amt {
    font-size: 0.75rem; color: var(--text-secondary);
    width: 4.5rem; text-align: right; font-variant-numeric: tabular-nums;
}
.prx-bar-method {
    font-size: 0.5625rem; font-weight: 700;
    padding: 0.125rem 0.4375rem; border-radius: 99px;
    white-space: nowrap; text-transform: uppercase; letter-spacing: 0.04em;
}
.prx-bar-method.det  { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-bar-method.llm  { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-bar-method.ret  { background: var(--amber-50);  color: var(--amber-700);  border: 1px solid var(--amber-100); }
.prx-bar-method.rule { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }

/* ─── Audit trail ───────────────────────────────────────────────── */
.prx-audit-row {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 0.9375rem 0; border-bottom: 1px solid var(--border-soft);
}
.prx-audit-row:last-child { border-bottom: none; }
.prx-audit-method-badge {
    flex-shrink: 0; font-size: 0.5rem; font-weight: 800;
    padding: 0.25rem 0.5rem; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.06em;
    margin-top: 0.1875rem; white-space: nowrap;
    min-width: 5.5rem; text-align: center;
}
.prx-audit-method-badge.det  { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-audit-method-badge.llm  { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-audit-method-badge.ret  { background: var(--amber-50);  color: var(--amber-700);  border: 1px solid var(--amber-100); }
.prx-audit-method-badge.rule { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-audit-content { flex: 1; }
.prx-audit-title { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem; letter-spacing: -0.01em; }
.prx-audit-detail { font-size: 0.75rem; color: var(--text-secondary); line-height: 1.6; }
.prx-audit-formula {
    font-size: 0.75rem; color: var(--text-secondary); background: var(--bg-subtle);
    border: 1px solid var(--border); border-radius: var(--radius-sm);
    padding: 0.5rem 0.75rem; margin-top: 0.4375rem;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1.8;
}

/* ─── Confidence panel ──────────────────────────────────────────── */
.prx-conf-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.375rem; margin-bottom: 1.375rem;
    box-shadow: var(--shadow-sm);
}
.prx-conf-score {
    font-size: 3rem; font-weight: 800; letter-spacing: -0.05em;
    line-height: 1; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.prx-conf-score.HIGH   { color: var(--green-600); }
.prx-conf-score.MEDIUM { color: var(--amber-600); }
.prx-conf-score.LOW    { color: var(--red-600); }
.prx-conf-band {
    font-size: 0.75rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.05em;
    margin-top: 0.1875rem;
}
.prx-conf-band.HIGH   { color: var(--green-600); }
.prx-conf-band.MEDIUM { color: var(--amber-600); }
.prx-conf-band.LOW    { color: var(--red-600); }
.prx-conf-track {
    height: 6px; background: var(--bg-muted);
    border-radius: 99px; margin: 0.875rem 0; overflow: hidden;
}
.prx-conf-fill { height: 100%; border-radius: 99px; transition: width 0.5s ease; }
.prx-conf-fill.HIGH   { background: linear-gradient(90deg, var(--green-600), #10B981); }
.prx-conf-fill.MEDIUM { background: linear-gradient(90deg, var(--amber-600), #F59E0B); }
.prx-conf-fill.LOW    { background: linear-gradient(90deg, var(--red-600), #EF4444); }
.prx-conf-component-row {
    display: flex; align-items: center; justify-content: space-between;
    padding: 0.375rem 0; border-bottom: 1px solid var(--border-soft);
    font-size: 0.8125rem;
}
.prx-conf-component-row:last-child { border-bottom: none; }
.prx-conf-comp-name { color: var(--text-secondary); }
.prx-conf-comp-val { font-weight: 700; font-variant-numeric: tabular-nums; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.prx-conf-comp-val.pos { color: var(--green-600); }
.prx-conf-comp-val.neg { color: var(--red-600); }
.prx-conf-comp-val.neu { color: var(--text-primary); }

/* ─── Outcome pill ──────────────────────────────────────────────── */
.prx-outcome-pill {
    display: inline-flex; align-items: center; gap: 0.375rem;
    font-size: 0.6875rem; font-weight: 700;
    padding: 0.3125rem 0.875rem; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.prx-outcome-pill.ANSWER  { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-outcome-pill.QUALIFY { background: var(--amber-50);  color: var(--amber-700);  border: 1px solid var(--amber-100); }
.prx-outcome-pill.CLARIFY { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-outcome-pill.ABSTAIN { background: var(--red-50);    color: var(--red-700);    border: 1px solid var(--red-100); }

/* ─── Action card ───────────────────────────────────────────────── */
.prx-action-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); overflow: hidden; margin-bottom: 1.375rem;
    box-shadow: var(--shadow-sm);
}
.prx-action-card-head {
    background: linear-gradient(135deg, #1E1B4B 0%, #2E1065 100%);
    color: var(--text-inverse);
    padding: 0.875rem 1.375rem;
    font-size: 0.625rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    display: flex; align-items: center; justify-content: space-between;
}
.prx-action-row {
    display: grid; grid-template-columns: 9.5rem 1fr;
    border-bottom: 1px solid var(--border-soft);
}
.prx-action-row:last-child { border-bottom: none; }
.prx-action-key {
    font-size: 0.6875rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.05em;
    padding: 0.75rem 1.375rem; background: var(--bg-subtle);
    border-right: 1px solid var(--border-soft);
    display: flex; align-items: flex-start; padding-top: 0.875rem;
}
.prx-action-val {
    font-size: 0.875rem; color: var(--text-primary);
    padding: 0.75rem 1.375rem; line-height: 1.6;
}
.prx-action-val b { font-weight: 600; }
.prx-action-val.success { color: var(--green-700); font-weight: 600; }
.prx-action-val.warn    { color: var(--amber-700); font-weight: 600; }
.prx-action-val.purple  { color: var(--purple-700); font-weight: 600; }

/* ─── Evidence cards ────────────────────────────────────────────── */
.prx-evidence-row {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 0.9375rem; border-bottom: 1px solid var(--border-soft);
    transition: background 0.12s;
}
.prx-evidence-row:last-child { border-bottom: none; }
.prx-evidence-row:hover { background: var(--bg-subtle); border-radius: var(--radius-sm); }
.prx-ev-status-icon { font-size: 0.875rem; flex-shrink: 0; margin-top: 0.125rem; }
.prx-ev-content { flex: 1; }
.prx-ev-source {
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.25rem;
}
.prx-ev-statement { font-size: 0.875rem; color: var(--text-primary); line-height: 1.6; margin-bottom: 0.3rem; }
.prx-ev-meta { font-size: 0.6875rem; color: var(--text-tertiary); }
.prx-ev-badge {
    flex-shrink: 0; font-size: 0.5625rem; font-weight: 700;
    padding: 0.1875rem 0.5rem; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.prx-ev-badge.supporting    { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-ev-badge.contradicting { background: var(--red-50);    color: var(--red-700);    border: 1px solid var(--red-100); }
.prx-ev-badge.neutral       { background: var(--bg-muted);  color: var(--text-tertiary); border: 1px solid var(--border); }

/* ─── Memory cards ──────────────────────────────────────────────── */
.prx-mem-type-badge {
    display: inline-flex; align-items: center;
    font-size: 0.5625rem; font-weight: 800;
    padding: 0.125rem 0.4375rem; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.07em;
}
.prx-mem-type-badge.outcome     { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-mem-type-badge.decision    { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-mem-type-badge.learning    { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-mem-type-badge.superseded  { background: var(--bg-muted);  color: var(--text-tertiary); border: 1px solid var(--border); }

.prx-mem-status-badge {
    font-size: 0.5625rem; font-weight: 700;
    padding: 0.1875rem 0.5rem; border-radius: 99px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.prx-mem-status-badge.confirmed  { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-mem-status-badge.pending    { background: var(--amber-50);  color: var(--amber-700);  border: 1px solid var(--amber-100); }
.prx-mem-status-badge.rejected   { background: var(--red-50);    color: var(--red-700);    border: 1px solid var(--red-100); }
.prx-mem-status-badge.superseded { background: var(--bg-muted);  color: var(--text-tertiary); border: 1px solid var(--border); }

/* ─── Learning loop diagram ─────────────────────────────────────── */
.prx-loop {
    display: flex; align-items: center; gap: 0; overflow-x: auto;
    padding: 1.375rem 0; margin-bottom: 1.375rem;
}
.prx-loop-node {
    flex-shrink: 0; text-align: center;
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1rem 0.875rem;
    min-width: 108px;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s, transform 0.2s;
}
.prx-loop-node:hover { box-shadow: var(--shadow-md); transform: translateY(-1px); }
.prx-loop-node.active {
    border-color: var(--purple-600); background: var(--purple-50);
    box-shadow: 0 0 0 3px rgba(124,58,237,0.1), var(--shadow-sm);
}
.prx-loop-node.memory-node {
    border-color: var(--blue-600); background: var(--blue-50);
}
.prx-loop-icon { font-size: 1.375rem; margin-bottom: 0.4375rem; }
.prx-loop-label { font-size: 0.75rem; font-weight: 600; color: var(--text-primary); letter-spacing: -0.01em; }
.prx-loop-sub { font-size: 0.5625rem; color: var(--text-tertiary); margin-top: 0.1875rem; line-height: 1.4; }
.prx-loop-arrow {
    flex-shrink: 0; font-size: 1rem; color: var(--text-tertiary); padding: 0 0.25rem;
}

/* ─── Timeline ──────────────────────────────────────────────────── */
.prx-timeline { display: flex; align-items: flex-start; gap: 0; overflow-x: auto; padding-bottom: 0.5rem; }
.prx-tl-node {
    flex-shrink: 0; width: 176px; background: var(--surface);
    border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.9375rem;
    box-shadow: var(--shadow-sm);
}
.prx-tl-node.highlighted { border-color: var(--purple-600); background: var(--purple-50); }
.prx-tl-connector { flex: 1; min-width: 2rem; height: 1px; background: var(--border); margin-top: 1.75rem; flex-shrink: 0; }
.prx-tl-date { font-size: 0.5rem; font-weight: 700; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.25rem; }
.prx-tl-label { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem; letter-spacing: -0.01em; }
.prx-tl-sub { font-size: 0.6875rem; color: var(--text-secondary); line-height: 1.4; }

/* ─── Counterfactual + risk boxes ───────────────────────────────── */
.prx-counterfactual {
    background: var(--green-50); border: 1px solid var(--green-100);
    border-radius: var(--radius-md); padding: 1.125rem 1.375rem;
    margin-bottom: 1rem; font-size: 0.875rem;
    color: var(--green-700); line-height: 1.7;
}
.prx-risk-box {
    background: var(--amber-50); border: 1px solid var(--amber-100);
    border-radius: var(--radius-md); padding: 1.125rem 1.375rem;
    margin-bottom: 1rem; font-size: 0.875rem;
    color: var(--amber-700); line-height: 1.7;
}
.prx-risk-box b, .prx-counterfactual b { font-weight: 700; }
.prx-abstain-box {
    background: var(--red-50); border: 1px solid var(--red-100);
    border-radius: var(--radius-md); padding: 1.375rem;
    margin-bottom: 1rem;
}
.prx-abstain-title { font-size: 1rem; font-weight: 700; color: var(--red-700); margin-bottom: 0.4375rem; letter-spacing: -0.01em; }
.prx-abstain-body { font-size: 0.875rem; color: var(--red-700); line-height: 1.6; opacity: 0.85; }

/* ─── Source health grid ────────────────────────────────────────── */
.prx-source-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.875rem; margin-bottom: 1.75rem; }
.prx-source-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1rem 1.125rem;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s;
}
.prx-source-card:hover { box-shadow: var(--shadow-md); }
.prx-source-card::before {
    content: ''; position: absolute;
    left: 0; top: 0; bottom: 0; width: 3px;
    border-radius: var(--radius-md) 0 0 var(--radius-md);
}
.prx-source-card.fresh::before   { background: var(--green-600); }
.prx-source-card.stale::before   { background: var(--amber-600); }
.prx-source-card.missing::before { background: var(--red-600); }
.prx-source-name { font-size: 0.6875rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.4375rem; }
.prx-source-status { font-size: 0.75rem; font-weight: 600; display: flex; align-items: center; gap: 0.3rem; margin-bottom: 0.125rem; }
.prx-source-status.fresh   { color: var(--green-600); }
.prx-source-status.stale   { color: var(--amber-600); }
.prx-source-status.missing { color: var(--red-600); }
.prx-source-meta { font-size: 0.6875rem; color: var(--text-tertiary); line-height: 1.4; }

/* ─── Decision comparison ───────────────────────────────────────── */
.prx-dec-cmp-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.125rem; margin-bottom: 1.375rem; }
.prx-dec-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.375rem;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-sm);
}
.prx-dec-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
}
.prx-dec-card.baseline::before { background: var(--border); }
.prx-dec-card.memory::before   { background: linear-gradient(90deg, var(--purple-600), var(--purple-800)); }
.prx-dec-card-label {
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 1rem;
}

/* ─── Entitlement table ─────────────────────────────────────────── */
.prx-table-wrap {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); overflow: hidden;
    box-shadow: var(--shadow-sm); margin-bottom: 1.375rem;
}
.prx-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.prx-table thead tr { border-bottom: 1px solid var(--border); }
.prx-table th {
    font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary);
    text-transform: uppercase; letter-spacing: 0.07em;
    padding: 0.6875rem 1.125rem; text-align: left; background: var(--bg-subtle);
}
.prx-table td {
    padding: 0.6875rem 1.125rem; color: var(--text-secondary);
    border-bottom: 1px solid var(--border-soft); vertical-align: top;
}
.prx-table tr:last-child td { border-bottom: none; }
.prx-table tr:hover td { background: var(--bg-subtle); }
.prx-table .dim    { color: var(--text-tertiary); }
.prx-table .accent { color: var(--purple-600); font-weight: 600; }
.prx-table .ok     { color: var(--green-600); font-weight: 600; }
.prx-table .warn   { color: var(--amber-600); font-weight: 600; }
.prx-table .crit   { color: var(--red-600);   font-weight: 600; }
.prx-table .mono   { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; }

/* ─── Telemetry ─────────────────────────────────────────────────── */
.prx-tel-grid {
    display: flex; gap: 1.375rem; flex-wrap: wrap;
    margin-bottom: 0.75rem; align-items: center;
}
.prx-tel-item { font-size: 0.8125rem; color: var(--text-secondary); }
.prx-tel-item b { color: var(--text-primary); font-weight: 600; }

/* ─── Narrative / prose ─────────────────────────────────────────── */
.prx-narrative {
    background: var(--bg-subtle); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.125rem 1.375rem;
    font-size: 0.875rem; line-height: 1.8; color: var(--text-secondary);
    white-space: pre-wrap; margin-bottom: 0.875rem;
}
.prx-restricted-notice {
    background: var(--bg-muted); border: 1px dashed var(--border);
    border-radius: var(--radius-sm); padding: 0.9375rem 1.375rem;
    font-size: 0.8125rem; color: var(--text-tertiary); font-style: italic;
    margin-bottom: 0.875rem;
    display: flex; align-items: center; gap: 0.5rem;
}

/* ─── Empty state ───────────────────────────────────────────────── */
.prx-empty {
    padding: 3.5rem 1rem; text-align: center;
}
.prx-empty-icon { font-size: 2.25rem; margin-bottom: 0.875rem; }
.prx-empty-title { font-size: 1rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.4375rem; letter-spacing: -0.01em; }
.prx-empty-sub   { font-size: 0.8125rem; color: var(--text-tertiary); line-height: 1.6; max-width: 340px; margin: 0 auto; }

/* ─── Scenario launcher ─────────────────────────────────────────── */
.prx-scenario-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 1.125rem; margin-bottom: 1.375rem; }
.prx-scenario-card {
    background: var(--surface); border: 1px solid var(--border);
    border-radius: var(--radius-md); padding: 1.25rem;
    cursor: pointer; transition: border-color 0.2s, box-shadow 0.2s, transform 0.2s;
    box-shadow: var(--shadow-sm);
}
.prx-scenario-card:hover {
    border-color: var(--purple-600);
    box-shadow: var(--shadow-purple), var(--shadow-sm);
    transform: translateY(-1px);
}
.prx-scenario-num {
    font-size: 0.5625rem; font-weight: 700; color: var(--purple-600);
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.4375rem;
}
.prx-scenario-title { font-size: 0.9375rem; font-weight: 700; color: var(--text-primary); margin-bottom: 0.375rem; letter-spacing: -0.02em; }
.prx-scenario-desc { font-size: 0.8125rem; color: var(--text-secondary); line-height: 1.5; margin-bottom: 0.875rem; }

/* ─── Feedback ──────────────────────────────────────────────────── */
.prx-feedback-ok  { background: var(--green-50);  border: 1px solid var(--green-100);  border-radius: var(--radius-sm); padding: 0.9375rem 1.375rem; margin-bottom: 0.875rem; font-size: 0.875rem; color: var(--green-700); }
.prx-feedback-err { background: var(--red-50);    border: 1px solid var(--red-100);    border-radius: var(--radius-sm); padding: 0.9375rem 1.375rem; margin-bottom: 0.875rem; font-size: 0.875rem; color: var(--red-700); }

/* ─── Callout boxes ─────────────────────────────────────────────── */
.prx-callout {
    border-radius: var(--radius-sm); padding: 0.9375rem 1.375rem;
    font-size: 0.875rem; line-height: 1.6; margin-bottom: 1.125rem;
    display: flex; align-items: flex-start; gap: 0.75rem;
}
.prx-callout.info   { background: var(--blue-50);   border: 1px solid var(--blue-100);   color: var(--blue-700); }
.prx-callout.warn   { background: var(--amber-50);  border: 1px solid var(--amber-100);  color: var(--amber-700); }
.prx-callout.ok     { background: var(--green-50);  border: 1px solid var(--green-100);  color: var(--green-700); }
.prx-callout.purple { background: var(--purple-50); border: 1px solid var(--purple-200); color: var(--purple-700); }
.prx-callout-icon { flex-shrink: 0; font-size: 1.0625rem; margin-top: 0.0625rem; }
.prx-callout-body b { font-weight: 700; }

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
/* ─── Callout (updated) ─────────────────────────────────────────── */
.prx-callout.info   { background: var(--blue-50);   border: 1px solid var(--blue-100);   color: var(--blue-700); }
.prx-callout.warn   { background: var(--amber-50);  border: 1px solid var(--amber-100);  color: var(--amber-700); }
.prx-callout.ok     { background: var(--green-50);  border: 1px solid var(--green-100);  color: var(--green-700); }
.prx-callout.purple { background: var(--purple-50); border: 1px solid var(--purple-200); color: var(--purple-700); }
.prx-callout-icon { flex-shrink: 0; font-size: 1rem; margin-top: 0.125rem; }
.prx-callout-body b { font-weight: 700; }

/* ─── Section separator (replaces tabs) ─────────────────────────── */
.prx-section-sep {
    display: flex; align-items: center; gap: 1rem;
    margin: 2.25rem 0 1.5rem;
}
.prx-section-sep-line {
    flex: 1; height: 1px; background: var(--border);
}
.prx-section-sep-label {
    font-size: 0.5625rem; font-weight: 800;
    color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.12em;
    white-space: nowrap; flex-shrink: 0;
}
.prx-section-sep:first-child { margin-top: 1rem; }

/* ─── Memory Boost card (the "magic moment") ────────────────────── */
.prx-memory-boost {
    background: linear-gradient(135deg, #2E1065 0%, #4C1D95 60%, #5B21B6 100%);
    border-radius: var(--radius-lg);
    padding: 1.375rem 1.625rem;
    margin: 1.5rem 0;
    display: flex; align-items: flex-start; gap: 1.25rem;
    position: relative; overflow: hidden;
    box-shadow: 0 4px 16px rgba(91,33,182,0.25), 0 2px 6px rgba(0,0,0,0.1);
}
.prx-memory-boost::before {
    content: '';
    position: absolute; top: 0; right: 0; bottom: 0;
    width: 40%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.03));
    pointer-events: none;
}
.prx-memory-boost-icon {
    font-size: 1.75rem; flex-shrink: 0; margin-top: 0.125rem;
    filter: drop-shadow(0 0 8px rgba(167,139,250,0.5));
}
.prx-memory-boost-body { flex: 1; }
.prx-memory-boost-label {
    font-size: 0.5625rem; font-weight: 800; color: rgba(196,181,253,0.9);
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.375rem;
}
.prx-memory-boost-title {
    font-size: 1.0625rem; font-weight: 700; color: #FFFFFF;
    letter-spacing: -0.02em; margin-bottom: 0.25rem;
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.prx-memory-boost-sub {
    font-size: 0.8125rem; color: rgba(221,214,254,0.85); line-height: 1.6;
}
.prx-memory-boost-delta {
    flex-shrink: 0; text-align: right;
}
.prx-memory-boost-num {
    font-size: 2.25rem; font-weight: 800; color: #FFFFFF;
    letter-spacing: -0.05em; line-height: 1;
    font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
}
.prx-memory-boost-num-label {
    font-size: 0.625rem; font-weight: 600; color: rgba(196,181,253,0.8);
    text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.25rem;
}

/* ─── Inline KPI row with CTA ───────────────────────────────────── */
.prx-kpi-cta-row {
    display: flex; align-items: center; gap: 1rem;
    padding: 1rem 1.375rem;
    border-bottom: 1px solid var(--border-soft);
    cursor: pointer;
    transition: background 0.12s;
    position: relative;
}
.prx-kpi-cta-row:last-child { border-bottom: none; }
.prx-kpi-cta-row:hover { background: var(--bg-subtle); }
.prx-kpi-cta-row.material { border-left: 3px solid var(--red-600); }
.prx-kpi-cta-row.stable   { border-left: 3px solid var(--green-600); }
.prx-kpi-cta-row.warning  { border-left: 3px solid var(--amber-600); }
.prx-kpi-cta-row.pending  { border-left: 3px solid var(--border); }
.prx-kpi-cta-rank   { font-size: 0.625rem; font-weight: 700; color: var(--text-tertiary); width: 1.25rem; flex-shrink: 0; text-align: center; }
.prx-kpi-cta-icon   { font-size: 1rem; flex-shrink: 0; }
.prx-kpi-cta-name   { flex: 1; }
.prx-kpi-cta-kname  { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); letter-spacing: -0.01em; }
.prx-kpi-cta-meta   { font-size: 0.625rem; color: var(--text-tertiary); margin-top: 0.125rem; }
.prx-kpi-cta-value  { text-align: right; flex-shrink: 0; width: 5.5rem; }
.prx-kpi-cta-actual { font-size: 1rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.02em; font-family: 'Plus Jakarta Sans', 'Inter', sans-serif; }
.prx-kpi-cta-vs     { font-size: 0.5625rem; color: var(--text-tertiary); }
.prx-kpi-cta-delta  { font-size: 0.875rem; font-weight: 700; width: 4.5rem; text-align: right; flex-shrink: 0; font-variant-numeric: tabular-nums; }
.prx-kpi-cta-delta.neg  { color: var(--red-600); }
.prx-kpi-cta-delta.pos  { color: var(--green-600); }
.prx-kpi-cta-delta.zero { color: var(--text-tertiary); }
.prx-kpi-cta-fresh  { width: 6rem; flex-shrink: 0; }
.prx-kpi-cta-status { width: 7rem; flex-shrink: 0; }
.prx-kpi-cta-btn    { flex-shrink: 0; font-size: 0.6875rem; font-weight: 600; color: var(--purple-600); white-space: nowrap; }

/* ─── Demo launcher in sidebar ──────────────────────────────────── */
.prx-sidebar-demo-btn {
    margin: 0.875rem 0.875rem 0.5rem;
    padding: 0.75rem 1rem;
    background: linear-gradient(135deg, var(--purple-600) 0%, var(--purple-800) 100%);
    border-radius: var(--radius-md);
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(124,58,237,0.3);
    transition: box-shadow 0.2s, transform 0.15s;
    text-align: center;
}
.prx-sidebar-demo-btn:hover {
    box-shadow: 0 4px 12px rgba(124,58,237,0.4);
    transform: translateY(-1px);
}
.prx-sidebar-demo-label {
    font-size: 0.5rem; font-weight: 800; color: rgba(196,181,253,0.85);
    text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.25rem;
}
.prx-sidebar-demo-title {
    font-size: 0.8125rem; font-weight: 700; color: #FFFFFF;
    letter-spacing: -0.01em;
}
.prx-sidebar-demo-sub {
    font-size: 0.625rem; color: rgba(221,214,254,0.75);
    margin-top: 0.125rem;
}

/* ─── Scroll section wrapper ────────────────────────────────────── */
.prx-scroll-section {
    margin-bottom: 0.25rem;
}

/* ─── Approve action banner ─────────────────────────────────────── */
.prx-approve-banner {
    background: linear-gradient(135deg, #064E3B 0%, #065F46 100%);
    border-radius: var(--radius-lg);
    padding: 1.25rem 1.625rem;
    margin: 1.75rem 0 0.5rem;
    display: flex; align-items: center; justify-content: space-between;
    gap: 1.5rem;
    box-shadow: 0 4px 12px rgba(5,150,105,0.2);
}
.prx-approve-banner-text { flex: 1; }
.prx-approve-banner-title {
    font-size: 0.9375rem; font-weight: 700; color: #ECFDF5;
    letter-spacing: -0.02em; margin-bottom: 0.25rem;
}
.prx-approve-banner-sub {
    font-size: 0.8125rem; color: rgba(167,243,208,0.85); line-height: 1.5;
}

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


def section_sep(label: str) -> str:
    """Bold ruled section separator — replaces tabs in investigation scroll view."""
    return (f'<div class="prx-section-sep">'
            f'<div class="prx-section-sep-line"></div>'
            f'<div class="prx-section-sep-label">{label}</div>'
            f'<div class="prx-section-sep-line"></div>'
            f'</div>')


def memory_boost_card(pre_score: float, post_score: float, mem_pts: float,
                      scope: str = "", date_str: str = "") -> str:
    """Prominent purple card surfacing the memory boost — the product's magic moment."""
    delta = post_score - pre_score
    date_html = f' · from {date_str}' if date_str else ''
    scope_html = scope.replace('_', ' ').title() if scope else 'Driver + Zone'
    return (
        f'<div class="prx-memory-boost">'
        f'<div class="prx-memory-boost-icon">⊗</div>'
        f'<div class="prx-memory-boost-body">'
        f'<div class="prx-memory-boost-label">Memory Active · Praxis Learning Loop</div>'
        f'<div class="prx-memory-boost-title">Validated Precedent Retrieved{date_html}</div>'
        f'<div class="prx-memory-boost-sub">'
        f'A confirmed decision record from a similar situation ({scope_html}) was found '
        f'and applied to this analysis. Confidence increased from '
        f'<b style="color:#E9D5FF">{pre_score:.0f}</b> → '
        f'<b style="color:#FFFFFF">{post_score:.0f}</b> pts.'
        f'</div>'
        f'</div>'
        f'<div class="prx-memory-boost-delta">'
        f'<div class="prx-memory-boost-num">+{mem_pts:.0f}</div>'
        f'<div class="prx-memory-boost-num-label">Memory Points</div>'
        f'</div>'
        f'</div>'
    )




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
