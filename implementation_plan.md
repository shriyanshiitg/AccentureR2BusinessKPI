# PRAXIS — UX Redesign Specification

---

## Part 1: Product Understanding

### What is PRAXIS?
PRAXIS is a **KPI Intelligence-to-Action engine** for retail operations managers. It watches business metrics (Zone GMV, Stockout Rate, Delivery SLA, etc.), detects when something materially breaks, figures out *why* it broke, and tells the right person *exactly what to do about it* — with a transparent confidence score and traceable evidence.

### Who is the primary user?
**The Business Leader / Zone Operations Manager** — not a data scientist.  
They open this app at 9am to understand: *"Is anything on fire today, and if so, what do I do?"*  
They are busy. They don't read dashboards for fun. They need answers, not data.

### What problem does it solve?
Without PRAXIS: The manager stares at a GMV drop, pulls 3 different reports, emails 2 analysts, waits 4 hours, then acts on a gut feeling.  
With PRAXIS: In 2 minutes they know *what* broke, *why* it broke, *how confident* PRAXIS is, and *exactly what to do*.

### What is the user's end goal?
**Make a confident, fast, evidence-backed business decision and take action.**

---

## Part 2: UX Diagnosis — What's Wrong Right Now

### Critical UX Problems

**1. The sidebar has 11 navigation items.**
A first-time user sees: HOME, INVESTIGATE, DECISIONS, LEARNING, GOVERNANCE, DEMO. Six sections, eleven pages. They immediately wonder "where do I start?" None of the items communicate what they *do* or *why they matter*. This is developer navigation, not user navigation.

**2. The user journey is fragmented.**
The natural flow is: *See alert → Investigate → Get recommendation → Take action → Record outcome*.  
Right now these are 5 separate pages the user must manually click through. There is no guided handoff between steps. A judge demoing this will be lost.

**3. "Morning Briefing" is the homepage but it doesn't tell the product story.**
The page says "Good morning" and shows a table of KPIs. A first-time user thinks: "okay... so what?" There is nothing explaining what PRAXIS is, why they should trust it, or what they should do next.

**4. The Scenario Launcher is buried in DEMO at the bottom.**
This is the *most important* feature for a hackathon demo — it's what makes everything come alive. It's hidden. Judges may never find it.

**5. Tabs inside Investigation force the user to think.**
"① What Changed", "② Why It Happened" etc. — forcing a user through 7 tabs creates friction. The natural desire is to scroll through a story, not click through tabs.

**6. Technical sections pollute the UI.**
"C1–C5 Pipeline Architecture", "DuckDB Gateway", "BM25+emb retrieval" — these are engineering terms that a business user should never see. They break immersion.

**7. The Scenario Launcher instruction is condescending.**
"For judging: Run S1 first..." — This reads like a README, not a product. A real product guides you without instructions.

---

## Part 3: Redesigned User Journey

### The mental model the user should have:

```
PRAXIS watches your KPIs → alerts you to what matters → 
explains why → tells you what to do → gets smarter each time
```

### The 4 states of the product:

```
State 1: WATCH     — "Here's what happened today" (Morning Briefing)
State 2: UNDERSTAND — "Here's why it happened" (Investigation)  
State 3: ACT       — "Here's what to do" (Recommendation + Approve)
State 4: LEARN     — "Here's what Praxis learned from last time" (Memory)
```

### The redesigned flow:

```
Homepage (Watch)
└── Alert card → [Investigate →] button
    └── Investigation page (Understand) — single scroll, not tabs
        └── [Approve Recommendation →] button
            └── Action recorded → Memory loop shown inline
                └── [View how Praxis will handle this next time →]
```

---

## Part 4: Information Hierarchy — What Matters Most

### On every page, establish:
1. **Signal** — What is happening? (1 number, 1 status)
2. **Why** — What caused it? (1 dominant driver)
3. **Confidence** — How sure is PRAXIS? (1 score + band)
4. **Action** — What should I do? (1 primary CTA)
5. **Evidence** — Prove it (expandable, not shown by default)
6. **Audit** — Technical trace (hidden behind "View audit trail")

---

## Part 5: Navigation Redesign

### Current sidebar: 11 items across 6 sections.
### Redesigned sidebar: 5 items, 2 sections.

```
─────────────────────────
  PRAXIS                  
  KPI Intelligence         
─────────────────────────
  Active Persona pill      
─────────────────────────

  WORKSPACE
  ● Morning Briefing       ← "Today's alerts"
  ◎ Active Investigation   ← "Current analysis"
  ✓ Actions & Decisions    ← combines Recommended + Past

  SYSTEM
  ⊗ Memory & Learning      ← combines Learning + Memory
  ≡ Audit & Governance     ← combines all governance pages

─────────────────────────
  [▶ Run Demo] button      ← ALWAYS VISIBLE, never buried
─────────────────────────
```

