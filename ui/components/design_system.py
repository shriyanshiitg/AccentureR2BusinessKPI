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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

/* ─── Design tokens ─────────────────────────────────────────────── */
:root {
  --bg:           #FFFFFF;
  --bg-subtle:    #F8F9FB;
  --bg-muted:     #F1F3F7;
  --sidebar-bg:   #0D0F14;
  --surface:      #FFFFFF;
  --border:       #E5E7EB;
  --border-soft:  #F3F4F6;
  --border-strong:#D1D5DB;
  --text-primary:   #0A0E1A;
  --text-secondary: #4B5563;
  --text-tertiary:  #9CA3AF;
  --text-inverse:   #FFFFFF;
  --purple-50:  #F5F3FF; --purple-100: #EDE9FE; --purple-200: #DDD6FE;
  --purple-300: #C4B5FD; --purple-500: #8B5CF6; --purple-600: #7C3AED;
  --purple-700: #6D28D9; --purple-800: #5B21B6; --purple-900: #4C1D95;
  --green-50: #ECFDF5; --green-100: #D1FAE5; --green-600: #059669; --green-700: #047857;
  --red-50:   #FEF2F2; --red-100:   #FEE2E2; --red-600:   #DC2626; --red-700:   #B91C1C;
  --amber-50: #FFFBEB; --amber-100: #FEF3C7; --amber-600: #D97706; --amber-700: #B45309;
  --blue-50:  #EFF6FF; --blue-100:  #DBEAFE; --blue-600:  #2563EB; --blue-700:  #1D4ED8;
  --radius-sm: 6px; --radius-md: 10px; --radius-lg: 14px; --radius-xl: 18px; --radius-full: 999px;
  --shadow-xs: 0 1px 2px rgba(0,0,0,0.05);
  --shadow-sm: 0 1px 4px rgba(0,0,0,0.07), 0 1px 2px rgba(0,0,0,0.04);
  --shadow-md: 0 4px 14px rgba(0,0,0,0.08), 0 2px 4px rgba(0,0,0,0.04);
  --shadow-lg: 0 12px 32px rgba(0,0,0,0.1), 0 4px 8px rgba(0,0,0,0.05);
  --font-sans:    'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  --font-display: 'Plus Jakarta Sans', 'Inter', sans-serif;
}

/* ─── Reset ─────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }

/* ─── Remove Streamlit chrome ───────────────────────────────────── */
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"], .stDeployButton, .viewerBadge_container__1QSob
{ display: none !important; }
#MainMenu, footer { visibility: hidden !important; }

/* ─── App background ────────────────────────────────────────────── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.stApp {
  background-color: var(--bg-subtle) !important;
  font-family: var(--font-sans) !important;
  color: var(--text-primary) !important;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
[data-testid="stMainBlockContainer"] {
  padding: 2rem 2.5rem 3.5rem !important;
  max-width: 1140px;
}

/* ─── Sidebar — dark ────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background-color: var(--sidebar-bg) !important;
  border-right: none !important;
  box-shadow: 2px 0 24px rgba(0,0,0,0.18) !important;
}
[data-testid="stSidebar"] > div:first-child,
[data-testid="stSidebarContent"] {
  background-color: var(--sidebar-bg) !important;
  padding: 0 !important;
}
[data-testid="stSidebar"] * { color: rgba(255,255,255,0.82) !important; }
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown div { color: rgba(255,255,255,0.65) !important; }

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  border: none !important;
  color: rgba(255,255,255,0.65) !important;
  border-radius: var(--radius-md) !important;
  font-size: 0.8125rem !important;
  font-weight: 500 !important;
  padding: 0.5625rem 0.875rem !important;
  width: 100% !important;
  text-align: left !important;
  transition: background 0.12s, color 0.12s !important;
  letter-spacing: -0.01em !important;
  margin-bottom: 2px !important;
  height: auto !important;
  box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,255,255,0.07) !important;
  color: #FFFFFF !important;
  transform: none !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  background: rgba(124,58,237,0.22) !important;
  color: #C4B5FD !important;
  border-left: 2px solid var(--purple-500) !important;
  padding-left: calc(0.875rem - 2px) !important;
  border-radius: 0 var(--radius-md) var(--radius-md) 0 !important;
  font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background: rgba(124,58,237,0.32) !important;
  color: #FFFFFF !important;
}

/* Sidebar selectbox */
[data-testid="stSidebar"] .stSelectbox > div > div {
  background: rgba(255,255,255,0.07) !important;
  border: 1px solid rgba(255,255,255,0.12) !important;
  border-radius: var(--radius-md) !important;
  color: rgba(255,255,255,0.82) !important;
  font-size: 0.8125rem !important;
}

/* ─── Scrollbar ──────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.1); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.18); }

/* ─── Streamlit element resets ──────────────────────────────────── */
.stMarkdown { margin-bottom: 0 !important; }
.element-container { margin-bottom: 0 !important; }

