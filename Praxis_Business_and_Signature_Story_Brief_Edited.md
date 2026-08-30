# Praxis — Business & Signature-Story Brief
### Accenture Innovation Challenge 2026 · Round 2 · BusinessIntelligence.ai
**Team Worst Pace Scenario — Shriyansh Raj & Ishika Mandal**

---

## 1. Business Domain: Quick-Commerce Hyperlocal Delivery (India)

**Decision: A dark-store-based quick-commerce network** (10–15 min grocery/essentials delivery, Blinkit/Zepto/Instamart-style) — zone-level GMV, dark-store inventory, delivery SLA, and customer retention across a city network.

**Why not plain generic e-commerce:**
The problem statement's own worked example is "revenue dropped 8% in a region" for what reads as a generic online retailer. Picking plain e-commerce risks the prototype reading like a restatement of the prompt itself — the single highest-probability domain every other team will also reach for. The goal is to stay in the e-commerce family (for recruiter relevance) while picking a specific enough sub-vertical that the driver network is genuinely richer than "online store revenue."

**Why quick-commerce wins:**
- **Broad, current industry relevance:** it's squarely e-commerce/retail, which is directly legible to hiring teams at Amazon, Flipkart, Meesho, Myntra, Swiggy, Zepto, Blinkit, and any consulting firm's retail/e-commerce analytics practice — this keeps the project useful across placement conversations rather than tied to one narrow function.
- **One extra operational layer for free:** on top of standard e-commerce revenue mechanics, quick-commerce adds dark-store inventory management and delivery SLA — this gives real "multiple interacting drivers" complexity (stock, catchment density, rider capacity, weather, competitor dark-store openings) without needing to invent complexity.
- **Built-in lagged causal chain:** delivery SLA breaches and stockouts hit conversion and GMV immediately, but show up in customer retention weeks later — a strong, realistic source for the "meaningful signal vs. noise" and low-confidence/sparse-history scenarios the minimum prototype requires.
- **Current and defensible sector:** quick-commerce unit economics and hyperlocal ops are an active, widely-discussed topic in Indian retail right now, which reads as informed rather than dated to a judge.

---

## 2. KPIs (3–5), Formulas, and Grain

| # | KPI | Formula | Grain |
|---|-----|---------|-------|
| 1 | **Zone GMV** | Units Sold × Average Selling Price (post-discount) | Zone × Day |
| 2 | **Order Conversion Rate** | Completed Orders ÷ App Sessions with Cart Add | Zone × Day |
| 3 | **Dark-Store Stockout Rate** | Out-of-Stock SKU-Intervals ÷ Total Active SKU-Intervals | Dark Store × Day |
| 4 | **Delivery SLA Adherence** | Orders Delivered Within Promised Time ÷ Total Orders | Zone × Day |
| 5 | **Repeat Purchase Rate** | Customers with ≥2 Orders in Period ÷ Total Active Customers | Zone × Month |

**Why this set:** KPIs 1–4 form a same-week operationally connected driver chain that enables contribution and relationship analysis; the prototype will distinguish observed association from causal evidence. KPI 5 is a deliberately lagged, downstream KPI — it lets the demo show a sparse-history / delayed-effect scenario (a stockout/SLA problem in week 1 showing up as a retention dip weeks later), which most "explain this week's dashboard" competitors won't attempt.

---

## 3. Data Sources (Heterogeneous Grain & Cadence)

| Source | Type | Contents | Refresh Cadence | Grain |
|---|---|---|---|---|
| **Order Management System (OMS)** | Structured | Orders, GMV, SKU-level cart/checkout, discounts | Hourly/daily batch | Order-level |
| **Dark-Store Inventory & Delivery Fleet System** | Structured | Stock counts, rider assignment, delivery timestamps, SLA breaches | Near-real-time (minutes) | SKU × dark store, delivery-event-level |
| **Customer Voice** | Unstructured | App reviews, support chat transcripts, social mentions, CSAT surveys | Weekly, irregular | Free text, zone level |

This deliberately mismatches refresh cadence (minutes vs. hourly/daily vs. weekly) and grain (delivery-event vs. order vs. free text) — the exact heterogeneity Round 2 calls out as a required complexity, and it maps cleanly onto the "reconcile data and business context across heterogeneous sources" requirement without any artificial stitching.

---

## 4. Two Personas, Genuinely Different Narratives

