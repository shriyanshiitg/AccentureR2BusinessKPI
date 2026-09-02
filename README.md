# Praxis — KPI Intelligence to Action Engine

[![Tests](https://img.shields.io/badge/tests-76%2F76%20passing-success?style=flat-square&logo=pytest)](tests/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.14-blue?style=flat-square&logo=python)](requirements.txt)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://praxis-kpi.streamlit.app)
[![Architecture](https://img.shields.io/badge/architecture-C1--C5%20Deterministic-purple?style=flat-square)](docs/architecture/build_decisions.md)
[![Database](https://img.shields.io/badge/embedded%20db-DuckDB-yellow?style=flat-square&logo=duckdb)](data/)

> **Accenture Innovation Challenge 2026 · Round 2**  
> **Track:** BusinessIntelligence.ai  
> **Team:** Worst Pace Scenario (*Shriyansh Raj & Ishika Mandal*)  
> **Live Production URL:** [praxis-kpi.streamlit.app](https://praxis-kpi.streamlit.app)

---

## Executive Summary

Modern enterprise dashboards suffer from a fatal flaw: **they display dead numbers without context, accountability, or memory.** When a core metric drops, cross-functional teams waste days re-analyzing data in silos, repeating past operational mistakes, and arguing over root causes.

**Praxis** is an autonomous **Decision-Intelligence Engine** purpose-built for high-velocity dark store quick-commerce operations. It doesn't just display *what* changed; it deterministically computes *why* it moved, evaluates *what prior interventions achieved*, verifies *who holds organizational decision rights*, and drafts *audit-logged, persona-tailored action directives*.

> *"Every AI-BI tool can explain what changed. Praxis is the only one that remembers what happened last time — and got smarter before you asked again."*

```
                     ┌──────────────────────────────────────────────────────────┐
                     │                   RAW OPERATIONAL DATA                   │
                     │   Orders · Order Lines · Sessions · Inventory · Riders   │
                     └────────────────────────────┬─────────────────────────────┘
                                                  │
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRAXIS DETERMINISTIC CORE (C1–C5)                                     │
├────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│  [C1] DATA FOUNDATION       DQ Gate (Quarantine/Block) · Semantic Contracts · Entitlements · Lineage   │
│  [C2] STATISTICAL ENGINE    Operator 1-5 (Baseline → Detect → Decompose → Segment → Precedence Link)   │
│  [C5] MEMORY GATEWAY        Precedent Retrieval · Pre-approved fixture check · Anti-Self-Approval      │
│  [C3] REASONING & RETRIEVAL Hypothesis Generator · Hybrid BM25+Vector (RRF) · Challenge · Confidence   │
│  [C4] DECISION & GOVERNANCE Lever Catalog (L1–L7) · Execution Ceilings · Role-Based Persona Narrative  │
└────────────────────────────────────────────────┬───────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                4-TIER PROGRESSIVE DISCLOSURE UI                                        │
│     Morning Briefing    ──▶    Active Investigation    ──▶    Actions & Decisions    ──▶    Memory     │
│   (Signal & Urgency)         (Deterministic Proof)          (Ceilings & Levers)       (Compounding)    │
└────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## Live Demo & Signature Scenarios

Experience the hosted system live at **[https://praxis-kpi.streamlit.app](https://praxis-kpi.streamlit.app)**.

### 1. Compounding Memory Proof (Decision 1 vs Decision 3)
* **S1 (Cold Start)**: Dark store `DS003` experiences a sudden GMV drop caused by a localized stockout in dairy. With zero institutional precedents in memory, Praxis generates an investigation, corroborates signals with Customer Voice, applies conservative bounds, and issues an action at **Moderate Confidence (0.54)**.
* **S2 (Memory Boost)**: One week later, the same stockout signature recurs at `DS003`. Praxis detects the identical statistical profile, retrieves the approved and confirmed outcome of Decision 1 from memory, and automatically boosts confidence to **High Confidence (0.81)** with hardened execution readiness.

### 2. Principled Abstention (`DS099`)
* Dark store `DS099` is a newly launched store with less than 3 days of telemetry. Rather than hallucinating plausible explanations, Praxis hits a deterministic **INSUFFICIENT_HISTORY** floor, explicitly triggers **ABSTAIN**, and notifies operators that baseline history is inadequate for safe automated diagnosis.

### 3. Diffuse Multi-Driver Dynamics
* When an operational anomaly is driven by multi-causal, sub-threshold movements without a single dominant root driver, Praxis refuses to force-fit a narrative. It caps confidence at **Medium (QUALIFY)** and requires human-in-the-loop review.

### 4. Unscripted Resilience Verification (`seed=42`)
* Evaluated against randomized operational variations, Praxis proves it is a general-purpose diagnostic engine rather than a static demo script.

---

## Core Architecture Pillars

### [C1] Data & Semantic Foundation
* **Three-Tier Data Quality Gate**: Validates every incoming batch. Records failing critical checks are cleanly partitioned into `PASSED`, `QUARANTINED`, or `BLOCKED` (e.g., negative discounts, order lines with zero price, unknown store IDs).
* **Semantic KPI Contracts**: Centralized metadata registry declaring explicit mathematical formulations, additive vs. non-additive aggregation rules, grain definitions, and sensitivity thresholds.
* **Granular Entitlements**: Strict segregation of duties. *Dark Store Operations Managers* are restricted to their specific physical store and operational metrics; *Zone Business Heads* have regional visibility over aggregate GMV and financial levers.
* **Cryptographic Lineage**: Generates immutable SHA-256 finding signatures linking raw inputs directly to rendered recommendations.

### [C2] Deterministic Statistical Engine
* **Five-Operator Pipeline**:
  1. **Operator 1 (Baseline)**: Computes 7-day trailing medians and interquartile variance (excluding stale dates).
  2. **Operator 2 (Detection)**: Materiality scoring against contract-defined percentage and absolute deviation thresholds.
  3. **Operator 3 (Decomposition)**: Identifies primary and secondary driver attribution shares.
  4. **Operator 4 (Segmentation)**: Isolates store-level, category-level, and channel-level variance.
  5. **Operator 5 (Precedence Linkage)**: Enforces temporal ordering to prevent reverse-causality attribution.
* **Zero Hallucinations**: No LLM is involved in quantitative math. Statistical output is frozen into an immutable `EvidencePackage`.

### [C3] Reasoning & Hybrid Retrieval
* **Bounded Hypothesis Generation**: Hypotheses are constrained strictly to verified governed drivers.
* **Hybrid Customer Voice Retrieval**: Merges lexical matching (**BM25**) and dense semantic embeddings (**Sentence-Transformers** `all-MiniLM-L6-v2`) using **Reciprocal Rank Fusion (RRF)**.
* **Devil's Advocate Challenge**: Actively stress-tests hypotheses against contradictory operational data.
* **Four-Tier Confidence Formula**: Deterministic score based on sample size, signal strength, CV corroboration, and historical precedent.

### [C4] Decision Engine & Persona Governance
* **Governed Lever Catalog (L1–L7)**: Maps root drivers directly to operational playbooks (e.g., cross-store inventory transfer, emergency rider re-allocation, promotional correction).
* **Execution Ceilings**: Strict delegation boundaries. Decisions exceeding financial ceilings (e.g., >₹15,000 promo budget or >2 rider transfers) automatically escalate from store ops to the Zone Business Head.
* **Contextual Narrative Synthesis**: Generates crisp, role-tailored briefings using bounded LLM prompts that strictly explain pre-computed findings without altering numbers.

### [C5] Compounding Memory & Governance
* **Embedded DuckDB Store**: Persists every approved decision, executed lever, and observed post-action outcome.
* **Precedent Retrieval Gateway**: Queries historical actions by driver grain, store profile, and time distance.
* **Contradiction-Aware Feedback**: Failed past interventions are retained and actively penalize future hypothesis confidence, preventing recurring operational blunders.
* **Anti-Self-Approval Enforcement**: Live operational proposals cannot be self-admitted to memory without explicit human-in-the-loop review.

---

## 4-Tier Progressive Disclosure UI

The Praxis frontend is engineered in Streamlit following a custom dark obsidian design system optimized for high-pressure enterprise operations:

| Screen | Purpose & Architecture |
|---|---|
| **Morning Briefing** | Executive KPI alert queue with real-time status pills, severity ranking, and priority action cues. |
| **Active Investigation** | Interactive 5-operator waterfall charts, driver attribution splits, and customer voice evidence quotes. |
| **Actions & Decisions** | Action directives with execution ceilings, governance sign-offs, and historical decision tracking. |
| **Memory & Learning** | Visual knowledge graph of past interventions, outcome metrics, confidence boost trails, and learning delta. |
| **Audit & Governance** | End-to-end lineage explorer, data quality quarantine log, entitlement inspector, and JSON telemetry stream. |

---

## Directory Structure

```
.
├── .streamlit/                     # Streamlit server & cloud hosting configuration
│   └── config.toml                 # Dark theme tokens & production server settings
├── data/                           # Canonical local database & telemetry logs
│   ├── praxis.duckdb               # Pre-seeded DuckDB memory database
│   ├── resilience_test_output.json # Resilience evaluation log
│   └── telemetry.jsonl             # Structured event audit stream
├── docs/                           # Architecture documentation & technical specifications
│   ├── architecture/               # System design & audit documents
│   │   ├── build_decisions.md      # Autonomous build decision log (10 decisions)
│   │   ├── competitive_gap_analysis.md # Comparative positioning vs traditional BI
│   │   ├── genericity_audit.md     # Audit report on generic KPI contract extensibility
│   │   └── ui_redesign_plan.md     # 4-tier progressive disclosure UI specification
│   ├── assets/                     # Architecture diagrams & UI demonstration assets
│   └── specs/                      # Engineering briefs & mathematical method specifications
│       ├── 00_master_handoff_and_build_protocol.md
│       ├── 01_c1_data_semantic_foundation.md
│       ├── 02_c2_analytical_investigation_method.md
│       ├── 03_c3_reasoning_retrieval_method.md
│       ├── 04_c4_decision_persona_method.md
│       ├── 05_c5_memory_governance_method.md
│       ├── 06_build_orchestration_brief.md
│       └── 07_business_and_signature_story_brief.md
├── praxis/                         # Core Python engine (C1–C5)
│   ├── c1_data_foundation/         # DQ gate, schemas, KPI contracts, lineage, entitlements
│   ├── c2_analytical/              # Operators 1-5, planner, EvidencePackage
│   ├── c3_reasoning/               # Hypothesis generator, BM25+dense retrieval, confidence formula
│   ├── c4_decision/                # Lever catalog, decision rights, executive narrative renderer
│   ├── c5_memory/                  # DuckDB gateway, memory retrieval, confidence modifier
│   ├── llm/                        # Bounded LLM inference client (Groq / Gemini fallback)
│   ├── orchestration/              # State machine pipeline & telemetry logger
│   └── synthetic/                  # Scenario dataset generator & memory seed scripts
├── tests/                          # Enterprise test suite (76 automated tests)
│   ├── conftest.py                 # Pytest fixtures & isolated in-memory DB setups
│   ├── test_c1.py                  # C1 DQ gates, contracts, entitlements (15 tests)
│   ├── test_c2.py                  # C2 operators, baseline, decomposition (10 tests)
│   ├── test_c3.py                  # C3 reasoning, confidence formula, boundary (8 tests)
│   ├── test_c4.py                  # C4 lever mapping, ceilings, persona output (8 tests)
│   ├── test_c5.py                  # C5 memory gateway, precedent boost, contradiction (9 tests)
│   ├── test_genericity.py          # Generic KPI contract extensibility verification (25 tests)
│   └── test_resilience.py          # Unscripted operational simulation test (1 test)
├── ui/                             # Enterprise Streamlit application
│   ├── components/                 # Reusable UI modules (Briefing, Investigate, Decisions, etc.)
│   └── streamlit_app.py            # Primary application entry point & router
├── .env.example                    # Environment variable template
├── .gitignore                      # Git ignore rules
├── pytest.ini                      # Pytest configuration
├── README.md                       # Master project documentation
├── requirements.txt                # Python package dependencies
└── run_demo.sh                     # One-click local demo launcher
```

---

## Local Setup & Quickstart

### 1. Prerequisites
* **Python**: `3.10`, `3.11`, `3.12`, or `3.14`
* **Package Manager**: `pip` or `venv`

### 2. Clone & Install
```bash
git clone https://github.com/shriyanshiitg/AccentureR2BusinessKPI.git
cd AccentureR2BusinessKPI

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Optional: Add GROQ_API_KEY or GEMINI_API_KEY for real-time narrative synthesis.
# If omitted, Praxis seamlessly falls back to high-fidelity rule-based narratives.
```

### 4. Run Automated Test Suite
Execute the entire test suite across all 5 architectural components and genericity checks:
```bash
pytest tests/ -v
```
```
============================== 76 passed in 18.26s ==============================
```

### 5. Launch the Enterprise UI
```bash
# Option A: One-click launcher (resets & seeds demo memory, starts on port 8502)
chmod +x run_demo.sh
./run_demo.sh

# Option B: Standard Streamlit execution
python3 -m streamlit run ui/streamlit_app.py --server.port 8501
```
Open **`http://localhost:8501`** in your browser.

---

## Test Coverage Breakdown

| Component Area | Test File | Test Count | Key Invariants Verified |
|---|---|---|---|
| **C1 Data Foundation** | `tests/test_c1.py` | 15 | Strict DQ gating, missing field quarantine, negative discount rejection, role-based entitlement filtering, deterministic SHA-256 lineage. |
| **C2 Statistical Engine** | `tests/test_c2.py` | 10 | Trailing 7-day median baseline, materiality detection thresholds, driver decomposition attribution, temporal precedence ordering. |
| **C3 Reasoning & Retrieval** | `tests/test_c3.py` | 8 | 4-tier confidence formula bounds, hard caps on diffuse signals, Customer Voice hybrid RRF retrieval, LLM boundary integrity. |
| **C4 Decisions & Ceilings** | `tests/test_c4.py` | 8 | Governed lever selection (L1–L7), managerial execution ceiling enforcement, mandatory qualify caveats, persona narrative isolation. |
| **C5 Memory & Precedents** | `tests/test_c5.py` | 9 | Memory gateway admission, precedent exact grain match, band capping on single precedent, contradiction penalty, anti-self-approval. |
| **Genericity Audit** | `tests/test_genericity.py` | 25 | Hot-registration of new KPIs (`Cart Abandonment Rate`, etc.), dynamic driver discovery, zero code changes required for new metrics. |
| **Resilience Evaluation** | `tests/test_resilience.py` | 1 | Unscripted random simulation (`seed=42`) validating end-to-end stability without human intervention. |
| **Total Passed** | | **76 / 76** | **100% Passing** |

---

## Technology Stack

* **Statistical & Semantic Engine**: Python 3.10+, NumPy, SciPy, Pandas, Pydantic v2
* **Data Storage & Query Engine**: DuckDB (in-memory & embedded relational store)
* **Search & Retrieval**: `rank_bm25` (lexical) + `sentence-transformers` (dense semantic vectors)
* **Frontend Architecture**: Streamlit with custom CSS Design System & SVG typography
* **Testing & Quality Assurance**: Pytest 8.2+, JSON-Lines structured telemetry logging
* **Cloud Infrastructure**: Streamlit Community Cloud (Linux container environment)

---

## Authors & Acknowledgments

* **Shriyansh Raj** — *System Architecture, C1–C5 Pipeline Implementation, UI Engineering*
* **Ishika Mandal** — *Domain Modeling, Statistical Specifications, Governance Design*
* **Team**: *Worst Pace Scenario*
* **Event**: *Accenture Innovation Challenge 2026 (Round 2)*