**Key insight:** The "Scenario Launcher" is NOT a navigation destination. It's a *quick action*. It belongs as a persistent button at the bottom of the sidebar, always visible, inviting judges to interact.

---

## Part 6: Page-by-Page Redesign

### Page 1: Morning Briefing (WATCH)

**Current problems:**
- No product context for first-time users
- Decision brief is a bar, not a visual hierarchy
- KPI table has no visual affordance for "click this row to investigate"
- The investigation banner below is redundant with the table above

**Redesigned layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  [PRODUCT CONTEXT STRIP — only shown if no analysis run]     │
│  "PRAXIS detected 3 movements this week. 1 requires action." │
│  Tagline + what the product does in 1 sentence.             │
└─────────────────────────────────────────────────────────────┘

Good morning, Zone Z003.                          Mon 1 Sep · 09:15
Today: 3 KPIs flagged · 2 require immediate attention.

┌──────┬──────┬──────┐
│  5   │  3   │  2   │
│ KPIs │ Mat. │ Act. │
└──────┴──────┴──────┘

KPI PRIORITY QUEUE ─────────────────────────────────

[🔴 Zone GMV]  ₹21.0L  ↓25.0%  Root cause identified    [Investigate →]
[🔴 Stockout]   42%    ↑38.0%  Primary driver of GMV gap  [Investigate →]
[🟡 Delivery]   71%    ↓12.0%  Abstain · sparse data       [View →]
[🟢 Conversion] 5.8%   ↑0.1%   On track                   —
[⚪ Repeat]     —       —       Monthly KPI · no data       —

─────────────────────────────────────────────────────────────
ORGANISATIONAL EXPERIENCE BANNER (if memory > 0)
"Praxis has 1 validated record from a similar situation."
```

**Design decisions:**
- Each KPI row has an inline `[Investigate →]` button — eliminates the separate investigation banner
- Clicking a KPI row navigates to investigation — no extra step
- Remove the separate "Priority Investigation" banner — it's redundant
- Product context strip collapses after first run

---

### Page 2: Active Investigation (UNDERSTAND)

**Current problems:**
- 7 tabs require clicking — creates fragmentation and confusion
- "How Praxis Concluded" is a technical audit, not a user-facing tab
- Tab ⑦ "Signature Demo" is a developer artifact, not product
- User doesn't know which tab to click first

**Redesigned layout: Single scroll, progressive disclosure**

```
┌─────────────────────────────────────────────────────────────┐
│  INVESTIGATION                          [QUALIFY] [73% CONF] │
│  Zone GMV · Week 33 · Zone Z003                              │
└─────────────────────────────────────────────────────────────┘

━━ WHAT HAPPENED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [₹21.0L Actual]  [₹28.0L Expected]  [↓25% Gap]

  Zone GMV is 25% below expected performance.
  Movement is outside normal historical variation.
  
  ⚑ Data quality: No flags · Full confidence applied
  ● Source: SRC-OMS · 47 min ago

━━ WHY IT HAPPENED ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  #1  Stockout Rate · DS041    ████████████  73%  ₹2.8L
  #2  Delivery SLA Lag         ████          18%  ₹0.7L
  #3  Conversion Shortfall     ██             9%  ₹0.3L
                                              Method: Deterministic

  DS041 dark store has been in stockout for ~18 hours.
  This explains 73% of the GMV gap. [Supporting evidence ▾]

━━ CONFIDENCE & EVIDENCE ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [QUALIFY — 73% confident]
  ████████████░░░░░  
  
  Praxis qualifies this finding because: rider data is sparse.
  
  [▾ View 4 evidence items]   [▾ View audit trail]

━━ WHAT TO DO ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Action     Transfer inventory from DS038 to DS041
  Owner      Ops Manager · Zone Z003
  Timeline   Within 4 hours
  Impact     ₹1.8–2.2L GMV recovery projected
  Risk       Mild: DS038 may fall below comfort threshold

  [✓ Approve & Record Decision]   [Later]

━━ MEMORY BOOST (if S2) ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Praxis found 1 validated precedent from 2026-08-15 (+12 pts)
  
  [▾ Compare: Cold Start vs Memory-Enhanced]