| | **City/Zone Business Head** | **Dark-Store Operations Manager** |
|---|---|---|
| **Question they're asking** | "Why did the zone miss GMV target, and what's the lever I should pull this week?" | "What do I need to physically fix at my dark store today?" |
| **Evidence depth shown** | Zone-wide driver ranking, GMV/margin impact, confidence band | Single dark-store, single-SKU granularity |
| **Recommendation type** | Strategic reallocation ("shift inventory from Dark Store C to Dark Store A"; approve a 3-day local promo to offset SLA dip) | Operational task ("restock SKU X by 6 PM"; "add 2 riders to the evening shift") |
| **Decision rights reflected** | Can authorize cross-store inventory transfers / local promos | Can only execute pre-approved restock/staffing actions within threshold |
| **Delivery channel** | Weekly ops-review narrative | In-workflow ticket/task in the dark store's daily ops app |

The difference isn't tone — it's granularity, authority, and action type, which directly demonstrates the Round 2 requirement to encode decision rights and role-based personalization, not just reword the same sentence.

---

## 5. Signature Demo Moment

**Decision: showcase the compounding-memory thesis — "same signal, told twice."**

**The moment (≈25 seconds):**
A zone-level GMV dip driven by a dark-store stockout + SLA breach appears on screen — a specific SKU, a specific dark store. Praxis is run twice on the same signal, side by side:
- **Memory OFF ("Decision 1"):** a competent but generic explanation — stockout correlates with the drop, moderate confidence, a sensible but shallow recommendation (reorder the SKU).
- **Memory ON ("Decision 3"):** Praxis retrieves a governed memory of an *earlier, similar* stockout at a comparable dark store last month — cites what was tried (a cross-store inventory transfer, not just a reorder), what worked, and what didn't — and delivers a sharper, higher-confidence recommendation with a concrete "this worked last time" justification.

The line to land with judges: *"Every AI-BI tool in this room can explain what changed. This is the only one that remembers what happened last time — and got smarter before you asked again."*

**Why this moment over an alternative (e.g., the abstention/uncertainty moment):**
The abstention mechanism ("engine says 'I don't know, here's why'") is valuable and should still be built as one of the required scenarios, but it is a capability mature AI-BI products increasingly address through grounding, confidence and related controls. Our differentiation is therefore not simply abstention or KPI explanation; it is the governed decision-memory loop that connects prior decisions and outcomes to future recommendations. A judge should remember the *distinctive combination* rather than a generic AI-BI capability.

**Why it's realistic for a two-person team:** it does not require building the full governed-memory admission/quarantine pipeline described in the architecture. It requires:
1. One seeded historical decision+outcome record (a demo fixture, not a live-learned one).
2. A retrieval step that surfaces it when a similar signal recurs.
3. A simple UI toggle to show the "before/after" comparison.

That's a few days of focused build, not a production memory system — the rest of the governed-memory layer (full admission/quarantine workflow, temporal knowledge graph, trust/freshness scoring) can be presented as architecture and roadmap in the proposal, fully designed but only partially instantiated in the live prototype. The seeded historical decision/outcome should still enter the prototype through the same memory-admission interface that production memory would use, with the validation step explicitly pre-approved for the demonstration fixture. This keeps the demo honest: what's live is live, what's roadmap is clearly labeled as roadmap.

---

## 6. Competitive Positioning

| Capability | ThoughtSpot | Power BI / Fabric Copilot | Looker + Gemini | Tableau | Databricks Genie | **Praxis** |
|---|---|---|---|---|---|---|
| Explains "what changed" in NL | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| Ranks likely root causes | ✅ | Partial | Partial | Partial | Partial | ✅ |
| Persona-specific narratives + decision rights | ❌ | ❌ | ❌ | Partial | Partial | ✅ |
| Explicit uncertainty & abstention | ❌ | ❌ | ❌ | ❌ | Partial | ✅ |
| Captures decision → outcome | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| **Compounding organizational memory across decisions** | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |

**Differentiation statement:**
> "Every other AI-BI platform tells you what happened once; Praxis is the only one that remembers what happened last time and gets smarter before you ask again."

---

*All KPI formulas, data-source cadences, and dataset values used in the prototype are illustrative/simulated per Round 2's explicit allowance for sample data — the domain grounding and analytical logic are what should read as real.*