/* ─── Main buttons ───────────────────────────────────────────────── */
.stButton > button {
  font-family: var(--font-sans) !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  border-radius: var(--radius-md) !important;
  padding: 0.5625rem 1.25rem !important;
  border: 1.5px solid var(--border) !important;
  background: var(--surface) !important;
  color: var(--text-secondary) !important;
  transition: all 0.15s ease !important;
  cursor: pointer !important;
  letter-spacing: -0.01em !important;
  box-shadow: var(--shadow-xs) !important;
  height: auto !important;
  line-height: 1.5 !important;
}
.stButton > button:hover {
  border-color: var(--border-strong) !important;
  color: var(--text-primary) !important;
  box-shadow: var(--shadow-sm) !important;
  transform: translateY(-1px) !important;
}
.stButton > button[kind="primary"] {
  background: var(--purple-700) !important;
  border-color: var(--purple-700) !important;
  color: #FFFFFF !important;
  box-shadow: 0 2px 8px rgba(109,40,217,0.28) !important;
}
.stButton > button[kind="primary"]:hover {
  background: var(--purple-800) !important;
  border-color: var(--purple-800) !important;
  box-shadow: 0 4px 14px rgba(109,40,217,0.38) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ─── Tabs ───────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--bg-muted) !important;
  border-radius: var(--radius-md) !important;
  padding: 3px !important;
  gap: 2px !important;
  border: none !important;
  margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  border-radius: calc(var(--radius-md) - 2px) !important;
  color: var(--text-tertiary) !important;
  font-size: 0.8125rem !important;
  font-weight: 500 !important;
  padding: 0.4375rem 1rem !important;
  border: none !important;
  transition: all 0.12s !important;
  letter-spacing: -0.01em !important;
}
.stTabs [data-baseweb="tab"]:hover {
  color: var(--text-secondary) !important;
  background: rgba(255,255,255,0.6) !important;
}
.stTabs [aria-selected="true"] {
  background: var(--surface) !important;
  color: var(--text-primary) !important;
  box-shadow: var(--shadow-sm) !important;
  font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-highlight"],
.stTabs [data-baseweb="tab-border"] { display: none !important; }

/* ─── Expanders ──────────────────────────────────────────────────── */
.stExpander {
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--surface) !important;
  box-shadow: var(--shadow-xs) !important;
  margin-bottom: 0.75rem !important;
  overflow: hidden !important;
}
.stExpander > details > summary {
  padding: 1rem 1.25rem !important;
  font-size: 0.875rem !important;
  font-weight: 600 !important;
  color: var(--text-secondary) !important;
  background: transparent !important;
  border: none !important;
  cursor: pointer !important;
  transition: color 0.12s !important;
  letter-spacing: -0.01em !important;
}
.stExpander > details > summary:hover { color: var(--text-primary) !important; }
.stExpander > details[open] > summary { color: var(--text-primary) !important; }
.stExpander > details > div {
  padding: 0 1.25rem 1.25rem !important;
  border-top: 1px solid var(--border-soft) !important;
}

/* ─── Inputs ─────────────────────────────────────────────────────── */
.stSelectbox > label { display: none !important; }
.stSelectbox > div > div {
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  background: var(--surface) !important;
  font-size: 0.875rem !important;
  color: var(--text-secondary) !important;
  padding: 0.5rem 0.875rem !important;
  box-shadow: var(--shadow-xs) !important;
}
.stTextInput > div > div > input {
  border: 1.5px solid var(--border) !important;
  border-radius: var(--radius-md) !important;
  font-size: 0.875rem !important;
  padding: 0.5625rem 0.875rem !important;
  color: var(--text-primary) !important;
  background: var(--surface) !important;
  transition: border-color 0.15s, box-shadow 0.15s !important;
}
.stTextInput > div > div > input:focus {
  border-color: var(--purple-500) !important;
  box-shadow: 0 0 0 3px rgba(124,58,237,0.1) !important;
  outline: none !important;
}
.stRadio > label { font-size: 0.875rem !important; font-weight: 500 !important; color: var(--text-secondary) !important; }
hr { border: none !important; border-top: 1px solid var(--border) !important; margin: 1.5rem 0 !important; }

/* ════════════════════════════════════════════════════════════════════
   PRAXIS COMPONENT LIBRARY
   ════════════════════════════════════════════════════════════════════ */

/* ─── Page title & subtitle ─────────────────────────────────────── */
.prx-page-title {
  font-family: var(--font-display);
  font-size: 1.875rem;
  font-weight: 800;
  color: var(--text-primary);
  letter-spacing: -0.04em;
  line-height: 1.15;
  margin-bottom: 0.4375rem;
}
.prx-page-sub {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  line-height: 1.7;
  margin-bottom: 2rem;
  font-weight: 400;
  max-width: 60ch;
}

/* ─── Section label ──────────────────────────────────────────────── */
.prx-section-label {
  font-size: 0.5625rem;
  font-weight: 800;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin: 1.75rem 0 0.875rem;
  display: block;
}

/* ─── Section separator ──────────────────────────────────────────── */
.prx-section-sep {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 2.75rem 0 1.75rem;
}
.prx-section-sep-line { flex: 1; height: 1px; background: var(--border); }
.prx-section-sep-label {
  font-size: 0.5rem;
  font-weight: 800;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.16em;
  white-space: nowrap;
  padding: 0.25rem 0.875rem;
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
}

/* ─── Card system ────────────────────────────────────────────────── */
.prx-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.18s ease;
}
.prx-card:hover { box-shadow: var(--shadow-md); }
.prx-card-header {
  font-size: 0.5625rem;
  font-weight: 800;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 1.125rem;
  padding-bottom: 0.875rem;
  border-bottom: 1px solid var(--border-soft);
}
.prx-card-sm {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 1rem 1.25rem;
  margin-bottom: 0.625rem;
  box-shadow: var(--shadow-xs);
  transition: box-shadow 0.15s;
}
.prx-card-sm:hover { box-shadow: var(--shadow-sm); }

