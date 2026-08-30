# Praxis — AI Business Intelligence Engine
### Accenture Innovation Challenge 2026 · Round 2 · BusinessIntelligence.ai
**Team: Worst Pace Scenario (Shriyansh Raj & Ishika Mandal)**

---

## What is Praxis?

Praxis is a KPI intelligence-to-action engine for a quick-commerce dark-store network. It explains *why* a KPI moved, *who* should act, *what* lever to pull — and uniquely, it *remembers* prior decisions and outcomes to get smarter over time.

> *"Every AI-BI tool can explain what changed. This is the only one that remembers what happened last time — and got smarter before you asked again."*

---

## Quick Start

### 1. Install dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env and add your GROQ_API_KEY (already set if you ran setup)
```

### 3. Run the demo UI
```bash
python3 -m streamlit run ui/streamlit_app.py --server.port 8502
```
Open **http://localhost:8502** → click **▶ Run Signature Demo**

### 4. Run all acceptance tests
```bash
python3 -m pytest tests/ -v
```

---

## Pipeline

```
Synthetic Data Generator
        ↓
C1  Data & Semantic Foundation   (DQ gate, KPI contracts, entitlements, lineage)
        ↓
C2  Statistical Investigation    (Baseline → Detection → Decomposition → Segmentation → Precedence)
        ↓
C5  Memory Hook                  (retrieve prior decision outcomes for this driver/store)
        ↓
C3  Hypothesis Reasoning         (generate → CV retrieval → challenge → confidence score)
        ↓
C4  Decision & Narrative         (lever → decision rights → persona narrative)
        ↓
Telemetry JSON log
```

---

## Test Results

| Suite | Tests | Status |
|---|---|---|
| C1 §18 (DQ gate, KPI contracts, entitlements, lineage) | 15 | ✅ All pass |
| C2 §10 (5 operators, EvidencePackage) | 10 | ✅ All pass |
| C3 §12 (confidence formula, hard caps, abstention, LLM boundary) | 8 | ✅ All pass |
| C4 §8 (lever mapping, rights, caveat enforcement, entitlement) | 8 | ✅ All pass |
| C5 §7 (gateway, retrieval, band cap, contradicted precedent) | 9 | ✅ All pass |
| Resilience (seed=42 unscripted scenario) | 1 | ✅ Passes |
| **Total** | **51** | ✅ |

---

## Demo Scenarios

| Scenario | What it demonstrates |
|---|---|
| **Decision 1 vs Decision 3** | Compounding memory: same signal, higher confidence after 1 confirmed precedent |
| **Abstention** | INSUFFICIENT_HISTORY hard floor — engine refuses to guess for new store DS099 |
| **No Dominant Contributor** | Diffuse multi-driver pattern → QUALIFY, no force-fit |
| **Unscripted (seed=42)** | General-purpose engine, not a hardcoded demo |

---

## Key Design Decisions (see BUILD_DECISIONS.md)

- **GMV reconciliation tolerance:** `>₹1 or >0.5%` (C2 §0 adopted)
- **Tenure filter:** none applied for RPR (C1 §11 OPEN — metadata-flagged)
- **Month-end anchor for RPR:** last calendar day of month (BD-003)
- **₹15,000/2-rider auto-exec ceilings:** kept as prototype defaults (BD-004)
- **LLM:** Groq llama-3.3-70b-versatile, bounded to prose only (C3 §9 / C4 §6)
- **Second stockout date:** 2026-08-22, 7 days after S1 (BD-010)

---

## Architecture Principles

1. **LLM is not the source of quantitative truth** — all statistical tests, confidence scores, lever selection, and entitlement enforcement are deterministic code
2. **Missing ≠ negative evidence** (C1 §13) — absent data is scored as zero, never as a penalty
3. **Contradicted precedents are admitted and informative** (C5 §2.1) — a confirmed-wrong guess lowers future confidence in the mirror direction
4. **Every demo fixture enters via the same gateway** (C5 §2) — `demo_preapproved` is a value the gateway accepts, not a bypass
5. **Honesty over impressiveness** — ABSTAIN is the correct output when evidence is genuinely insufficient

---

## File Structure

```
praxis/
├── c1_data_foundation/   # Schemas, DQ gate, KPI contracts, entitlements, lineage
├── c2_analytical/        # 5 operators + investigation planner + EvidencePackage
├── c3_reasoning/         # Hypothesis generator, CV retrieval, challenge, confidence, HypothesisPackage
├── c4_decision/          # Lever catalogue, decision rights, narrative renderer, DecisionPackage
├── c5_memory/            # Memory gateway (DuckDB), retrieval, confidence boost
├── orchestration/        # Pipeline state machine, telemetry
├── synthetic/            # Data generator (5 scenarios) + memory seed script
└── llm/                  # Groq client (bounded)
ui/
└── streamlit_app.py      # Demo UI
tests/
├── test_c1.py … test_c5.py   # 50 acceptance tests
└── test_resilience.py         # Unscripted resilience test
data/
├── praxis.duckdb         # Persistent memory store
└── telemetry.jsonl       # Structured JSON telemetry log
BUILD_DECISIONS.md        # Autonomous build decisions log (10 entries)
```
