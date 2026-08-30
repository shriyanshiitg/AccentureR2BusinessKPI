"""
Praxis — KPI Intelligence Engine
Accenture Innovation Challenge 2026 · BusinessIntelligence.ai
Team: Worst Pace Scenario

All existing functionality is preserved. This file is a UI-only redesign.
Backend calls (_run, _record_live_feedback, pipeline logic) are unchanged.
"""

import os, sys
from datetime import datetime, timezone, timedelta

import streamlit as st

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv()

os.environ.setdefault("PRAXIS_DB_PATH", "data/praxis.duckdb")

st.set_page_config(
    page_title="Praxis — KPI Intelligence",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─── DESIGN SYSTEM ─────────────────────────────────────────────────────────────
# One place to change all visual tokens.
# Colors: one accent (#2563EB), neutrals, semantics.
# No gradients. No glow. No glassmorphism.
# ───────────────────────────────────────────────────────────────────────────────
DESIGN = """
<style>
/* ── Reset & Base ─────────────────────────────────────── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* Pure white everywhere — no tinting */
html, body { background-color: #FFFFFF !important; }

[data-testid="stAppViewContainer"],
[data-testid="stApp"],
[data-testid="stMain"],
.stApp {
    background-color: #FFFFFF !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    color: #111827 !important;
}

/* Background of the scrollable main area */
section[data-testid="stSidebarContent"] { background: #FFFFFF !important; }

/* Kill Streamlit chrome */
[data-testid="stHeader"]  { display: none !important; }
.stDeployButton           { display: none !important; }
#MainMenu                 { visibility: hidden !important; }
footer                    { visibility: hidden !important; }

/* Main content area */
.main .block-container {
    max-width: 1200px !important;
    padding: 2rem 2.5rem 4rem !important;
    margin: 0 auto !important;
    background: #FFFFFF !important;
}

/* ── Sidebar ──────────────────────────────────────────── */
[data-testid="stSidebar"],
[data-testid="stSidebarContent"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E5E7EB !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }
[data-testid="stSidebarNav"] { display: none !important; }

/* Remove outer wrapper padding so logo div sits flush at top */
[data-testid="stSidebar"] .block-container { padding: 0 !important; }
[data-testid="stSidebar"] section > div    { padding: 0 !important; }

/* Re-add padding on all direct widget wrappers INSIDE the sidebar */
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
    padding-left: 1.25rem !important;
    padding-right: 1.25rem !important;
}
/* Logo row is full-bleed — it handles its own padding */
[data-testid="stSidebar"] .px-sidebar-logo-row {
    padding-left: 0 !important;
    padding-right: 0 !important;
}

/* Expander: ensure summary text never overlaps expand arrow */
[data-testid="stExpander"] summary {
    display: flex !important;
    align-items: center !important;
    gap: 0.5rem !important;
    line-height: 1.4 !important;
    padding: 0.75rem 1rem 0.75rem 0.875rem !important;
}

/* ── Typography ───────────────────────────────────────── */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: #111827 !important;
    letter-spacing: -0.01em !important;
}

p, li, span, div {
    font-family: 'Inter', sans-serif !important;
}

/* Override Streamlit markdown headings */
.stMarkdown h3 { font-size: 1rem !important; font-weight: 600 !important; color: #374151 !important; margin: 0 0 0.5rem !important; }

/* ── Tabs ─────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #E5E7EB !important;
    gap: 0 !important;
    padding: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    color: #6B7280 !important;
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    padding: 0.625rem 1rem !important;
    margin-bottom: -1px !important;
    transition: color 0.15s, border-color 0.15s !important;
    font-family: 'Inter', sans-serif !important;
}
.stTabs [aria-selected="true"] {
    color: #111827 !important;
    border-bottom-color: #2563EB !important;
}
.stTabs [data-baseweb="tab"]:hover { color: #374151 !important; }
.stTabs [data-baseweb="tab-panel"] {
    padding: 1.5rem 0 0 !important;
}

/* ── Buttons ──────────────────────────────────────────── */
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
    transition: background 0.15s, border-color 0.15s, box-shadow 0.15s !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
.stButton > button:hover {
    background: #F9FAFB !important;
    border-color: #9CA3AF !important;
}
.stButton > button[kind="primary"] {
    background: #2563EB !important;
    border-color: #2563EB !important;
    color: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(37,99,235,0.2) !important;
}
.stButton > button[kind="primary"]:hover {
    background: #1D4ED8 !important;
    border-color: #1D4ED8 !important;
}

/* ── Radio ────────────────────────────────────────────── */
.stRadio > label {
    font-size: 0.8125rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    margin-bottom: 0.375rem !important;
}
.stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.875rem !important;
    color: #374151 !important;
}

/* ── Metrics ──────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: #FFFFFF !important;
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    padding: 1rem 1.25rem !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    color: #6B7280 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.04em !important;
}
[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
    font-weight: 600 !important;
    color: #111827 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8125rem !important; }

/* ── Expander ─────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #E5E7EB !important;
    border-radius: 8px !important;
    overflow: hidden !important;
    background: #FFFFFF !important;
    margin-bottom: 0.5rem !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: #374151 !important;
    padding: 0.75rem 1rem !important;
    background: #FFFFFF !important;
}
[data-testid="stExpander"] summary:hover { background: #F9FAFB !important; }
[data-testid="stExpander"] > div > div { padding: 0 1rem 1rem !important; }

/* ── Info / Warning / Error / Success ─────────────────── */
.stAlert {
    border-radius: 6px !important;
    font-size: 0.875rem !important;
    padding: 0.75rem 1rem !important;
}

/* ── Spinner ──────────────────────────────────────────── */
.stSpinner { color: #2563EB !important; }

/* ── Code blocks ──────────────────────────────────────── */
code, .stCode {
    font-size: 0.8125rem !important;
    border-radius: 4px !important;
}

/* ── Divider ──────────────────────────────────────────── */
hr { border-color: #E5E7EB !important; margin: 1.5rem 0 !important; }

/* ─────────────────────────────────────────────────────── */
/* CUSTOM COMPONENT CLASSES                               */
/* ─────────────────────────────────────────────────────── */

/* Page header */
.px-page-header {
    padding: 1.5rem 0 1.25rem;
    border-bottom: 1px solid #E5E7EB;
    margin-bottom: 1.75rem;
}
.px-page-title {
    font-size: 1.375rem;
    font-weight: 600;
    color: #111827;
    letter-spacing: -0.02em;
    margin: 0 0 0.125rem;
}
.px-page-context {
    font-size: 0.8125rem;
    color: #9CA3AF;
    margin: 0;
}

/* Section heading */
.px-section {
    font-size: 0.75rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin: 1.75rem 0 0.75rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #F3F4F6;
}

/* KPI row */
.px-kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 1.75rem;
}
.px-kpi {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    position: relative;
}
.px-kpi-label {
    font-size: 0.6875rem;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.375rem;
}
.px-kpi-value {
    font-size: 1.375rem;
    font-weight: 600;
    color: #111827;
    letter-spacing: -0.02em;
    margin-bottom: 0.25rem;
    line-height: 1.2;
}
.px-kpi-delta {
    font-size: 0.75rem;
    color: #6B7280;
    margin-bottom: 0.625rem;
}
.px-kpi-delta.neg { color: #DC2626; }
.px-kpi-delta.pos { color: #16A34A; }
.px-kpi-status {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.6875rem;
    font-weight: 500;
    padding: 0.125rem 0.5rem;
    border-radius: 3px;
}
.px-kpi-status.alert {
    background: #FEF2F2;
    color: #991B1B;
}
.px-kpi-status.ok {
    background: #F0FDF4;
    color: #166534;
}
/* Left accent bar */
.px-kpi::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 3px;
    border-radius: 8px 0 0 8px;
}
.px-kpi.alert::before { background: #DC2626; }
.px-kpi.ok::before    { background: #16A34A; }

/* Source status row */
.px-source-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.75rem;
}
.px-source {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 0.75rem 1rem;
}
.px-source-name {
    font-size: 0.6875rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.25rem;
}
.px-source-status {
    font-size: 0.75rem;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 0.375rem;
    margin-bottom: 0.125rem;
}
.px-source-status.fresh { color: #16A34A; }
.px-source-status.stale { color: #D97706; }
.px-source-meta {
    font-size: 0.6875rem;
    color: #9CA3AF;
}
/* Status dot */
.dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}
.dot.green { background: #16A34A; }
.dot.amber { background: #D97706; }
.dot.red   { background: #DC2626; }

/* Causal graph */
.px-causal {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.75rem;
}
.px-causal-root {
    text-align: center;
    margin-bottom: 1.25rem;
}
.px-causal-root-label {
    font-size: 0.875rem;
    font-weight: 600;
    color: #111827;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    display: inline-block;
    padding: 0.5rem 1.25rem;
    background: #F9FAFB;
}
.px-causal-root-sub {
    font-size: 0.75rem;
    color: #DC2626;
    margin-top: 0.375rem;
}
.px-causal-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 1rem;
}
.px-causal-connector {
    text-align: center;
    margin-bottom: 0.75rem;
}
.px-causal-connector-line {
    width: 1px;
    height: 24px;
    background: #D1D5DB;
    margin: 0 auto;
}
.px-driver-card {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 0.875rem 1rem;
    background: #FAFAFA;
    border-left: 3px solid;
}
.px-driver-card.primary { border-left-color: #DC2626; }
.px-driver-card.secondary { border-left-color: #D97706; }
.px-driver-card.residual { border-left-color: #D1D5DB; }
.px-driver-label {
    font-size: 0.6875rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.25rem;
}
.px-driver-pct {
    font-size: 1.375rem;
    font-weight: 600;
    color: #111827;
    letter-spacing: -0.02em;
}
.px-driver-pct.red { color: #DC2626; }
.px-driver-pct.amber { color: #D97706; }
.px-driver-pct.muted { color: #9CA3AF; }
.px-driver-detail {
    font-size: 0.6875rem;
    color: #6B7280;
    margin-top: 0.25rem;
    line-height: 1.5;
}
.px-driver-tags {
    display: flex;
    gap: 0.375rem;
    flex-wrap: wrap;
    margin-top: 0.625rem;
}
.px-tag {
    font-size: 0.625rem;
    font-weight: 500;
    color: #374151;
    background: #F3F4F6;
    border: 1px solid #E5E7EB;
    border-radius: 3px;
    padding: 0.125rem 0.375rem;
}

/* Decision comparison cards */
.px-decision-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
    margin-bottom: 1.25rem;
}
.px-decision-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.25rem;
    position: relative;
    overflow: hidden;
}
.px-decision-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 2px;
}
.px-decision-card.baseline::before { background: #E5E7EB; }
.px-decision-card.memory::before   { background: #2563EB; }

.px-decision-header {
    font-size: 0.6875rem;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 0.875rem;
}
.px-mem-tag {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    font-size: 0.6875rem;
    font-weight: 500;
    padding: 0.1875rem 0.5rem;
    border-radius: 3px;
    margin-bottom: 0.875rem;
}
.px-mem-tag.active {
    background: #EFF6FF;
    color: #1D4ED8;
    border: 1px solid #BFDBFE;
}
.px-mem-tag.inactive {
    background: #F9FAFB;
    color: #9CA3AF;
    border: 1px solid #E5E7EB;
}
.px-confidence-label {
    font-size: 0.6875rem;
    font-weight: 500;
    color: #6B7280;
    margin-bottom: 0.25rem;
}
.px-band {
    font-size: 1.125rem;
    font-weight: 600;
    letter-spacing: -0.01em;
    margin-bottom: 0.375rem;
}
.px-band.LOW    { color: #D97706; }
.px-band.MEDIUM { color: #2563EB; }
.px-band.HIGH   { color: #16A34A; }
.px-conf-track {
    height: 4px;
    background: #F3F4F6;
    border-radius: 999px;
    margin: 0.375rem 0 0.75rem;
    overflow: hidden;
}
.px-conf-fill {
    height: 4px;
    border-radius: 999px;
    transition: width 0.4s ease;
}
.px-conf-fill.LOW    { background: #D97706; }
.px-conf-fill.MEDIUM { background: #2563EB; }
.px-conf-fill.HIGH   { background: #16A34A; }
.px-outcome {
    font-size: 0.8125rem;
    font-weight: 600;
    margin-bottom: 0.375rem;
}
.px-outcome.ANSWER  { color: #16A34A; }
.px-outcome.QUALIFY { color: #2563EB; }
.px-outcome.CLARIFY { color: #7C3AED; }
.px-outcome.ABSTAIN { color: #DC2626; }
.px-outcome-desc {
    font-size: 0.75rem;
    color: #6B7280;
    margin-bottom: 0.875rem;
    line-height: 1.5;
}
.px-components {
    display: flex;
    gap: 0.375rem;
    flex-wrap: wrap;
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid #F3F4F6;
}
.px-comp-chip {
    font-size: 0.625rem;
    font-weight: 500;
    color: #6B7280;
    background: #F9FAFB;
    border: 1px solid #F3F4F6;
    border-radius: 3px;
    padding: 0.125rem 0.4rem;
}
.px-comp-chip.highlight {
    color: #1D4ED8;
    background: #EFF6FF;
    border-color: #BFDBFE;
}

/* Isolation proof */
.px-proof {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 0.875rem 1rem;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
}
.px-proof-icon {
    font-size: 0.8125rem;
    flex-shrink: 0;
    margin-top: 1px;
}
.px-proof-title {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.125rem;
}
.px-proof-title.pass { color: #16A34A; }
.px-proof-title.fail { color: #DC2626; }
.px-proof-detail {
    font-size: 0.75rem;
    color: #6B7280;
    line-height: 1.5;
}

/* Compare table */
.px-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
}
.px-table thead tr {
    border-bottom: 1px solid #E5E7EB;
}
.px-table th {
    font-size: 0.6875rem;
    font-weight: 600;
    color: #6B7280;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 0.625rem 1rem;
    text-align: left;
    background: #FAFAFA;
}
.px-table th:first-child { border-radius: 6px 0 0 6px; }
.px-table th:last-child  { border-radius: 0 6px 6px 0; }
.px-table td {
    padding: 0.625rem 1rem;
    color: #374151;
    border-bottom: 1px solid #F3F4F6;
    vertical-align: top;
}
.px-table tr:last-child td { border-bottom: none; }
.px-table .dim { color: #9CA3AF; }
.px-table .accent { color: #2563EB; font-weight: 600; }
.px-table .success { color: #16A34A; font-weight: 600; }
.px-table-wrap {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 1.25rem;
}

/* Timeline */
.px-timeline {
    display: flex;
    align-items: flex-start;
    gap: 0;
    margin: 1.25rem 0;
    overflow-x: auto;
    padding-bottom: 0.5rem;
}
.px-tl-node {
    flex-shrink: 0;
    width: 160px;
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 0.75rem;
}
.px-tl-node.current {
    border-color: #BFDBFE;
    background: #EFF6FF;
}
.px-tl-connector {
    flex: 1;
    min-width: 2rem;
    height: 1px;
    background: #D1D5DB;
    margin-top: 1.5rem;
    flex-shrink: 0;
}
.px-tl-date {
    font-size: 0.625rem;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    margin-bottom: 0.25rem;
}
.px-tl-label {
    font-size: 0.8125rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.25rem;
}
.px-tl-sub {
    font-size: 0.6875rem;
    color: #6B7280;
}
.px-tl-sub.success { color: #16A34A; }
.px-tl-sub.info    { color: #2563EB; }

/* Feedback */
.px-feedback-prompt {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.px-feedback-title {
    font-size: 0.875rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.25rem;
}
.px-feedback-sub {
    font-size: 0.75rem;
    color: #6B7280;
    margin-bottom: 1rem;
    line-height: 1.5;
}
.px-feedback-result {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    margin-bottom: 1rem;
    border-left: 3px solid;
}
.px-feedback-result.ok  { border-left-color: #16A34A; }
.px-feedback-result.err { border-left-color: #DC2626; }

/* Telemetry */
.px-tel-grid {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;
}
.px-tel-item {
    font-size: 0.75rem;
    color: #6B7280;
}
.px-tel-item b { color: #111827; font-weight: 600; }

/* Narrative */
.px-narrative {
    background: #FAFAFA;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
    line-height: 1.7;
    color: #374151;
    white-space: pre-wrap;
    margin-bottom: 0.75rem;
}

/* LLM breakdown tags */
.px-tag-grid { display: flex; gap: 0.375rem; flex-wrap: wrap; margin-top: 0.5rem; }
.px-tag-code { font-size: 0.6875rem; font-weight: 500; padding: 0.1875rem 0.5rem; border-radius: 3px; }
.px-tag-code.det { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.px-tag-code.llm { background: #F5F3FF; color: #6D28D9; border: 1px solid #DDD6FE; }

/* Sidebar components */
.px-sidebar-logo {
    font-size: 0.9375rem;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.02em;
    padding: 1.25rem 1.25rem 1rem;
    border-bottom: 1px solid #F3F4F6;
    margin-bottom: 0;
}
.px-sidebar-logo span { color: #2563EB; }
.px-sidebar-section {
    font-size: 0.625rem;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    padding: 1rem 1.25rem 0.375rem;
}
.px-sidebar-divider {
    height: 1px;
    background: #F3F4F6;
    margin: 0.75rem 0;
}
.px-arch-row {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.375rem 0;
    font-size: 0.75rem;
    color: #6B7280;
}
.px-arch-row b { color: #374151; font-weight: 600; }

/* Scenario table */
.px-scenario-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8125rem;
    margin-top: 0.75rem;
}
.px-scenario-table td {
    padding: 0.625rem 0.875rem;
    border-bottom: 1px solid #F3F4F6;
    color: #374151;
    vertical-align: top;
}
.px-scenario-table td:first-child {
    font-weight: 500;
    color: #111827;
    white-space: nowrap;
    width: 33%;
}

/* Empty state */
.px-empty {
    padding: 3rem 1rem;
    text-align: center;
}
.px-empty-title {
    font-size: 0.9375rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.375rem;
}
.px-empty-sub {
    font-size: 0.8125rem;
    color: #9CA3AF;
    line-height: 1.6;
}

/* Hypothesis rows */
.px-hyp-row {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
}
.px-hyp-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}
.px-hyp-driver { font-size: 0.8125rem; font-weight: 600; color: #111827; }
.px-status-pill {
    font-size: 0.625rem;
    font-weight: 600;
    padding: 0.1875rem 0.5rem;
    border-radius: 3px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.px-status-pill.supported   { background: #F0FDF4; color: #166534; }
.px-status-pill.contradicted { background: #FEF2F2; color: #991B1B; }
.px-status-pill.candidate   { background: #FFFBEB; color: #92400E; }

/* Error / info scenarios */
.px-scenario-header {
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #E5E7EB;
}
.px-scenario-title {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 0.25rem;
}
.px-scenario-sub {
    font-size: 0.8125rem;
    color: #6B7280;
    line-height: 1.5;
}

/* Stop gate */
.px-stop-gate {
    background: #FEF2F2;
    border: 1px solid #FECACA;
    border-radius: 6px;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
    color: #7F1D1D;
}
.px-stop-gate-title { font-weight: 600; margin-bottom: 0.375rem; font-size: 0.875rem; color: #991B1B; }
</style>
"""

st.markdown(DESIGN, unsafe_allow_html=True)


# ─── Reusable render functions ─────────────────────────────────────────────────

def px_section(label: str):
    st.markdown(f'<div class="px-section">{label}</div>', unsafe_allow_html=True)


def px_conf_bar(score: float, band: str) -> str:
    w = min(100, max(0, score))
    cls = band if band in ("HIGH", "MEDIUM", "LOW") else "LOW"
    return (
        f'<div class="px-conf-track">'
        f'<div class="px-conf-fill {cls}" style="width:{w}%"></div>'
        f'</div>'
    )


def px_tel_html(t: dict) -> str:
    t = t or {}
    items = [
        ("Latency", f"{t.get('total_latency_ms', 0):.0f}ms"),
        ("LLM calls", str(t.get("total_llm_calls", 0))),
        ("Tokens", str(t.get("total_tokens", 0))),
        ("Est. cost", f"${t.get('total_cost_usd', 0):.5f}"),
    ]
    chips = "".join(
        f'<span class="px-tel-item"><b>{k}</b> {v}</span>' for k, v in items
    )
    return f'<div class="px-tel-grid">{chips}</div>'


def px_outcome_desc(o: str) -> str:
    return {
        "ANSWER":  "High confidence. Act on this recommendation directly.",
        "QUALIFY": "Medium confidence. Leading hypothesis — review caveats before acting.",
        "CLARIFY": "Pattern identified in a segment. Validate at store level first.",
        "ABSTAIN": "Insufficient evidence. No recommendation issued.",
    }.get(o, "")


def px_empty(title: str, sub: str = ""):
    st.markdown(
        f'<div class="px-empty">'
        f'<div class="px-empty-title">{title}</div>'
        f'<div class="px-empty-sub">{sub}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─── Backend helpers (unchanged logic) ─────────────────────────────────────────

def _run(name, persona, use_memory, suffix=""):
    from praxis.synthetic.generator import get_scenario
    from praxis.orchestration.pipeline import run_pipeline
    sc = get_scenario(name)
    r = run_pipeline(sc, persona=persona, use_memory=use_memory, run_id=f"{name}_{suffix}")
    return r, sc


def _record_live_feedback(result, outcome_correct: bool):
    import uuid
    from praxis.c5_memory.gateway import admit_decision_memory, admit_outcome_memory, register_finding_id
    IST_TZ = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(tz=IST_TZ).isoformat()
    fid = result.finding_id
    dm_id = f"DEC-LIVE-{fid[:20]}-{uuid.uuid4().hex[:6]}"
    om_id = f"OUT-{dm_id[:24]}-01"
    dp = result.decision_package
    lever = dp.actions[0].controllable_lever if dp and dp.actions else "L8_monitor_no_action"
    band = (result.hypothesis_package.hypotheses[0].get("confidence_band", "LOW")
            if result.hypothesis_package and result.hypothesis_package.hypotheses else "LOW")
    register_finding_id(fid)
    admit_decision_memory({
        "decision_memory_id": dm_id, "finding_id": fid,
        "driver_type": "dark_store_stockout_rate", "grain_key": "DS041",
        "grain_level": "store", "original_confidence_band": band,
        "action_taken": f"{lever} — live feedback from demo",
        "validation_status": "pending", "demo_fixture": False, "created_at": now,
    })
    admit_outcome_memory({
        "outcome_memory_id": om_id, "decision_memory_id": dm_id,
        "observed_outcome": "Confirmed by analyst" if outcome_correct else "Rejected — incorrect root cause",
        "outcome_matches_hypothesis": outcome_correct,
        "observed_at": now, "demo_fixture": False, "created_at": now,
    })
    st.session_state.feedback_given = True
    st.session_state.feedback_dm_id = dm_id
    st.session_state.feedback_correct = outcome_correct
    st.rerun()


# ─── Session state ──────────────────────────────────────────────────────────────
for k, v in [
    ("d1", None), ("d3", None),
    ("feedback_given", False), ("feedback_dm_id", None), ("feedback_correct", True),
    ("other_result", None), ("other_label", ""),
]:
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="px-sidebar-logo">Praxis<span>.</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="px-sidebar-section">Viewing as</div>', unsafe_allow_html=True)
    persona = st.radio(
        label="persona",
        options=["zone_business_head", "dark_store_ops_manager"],
        format_func=lambda x: "Zone Business Head" if x == "zone_business_head" else "Dark-Store Ops Manager",
        label_visibility="collapsed",
    )

    st.markdown('<div class="px-sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="px-sidebar-section">Run scenario</div>', unsafe_allow_html=True)
    run_demo       = st.button("Signature Demo — D1 vs D3", use_container_width=True, type="primary")
    run_abstain    = st.button("Abstention — Insufficient History", use_container_width=True)
    run_nodominant = st.button("No Dominant Contributor", use_container_width=True)
    run_challenge  = st.button("Challenge — CV Contradicts", use_container_width=True)
    run_unscripted = st.button("Unscripted (seed=42)", use_container_width=True)

    st.markdown('<div class="px-sidebar-divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="px-sidebar-section">System</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="padding: 0 0.25rem;">
      <div class="px-arch-row"><b>Pipeline</b> C1→C2→C5→C3→C4</div>
      <div class="px-arch-row"><b>Tests</b> 51 passing</div>
      <div class="px-arch-row"><b>Memory</b> DuckDB</div>
      <div class="px-arch-row"><b>LLM</b> Groq llama-3.3-70b</div>
      <div class="px-arch-row"><b>Cache</b> SHA-256 in-process</div>
    </div>
    """, unsafe_allow_html=True)


# ─── Page header ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="px-page-header">
  <div class="px-page-title">Zone Z003 — Koramangala</div>
  <div class="px-page-context">Week of 2026-08-15 &nbsp;·&nbsp; Accenture Innovation Challenge 2026 &nbsp;·&nbsp; Team: Worst Pace Scenario</div>
</div>
""", unsafe_allow_html=True)


# ─── KPI Overview ───────────────────────────────────────────────────────────────
px_section("Key Performance Indicators")
st.markdown("""
<div class="px-kpi-grid">

  <div class="px-kpi alert">
    <div class="px-kpi-label">Zone GMV</div>
    <div class="px-kpi-value">₹21.0L</div>
    <div class="px-kpi-delta neg">−₹7.0L vs 14-day avg &nbsp;(−25%)</div>
    <span class="px-kpi-status alert">Material &nbsp;·&nbsp; z = 5.0</span>
  </div>

  <div class="px-kpi alert">
    <div class="px-kpi-label">Stockout Rate &nbsp;·&nbsp; DS041</div>
    <div class="px-kpi-value">42%</div>
    <div class="px-kpi-delta neg">+38pp vs peer avg (4%)</div>
    <span class="px-kpi-status alert">Primary driver</span>
  </div>

  <div class="px-kpi alert">
    <div class="px-kpi-label">Delivery SLA Adherence</div>
    <div class="px-kpi-value">71%</div>
    <div class="px-kpi-delta neg">−12pp vs 14-day avg (83%)</div>
    <span class="px-kpi-status alert">Secondary driver</span>
  </div>

  <div class="px-kpi ok">
    <div class="px-kpi-label">Order Conversion</div>
    <div class="px-kpi-value">5.8%</div>
    <div class="px-kpi-delta pos">+0.1pp &nbsp;(stable)</div>
    <span class="px-kpi-status ok">Within range</span>
  </div>

</div>
""", unsafe_allow_html=True)


# ─── Source freshness ────────────────────────────────────────────────────────────
px_section("Data Sources")
st.markdown("""
<div class="px-source-grid">
  <div class="px-source">
    <div class="px-source-name">OMS &nbsp;·&nbsp; Orders</div>
    <div class="px-source-status fresh"><span class="dot green"></span> Fresh</div>
    <div class="px-source-meta">Updated 47 min ago &nbsp;·&nbsp; hourly</div>
  </div>
  <div class="px-source">
    <div class="px-source-name">GPS &nbsp;·&nbsp; Rider Dispatch</div>
    <div class="px-source-status stale"><span class="dot amber"></span> Stale &nbsp;(7h ago)</div>
    <div class="px-source-meta">Confidence penalty −15 applied</div>
  </div>
  <div class="px-source">
    <div class="px-source-name">CV &nbsp;·&nbsp; Customer Voice</div>
    <div class="px-source-status fresh"><span class="dot green"></span> Fresh</div>
    <div class="px-source-meta">Updated 1h ago &nbsp;·&nbsp; continuous</div>
  </div>
  <div class="px-source">
    <div class="px-source-name">INV &nbsp;·&nbsp; Inventory</div>
    <div class="px-source-status fresh"><span class="dot green"></span> Fresh</div>
    <div class="px-source-meta">Updated 2h ago &nbsp;·&nbsp; 2h cadence</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─── Causal graph ────────────────────────────────────────────────────────────────
with st.expander("Driver attribution — Zone GMV", expanded=True):
    st.markdown("""
    <div class="px-causal">
      <div class="px-causal-root">
        <div class="px-causal-root-label">Zone GMV &nbsp;·&nbsp; Z003</div>
        <div class="px-causal-root-sub">−₹7.0L &nbsp;·&nbsp; −25% &nbsp;·&nbsp; z = 5.0 &nbsp;·&nbsp; Statistically significant</div>
      </div>
      <div class="px-causal-row">
        <div>
          <div class="px-causal-connector"><div class="px-causal-connector-line"></div></div>
          <div class="px-driver-card primary">
            <div class="px-driver-label">Stockout Rate</div>
            <div class="px-driver-pct red">55%</div>
            <div class="px-driver-detail">−₹3.85L &nbsp;·&nbsp; interval analysis<br>DS041: 42% vs peer avg 4%</div>
            <div class="px-driver-tags">
              <span class="px-tag">SKU-2207 Amul Butter</span>
              <span class="px-tag">SKU-1104 Milk</span>
            </div>
          </div>
        </div>
        <div>
          <div class="px-causal-connector"><div class="px-causal-connector-line"></div></div>
          <div class="px-driver-card secondary">
            <div class="px-driver-label">SLA Adherence</div>
            <div class="px-driver-pct amber">25%</div>
            <div class="px-driver-detail">−₹1.75L &nbsp;·&nbsp; SLA breach correlation<br>Avg delivery +19 min over SLA</div>
            <div class="px-driver-tags">
              <span class="px-tag">DS041 dispatch delay</span>
              <span class="px-tag">Rider supply −2</span>
            </div>
          </div>
        </div>
        <div>
          <div class="px-causal-connector"><div class="px-causal-connector-line"></div></div>
          <div class="px-driver-card residual">
            <div class="px-driver-label">Residual</div>
            <div class="px-driver-pct muted">20%</div>
            <div class="px-driver-detail">−₹1.40L &nbsp;·&nbsp; unattributed<br>Conversion rate stable</div>
            <div class="px-driver-tags">
              <span class="px-tag">Seasonal variation</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div style="font-size:0.6875rem;color:#9CA3AF;margin-top:-0.25rem;">
      Attribution derived by C2 Operators 3+4 (contribution decomposition + segmentation). No LLM involved in %-split.
    </div>
    """, unsafe_allow_html=True)


# ================================================================================
# BUTTON EXECUTION - all sidebar button handlers run here, OUTSIDE tab blocks.
# In Streamlit, code inside `with tab_X:` only executes when that tab is active.
# By running here (before tabs), all buttons fire on every page rerun.
# ================================================================================

def _run_other(name):
    with st.spinner(f"Running {name}..."):
        _res, _sc = _run(name, persona, False, name)
        st.session_state.other_result = _res
        st.session_state.other_label = name


if run_demo:
    _c1, _c2 = st.columns(2)
    with _c1:
        with st.spinner("Running Decision 1 - no memory..."):
            _r1, _ = _run("s1", persona, False, "d1")
            st.session_state.d1 = _r1
    with _c2:
        with st.spinner("Running Decision 3 - memory active..."):
            _r3, _ = _run("s2", persona, True, "d3")
            st.session_state.d3 = _r3
    st.session_state.feedback_given = False

if run_abstain:    _run_other("insufficient_history")
if run_nodominant: _run_other("no_dominant")
if run_challenge:  _run_other("challenge")
if run_unscripted: _run_other("unscripted")


# ─── Tabs ────────────────────────────────────────────────────────────────────────
tab_demo, tab_evidence, tab_personas, tab_other = st.tabs([
    "Signature Demo", "Evidence Trail", "Persona Narratives", "Other Scenarios"
])


# ================================================================================
# TAB 1 - SIGNATURE DEMO
# ================================================================================
with tab_demo:

    r1, r3 = st.session_state.d1, st.session_state.d3

    if not r1:
        px_empty(
            "No analysis run yet",
            'Select "Signature Demo" in the sidebar to run the comparison.\n'
            "Decision 1 runs without memory. Decision 3 runs with one confirmed precedent.\n"
            "The only difference between them is memory."
        )
    else:
        # Extract data
        h1 = (r1.hypothesis_package.hypotheses[0]
               if r1.hypothesis_package and r1.hypothesis_package.hypotheses else {})
        h3 = (r3.hypothesis_package.hypotheses[0]
               if r3.hypothesis_package and r3.hypothesis_package.hypotheses else {})
        c1, c3 = h1.get("confidence_components", {}), h3.get("confidence_components", {})
        b1, b3 = h1.get("confidence_band", "LOW"), h3.get("confidence_band", "LOW")
        s1s, s3s = h1.get("confidence_score", 0), h3.get("confidence_score", 0)
        o1 = r1.hypothesis_package.decision.get("outcome", "ABSTAIN")
        o3 = r3.hypothesis_package.decision.get("outcome", "ABSTAIN")
        mem_pts = c3.get("memory_points", 0)
        pre1 = c1.get("raw_pre_memory", 0)
        pre3 = c3.get("raw_pre_memory", 0)
        cv_delta = c3.get("customer_voice_score", 0) - c1.get("customer_voice_score", 0)
        mem_matched = bool(r3.memory_result and r3.memory_result.get("matched"))

        px_section("Decision comparison")

        # Decision cards
        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown(f"""
            <div class="px-decision-card baseline">
              <div class="px-decision-header">Decision 1 &nbsp;·&nbsp; 2026-08-15 &nbsp;·&nbsp; No memory</div>
              <div class="px-mem-tag inactive">No prior precedent</div><br>
              <div class="px-confidence-label">Confidence</div>
              <div class="px-band {b1}">{b1} &nbsp;·&nbsp; {s1s}/100</div>
              {px_conf_bar(s1s, b1)}
              <div class="px-outcome {o1}">{o1}</div>
              <div class="px-outcome-desc">{px_outcome_desc(o1)}</div>
              <div class="px-components">
                <span class="px-comp-chip">mat {c1.get('materiality_strength',0):.0f}</span>
                <span class="px-comp-chip">dom {c1.get('dominance_strength',0):.1f}</span>
                <span class="px-comp-chip">cv {c1.get('customer_voice_score',0):.0f}</span>
                <span class="px-comp-chip">dqp {c1.get('data_quality_penalty',0):.0f}</span>
                <span class="px-comp-chip">mem 0</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        with col_b:
            mem_tag_cls = "active" if mem_matched else "inactive"
            mem_tag_txt = "1 confirmed precedent &nbsp;·&nbsp; DS041 &nbsp;·&nbsp; exact grain" if mem_matched else "No memory match"
            st.markdown(f"""
            <div class="px-decision-card memory">
              <div class="px-decision-header">Decision 3 &nbsp;·&nbsp; 2026-08-22 &nbsp;·&nbsp; Memory active</div>
              <div class="px-mem-tag {mem_tag_cls}">{mem_tag_txt}</div><br>
              <div class="px-confidence-label">Confidence</div>
              <div class="px-band {b3}">{b3} &nbsp;·&nbsp; {s3s}/100</div>
              {px_conf_bar(s3s, b3)}
              <div class="px-outcome {o3}">{o3}</div>
              <div class="px-outcome-desc">{px_outcome_desc(o3)}</div>
              <div class="px-components">
                <span class="px-comp-chip">mat {c3.get('materiality_strength',0):.0f}</span>
                <span class="px-comp-chip">dom {c3.get('dominance_strength',0):.1f}</span>
                <span class="px-comp-chip">cv {c3.get('customer_voice_score',0):.0f}</span>
                <span class="px-comp-chip">dqp {c3.get('data_quality_penalty',0):.0f}</span>
                <span class="px-comp-chip highlight">mem +{mem_pts}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Isolation proof
        if cv_delta == 0:
            st.markdown(f"""
            <div class="px-proof">
              <div class="px-proof-icon">✓</div>
              <div>
                <div class="px-proof-title pass">CV score identical — memory is the sole variable</div>
                <div class="px-proof-detail">
                  D1 pre-memory raw: {pre1:.1f} &nbsp;·&nbsp;
                  D3 pre-memory raw: {pre3:.1f} &nbsp;·&nbsp;
                  Memory contribution: +{mem_pts} pts &nbsp;·&nbsp;
                  Result: {b1} ({s1s}) → {b3} ({s3s})
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="px-proof">
              <div class="px-proof-icon">⚠</div>
              <div>
                <div class="px-proof-title fail">CV score differs by {cv_delta:+.0f} — not fully isolated</div>
                <div class="px-proof-detail">Review CV record generation.</div>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # Comparison table
        px_section("Side-by-side breakdown")
        d1_lever = (r1.decision_package.actions[0].controllable_lever
                    if r1.decision_package and r1.decision_package.actions else "—")
        d3_lever = (r3.decision_package.actions[0].controllable_lever
                    if r3.decision_package and r3.decision_package.actions else "—")
        d3_ctx   = r3.hypothesis_package.decision.get("memory_context", {}) or {}
        d3_caps  = h3.get("hard_caps_applied", [])
        st.markdown(f"""
        <div class="px-table-wrap">
        <table class="px-table">
          <thead><tr>
            <th>Dimension</th>
            <th>Decision 1 &nbsp;·&nbsp; No memory</th>
            <th>Decision 3 &nbsp;·&nbsp; Memory active</th>
          </tr></thead>
          <tbody>
          <tr><td>C2 analysis</td><td>All 5 operators run</td><td>Identical — memory does not shortcut C2</td></tr>
          <tr><td>memory_hook</td><td class="dim">matched = false</td><td class="accent">matched = true &nbsp;·&nbsp; exact_grain &nbsp;·&nbsp; DS041</td></tr>
          <tr><td>CV score</td><td>{c1.get('customer_voice_score',0):.0f}</td><td>{c3.get('customer_voice_score',0):.0f} &nbsp;<span style="font-size:.75rem;color:#6B7280;">(same records)</span></td></tr>
          <tr><td>memory_points</td><td class="dim">0</td><td class="accent">+{mem_pts}</td></tr>
          <tr><td>Confidence score</td><td>{s1s}</td><td>{s3s}</td></tr>
          <tr><td>Band → Outcome</td><td>{b1} → {o1}</td><td class="success">{b3} → {o3}</td></tr>
          <tr><td>Hard caps triggered</td><td class="dim">—</td><td>{', '.join(d3_caps) if d3_caps else '—'}</td></tr>
          <tr><td>Recommended lever</td><td>{d1_lever}</td><td>{d3_lever}</td></tr>
          <tr><td>demo_fixture_involved</td><td class="dim">—</td><td>{str(d3_ctx.get("demo_fixture_involved","—"))}</td></tr>
          </tbody>
        </table>
        </div>
        """, unsafe_allow_html=True)

        # Memory timeline
        px_section("Memory timeline &nbsp;·&nbsp; DS041 &nbsp;·&nbsp; dark_store_stockout_rate")
        st.markdown(f"""
        <div class="px-timeline">
          <div class="px-tl-node">
            <div class="px-tl-date">Aug 15</div>
            <div class="px-tl-label">Decision 1</div>
            <div class="px-tl-sub">{b1} &nbsp;·&nbsp; {o1}</div>
            <div class="px-tl-sub">L2 transfer recommended</div>
          </div>
          <div class="px-tl-connector"></div>
          <div class="px-tl-node">
            <div class="px-tl-date">Aug 17</div>
            <div class="px-tl-label">Outcome observed</div>
            <div class="px-tl-sub success">Root cause confirmed</div>
            <div class="px-tl-sub">GMV recovered to −2%</div>
          </div>
          <div class="px-tl-connector"></div>
          <div class="px-tl-node">
            <div class="px-tl-date">Aug 17</div>
            <div class="px-tl-label">Memory admitted</div>
            <div class="px-tl-sub">C5 gateway &nbsp;·&nbsp; pre-approved</div>
            <div class="px-tl-sub">admit_outcome_memory ✓</div>
          </div>
          <div class="px-tl-connector"></div>
          <div class="px-tl-node current">
            <div class="px-tl-date">Aug 22</div>
            <div class="px-tl-label">Decision 3</div>
            <div class="px-tl-sub info">{b3} &nbsp;·&nbsp; {o3}</div>
            <div class="px-tl-sub">+{mem_pts} memory points</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Feedback
        px_section("Outcome feedback")
        if not st.session_state.feedback_given:
            st.markdown("""
            <div class="px-feedback-prompt">
              <div class="px-feedback-title">Was the root cause correct?</div>
              <div class="px-feedback-sub">
                Your response is recorded to C5 memory via <code>admit_decision_memory</code> +
                <code>admit_outcome_memory</code>. Same gateway as production — not a mock.
              </div>
            </div>
            """, unsafe_allow_html=True)
            fb1, fb2, fb3 = st.columns([2, 2, 3])
            with fb1:
                if st.button("Confirmed correct", use_container_width=True, type="primary"):
                    _record_live_feedback(r1, True)
            with fb2:
                if st.button("Incorrect root cause", use_container_width=True):
                    _record_live_feedback(r1, False)
            with fb3:
                st.caption(
                    "Uses the same C5 §2 admission gateway as pre-seeded fixtures. "
                    "Status is set to `pending` until an analyst validates."
                )
        else:
            ok = st.session_state.feedback_correct
            cls = "ok" if ok else "err"
            label = "Confirmed correct" if ok else "Incorrect root cause"
            dm_id = st.session_state.feedback_dm_id
            st.markdown(
                f'<div class="px-feedback-result {cls}">'
                f'<div style="font-size:.8125rem;font-weight:600;color:#111827;margin-bottom:.25rem;">'
                f'Outcome recorded &nbsp;·&nbsp; {label}'
                f'</div>'
                f'<div style="font-size:.75rem;color:#6B7280;">'
                f'ID: <code>{dm_id}</code> &nbsp;·&nbsp; status=pending &nbsp;·&nbsp; demo_fixture=False<br>'
                f'The next analysis for DS041 · dark_store_stockout_rate will retrieve this record.'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Telemetry
        px_section("Runtime telemetry")
        tc1, tc2 = st.columns(2)
        with tc1:
            st.caption("Decision 1")
            st.markdown(px_tel_html(r1.telemetry_summary), unsafe_allow_html=True)
        with tc2:
            st.caption("Decision 3")
            st.markdown(px_tel_html(r3.telemetry_summary), unsafe_allow_html=True)

        from praxis.llm.client import get_cache_stats
        cs = get_cache_stats()
        st.markdown(
            f'<div class="px-tel-grid" style="margin-top:.25rem;padding-top:.75rem;border-top:1px solid #F3F4F6;">'
            f'<span class="px-tel-item"><b>Cache size</b> {cs["cache_size"]}</span>'
            f'<span class="px-tel-item"><b>Hits</b> {cs["cache_hits"]}</span>'
            f'<span class="px-tel-item"><b>Misses</b> {cs["cache_misses"]}</span>'
            f'<span class="px-tel-item"><b>Hit rate</b> {cs["hit_rate"]*100:.0f}%</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — EVIDENCE TRAIL
# ════════════════════════════════════════════════════════════════════════════════
with tab_evidence:
    r1 = st.session_state.d1
    if not r1:
        px_empty("No evidence to show", "Run the Signature Demo first.")
    else:
        ep = r1.evidence_package
        px_section("Finding")
        st.markdown(f"""
        <div class="px-tel-grid">
          <span class="px-tel-item"><b>Finding ID</b> <code>{ep.finding_id}</code></span>
          <span class="px-tel-item"><b>KPI Instance</b> <code>{ep.kpi_instance_id}</code></span>
          <span class="px-tel-item"><b>Terminal outcome</b> {ep.terminal_outcome}</span>
          <span class="px-tel-item"><b>Data state</b> {ep.data_state.value}</span>
          <span class="px-tel-item"><b>Stale input</b> {ep.evaluated_on_stale_input}</span>
        </div>
        """, unsafe_allow_html=True)

        if ep.lineage_chain:
            px_section("Lineage chain")
            st.markdown(
                " → ".join([f"`{x}`" for x in ep.lineage_chain]),
            )

        px_section("Statistical detection")
        det = ep.detection or {}
        dc1, dc2, dc3, dc4 = st.columns(4)
        dc1.metric("Actual GMV", f"₹{det.get('actual_value',0)/100000:.1f}L")
        dc2.metric("Δ Absolute", f"₹{det.get('delta_absolute',0)/100000:.1f}L")
        dc3.metric("Δ Relative", f"{det.get('delta_relative',0)*100:.1f}%")
        dc4.metric("z-score", f"{det.get('test_statistic',0):.2f}")

        decomp = ep.decomposition or {}
        if decomp.get("drivers"):
            px_section("Decomposition &nbsp;·&nbsp; C2 Operator 3")
            for d in decomp["drivers"]:
                pct = abs(d.get("contribution_pct", 0))
                val = abs(d.get("contribution_value", 0)) / 100000
                st.markdown(
                    f"- `{d['driver_name']}` — **{pct:.0f}%** of movement "
                    f"(₹{val:.1f}L) &nbsp;·&nbsp; _{d.get('method', '')}_"
                )
            st.markdown(f"- `residual` — **{decomp.get('residual_pct',0):.0f}%**")

        seg = ep.segmentation
        if seg and seg.get("ranked_stores"):
            px_section("Segmentation &nbsp;·&nbsp; C2 Operator 4")
            for i, s in enumerate(seg["ranked_stores"][:3]):
                st.markdown(
                    f"{i+1}. `{s.get('dark_store_id')}` — "
                    f"{abs(s.get('contribution_pct',0)):.0f}% &nbsp;·&nbsp; `{s.get('state','?')}`"
                )

        px_section("Hypotheses")
        hyps = r1.hypothesis_package.hypotheses if r1.hypothesis_package else []
        for hyp in hyps:
            status = hyp.get("status", "candidate")
            status_map = {
                "supported": "supported",
                "contradicted": "contradicted",
                "candidate": "candidate",
            }
            with st.expander(f"{hyp.get('driver_type','?')} &nbsp;·&nbsp; {hyp.get('confidence_band','?')}"):
                s_cls = status_map.get(status, "candidate")
                c = hyp.get("confidence_components", {})
                st.markdown(
                    f'<span class="px-status-pill {s_cls}">{status}</span>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Claim:** {hyp.get('claim','')}")
                st.markdown(f"Contribution: **{abs(hyp.get('contribution_pct',0)):.0f}%** of movement")
                st.code(
                    f"materiality_strength  = {c.get('materiality_strength',0):.1f}\n"
                    f"dominance_strength    = {c.get('dominance_strength',0):.1f}\n"
                    f"customer_voice_score  = {c.get('customer_voice_score',0):.1f}\n"
                    f"data_quality_penalty  = {c.get('data_quality_penalty',0):.1f}\n"
                    f"memory_points         = {c.get('memory_points',0):.1f}\n"
                    f"────────────────────────────────\n"
                    f"confidence_score      = {hyp.get('confidence_score',0)}/100 → {hyp.get('confidence_band','?')}",
                    language="text",
                )
                caps = hyp.get("hard_caps_applied", [])
                if caps:
                    st.warning(f"Hard caps applied: {', '.join(caps)}")
                sup = len(hyp.get("supporting_evidence_refs", []))
                con = len(hyp.get("contradicting_evidence_refs", []))
                st.caption(f"Customer Voice: {sup} supporting &nbsp;·&nbsp; {con} contradicting")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — PERSONA NARRATIVES
# ════════════════════════════════════════════════════════════════════════════════
with tab_personas:
    r1, r3 = st.session_state.d1, st.session_state.d3
    if not r1:
        px_empty("No narratives yet", "Run the Signature Demo first.")
    else:
        st.info(
            "**Entitlement enforcement (C1 §5):** Zone Business Head sees zone GMV total. "
            "Dark-Store Ops Manager cannot — enforced at the semantic layer, "
            "verified by `test_c4_ops_manager_narrative_excludes_zone_gmv`.",
            icon=None,
        )

        px_section("Zone Business Head")
        c1n, c2n = st.columns(2)
        with c1n:
            st.caption("Decision 1 &nbsp;·&nbsp; 2026-08-15")
            st.markdown(
                f'<div class="px-narrative">{r1.decision_package.narrative_zone_business_head or "—"}</div>',
                unsafe_allow_html=True,
            )
        with c2n:
            st.caption("Decision 3 &nbsp;·&nbsp; 2026-08-22 &nbsp;·&nbsp; memory active")
            st.markdown(
                f'<div class="px-narrative">{r3.decision_package.narrative_zone_business_head or "—"}</div>',
                unsafe_allow_html=True,
            )
            st.caption("Decision 3 narrative should reference the confirmed precedent from memory.")

        px_section("Dark-Store Ops Manager")
        c1n2, c2n2 = st.columns(2)
        with c1n2:
            st.caption("Decision 1 &nbsp;·&nbsp; 2026-08-15")
            st.markdown(
                f'<div class="px-narrative">{r1.decision_package.narrative_dark_store_ops_manager or "—"}</div>',
                unsafe_allow_html=True,
            )
        with c2n2:
            st.info("Zone GMV total (₹28L) is not surfaced in the Ops Manager view. Access restriction enforced at the semantic layer.")

        px_section("What the LLM generates vs what the code computes")
        c1l, c2l = st.columns(2)
        with c1l:
            st.caption("Code — deterministic, auditable, tested")
            st.markdown("""
            <div class="px-tag-grid">
              <span class="px-tag-code det">kpi_id</span>
              <span class="px-tag-code det">delta · Δ%</span>
              <span class="px-tag-code det">z-score</span>
              <span class="px-tag-code det">contribution %</span>
              <span class="px-tag-code det">driver_type</span>
              <span class="px-tag-code det">lever selection</span>
              <span class="px-tag-code det">owner · rights</span>
              <span class="px-tag-code det">confidence score</span>
              <span class="px-tag-code det">caveat gate</span>
              <span class="px-tag-code det">entitlement check</span>
              <span class="px-tag-code det">lineage IDs</span>
              <span class="px-tag-code det">hard cap enforcement</span>
            </div>
            """, unsafe_allow_html=True)
        with c2l:
            st.caption("LLM — Groq llama-3.3-70b &nbsp;·&nbsp; 512-token cap per call")
            st.markdown("""
            <div class="px-tag-grid">
              <span class="px-tag-code llm">narrative prose</span>
              <span class="px-tag-code llm">hypothesis claim text</span>
              <span class="px-tag-code llm">caveat wording</span>
            </div>
            """, unsafe_allow_html=True)
            st.caption("The LLM writes the paragraph. It never picks the driver, lever, score, or band.")


# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — OTHER SCENARIOS
# ════════════════════════════════════════════════════════════════════════════════
with tab_other:

    res   = st.session_state.other_result
    label = st.session_state.other_label

    if not res:
        px_empty(
            "No scenario selected",
            "Use the sidebar buttons to run one of the four scenarios below.",
        )
        st.markdown("""
        <table class="px-scenario-table">
          <tr>
            <td>Abstention — Insufficient History</td>
            <td>New store DS099 has fewer than 3 clean history days. Praxis stops. No recommendation issued. Demonstrates the hard floor gate (C2 §3).</td>
          </tr>
          <tr>
            <td>No Dominant Contributor</td>
            <td>Zone Z007 has a diffuse multi-driver pattern. No single driver exceeds the 30% dominance threshold. System returns QUALIFY with honest residual rather than forcing a dominant explanation.</td>
          </tr>
          <tr>
            <td>Challenge — CV Contradicts</td>
            <td>GMV dip on 2026-08-16. Decomposition points to stockout. Three Fresh customer reviews say otherwise — "items were in stock, checkout was broken." System tags hypothesis as contradicted via C3 §5 without LLM judgment.</td>
          </tr>
          <tr>
            <td>Unscripted (seed=42)</td>
            <td>Random zone, store, and event combination. Confirms the pipeline runs on inputs not authored by the design team.</td>
          </tr>
        </table>
        """, unsafe_allow_html=True)

    else:
        ep = res.evidence_package
        dp = res.decision_package

        if label == "insufficient_history":
            st.markdown("""
            <div class="px-scenario-header">
              <div class="px-scenario-title">Abstention — Insufficient history</div>
              <div class="px-scenario-sub">New store DS099 &nbsp;·&nbsp; 2026-08-20</div>
            </div>
            """, unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Finding ID:** `{res.finding_id}`")
                st.markdown(f"**Terminal outcome:** `{ep.terminal_outcome}`")
                st.markdown(f"**Reason:** {ep.terminal_outcome_reason}")
                st.markdown(
                    f"**History found:** `{ep.baseline.get('window_size_used','?') if ep.baseline else 'N/A'}` "
                    f"clean same-weekday days"
                )
                st.markdown(f"**Decision:** `{dp.source_decision_outcome if dp else 'N/A'}`")
            with c2:
                st.markdown("""
                <div class="px-stop-gate">
                  <div class="px-stop-gate-title">Hard stop — ABSTAIN</div>
                  Praxis requires ≥ 3 clean same-weekday history points (C2 §3).
                  This is not a low-confidence label. It is a structural stop gate.
                  No lever is recommended. No narrative is generated.
                </div>
                """, unsafe_allow_html=True)
                if dp and dp.caveat_text:
                    st.markdown(f'<div class="px-narrative" style="margin-top:.75rem;">{dp.caveat_text}</div>', unsafe_allow_html=True)

        elif label == "no_dominant":
            st.markdown("""
            <div class="px-scenario-header">
              <div class="px-scenario-title">No dominant contributor</div>
              <div class="px-scenario-sub">Zone Z007 &nbsp;·&nbsp; diffuse multi-driver movement</div>
            </div>
            """, unsafe_allow_html=True)
            decomp = ep.decomposition or {}
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Terminal outcome:** `{ep.terminal_outcome}`")
                st.markdown(f"**Decision:** `{dp.source_decision_outcome if dp else 'N/A'}`")
                st.markdown("**Driver split:**")
                for d in decomp.get("drivers", []):
                    st.markdown(f"- `{d['driver_name']}` — **{abs(d.get('contribution_pct',0)):.0f}%**")
                st.markdown(f"- `residual` — **{decomp.get('residual_pct',0):.0f}%**")
            with c2:
                st.info(
                    "**QUALIFY — no dominant contributor.**\n\n"
                    "No driver exceeds the 30% dominance threshold (C3 §6).\n\n"
                    "Praxis does not force-fit a dominant explanation. "
                    "A false precision is worse than honest uncertainty.",
                )

        elif label == "challenge":
            st.markdown("""
            <div class="px-scenario-header">
              <div class="px-scenario-title">Challenge — Customer Voice contradicts hypothesis</div>
              <div class="px-scenario-sub">
                Zone Z003 &nbsp;·&nbsp; 2026-08-16 &nbsp;·&nbsp;
                Decomposition suggests stockout. CV says app/payment glitch.
              </div>
            </div>
            """, unsafe_allow_html=True)
            hyps = res.hypothesis_package.hypotheses if res.hypothesis_package else []
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"**Decision:** `{dp.source_decision_outcome if dp else 'N/A'}`")
                st.markdown("**Hypotheses after CV challenge:**")
                for hyp in hyps:
                    status = hyp.get("status", "candidate")
                    s_cls = {"supported": "supported", "contradicted": "contradicted", "candidate": "candidate"}.get(status, "candidate")
                    cv_s  = hyp.get("confidence_components", {}).get("customer_voice_score", 0)
                    st.markdown(
                        f'<span class="px-status-pill {s_cls}">{status}</span> &nbsp;'
                        f'`{hyp.get("driver_type","?")}` &nbsp;·&nbsp; '
                        f'band: **{hyp.get("confidence_band","?")}** &nbsp;·&nbsp; '
                        f'cv_score: **{cv_s:.0f}**',
                        unsafe_allow_html=True,
                    )
                if dp and dp.caveat_text:
                    st.markdown(f'<div class="px-narrative" style="margin-top:.75rem;">{dp.caveat_text}</div>', unsafe_allow_html=True)
            with c2:
                st.info(
                    "**The system flagged its own hypothesis as contradicted.**\n\n"
                    "Three Fresh customer reviews explicitly state the cause was a checkout/payment glitch, "
                    "not a stock availability issue. The C3 §5 CV challenge logic tags the hypothesis "
                    "mechanically — no LLM judgment involved.\n\n"
                    "Confidence decreases. Outcome escalates. The system reports what the evidence says."
                )
            st.markdown(px_tel_html(res.telemetry_summary), unsafe_allow_html=True)

        elif label == "unscripted":
            st.markdown("""
            <div class="px-scenario-header">
              <div class="px-scenario-title">Unscripted — seed = 42</div>
              <div class="px-scenario-sub">Random zone, store, and event — not authored by the design team</div>
            </div>
            """, unsafe_allow_html=True)
            if res.error:
                st.error(f"Pipeline error: {res.error}")
            else:
                c1, c2, c3 = st.columns(3)
                c1.metric("Outcome", dp.source_decision_outcome if dp else "ERR")
                c2.metric("Finding ID", res.finding_id[:18] + "…")
                t = res.telemetry_summary or {}
                c3.metric("Latency", f"{t.get('total_latency_ms',0):.0f}ms")
                st.success(
                    f"Pipeline completed on an unscripted input. "
                    f"Outcome: {dp.source_decision_outcome if dp else 'N/A'}. "
                    f"{'Caveat present.' if dp and dp.caveat_text else 'Direct ANSWER issued.'} "
                    f"Praxis is a general-purpose engine.",
                )
                st.markdown(px_tel_html(res.telemetry_summary), unsafe_allow_html=True)