/* ─── Sidebar logo ───────────────────────────────────────────────── */
.prx-sidebar-logo {
  padding: 1.5rem 1.25rem 1rem;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  margin-bottom: 0.375rem;
}
.prx-sidebar-logo-mark {
  display: flex;
  align-items: center;
  gap: 0.5625rem;
  font-family: var(--font-display);
  font-size: 1.25rem;
  font-weight: 800;
  color: #FFFFFF;
  letter-spacing: -0.04em;
  margin-bottom: 0.25rem;
}
.prx-sidebar-logo-mark .acc { color: var(--purple-300); }
.prx-sidebar-logo-icon {
  width: 1.75rem;
  height: 1.75rem;
  background: linear-gradient(135deg, var(--purple-600), var(--purple-900));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 2px 8px rgba(124,58,237,0.45);
  flex-shrink: 0;
}
.prx-sidebar-logo-sub {
  font-size: 0.625rem;
  color: rgba(255,255,255,0.38);
  letter-spacing: 0.03em;
  margin-left: 2.3125rem;
}

/* ─── Sidebar persona ────────────────────────────────────────────── */
.prx-sidebar-persona {
  padding: 0.75rem 1rem;
  margin: 0 0.75rem 0.5rem;
  background: rgba(255,255,255,0.05);
  border-radius: var(--radius-md);
  border: 1px solid rgba(255,255,255,0.08);
}
.prx-sidebar-persona-label {
  display: block;
  font-size: 0.4375rem;
  font-weight: 800;
  color: rgba(255,255,255,0.35);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 0.1875rem;
}
.prx-sidebar-persona-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: rgba(255,255,255,0.88);
  letter-spacing: -0.01em;
}

/* ─── Sidebar nav ────────────────────────────────────────────────── */
.prx-sidebar-group {
  font-size: 0.4375rem;
  font-weight: 800;
  color: rgba(255,255,255,0.28);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  padding: 1rem 1.25rem 0.375rem;
}
.prx-sidebar-divider {
  height: 1px;
  background: rgba(255,255,255,0.07);
  margin: 0.5rem 1.25rem;
}

/* ─── Sidebar demo CTA ───────────────────────────────────────────── */
.prx-sidebar-demo-btn {
  margin: 0.75rem 0.875rem 0.5rem;
  padding: 1rem 1.125rem;
  background: linear-gradient(135deg, #5B21B6 0%, #4C1D95 100%);
  border-radius: var(--radius-md);
  border: 1px solid rgba(196,181,253,0.18);
  box-shadow: 0 2px 14px rgba(91,33,182,0.38);
  transition: box-shadow 0.2s, transform 0.15s;
  text-align: left;
  cursor: pointer;
}
.prx-sidebar-demo-btn:hover {
  box-shadow: 0 4px 20px rgba(91,33,182,0.48);
  transform: translateY(-1px);
}
.prx-sidebar-demo-label {
  font-size: 0.4375rem;
  font-weight: 800;
  color: rgba(196,181,253,0.75);
  text-transform: uppercase;
  letter-spacing: 0.14em;
  margin-bottom: 0.3125rem;
}
.prx-sidebar-demo-title {
  font-size: 0.875rem;
  font-weight: 700;
  color: #FFFFFF;
  letter-spacing: -0.02em;
  margin-bottom: 0.125rem;
}
.prx-sidebar-demo-sub {
  font-size: 0.6875rem;
  color: rgba(221,214,254,0.6);
}

/* ─── Sidebar footer ─────────────────────────────────────────────── */
.prx-sidebar-footer {
  padding: 0.875rem 1.25rem 1.25rem;
  border-top: 1px solid rgba(255,255,255,0.06);
  margin-top: 0.5rem;
}
.prx-sidebar-footer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.625rem;
  color: rgba(255,255,255,0.3);
  margin-bottom: 0.3125rem;
  letter-spacing: 0.01em;
}
.prx-sidebar-footer-item:last-child { margin-bottom: 0; }
.prx-sidebar-footer-item span { color: rgba(255,255,255,0.22); }
.prx-sidebar-footer-item b   { color: rgba(255,255,255,0.52); font-weight: 600; }

/* ─── Top bar ────────────────────────────────────────────────────── */
.prx-topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 0 1.125rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.prx-topbar-breadcrumb {
  font-size: 0.8125rem;
  color: var(--text-tertiary);
  letter-spacing: -0.01em;
}
.prx-topbar-breadcrumb b { color: var(--text-secondary); font-weight: 600; }
.prx-topbar-right { display: flex; align-items: center; gap: 0.75rem; }
.prx-topbar-tel {
  font-size: 0.6875rem;
  color: var(--text-tertiary);
  background: var(--bg-muted);
  border: 1px solid var(--border);
  border-radius: var(--radius-full);
  padding: 0.3125rem 0.75rem;
  font-variant-numeric: tabular-nums;
}