```

**Design decisions:**
- Single scroll replaces 7 tabs. Judges see the whole story at once.
- Each section is visually separated with a bold section break
- Evidence and audit trail are collapsed by default (expandable)
- The `[Approve & Record Decision]` CTA is embedded within the page, not on a separate "Recommended Actions" page
- This eliminates the need for a separate "Recommended Actions" navigation item

---

### Page 3: Actions & Decisions (ACT + HISTORY)

**Simplified:** Two tabs — `Active` (current recommendation) + `History` (past decisions).  
The current separate "Recommended Actions" and "Past Decisions" pages merge here.

---

### Page 4: Memory & Learning (LEARN)

**Simplified:** Show the learning loop diagram, then the memory records table.  
Remove the "What Praxis Has Learned" + "Memory" split. One page, one story.

---

### Page 5: Audit & Governance (VERIFY)

**Simplified:** Three sub-tabs — `Evidence Trail`, `Data Health`, `Access & Telemetry`.  
This consolidates 4 pages into 1.

---

## Part 7: Visual Design Decisions

### Layout principles:
1. **Every section starts with a bold separator header** (e.g., `━━ WHY IT HAPPENED ━━`)  
   — replaces Streamlit tabs, gives page structure without clicks
2. **CTAs are always action verbs**: "Investigate →", "Approve & Record", not "Submit"
3. **Confidence score is the most important number** — always shown prominently near the KPI name
4. **Memory boost is always surfaced** when it exists — this is the product's "magic moment"
5. **Progressive disclosure everywhere**: data quality flags, evidence, audit trail all collapsed

### Color usage:
- 🔴 Red = material movement, requires action
- 🟡 Amber = qualified / uncertain / stale
- 🟢 Green = on track / approved / confirmed
- 🟣 Purple = memory / PRAXIS intelligence (brand color)
- ⚪ Gray = inactive / not applicable

### Typography hierarchy:
- KPI name: `1.25rem / 700` — biggest thing on screen after the metric value
- Metric value: `2rem / 800 / Plus Jakarta Sans`
- Section headers: `0.625rem / 700 / UPPERCASE / tracked` — structural separator
- Body: `0.875rem / 400 / Inter` — comfortable reading
- Metadata: `0.6875rem / 500 / muted gray` — don't compete

### The "magic moment" for judges:
When a judge runs S1 then S2, the investigation page should show:
```
┌────────────────────────────────────────────────┐
│  ⊗ Memory Boost Active                         │
│  Praxis found a validated precedent from       │
│  Aug 15, 2026. Confidence increased +12 pts.  │
│  Cold start: 60 pts → With memory: 72 pts     │
└────────────────────────────────────────────────┘
```
This purple card should appear prominently, BEFORE the confidence section. It's the product's proof point.

---

## Part 8: Implementation Plan

### Files to change:
1. **`ui/streamlit_app.py`** — Rebuild navigation (5 items), make sidebar "Run Demo" button persistent, route pages
2. **`ui/components/morning_briefing.py`** — Add inline Investigate buttons per KPI row, remove redundant banner
3. **`ui/components/investigation.py`** — Replace 7 tabs with single scroll using `st.container()` sections
4. **`ui/components/decisions.py`** — Merge "Recommended Actions" + "Past Decisions" into one page with tabs
5. **`ui/components/learning.py`** — Merge "What Praxis Learned" + "Memory" into one page
6. **`ui/components/governance.py`** — Merge 4 governance pages into one page with 3 sub-tabs
7. **`ui/components/design_system.py`** — Add scroll-section separator CSS, memory-boost card CSS

### Order of implementation:
1. Navigation refactor (sidebar) — unblocks everything else
2. Morning Briefing inline CTA
3. Investigation scroll → sections (biggest UX win)
4. Page merges (Decisions, Learning, Governance)
5. Polish pass (memory boost card, transition animations)

### Constraint: Zero backend changes.
All routing/state changes are session_state only. Backend pipeline unchanged.

---

## Part 9: The Demo Story (for judges)

A judge sitting down cold should experience this:

```
1. Open app → "Good morning. 3 KPIs need attention."
             → Immediately understand what the product does.

2. Click [Investigate →] on Zone GMV
             → See: what changed, why, how confident, what to do.
             → All on one scroll, no tab clicking.

3. Click [Approve & Record Decision]
             → Confirmation screen + memory loop shown.
             → "This decision has been recorded for future use."

4. Sidebar → [▶ Run Demo: S2 (Memory)]
             → Run S2 → Purple "Memory Boost Active" card appears.
             → Confidence jumps from 60 → 72. The product proves itself.

5. Sidebar → Audit & Governance
             → Show evidence trail, data freshness, entitlements.
             → "Everything is traceable. Nothing is made up."
```

Total demo time: **< 3 minutes**. Self-explanatory. No explanation required.

---

> **Design principle**: If a user needs to read a label to understand what something does, the label is wrong. If a user needs an instruction to know what to click, the layout is wrong. Redesign until both are true.