/* ─── Scan bar (Morning Briefing hero) ──────────────────────────── */
.prx-scan-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem 1.875rem;
  margin-bottom: 1.75rem;
  box-shadow: var(--shadow-sm);
  gap: 1.5rem;
}
.prx-scan-label {
  font-size: 0.5rem;
  font-weight: 800;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  margin-bottom: 0.3125rem;
}
.prx-scan-meta {
  font-size: 0.9375rem;
  color: var(--text-secondary);
  font-weight: 400;
  letter-spacing: -0.01em;
  line-height: 1.4;
}
.prx-scan-stat-wrap {
  display: flex;
  align-items: center;
  gap: 2.5rem;
  flex-shrink: 0;
}
.prx-scan-stat { text-align: center; }
.prx-scan-stat-num {
  font-family: var(--font-display);
  font-size: 2.25rem;
  font-weight: 800;
  letter-spacing: -0.055em;
  line-height: 1;
  margin-bottom: 0.25rem;
}
.prx-scan-stat-label {
  font-size: 0.5rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  white-space: nowrap;
}

/* ─── KPI queue ──────────────────────────────────────────────────── */
.prx-queue-wrap {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.5rem;
}
.prx-queue-header {
  display: grid;
  grid-template-columns: 2rem 2rem 1fr 6rem 5rem 7rem 9rem 5rem;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1.375rem;
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border);
  font-size: 0.5rem;
  font-weight: 800;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
}
.prx-queue-row {
  display: grid;
  grid-template-columns: 2rem 2rem 1fr 6rem 5rem 7rem 9rem 5rem;
  align-items: center;
  gap: 1rem;
  padding: 1.0625rem 1.375rem;
  border-bottom: 1px solid var(--border-soft);
  transition: background 0.1s;
  position: relative;
}
.prx-queue-row:last-child { border-bottom: none; }
.prx-queue-row:hover { background: var(--bg-subtle); }
.prx-queue-row.material { border-left: 3px solid var(--red-600); }
.prx-queue-row.stable   { border-left: 3px solid var(--green-600); }
.prx-queue-row.pending  { border-left: 3px solid var(--border); }
.prx-queue-priority { font-size: 0.625rem; font-weight: 700; color: var(--text-tertiary); text-align: center; }
.prx-queue-name  { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); letter-spacing: -0.01em; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.prx-queue-meta  { font-size: 0.5625rem; color: var(--text-tertiary); margin-top: 0.125rem; }
.prx-queue-values{ text-align: right; }
.prx-queue-actual{ font-family: var(--font-display); font-size: 1.0625rem; font-weight: 800; color: var(--text-primary); letter-spacing: -0.03em; line-height: 1.1; }
.prx-queue-vs    { font-size: 0.5rem; color: var(--text-tertiary); letter-spacing: 0.02em; }
.prx-queue-delta { font-size: 0.875rem; font-weight: 700; text-align: right; font-variant-numeric: tabular-nums; }
.prx-queue-delta.neg  { color: var(--red-600); }
.prx-queue-delta.pos  { color: var(--green-600); }
.prx-queue-delta.zero { color: var(--text-tertiary); }
.prx-queue-icon  { font-size: 0.875rem; }

/* ─── Investigation panel ────────────────────────────────────────── */
.prx-inv-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
  margin-bottom: 1.5rem;
}
.prx-inv-panel-head {
  display: flex; align-items: center; justify-content: space-between;
  padding: 1.125rem 1.5rem;
  background: var(--bg-subtle);
  border-bottom: 1px solid var(--border);
}
.prx-inv-panel-title { font-size: 0.9375rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.02em; }
.prx-inv-panel-body  { padding: 1.5rem; }

/* ─── Badges ─────────────────────────────────────────────────────── */
.prx-badge {
  display: inline-flex; align-items: center; gap: 0.3125rem;
  padding: 0.25rem 0.625rem;
  border-radius: var(--radius-full);
  font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.01em;
  white-space: nowrap; line-height: 1;
}
.prx-badge.critical { background: var(--red-50);    color: var(--red-700);    border: 1px solid #FECACA; }
.prx-badge.warning  { background: var(--amber-50);  color: var(--amber-700);  border: 1px solid #FDE68A; }
.prx-badge.ok       { background: var(--green-50);  color: var(--green-700);  border: 1px solid #BBF7D0; }
.prx-badge.pending  { background: #F9FAFB;           color: #6B7280;           border: 1px solid var(--border); }
.prx-badge.muted    { background: var(--bg-muted);  color: var(--text-tertiary); border: 1px solid var(--border); }
.prx-badge.info     { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-badge.purple   { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }

/* ─── Outcome pill ───────────────────────────────────────────────── */
.prx-outcome-pill {
  display: inline-flex; align-items: center; gap: 0.3125rem;
  padding: 0.3125rem 0.8125rem;
  border-radius: var(--radius-full);
  font-size: 0.75rem; font-weight: 700; letter-spacing: 0.04em;
}
.prx-outcome-pill.ANSWER  { background: var(--green-50);  color: var(--green-700);     border: 1.5px solid #BBF7D0; }
.prx-outcome-pill.QUALIFY { background: var(--amber-50);  color: var(--amber-700);     border: 1.5px solid #FDE68A; }
.prx-outcome-pill.CLARIFY { background: var(--blue-50);   color: var(--blue-700);      border: 1.5px solid var(--blue-100); }
.prx-outcome-pill.ABSTAIN { background: var(--bg-muted);  color: var(--text-tertiary); border: 1.5px solid var(--border); }

/* ─── Freshness ──────────────────────────────────────────────────── */
.prx-freshness {
  display: inline-flex; align-items: center; gap: 0.3125rem;
  font-size: 0.6875rem; color: var(--text-tertiary); font-weight: 500; white-space: nowrap;
}
.prx-status-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.prx-status-dot.green { background: var(--green-600); box-shadow: 0 0 4px rgba(5,150,105,.45); }
.prx-status-dot.amber { background: var(--amber-600); box-shadow: 0 0 4px rgba(217,119,6,.45); }
.prx-status-dot.red   { background: var(--red-600);   box-shadow: 0 0 4px rgba(220,38,38,.45); }

/* ─── Bar chart ──────────────────────────────────────────────────── */
.prx-bar-chart { padding: 0.25rem 0; }
.prx-bar-row {
  display: flex; align-items: center; gap: 0.875rem;
  padding: 0.625rem 0;
  border-bottom: 1px solid var(--border-soft);
}
.prx-bar-row:last-child { border-bottom: none; }
.prx-bar-rank  { font-size: 0.5625rem; font-weight: 700; color: var(--text-tertiary); width: 1.25rem; text-align: center; flex-shrink: 0; }
.prx-bar-label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); flex: 1; letter-spacing: -0.01em; }
.prx-bar-track { flex: 2; height: 7px; background: var(--bg-muted); border-radius: 4px; overflow: hidden; }
.prx-bar-fill  { height: 100%; border-radius: 4px; transition: width 0.45s cubic-bezier(.22,1,.36,1); }
.prx-bar-fill.c1      { background: linear-gradient(90deg, var(--purple-700), var(--purple-500)); }
.prx-bar-fill.c2      { background: linear-gradient(90deg, var(--blue-600), #60A5FA); }
.prx-bar-fill.c3      { background: linear-gradient(90deg, var(--amber-600), #FCD34D); }
.prx-bar-fill.c4      { background: linear-gradient(90deg, var(--green-600), #34D399); }
.prx-bar-fill.residual{ background: var(--border-strong); }
.prx-bar-pct { font-size: 0.875rem; font-weight: 700; color: var(--text-primary); width: 2.75rem; text-align: right; font-variant-numeric: tabular-nums; }
.prx-bar-amt { font-size: 0.8125rem; color: var(--text-secondary); width: 4.25rem; text-align: right; font-variant-numeric: tabular-nums; }
.prx-bar-method {
  font-size: 0.5rem; font-weight: 800; padding: 0.125rem 0.5rem;
  border-radius: var(--radius-full); text-transform: uppercase; letter-spacing: 0.07em; flex-shrink: 0;
}
.prx-bar-method.det  { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-bar-method.llm  { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-bar-method.ret  { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.prx-bar-method.rule { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }

/* ─── Confidence display ─────────────────────────────────────────── */
.prx-conf-wrap {
  background: var(--bg-subtle);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.375rem;
  text-align: center;
  margin-bottom: 1rem;
}
.prx-conf-score {
  font-family: var(--font-display);
  font-size: 3.75rem;
  font-weight: 800;
  letter-spacing: -0.07em;
  line-height: 1;
  margin-bottom: 0.5rem;
}
.prx-conf-score.HIGH    { color: var(--green-600); }
.prx-conf-score.MEDIUM  { color: var(--amber-600); }
.prx-conf-score.LOW     { color: var(--red-600); }
.prx-conf-score.ABSTAIN { color: var(--text-tertiary); }
.prx-conf-band {
  font-size: 0.625rem; font-weight: 800;
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.875rem;
}
.prx-conf-band.HIGH    { color: var(--green-600); }
.prx-conf-band.MEDIUM  { color: var(--amber-600); }
.prx-conf-band.LOW     { color: var(--red-600); }
.prx-conf-band.ABSTAIN { color: var(--text-tertiary); }
.prx-conf-track {
  height: 7px; background: var(--bg-muted); border-radius: 4px; overflow: hidden; margin-top: 0.5rem;
}
.prx-conf-fill { height: 100%; border-radius: 4px; transition: width 0.55s cubic-bezier(.22,1,.36,1); }
.prx-conf-fill.HIGH    { background: linear-gradient(90deg, var(--green-700), var(--green-600)); }
.prx-conf-fill.MEDIUM  { background: linear-gradient(90deg, var(--amber-700), var(--amber-600)); }
.prx-conf-fill.LOW     { background: linear-gradient(90deg, var(--red-700), var(--red-600)); }
.prx-conf-fill.ABSTAIN { background: var(--border-strong); }
.prx-conf-component-row {
  display: flex; justify-content: space-between; align-items: center;
  padding: 0.4375rem 0; border-bottom: 1px solid var(--border-soft);
  font-size: 0.8125rem;
}
.prx-conf-component-row:last-child { border-bottom: none; }
.prx-conf-comp-name { color: var(--text-secondary); }
.prx-conf-comp-val  { font-weight: 700; font-variant-numeric: tabular-nums; }
.prx-conf-comp-val.pos { color: var(--green-600); }
.prx-conf-comp-val.neg { color: var(--red-600); }
.prx-conf-comp-val.neu { color: var(--text-tertiary); }

/* ─── Evidence rows ──────────────────────────────────────────────── */
.prx-evidence-row {
  display: flex; align-items: flex-start; gap: 0.875rem;
  padding: 1rem 1.375rem;
  border-bottom: 1px solid var(--border-soft);
  transition: background 0.1s;
}
.prx-evidence-row:last-child { border-bottom: none; }
.prx-evidence-row:hover { background: var(--bg-subtle); }
.prx-ev-status-icon { font-size: 0.875rem; margin-top: 0.125rem; flex-shrink: 0; }
.prx-ev-content     { flex: 1; min-width: 0; }
.prx-ev-source   { font-size: 0.5625rem; font-weight: 800; color: var(--text-tertiary); text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 0.25rem; }
.prx-ev-statement{ font-size: 0.875rem; color: var(--text-primary); line-height: 1.55; margin-bottom: 0.25rem; }
.prx-ev-meta     { font-size: 0.6875rem; color: var(--text-tertiary); }
.prx-ev-badge {
  font-size: 0.5rem; font-weight: 800; padding: 0.1875rem 0.5rem;
  border-radius: var(--radius-full); text-transform: uppercase; letter-spacing: 0.07em; flex-shrink: 0; margin-top: 0.125rem;
}
.prx-ev-badge.supporting   { background: var(--green-50); color: var(--green-700); border: 1px solid var(--green-100); }
.prx-ev-badge.contradicting{ background: var(--red-50);   color: var(--red-700);   border: 1px solid var(--red-100); }
.prx-ev-badge.neutral      { background: var(--bg-muted); color: var(--text-tertiary); border: 1px solid var(--border); }

/* ─── Audit rows ─────────────────────────────────────────────────── */
.prx-audit-row {
  display: flex; align-items: flex-start; gap: 1rem;
  padding: 1rem 0; border-bottom: 1px solid var(--border-soft);
}
.prx-audit-row:last-child { border-bottom: none; }
.prx-audit-method-badge {
  font-size: 0.5rem; font-weight: 800; padding: 0.25rem 0.5625rem;
  border-radius: var(--radius-sm); text-transform: uppercase; letter-spacing: 0.07em;
  white-space: nowrap; flex-shrink: 0; margin-top: 0.0625rem;
}
.prx-audit-method-badge.det  { background: var(--blue-50);   color: var(--blue-700);   border: 1px solid var(--blue-100); }
.prx-audit-method-badge.llm  { background: var(--purple-50); color: var(--purple-700); border: 1px solid var(--purple-200); }
.prx-audit-method-badge.ret  { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.prx-audit-method-badge.rule { background: var(--green-50);  color: var(--green-700);  border: 1px solid var(--green-100); }
.prx-audit-content { flex: 1; min-width: 0; }
.prx-audit-title  { font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.25rem; letter-spacing: -0.01em; }
.prx-audit-detail { font-size: 0.8125rem; color: var(--text-secondary); line-height: 1.65; }
.prx-audit-formula {
  font-family: 'SF Mono', 'Fira Code', 'Monaco', monospace;
  font-size: 0.75rem; color: var(--purple-700);
  background: var(--purple-50); border: 1px solid var(--purple-100);
  border-radius: var(--radius-sm); padding: 0.5625rem 0.875rem;
  margin-top: 0.5rem; white-space: pre; overflow-x: auto;
}

/* ─── Action card ────────────────────────────────────────────────── */
.prx-action-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  margin-bottom: 1rem;
  box-shadow: var(--shadow-sm);
  transition: box-shadow 0.15s;
}
.prx-action-card:hover { box-shadow: var(--shadow-md); }
.prx-action-card-head {
  background: var(--bg-subtle);
  padding: 0.875rem 1.375rem;
  font-size: 0.5rem; font-weight: 800; color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.1em;
  border-bottom: 1px solid var(--border);
}
.prx-action-row {
  display: flex; align-items: flex-start;
  padding: 0.9375rem 1.375rem;
  border-bottom: 1px solid var(--border-soft);
  gap: 1.5rem;
}
.prx-action-row:last-child { border-bottom: none; }
.prx-action-key {
  font-size: 0.6875rem; font-weight: 700; color: var(--text-tertiary);
  width: 11rem; flex-shrink: 0; padding-top: 0.125rem;
  text-transform: uppercase; letter-spacing: 0.05em;
}
.prx-action-val { font-size: 0.9rem; color: var(--text-primary); flex: 1; line-height: 1.55; letter-spacing: -0.01em; }
.prx-action-val.purple  { color: var(--purple-700); font-weight: 600; }
.prx-action-val.success { color: var(--green-700); font-weight: 500; }
.prx-action-val.warn    { color: var(--amber-700); }

/* ─── Decision comparison cards ─────────────────────────────────── */
.prx-dec-card {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 1.375rem; box-shadow: var(--shadow-sm);
}
.prx-dec-card.memory {
  border-color: var(--purple-200); background: var(--purple-50);
  box-shadow: 0 2px 14px rgba(124,58,237,0.1);
}
.prx-dec-card-label {
  font-size: 0.5rem; font-weight: 800; color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 1rem;
}

/* ─── Memory Boost card ──────────────────────────────────────────── */
.prx-memory-boost {
  background: linear-gradient(135deg, #1E0B4B 0%, #3B0764 45%, #4C1D95 100%);
  border-radius: var(--radius-xl);
  padding: 1.625rem 1.875rem;
  margin: 1.5rem 0;
  display: flex; align-items: flex-start; gap: 1.375rem;
  position: relative; overflow: hidden;
  box-shadow: 0 8px 28px rgba(76,29,149,0.32), 0 2px 8px rgba(0,0,0,0.15);
  border: 1px solid rgba(196,181,253,0.18);
}
.prx-memory-boost::before {
  content: '';
  position: absolute; top: -60%; right: -15%;
  width: 320px; height: 320px;
  background: radial-gradient(circle, rgba(167,139,250,0.12) 0%, transparent 65%);
  pointer-events: none;
}
.prx-memory-boost-icon {
  font-size: 2.25rem; flex-shrink: 0; margin-top: 0.125rem;
  filter: drop-shadow(0 0 12px rgba(196,181,253,0.6));
}
.prx-memory-boost-body { flex: 1; }
.prx-memory-boost-label {
  font-size: 0.4375rem; font-weight: 800; color: rgba(196,181,253,0.7);
  text-transform: uppercase; letter-spacing: 0.16em; margin-bottom: 0.4375rem;
}
.prx-memory-boost-title {
  font-family: var(--font-display);
  font-size: 1.1875rem; font-weight: 700; color: #FFFFFF;
  letter-spacing: -0.03em; margin-bottom: 0.4375rem; line-height: 1.2;
}
.prx-memory-boost-sub { font-size: 0.875rem; color: rgba(221,214,254,0.78); line-height: 1.7; }
.prx-memory-boost-delta { flex-shrink: 0; text-align: right; }
.prx-memory-boost-num {
  font-family: var(--font-display);
  font-size: 3rem; font-weight: 800; color: #FFFFFF;
  letter-spacing: -0.07em; line-height: 1;
}
.prx-memory-boost-num-label {
  font-size: 0.5rem; font-weight: 800; color: rgba(196,181,253,0.65);
  text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.375rem; white-space: nowrap;
}

/* ─── Callout boxes ──────────────────────────────────────────────── */
.prx-callout {
  border-radius: var(--radius-md); padding: 0.9375rem 1.25rem;
  font-size: 0.875rem; line-height: 1.65; margin-bottom: 1rem;
  display: flex; align-items: flex-start; gap: 0.75rem;
}
.prx-callout.info   { background: var(--blue-50);   border: 1px solid var(--blue-100);   color: var(--blue-700); }
.prx-callout.warn   { background: var(--amber-50);  border: 1px solid var(--amber-100);  color: var(--amber-700); }
.prx-callout.ok     { background: var(--green-50);  border: 1px solid var(--green-100);  color: var(--green-700); }
.prx-callout.purple { background: var(--purple-50); border: 1px solid var(--purple-200); color: var(--purple-700); }
.prx-callout-icon { flex-shrink: 0; font-size: 1rem; margin-top: 0.125rem; }
.prx-callout-body b { font-weight: 700; }

/* ─── Narrative block ────────────────────────────────────────────── */
.prx-narrative {
  font-size: 0.9375rem; line-height: 1.8; color: var(--text-primary);
  padding: 1.375rem 1.5rem;
  background: var(--bg-subtle);
  border-left: 3px solid var(--purple-400, #A78BFA);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  margin-bottom: 1rem; font-style: italic;
}

/* ─── Abstain / uncertainty ──────────────────────────────────────── */
.prx-abstain-box {
  background: var(--bg-subtle); border: 1px solid var(--border);
  border-radius: var(--radius-lg); padding: 1.625rem;
  margin-bottom: 1rem; border-left: 4px solid var(--amber-600);
}
.prx-abstain-title { font-size: 1rem; font-weight: 700; color: var(--amber-700); margin-bottom: 0.5rem; letter-spacing: -0.01em; }
.prx-abstain-body  { font-size: 0.875rem; color: var(--text-secondary); line-height: 1.7; }

/* ─── Counterfactual & risk ──────────────────────────────────────── */
.prx-counterfactual {
  background: var(--green-50); border: 1px solid var(--green-100);
  border-radius: var(--radius-md); padding: 1.125rem 1.375rem;
  font-size: 0.875rem; color: var(--text-primary); line-height: 1.75; margin-bottom: 1rem;
}
.prx-risk-box {
  background: var(--amber-50); border: 1px solid var(--amber-100);
  border-radius: var(--radius-md); padding: 1.125rem 1.375rem;
  font-size: 0.875rem; color: var(--text-primary); line-height: 1.75; margin-bottom: 1rem;
}

/* ─── Learning loop diagram ──────────────────────────────────────── */
.prx-loop {
  display: flex; align-items: center; justify-content: center;
  gap: 0; padding: 1.5rem 0; flex-wrap: wrap; row-gap: 1rem;
}
.prx-loop-node {
  display: flex; flex-direction: column; align-items: center; gap: 0.375rem;
  padding: 1rem 1.125rem;
  background: var(--surface); border: 1.5px solid var(--border);
  border-radius: var(--radius-md); min-width: 6rem; text-align: center;
  transition: box-shadow 0.18s, border-color 0.18s;
}
.prx-loop-node:hover { box-shadow: var(--shadow-md); }
.prx-loop-node.active       { border-color: var(--purple-300); background: var(--purple-50); }
.prx-loop-node.memory-node  { border-color: var(--purple-500); background: linear-gradient(135deg, var(--purple-50), var(--purple-100)); }
.prx-loop-icon  { font-size: 1.5rem; }
.prx-loop-label { font-size: 0.75rem; font-weight: 700; color: var(--text-primary); letter-spacing: -0.01em; }
.prx-loop-sub   { font-size: 0.5rem; color: var(--text-tertiary); white-space: nowrap; }
.prx-loop-arrow { font-size: 1.125rem; color: var(--border-strong); padding: 0 0.25rem; flex-shrink: 0; }

/* ─── Memory status badges ───────────────────────────────────────── */
.prx-mem-status-badge {
  font-size: 0.5rem; font-weight: 800;
  padding: 0.1875rem 0.5rem;
  border-radius: var(--radius-full);
  text-transform: uppercase; letter-spacing: 0.08em; white-space: nowrap;
}
.prx-mem-status-badge.confirmed  { background: var(--green-50); color: var(--green-700); border: 1px solid var(--green-100); }
.prx-mem-status-badge.pending    { background: var(--amber-50); color: var(--amber-700); border: 1px solid var(--amber-100); }
.prx-mem-status-badge.rejected   { background: var(--red-50);   color: var(--red-700);   border: 1px solid var(--red-100); }
.prx-mem-status-badge.superseded { background: var(--bg-muted); color: var(--text-tertiary); border: 1px solid var(--border); }

/* ─── Table ──────────────────────────────────────────────────────── */
.prx-table-wrap {
  border: 1px solid var(--border); border-radius: var(--radius-lg);
  overflow: hidden; box-shadow: var(--shadow-xs); margin-bottom: 1rem;
}
.prx-table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.prx-table thead tr { background: var(--bg-subtle); border-bottom: 1px solid var(--border); }
.prx-table th {
  padding: 0.75rem 1.25rem;
  font-size: 0.5rem; font-weight: 800; color: var(--text-tertiary);
  text-transform: uppercase; letter-spacing: 0.1em; text-align: left; white-space: nowrap;
}
.prx-table td {
  padding: 0.9375rem 1.25rem; color: var(--text-secondary);
  border-bottom: 1px solid var(--border-soft); vertical-align: middle;
}
.prx-table tbody tr:last-child td { border-bottom: none; }
.prx-table tbody tr:hover td { background: var(--bg-subtle); }
.prx-table td.ok   { color: var(--green-600); font-weight: 600; }
.prx-table td.warn { color: var(--amber-600); font-weight: 600; }
.prx-table td.crit { color: var(--red-600);   font-weight: 600; }
.prx-table .mono   { font-family: 'SF Mono','Fira Code','Monaco',monospace; font-size: 0.8125rem; }

/* ─── Telemetry ──────────────────────────────────────────────────── */
.prx-tel-grid {
  background: var(--bg-muted); border: 1px solid var(--border);
  border-radius: var(--radius-full); padding: 0.375rem 1rem; display: inline-block;
}
.prx-tel-item  { font-size: 0.6875rem; color: var(--text-tertiary); }
.prx-tel-item b{ color: var(--text-secondary); font-weight: 600; }

/* ─── Feedback ───────────────────────────────────────────────────── */
.prx-feedback-ok {
  background: var(--green-50); border: 1px solid var(--green-100);
  border-radius: var(--radius-md); padding: 0.875rem 1.25rem;
  font-size: 0.875rem; color: var(--green-700); margin-bottom: 0.75rem;
}
.prx-feedback-err {
  background: var(--red-50); border: 1px solid var(--red-100);
  border-radius: var(--radius-md); padding: 0.875rem 1.25rem;
  font-size: 0.875rem; color: var(--red-700); margin-bottom: 0.75rem;
}

/* ─── Empty states ───────────────────────────────────────────────── */
.prx-empty { text-align: center; padding: 3.5rem 2rem; color: var(--text-tertiary); }
.prx-empty-icon  { font-size: 2.5rem; margin-bottom: 0.875rem; opacity: 0.35; }
.prx-empty-title { font-size: 1rem; font-weight: 600; color: var(--text-secondary); margin-bottom: 0.375rem; letter-spacing: -0.01em; }
.prx-empty-sub   { font-size: 0.875rem; color: var(--text-tertiary); line-height: 1.65; max-width: 32ch; margin: 0 auto; }

/* ─── Approve banner ─────────────────────────────────────────────── */
.prx-approve-banner {
  background: linear-gradient(135deg, #064E3B 0%, #065F46 100%);
  border-radius: var(--radius-lg); padding: 1.25rem 1.75rem;
  margin: 1.75rem 0 0.5rem;
  display: flex; align-items: center; justify-content: space-between; gap: 1.5rem;
  box-shadow: 0 4px 18px rgba(5,150,105,0.2);
  border: 1px solid rgba(52,211,153,0.18);
}
.prx-approve-banner-title { font-size: 0.9375rem; font-weight: 700; color: #ECFDF5; letter-spacing: -0.02em; margin-bottom: 0.25rem; }
.prx-approve-banner-sub   { font-size: 0.8125rem; color: rgba(167,243,208,0.85); line-height: 1.5; }

/* ─── Animations ─────────────────────────────────────────────────── */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
.prx-card, .prx-scan-bar, .prx-memory-boost, .prx-action-card, .prx-queue-wrap {
  animation: fadeInUp 0.22s ease both;
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
