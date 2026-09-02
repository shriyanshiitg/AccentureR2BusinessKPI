# PRAXIS — Executive Product & UI Redesign Specification
*Version 1.0 · A Master Blueprint for Enterprise Decision Intelligence*

---

## 1. Executive Summary & Product Identity

### 1.1 What Praxis Is
Praxis is an **autonomous executive decision-support system** engineered to bridge the gap between telemetry signals and operational intervention in high-velocity commerce. 

It is designed to emulate the cognitive workflow of an elite McKinsey or Accenture engagement partner paired with a senior operations analyst:
* It continuously monitors the enterprise pulse across complex multi-echelon environments.
* It autonomously investigates anomalous deviations before an executive even opens a report.
* It quantifies exact financial and operational causality.
* It synthesizes evidence-backed, policy-compliant operational interventions.
* It captures empirical execution outcomes into governed organizational memory, ensuring the firm systematically gets smarter over time.

### 1.2 What Praxis Is Not
To preserve the purity of the executive experience, Praxis explicitly rejects four common product archetypes:

1. **Not a Business Intelligence (BI) Dashboard**: BI dashboards present passive grids of charts, expecting the user to slice, dice, filter, and hypothesize about why a metric moved. Praxis does not make the executive do the analyst's job; Praxis delivers synthesized conclusions.
2. **Not a Reporting or Telemetry Tool**: Reporting tools dump metrics and status tables into static views. Praxis delivers structured decision packages with quantified business impact, risk bounds, and operational directives.
3. **Not an AI Playground or Chat Console**: Prompt boxes place the cognitive burden of query formulation on the leader. Praxis presents structured, proactive briefings with transparent audit trails—deterministic calculations where accuracy is mandatory, supplemented by generative reasoning strictly for contextual narrative synthesis.
4. **Not a Developer Console**: It does not expose pipeline stages, tensor dimensions, raw query strings, vector similarity coefficients, or token latency in primary user views.

---

## 2. Forensic Audit of Existing UX Failures

A rigorous critique of current analytical interfaces reveals several pervasive usability antipatterns that degrade executive trust and decision velocity:

### 2.1 Information Overload vs. Decision Velocity
* **The Antipattern**: Cramming dozens of widgets, statistical indices, raw transaction rows, and metadata badges onto a single viewport under the guise of "giving users complete context."
* **Why It Destroys Usability**: Cognitive load theory demonstrates that working memory is severely limited under high pressure. When an executive is confronted with 40 competing visual elements simultaneously, visual paralysis ensues. The cognitive cost of discerning what matters exceeds the value of the information itself.

### 2.2 Flat Visual Hierarchy & Uniform Weighting
* **The Antipattern**: Formatting every card, container, and metric tile with identical border weights, padding, typography sizes, and container backgrounds.
* **Why It Destroys Usability**: When every metric is visually "loud," nothing is heard. An alert representing a ₹3.5L cash leak must not look identical to an informational card stating a data feed was refreshed 12 minutes ago. Uniform weight forces the user's eye to sequentially scan every pixel rather than immediately anchoring to the business-critical anomaly.

### 2.3 Premature Technical Exposure
* **The Antipattern**: Displaying mathematical mechanics (e.g., Z-scores, p-values, regression residuals, vector cosine distances) at the top of the decision hierarchy.
* **Why It Destroys Usability**: Business leaders think in terms of revenue, margin, delivery SLAs, customer retention, and operational risk. Presenting statistical plumbing before the business verdict erodes credibility, signaling that the system was built for the engineer who wrote it rather than the leader tasked with acting upon it.

### 2.4 Documentation Paradigms vs. Workflow Paradigms
* **The Antipattern**: Structuring interfaces as reference encyclopedias or technical manuals with exhaustive tabbed navigations (e.g., "Data Sources", "Model Config", "Audit DAGs").
* **Why It Destroys Usability**: Executives do not browse reference manuals during an operational incident; they execute workflows. A page must guide the user along a natural cognitive progression: *Notice → Diagnose → Evaluate → Decide → Verify*.

### 2.5 Forcing Reading Over Scanning
* **The Antipattern**: Presenting insights in dense walls of narrative prose or multi-column data tables without visual anchoring, typographic hierarchy, or scannable data visualization.
* **Why It Destroys Usability**: Executives scan in F-shaped or Z-shaped patterns, spending under 10 to 15 seconds on initial evaluation. If the primary takeaway cannot be absorbed within that window, the tool is abandoned for verbal briefings or executive summaries prepared manually by staff.

### 2.6 Fragmented Storytelling & Orphaned Data
* **The Antipattern**: Isolating the alert from the root cause, and isolating the root cause from the recommended action across disconnected screens.
* **Why It Destroys Usability**: An executive is forced to mentally assemble puzzle pieces across multiple views: "I saw GMV dropped on Screen A, I saw a stockout chart on Screen B, now what lever am I supposed to pull on Screen C?" This fragmentation induces hesitation and delays operational response.

---

## 3. Product Vision & Emotional Architecture

### 3.1 The Intended Emotional Experience
> *"Using Praxis should feel like opening a private morning briefing prepared overnight by the company's sharpest, most trusted principal consultant."*

When an executive engages with Praxis, the interaction must evoke:
* **Immediate Calm**: The visual field is quiet, spacious, structured, and free of visual clutter. The interface radiates order and command.
* **Effortless Clarity**: The user never wonders, *"What am I looking at?"* or *"What am I supposed to do next?"* The answer is unmistakable within seconds.
* **Quiet Confidence**: Praxis does not boast, flash animations, or rely on gimmicky graphics. It states findings with dignified precision, candidly admitting when data is inconclusive.
* **Uncompromising Trust**: Every assertion is visibly backed by an unbroken chain of empirical evidence that can be inspected on demand without cluttering the main story.

### 3.2 Product Persona
* **Composed & Authoritative**: Speaks in crisp, definitive business language.
* **Transparent & Honest**: Never obfuscates uncertainty or overstates claims. Distinguishes rigorously between correlation, quantitative attribution, and verified causation.
* **Action-Oriented**: Always pairs an identified problem with a viable, policy-governed intervention, quantified impact, and an assigned owner.
* **Continuously Compounding**: Remembers every approved decision and verified outcome, growing visibly smarter with each operational cycle.

---

## 4. UI Personality & Behavioral Tone

While Section 3 defines the high-level product identity, UI Personality governs how the digital interface visually behaves and speaks across every pixel:

* **Calm & Measured**: The UI never shouts. It does not use flashing red banners, animated bells, or dramatic sound effects. Status is communicated through quiet color contrast and crisp typography.
* **Executive & Institutional**: Feels like high-end financial or strategy consulting software. It evokes the gravity of a corporate boardroom rather than the informality of a social application.
* **Premium & Deliberate**: Every padding value, border radius, and font weight is mathematically proportioned. There are no haphazard offsets, awkward line wraps, or unstyled default widgets.
* **Minimalist & Distraction-Free**: Whitespace is treated as a first-class architectural material. Empty space represents mental breathing room for the decision-maker.
* **Trustworthy & Audit-Ready**: Data presentation is sober and unassailable. Numbers are formatted with standard financial notation, currencies are explicit, and confidence intervals are visible alongside point estimates.
* **Quiet Affordance**: Interactive elements (buttons, disclosures, persona pills) signal clickability through subtle elevation and hover states, never through garish gradients or bouncy micro-interactions.
* **Human-Centered & Consultant-Grade**: The narrative prose generated by the system reads as if authored by an executive partner—grammatically flawless, syntactically concise, and focused on strategic stakes.
* **Explicitly Never Playful**: No emojis as primary status indicators, no congratulatory confetti, no badges awarded to the user, and no casual conversational filler ("Hey there! Let's check some numbers!").
* **Explicitly Never Gamified**: Executives are managing multi-million-rupee retail supply chains. The interface reflects that serious responsibility.
* **Explicitly Never Futuristic/Cyberpunk**: No dark glassmorphism glows, neon outlines, robotic gridlines, or sci-fi iconography.

---

## 5. Foundational Design Principles

These 12 inviolable principles govern every architectural and visual decision across the entire Praxis platform:

1. **One Screen → One Primary Business Question**: Every screen must have a single, unambiguous objective. Any element that does not directly contribute to answering that screen's core question is either removed or relegated to progressive disclosure.
2. **Answer Before Evidence**: Never make an executive read the proof before seeing the conclusion. Present the verdict first, followed by the supporting decomposition, followed by the raw data on demand.
3. **Strict 4-Layer Progressive Disclosure**:
   * *Layer 1 (0–5 seconds)*: The executive answer and primary action.
   * *Layer 2 (5–15 seconds)*: The core explanation, decomposition, and financial impact.
   * *Layer 3 (15–30 seconds)*: Confidence scoring, memory precedents, and risk boundaries.
   * *Layer 4 (Deep Dive)*: Granular logs, telemetry, statistical validations, and audit DAGs.
4. **Scan First, Read Later, Audit on Demand**: Structure typography, whitespace, and metric sizing so that a 10-second glance delivers the full situation report, while allowing a 5-minute deep dive for technical auditability.
5. **Decision Density Over Information Density**: Optimize for the speed and accuracy with which a leader can make a business decision, not the total volume of data points packed into the viewport.
6. **Show Confidence & Uncertainty Honestly**: System confidence must be transparently displayed. If evidence is ambiguous, the system must explicitly abstain from guessing and clearly state why. Abstention is an elite feature, not a failure.
7. **Size Before Color; Whitespace Before Borders**: Visual prominence must be established through typographic scale, hierarchy, and generous breathing room. Color must be reserved exclusively for semantic state (critical alerts, positive trends, verified memory).
8. **Business Language Before Technical Taxonomy**: Speak in terms of "Gross Merchandise Value", "Store Stockout Rate", and "Driver Reallocation", never "Vector Embeddings", "LLM Inference Tokens", or "SQL Join Latency".
9. **No Orphaned Anomalies**: An identified deviation must never be presented without its quantified business impact, dominant root cause, and a concrete recommended mitigation.
10. **The Closed Learning Loop Must Be Visible**: Show how today's approved decisions and verified real-world outcomes directly compound the system's confidence for tomorrow's challenges.
11. **Persona-Specific Cognitive Scoping**: Information must automatically conform to the user's operational authority. A Zone Head sees zone-wide aggregations and cross-store allocations; a Dark Store Manager sees store-specific stock events and physical pick-and-pack queues.
12. **Quiet Elegance (The Stripe/Apple Standard)**: Avoid flashy AI aesthetics, futuristic dark glass glows, and complex decorative animations. Employ clean surfaces, deliberate typography, razor-sharp alignment, and intentional whitespace.

---

## 6. Global Layout System

To ensure that every screen feels like an organic chapter of a single unified product, Praxis enforces a strict universal page layout rhythm:

### 6.1 The Universal Page Skeleton
Every screen in Praxis conforms to a rigid, top-to-bottom structural hierarchy:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. GLOBAL STICKY HEADER (Persistent Brand, Context & Persona Indicator)│
├────────────────────────────────────────────────────────────────────────┤
│ 2. PAGE TITLE BLOCK (Title, Subtitle / Executive One-Liner, Metadata) │
├────────────────────────────────────────────────────────────────────────┤
│ 3. LAYER 1 HERO SECTION (Dominant Incident Card or Verdict Trio)       │
├────────────────────────────────────────────────────────────────────────┤
│ 4. LAYER 2 PRIMARY NARRATIVE (Causal Breakdown, Drivers & Stable Grid) │
├────────────────────────────────────────────────────────────────────────┤
│ 5. LAYER 3 STRATEGIC CONTEXT (Memory Boost, Confidence, Decision Memo) │
├────────────────────────────────────────────────────────────────────────┤
│ 6. LAYER 4 TECHNICAL DETAILS DRAWER (Audit DAG, Telemetry, Raw Logs)   │
├────────────────────────────────────────────────────────────────────────┤
│ 7. PERSISTENT FOOTER (Operational Scope, System Telemetry Summary)    │
└────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Structural Specifications
* **Sidebar Architecture**:
  * Fixed width: 260px.
  * Theme: Deep executive obsidian (`#0D0F14`).
  * Stays pinned on the left; does not scroll with main content.
  * Contains only top-level workflow navigation, active persona selector, and demo trigger.
* **Sticky Top Navigation Bar**:
  * Height: 56px.
  * Background: Pure white (`#FFFFFF`) with 85% background blur and 1px border-bottom (`#E5E7EB`).
  * Stays pinned at the top of the viewport during vertical scrolling.
  * Houses the wordmark (`PRAXIS`), active persona pill, zone indicator (`Zone Z003 · Koramangala`), and live sync pulse.
* **Main Content Viewport Canvas**:
  * Background: Soft executive off-white canvas (`#F8F9FB`).
  * Maximum content width: `1140px` centered.
  * Horizontal padding: `40px` (desktop), `24px` (tablet).
  * Vertical canvas padding: `32px` top, `64px` bottom.
  * Constrained line length: Body narrative text never exceeds `65ch` (characters per line) to maximize reading comprehension.
* **Vertical Spacing Rhythm**:
  * Distance between Top Bar and Page Title: `24px`.
  * Distance between Page Title and Subtitle: `6px`.
  * Distance between Subtitle and Hero Section: `32px`.
  * Distance between Major Narrative Sections: `48px`.
  * Distance between Cards within a Grid: `20px`.
  * Distance between Cards and Technical Drawers: `40px`.
* **The 12-Column Responsive Grid**:
  * Total Columns: 12.
  * Gutter Width: `24px`.
  * Grid Configurations:
    * *Hero Split*: 8 columns (Primary Anomaly/Verdict) + 4 columns (Financial Stakes / Confidence).
    * *Verdict Trio*: 4 columns + 4 columns + 4 columns.
    * *Stable KPI Grid*: 6 columns + 6 columns (2-column layout) or 4 columns + 4 columns + 4 columns (3-column layout).
    * *Full Narrative Width*: 12 columns.
* **Container Hierarchy**:
  * *Level 0 (Base Canvas)*: `#F8F9FB` — Ambient backdrop.
  * *Level 1 (Card Surface)*: `#FFFFFF` — Primary content containers with `14px` border radius and `1px solid #E5E7EB`.
  * *Level 2 (Recessed Well)*: `#F1F3F7` — Embedded metric blocks, stat highlights, or sub-groupings within cards.
  * *Level 3 (Elevated Island)*: Multi-layered drop shadows (`0 8px 24px rgba(0,0,0,0.06)`) reserved for critical incident cards and primary action triggers.

---

## 7. Complete Design Token System
*(Defined strictly as conceptual design tokens; zero CSS implementation code)*

No arbitrary numbers or unmapped colors may be introduced into the interface. Every visual dimension must map to this token architecture:

### 7.1 Typography Scale
Praxis pairs **Plus Jakarta Sans** (authoritative, geometric display numerals and section titles) with **Inter** (crystal-clear, neutral body typography):

| Token Name | Font Family | Size | Weight | Line Height | Tracking | Semantic Usage |
|---|---|---|---|---|---|---|
| `font-display-hero` | Plus Jakarta Sans | 44px (2.75rem) | 800 (Bold) | 1.10 | -0.04em | Critical KPI numbers, primary financial gap figures |
| `font-display-lg` | Plus Jakarta Sans | 32px (2.00rem) | 800 (Bold) | 1.15 | -0.035em | Verdict Trio numbers, incident hero headline |
| `font-title-page` | Plus Jakarta Sans | 24px (1.50rem) | 800 (Bold) | 1.25 | -0.03em | Primary page headers ("Executive Decision Brief") |
| `font-title-section` | Plus Jakarta Sans | 18px (1.125rem) | 700 (Bold) | 1.35 | -0.02em | Section separator headers, primary card headers |
| `font-body-lead` | Inter | 16px (1.00rem) | 500 (Medium) | 1.65 | -0.01em | Subtitles, executive incident summaries |
| `font-body-base` | Inter | 14px (0.875rem) | 400 (Regular) | 1.65 | 0.00em | Standard narrative prose, driver descriptions |
| `font-body-strong` | Inter | 14px (0.875rem) | 600 (Semi-bold) | 1.65 | 0.00em | Key terms, inline impact callouts, table labels |
| `font-caption` | Inter | 12px (0.75rem) | 500 (Medium) | 1.50 | 0.01em | Secondary metadata, persona badges, freshness tags |
| `font-overline` | Inter | 10px (0.625rem) | 800 (Bold) | 1.40 | 0.12em | Uppercase section labels, card eyebrow tags |
| `font-code` | JetBrains Mono | 12px (0.75rem) | 500 (Medium) | 1.50 | 0.00em | Finding IDs, lineage hashes, entity keys |

### 7.2 Spacing & Layout Scale
Derived from a strict 4-point/8-point base module:
* `space-1`: 4px (Micro offsets, status dot gaps)
* `space-2`: 8px (Inner badge padding, tight stack gaps)
* `space-3`: 12px (Form row gaps, metadata chip padding)
* `space-4`: 16px (Compact card padding, standard gutter)
* `space-5`: 20px (Grid card spacing)
* `space-6`: 24px (Standard card padding, column gutters)
* `space-8`: 32px (Hero card padding, major section gaps)
* `space-12`: 48px (Macro narrative separation)
* `space-16`: 64px (Canvas vertical boundaries)

### 7.3 Border Radius System
* `radius-sm`: 6px (Input fields, buttons, pills, status chips)
* `radius-md`: 10px (Sub-cards, recessed stat wells, notice boxes)
* `radius-lg`: 14px (Primary card containers, hero alert blocks)
* `radius-xl`: 18px (Floating modals, overarching workflow shells)
* `radius-full`: 999px (Pills, badges, avatars, dot indicators)

### 7.4 Shadow & Elevation Levels
* `elevation-0`: Flat (No shadow; 1px border only. Used for recessed wells).
* `elevation-1`: Subtle (`0 1px 3px rgba(0,0,0,0.05), 0 1px 2px rgba(0,0,0,0.03)` — Standard card at rest).
* `elevation-2`: Medium (`0 4px 14px rgba(0,0,0,0.06), 0 2px 4px rgba(0,0,0,0.02)` — Card hover state, dropdown menus).
* `elevation-3`: High (`0 8px 24px rgba(0,0,0,0.08), 0 3px 8px rgba(0,0,0,0.03)` — Hero incident cards, sticky headers).
* `elevation-4`: Floating (`0 16px 40px rgba(0,0,0,0.12), 0 6px 12px rgba(0,0,0,0.04)` — Modals, drawer overlays).

### 7.5 Color Palette & Semantic Assignment
* **Neutral Executive Scale**:
  * `neutral-950` (`#0A0E1A`): Primary text, wordmarks, authoritative headers.
  * `neutral-700` (`#374151`): Secondary narrative prose, card body text.
  * `neutral-500` (`#6B7280`): Tertiary metadata, timestamps, baseline notes.
  * `neutral-400` (`#9CA3AF`): Borders, inactive tabs, muted icons.
  * `neutral-200` (`#E5E7EB`): Card perimeter borders, table horizontal rules.
  * `neutral-100` (`#F1F3F7`): Recessed stat wells, chip backgrounds.
  * `neutral-50` (`#F8F9FB`): Global background canvas.
  * `neutral-0` (`#FFFFFF`): Card surface, modal surfaces.
* **Brand Royal Violet (Intelligence & Memory)**:
  * `violet-900` (`#4C1D95`): Memory boost text highlights, deep gradient stops.
  * `violet-800` (`#5B21B6`): Primary action button, Memory Boost hero background.
  * `violet-600` (`#7C3AED`): Active sidebar selection, brand accents, flow arrows.
  * `violet-100` (`#EDE9FE`): Memory badge backgrounds, active pill highlights.
  * `violet-50` (`#F5F3FF`): Memory reassurance strip, subtle violet card tints.
* **Semantic Operational Status**:
  * **Critical / Action Required**: `crimson-600` (`#DC2626`) on `crimson-50` (`#FEF2F2`) with `crimson-200` border.
  * **Healthy / Operational**: `emerald-600` (`#059669`) on `emerald-50` (`#ECFDF5`) with `emerald-200` border.
  * **Warning / Qualified**: `amber-600` (`#D97706`) on `amber-50` (`#FFFBEB`) with `amber-200` border.
  * **Informational / Contextual**: `blue-600` (`#2563EB`) on `blue-50` (`#EFF6FF`) with `blue-200` border.

### 7.6 Component Sizing & Styling Philosophies
* **Buttons**:
  * *Primary*: Solid `violet-800` fill, white text, subtle hover lift, font-weight 600. Reserved strictly for the single primary decision on a page.
  * *Secondary*: Outlined (`1px solid neutral-200`), white background, `neutral-700` text, subtle elevation on hover.
  * *Ghost / Tertiary*: Text-only with chevron, no background, `violet-600` color.
  * *Destructive*: Outlined crimson border, crimson text, used for rejection/escalation.
* **Badges & Pills**: Height 24px, pill-radius (`999px`), uppercase `font-overline`, padding `2px 10px`. Semantic border + subtle background tint.
* **Tables**: Zero vertical borders. Thin 1px horizontal dividers (`neutral-200`). Row height 48px. Header row uppercase, tracked (`0.08em`), muted gray. Numbers right-aligned and tabular.
* **Horizontal Charts / Bars**: Height 12px, border-radius 6px, smooth fill, right-aligned percentage and rupee values. Never display 3D charts, radial gauges with thick borders, or decorative pie charts.

---

## 8. Navigation Principles & Executive Flow

Navigation exists exclusively to **advance the operational decision workflow**, not to expose code packages or database directories:

### 8.1 Sidebar Membership Rules
* **What Belongs in the Sidebar**:
  1. *Brand Identity*: Clean wordmark + product descriptor.
  2. *Active Persona Switcher*: Prominent dropdown allowing seamless toggle between Business Leader and Operations Manager.
  3. *Primary Workflow Navigation (3 items)*:
     * `◉ Morning Briefing` (Today's urgent events)
     * `⌕ Active Investigation` (Causal forensic workspace)
     * `✓ Actions & Decisions` (Executive action directive & past history)
  4. *System Architecture Navigation (2 items)*:
     * `⊗ Memory & Learning` (Compounding organizational knowledge)
     * `≡ Audit & Governance` (Lineage, DQ gates, security, telemetry)
  5. *Live Demo Trigger*: Persistent action container to run signature demo scenarios without menu hunting.
* **What Must NEVER Appear in the Sidebar**:
  * Sub-tabs (e.g., "What Changed", "Why", "Audit").
  * Individual KPI names (e.g., "Zone GMV", "Repeat Purchase Rate").
  * Raw database tables (e.g., "DuckDB tables", "Lineage registry").
  * Developer debug toggles, environment variables, or raw JSON inspectors.
  * More than 5 primary navigation links.

### 8.2 Persona Switching & Context Persistence
* When a user toggles from *Business Leader* to *Operations Manager*:
  * The application does **not** change URL or reload the session.
  * The data model immediately recalculates entitlements at the semantic layer.
  * The view updates dynamically: Zone totals disappear for the Operations Manager, replaced by Dark Store DS041 contribution metrics; the narrative tone shifts from financial strategy to physical stock reallocations.
  * Active investigation state, selected scenario, and historical logs remain fully preserved.

### 8.3 Breadcrumb Philosophy
* Positioned directly below the sticky top bar.
* Single-line, unobtrusive hierarchy: `Zone Z003 · Koramangala › Week 33 · Aug 2026 › Zone GMV Deficit`.
* Functions as a spatial anchor so the executive always knows their organizational grain without visual distraction.

### 8.4 Cross-Page Narrative Transitions
* Pages do not exist in isolation; they hand off to one another like relay runners:
  * Morning Briefing incident card concludes with: `⌕ Investigate Root Cause & Action →` (navigates to Investigation).
  * Investigation recommendation concludes with: `✓ Proceed to Action & Approval →` (navigates to Decisions).
  * Decision approval concludes with: `⊗ View Updated Memory Precedent →` (navigates to Memory).

---

## 9. Information Architecture & The Executive Narrative Arc

Rather than organizing the product into technical modules or database tables, Praxis is architected as an unbroken **5-Stage Operational Business Workflow**:

```
┌─────────────────────────┐
│   1. MORNING BRIEFING   │  "What needs my attention today?"
└────────────┬────────────┘
             │ (User selects critical incident)
             ▼
┌─────────────────────────┐
│ 2. ACTIVE INVESTIGATION │  "Why did this happen?"
└────────────┬────────────┘
             │ (User evaluates causal decomposition & precedents)
             ▼
┌─────────────────────────┐
│  3. ACTIONS & DECISIONS │  "What should we do about it?"
└────────────┬────────────┘
             │ (User approves directive & dispatches action)
             ▼
┌─────────────────────────┐
│   4. MEMORY & LEARNING  │  "Did it work, and how did Praxis learn?"
└────────────┬────────────┘
             │ (System records empirical outcome & updates weights)
             ▼
┌─────────────────────────┐
│  5. AUDIT & GOVERNANCE  │  "Why should the enterprise trust this?"
└─────────────────────────┘
```

### Stage 1: Morning Briefing
* **Purpose**: Provide a calm, instantaneous situation report at the start of the executive's day.
* **Exit Condition**: The leader identifies the single critical operational fire requiring intervention and transitions directly into the investigation.

### Stage 2: Active Investigation
* **Purpose**: Unpack the root cause of the anomaly with mathematical rigor and clear visual decomposition.
* **Exit Condition**: The leader understands exactly what broke, why it broke, and the degree of empirical confidence before reviewing the solution.

### Stage 3: Actions & Decisions
* **Purpose**: Present a fully synthesized, policy-verified operational intervention with quantified recovery expectations and clear decision rights.
* **Exit Condition**: The leader approves, rejects, or delegates the operational directive with a single decisive interaction.

### Stage 4: Memory & Learning
* **Purpose**: Demonstrate the compounding intelligence of the organization by proving how past decisions and empirical outcomes elevate future confidence.
* **Exit Condition**: The leader verifies that the decision loop is closed and organizational memory has been updated.

### Stage 5: Audit & Governance
* **Purpose**: Provide complete regulatory, data health, and algorithmic transparency for compliance, audit, and operational engineering teams.
* **Exit Condition**: Auditors and technical specialists verify end-to-end data lineage, telemetry health, and row-level entitlement integrity.

---

## 10. Comprehensive Page-by-Page Specifications

---

### Page 1: Morning Briefing
* **Primary Business Question**: *"What needs my attention right now?"*
* **Target Persona**: Zone Business Head / Operations Director.
* **Primary Message**: 
  > "Zone GMV is ₹3.5L below baseline target due to an acute inventory stockout at Dark Store DS041 (Koramangala South). 5 other core KPIs remain stable and on track."
* **Information Priority**:
  1. *Urgent Business Incident Card*: Dominates the screen; highlights the single critical deviation, its financial deficit, and the primary root cause.
  2. *Primary Call to Action*: Direct, unmistakable button to enter the root-cause investigation.
  3. *Stable Operations Grid*: Calm, compact status chips showing healthy KPIs operating within normal parameters.
  4. *Memory Status Indicator*: Reassurance that historical precedents are active and ready to assist today's decisions.
* **Secondary Information**: Baseline historical comparison window, timestamp of last telemetry sync, operational zone tags.
* **Technical Details (Relegated)**: Stream event IDs, raw telemetry polling frequencies, individual store sample counts.
* **Expected User Behavior**: Executive scans the screen for under 10 seconds, immediately understands the sole fire in their zone, and clicks the primary action button.
* **Exit Condition**: Executive clicks `Investigate Root Cause & Action →` to transition into Stage 2.
* **Memory Imprint Upon Leaving**: *"There is exactly one issue today: Koramangala South has a stockout costing us ₹3.5L, and Praxis has already diagnosed it."*

---

### Page 2: Active Investigation
* **Primary Business Question**: *"Why did this anomaly occur, and how certain are we?"*
* **Target Persona**: Zone Business Head & Dark Store Operations Manager.
* **Primary Message**:
  > "The ₹3.5L GMV shortfall is 76.2% driven by a stockout of SKU-2207 and 3 related dairy SKUs at Store DS041. Praxis has HIGH confidence (72/100) supported by a verified historical precedent from August 15."
* **Information Priority**:
  1. *The Executive Verdict Trio*: Three prominent hero pillars at the top of the viewport:
     * Deficit / Performance Gap (`-₹3.5L / -7.8%`)
     * Dominant Causal Factor (`DS041 Stockout / 76.2% share`)
     * Recommended Recovery (`₹3.2L via Cross-Store Reallocation`)
  2. *Driver Decomposition Waterfall*: Ranked horizontal impact bars comparing the stockout driver against secondary operational noise.
  3. *The Memory Boost Hero Card*: Prominent visual celebration of organizational memory—proving that a prior recovery on Aug 15 boosted confidence by +12 points.
  4. *Confidence Gauge & Uncertainty Boundaries*: Honest presentation of confidence score and what unobserved variables could alter the conclusion.
  5. *Action Preview & Transition*: Direct trigger to advance into the execution phase.
* **Secondary Information**: Store segmentation rankings, qualitative customer review excerpts corroborating the stockout.
* **Technical Details (Relegated to Drawer)**: Z-scores, baseline standard deviations, query execution latency, lineage hash keys.
* **Expected User Behavior**: Executive reviews the verdict in 5 seconds, scrolls down to verify the driver breakdown and memory boost in 20 seconds, and proceeds to action.
* **Exit Condition**: Executive clicks `Proceed to Action & Approval →`.
* **Memory Imprint Upon Leaving**: *"The stockout at DS041 is mathematically verified as the real cause, supported by an identical incident we successfully resolved on August 15."*

---

### Page 3: Actions & Decisions
* **Primary Business Question**: *"What specific operational directive should be executed, and by whom?"*
* **Target Persona**: Zone Business Head (approver) / Dark Store Operations Manager (executor).
* **Primary Message**:
  > "Dispatch an L2 emergency cross-store inventory transfer of 450 units from Store DS043 to Store DS041 within 2 hours. This will recover ₹3.2L (91% of the deficit) within 36 hours."
* **Information Priority**:
  1. *Action Hero Card*: Clear executive directive stating the exact physical lever, source and destination nodes, and recovery timeline.
  2. *Operational Metrics Banner*: Expected financial recovery (`₹3.2L`), execution risk (`LOW / Within SLA`), and governance authority (`Dark Store Ops Manager`).
  3. *Operational Decision Memo*: Role-tailored memo written in executive prose explaining the operational context and monitoring requirements.
  4. *One-Click Execution Controls*: High-affordance `✓ Approve & Dispatch Directive` button paired with an `Escalate / Reject` secondary option.
  5. *Closed-Loop Outcome Capture*: Simple interface to log empirical results once the transfer lands.
* **Secondary Information**: Monitoring cadence (hourly inventory checks), downstream repeat purchase risk warnings.
* **Technical Details (Relegated)**: ERP dispatch API schema, webhook retry payloads, token generation logs.
* **Expected User Behavior**: Leader validates that the action is within policy, verifies the expected recovery, and clicks `Approve`.
* **Exit Condition**: Executive approves the directive, generating a persistent `DecisionMemory` record.
* **Memory Imprint Upon Leaving**: *"I approved an inventory transfer from DS043 to DS041 that will recover ₹3.2L of our GMV by tomorrow afternoon."*

---

### Page 4: Organizational Memory & Learning
* **Primary Business Question**: *"How does Praxis compound intelligence and improve future decisions?"*
* **Target Persona**: Executive Leadership, Continuous Improvement Directors, Operations Managers.
* **Primary Message**:
  > "Praxis does not store opinions; it stores mathematically validated decision precedents. By verifying that the Aug 15 transfer resolved a similar deficit, today's decision confidence was boosted from 60 (QUALIFY) to 72 (ANSWER)."
* **Information Priority**:
  1. *The Compounding Value Proof Card*: Visual side-by-side comparison showing Decision 1 (Cold Start: 60 pts) vs. Decision 2 (Memory Enhanced: 72 pts), highlighting the +12 pt confidence boost.
  2. *The Closed-Loop Flow Diagram*: Clean, 5-stage conceptual cycle: *Incident → Action → Outcome → Precedent → Confidence Boost*.
  3. *Active Precedent Portfolio*: Executive case cards of historical interventions, documented recovery amounts, and validation timestamps.
  4. *Governance & Anti-Hallucination Drawer*: Collapsible drawer explaining the C5 gateway admission rules (idempotency, lineage validation, supersession model).
* **Secondary Information**: Record admission dates, driver classification tags, grain levels (Store vs. Zone).
* **Technical Details (Relegated)**: DuckDB table schemas, SQL foreign key constraints, quarantine error codes.
* **Expected User Behavior**: Leader explores the precedent portfolio, gaining deep confidence that Praxis is an institutional asset that prevents recurring operational errors.
* **Exit Condition**: Leader understands the closed learning loop and returns to daily operations.
* **Memory Imprint Upon Leaving**: *"Praxis isn't just an algorithm; it's our company's institutional memory that ensures we never solve the same problem from scratch twice."*

---

### Page 5: Audit & Governance
* **Primary Business Question**: *"Why should enterprise risk, compliance, and engineering leaders trust this system?"*
* **Target Persona**: Enterprise Risk Officers, Compliance Auditors, Lead Data Architects.
* **Primary Message**:
  > "Every claim made by Praxis is deterministically traceable back to immutable raw event streams with strict row-level security and zero LLM hallucination in quantitative logic."
* **Information Priority**:
  1. *Trust Summary Bar*: High-level audit status: `Lineage Complete · DQ Gate Passing · Zero Hallucination Boundary Enforced`.
  2. *End-to-End Lineage DAG*: Visual step-by-step trace from raw inventory stream events to final decision packages.
  3. *Data Health & DQ Gate Monitor*: Status cards tracking data completeness, schema validity, and freshness.
  4. *Row-Level Entitlements Verification*: Clear proof that sensitive financial totals (e.g. Zone GMV) are hidden from store-level personnel.
  5. *Execution Telemetry & Cost Ledger*: Latency profiles, LLM token counts, and operational compute costs.
* **Secondary Information**: Transformation pipeline IDs, event sequence numbers, execution timestamps.
* **Technical Details**: Raw JSON payload inspectors, exception traces, database connection parameters.
* **Expected User Behavior**: Compliance officers and engineers inspect the audit trails, verify algorithmic boundaries, and validate enterprise readiness.
* **Exit Condition**: Auditor completes validation and signs off on operational governance.
* **Memory Imprint Upon Leaving**: *"Praxis adheres to enterprise-grade compliance: deterministic mathematics are strictly separated from generative narrative, and data privacy is enforced at the semantic layer."*

---

## 11. The Flagship Experience: Deep Investigation Workflow

The Active Investigation screen is the crown jewel of Praxis. It must accommodate four distinct cognitive depths seamlessly on a single scrollable canvas:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 1. THE 5-SECOND SCAN EXPERIENCE (Immediate Visual Anchoring)          │
│ • Executive Verdict Trio: Deficit (-₹3.5L) | Cause (DS041) | Fix (₹3.2L)│
│ • Outcome Pill: [✓ ANSWER · High Confidence (72/100)]                  │
├────────────────────────────────────────────────────────────────────────┤
│ 2. THE 20-SECOND EVALUATION (Causal & Location Decomposition)          │
│ • Driver Contribution Waterfall: Stockout Rate 76.2% vs Order Vol 14% │
│ • Location Segmentation: DS041 highlighted (88% of store variance)   │
├────────────────────────────────────────────────────────────────────────┤
│ 3. THE 1-MINUTE VALIDATION (Memory Precedent & Confidence Rigor)      │
│ • Memory Boost Hero: +12 pts from validated Aug 15 transfer precedent │
│ • Confidence Component Stack: Materiality + Dominance - Penalties     │
│ • Competing Hypotheses: Competitor promo analyzed and rejected        │
├────────────────────────────────────────────────────────────────────────┤
│ 4. DEEP AUDIT & ACTION DISPATCH (Governance & Execution)               │
│ • Counterfactual Model: What GMV would be if DS041 did not stock out  │
│ • Downstream Risk: Lagged repeat purchase impact warning              │
│ • Action Command Block: Direct dispatch button to Actions Workspace   │
│ • Collapsible Technical Drawer: Raw event trace, SQL hash, latency ms │
└────────────────────────────────────────────────────────────────────────┘
```

### 11.1 The Exact Scroll Narrative Progression
As an executive smoothly scrolls down the Investigation page, each section anticipates and answers their next logical question:

1. **"What is the damage?"** → Top Verdict Trio establishes the ₹3.5L deficit immediately.
2. **"What broke?"** → Driver waterfall isolates the stockout as explaining 76.2% of the gap.
3. **"Where did it break?"** → Location ranking pinpoints Dark Store DS041 in Koramangala South.
4. **"Have we seen this before?"** → The Memory Boost Card slides into view, proving an identical issue was solved on Aug 15.
5. **"How sure are we?"** → Confidence gauge shows 72/100, explicitly detailing that alternative hypotheses (e.g. competitor pricing) were tested and ruled out.
6. **"What if we fix it?"** → Counterfactual scenario calculates a ₹3.2L recovery.
7. **"What do I do right now?"** → High-affordance primary button routes the executive directly to execution.
8. **"Show me the proof for compliance."** → Discreet bottom expander opens the complete deterministic lineage DAG.

---

## 12. Structural ASCII Wireframes

These structural wireframes establish the universal skeleton and spatial flow for every screen in the system:

### 12.1 Global Application Shell
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ [⬡ PRAXIS] KPI Intelligence   │ 👤 Business Leader (Zone Z003) │ 🟢 Telemetry Active │
├───────────────┬──────────────────────────────────────────────────────────────────────┤
│ WORKSPACE     │ BREADCRUMB: Zone Z003 › Week 33 · Aug 2026 › Active Investigation     │
│ ◉ Morning     ├──────────────────────────────────────────────────────────────────────┤
│ ⌕ Investigate │ PAGE TITLE: Executive Investigation — Zone GMV                       │
│ ✓ Decisions   │ SUBTITLE: Forensic root-cause analysis for Zone Z003 · Koramangala   │
│               ├──────────────────────────────────────────────────────────────────────┤
│ SYSTEM        │                                                                      │
│ ⊗ Memory      │                      [ MAIN CONTENT CANVAS ]                         │
│ ≡ Governance  │                                                                      │
│               │                                                                      │
│ ───────────── │                                                                      │
│ ▶ LIVE DEMO   │                                                                      │
│ [S1] [S2]     │                                                                      │
└───────────────┴──────────────────────────────────────────────────────────────────────┘
```

### 12.2 Morning Briefing Wireframe
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Good morning.                                                                        │
│ Here's what needs your attention today — Mon, 1 Sep 2026 · 09:15 IST.                │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ 🔴 ACTION REQUIRED · Primary Operational Incident                                │ │
│ │ Zone GMV is 7.8% below baseline target — ₹3.5L Deficit                           │ │
│ │ Root cause: 76.2% of gap isolated to inventory stockout at Store DS041.          │ │
│ │ ┌───────────────────┐ ┌────────────────────┐ ┌─────────────────────────────────┐ │ │
│ │ │ ACTUAL VS TARGET  │ │ FINANCIAL STAKES   │ │ OPERATIONAL SCOPE               │ │ │
│ │ │ ₹41.5L vs ₹45.0L  │ │ -₹3.5L Deficit     │ │ Dark Store DS041 · Koramangala  │ │ │
│ │ └───────────────────┘ └────────────────────┘ └─────────────────────────────────┘ │ │
│ │ [ ⌕ Investigate Root Cause & Action → ]      [ ▶ Run S2 (Memory-Enhanced) ]      │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ STABLE OPERATIONS & CONTINUOUS MONITORING (5 KPIs)                                   │
│ ┌──────────────────────────┐ ┌──────────────────────────┐ ┌────────────────────────┐ │
│ │ Stockout Rate · DS042    │ │ Delivery SLA Adherence   │ │ Customer Satisfaction  │ │
│ │ 🟢 2.1% · Stable (Live)  │ │ 🟢 96.4% · Stable (Live) │ │ 🟢 4.7/5 · Stable      │ │
│ └──────────────────────────┘ └──────────────────────────┘ └────────────────────────┘ │
│ ┌──────────────────────────┐ ┌──────────────────────────┐                            │
│ │ Order Fulfillment Rate   │ │ Rider Fleet Availability │                            │
│ │ 🟢 98.8% · Stable (Live) │ │ 🟢 91.2% · Stable (Live) │                            │
│ └──────────────────────────┘ └──────────────────────────┘                            │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ⊗ COMPOUNDING ORGANIZATIONAL MEMORY                                              │ │
│ │ Praxis has 1 validated decision precedent ready to boost today's investigation.  │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 12.3 Active Investigation Wireframe (Flagship Single-Scroll)
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Executive Investigation — Zone GMV                                                   │
│ Scenario: S1 · Period: Week 33 · Zone: Z003          [ ✓ ANSWER · High Confidence ]  │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────┐  ┌─────────────────────────┐  ┌───────────────────────────┐ │
│ │ 01 · BUSINESS DEFICIT│  │ 02 · DOMINANT ROOT CAUSE│  │ 03 · RECOMMENDED FIX      │ │
│ │ -₹3.5L               │  │ DS041 Stockout          │  │ ₹3.2L Recovery            │ │
│ │ 7.8% below baseline  │  │ Explains 76.2% of gap   │  │ L2 Cross-Store Transfer   │ │
│ └──────────────────────┘  └─────────────────────────┘  └───────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ── WHAT HAPPENED ─────────────────────────────────────────────────────────────────── │
│ ┌────────────────────────┐ ┌──────────────────────────┐ ┌──────────────────────────┐ │
│ │ Actual: ₹41.5L         │ │ Expected: ₹45.0L         │ │ Performance Gap: -₹3.5L  │ │
│ └────────────────────────┘ └──────────────────────────┘ └──────────────────────────┘ │
│ Performance gap is outside normal historical variation and economically material.    │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ── WHY IT HAPPENED (CAUSAL ATTRIBUTION) ───────────────────────────────────────────── │
│ #1 Dark Store Stockout Rate  [████████████████████████░░░░] 76.2% (₹2.7L)  Dominant  │
│ #2 Order Volume Contraction  [████░░░░░░░░░░░░░░░░░░░░░░░░] 14.1% (₹0.5L)  Secondary │
│ #3 Competitor Promo Effect   [██░░░░░░░░░░░░░░░░░░░░░░░░░░]  9.7% (₹0.3L)  Unverified│
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ ⊗ VALIDATED HISTORICAL PRECEDENT RETRIEVED (Aug 15, 2026)                        │ │
│ │ Matching incident found at Store DS041. Confidence boosted: 60 → 72 pts.         │ │
│ │ Net Memory Boost: [ +12 pts ]                                                    │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ── CONFIDENCE & EVIDENCE ─────────────────────────────────────────────────────────── │
│ ┌───────────────────────┐  ┌───────────────────────────────────────────────────────┐ │
│ │ SCORE: 72/100         │  │ Why this confidence level:                            │ │
│ │ HIGH · Strong Evidence│  │ + Quantitative dominance verified (+38 pts)           │ │
│ │ [███████████████░░░░] │  │ + Validated memory precedent applied (+12 pts)        │ │
│ │ Range: 0 to 100       │  │ - Unobserved competitor price log (-8 pts)            │ │
│ └───────────────────────┘  └───────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ── WHAT TO DO (RECOMMENDED ACTION) ───────────────────────────────────────────────── │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Action: Execute L2 Cross-Store Transfer: DS043 → DS041 (450 units dairy SKUs)   │ │
│ │ Authority: Dark-Store Ops Manager (Within SLA ≤ 2h)                              │ │
│ │ Expected Impact: ₹3.2L recovered within 36 hours (91% of deficit)               │ │
│ │ Monitoring Plan: Hourly stockout audits at DS041; daily GMV reconciliation.      │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│ [ ✓ Proceed to Executive Action & Approval → ]                                       │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ▼ View Complete Deterministic Method Audit Trail (C1–C5 Step Attribution)            │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 12.4 Actions & Decisions Wireframe
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Actions &amp; Decisions                                                               │
│ Active Operational Directive · Historical Approval Ledger                           │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ [ ✓ Active Recommendation ]                  [ ⊞ Decision History & Learning ]       │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ RECOMMENDED DIRECTIVE #1                                                         │ │
│ │ Action: L2 Emergency Inventory Reallocation (DS043 → DS041)                      │ │
│ │ Recoverable Value: ₹3.2L | Time to Recovery: 36h | Execution Risk: LOW           │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ OPERATIONAL DECISION MEMO                                                        │ │
│ │ Recipient: Business Leader (Zone Z003)                                           │ │
│ │ "DS041 stockout of butter and related dairy items accounts for ₹2.7L of the gap. │ │
│ │ DS043 has 14 days of forward cover. Directing a transfer of 450 units will       │ │
│ │ restore fill rate without jeopardizing DS043 SLAs."                              │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│ [ ✓ Approve & Dispatch Directive ]           [ ✗ Escalate / Request Alternate ]      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 12.5 Memory & Learning Wireframe
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Organizational Intelligence &amp; Memory                                              │
│ Governed Institutional Knowledge · Closed Learning Loop                              │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ THE COMPOUNDING VALUE PROOF                                                      │ │
│ │ ┌─────────────────────────┐        ┌─────────────┐        ┌────────────────────┐ │ │
│ │ │ Decision 1 · Cold Start │        │             │        │ Decision 2 · Boost │ │ │
│ │ │ 60/100 · QUALIFY        │   →    │ +12 pt Boost│   →    │ 72/100 · ANSWER    │ │ │
│ │ │ No prior corporate memory│       │             │        │ Precedent Admitted │ │ │
│ │ └─────────────────────────┘        └─────────────┘        └────────────────────┘ │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ THE CLOSED LEARNING LOOP                                                             │
│ [1. Signal Detected] → [2. Action Approved] → [3. Outcome Confirmed] → [4. Memory]   │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ VALIDATED INSTITUTIONAL PRECEDENT PORTFOLIO                                          │
│ ┌──────────────────────────────────────────────────────────────────────────────────┐ │
│ │ Precedent #DM-001 · Store DS041 Stockout · Admitted 15 Aug 2026                  │ │
│ │ Action: L2 Cross-Store Transfer · Outcome: ₹3.2L Recovered (Confirmed)           │ │
│ └──────────────────────────────────────────────────────────────────────────────────┘ │
│ ▼ View C5 Memory Gateway Rules, Idempotency & Supersession Architecture              │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### 12.6 Audit & Governance Wireframe
```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ Audit &amp; Governance Center                                                         │
│ Lineage Verification · Data Quality Gates · Security Entitlements · Telemetry       │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ [ Lineage & Evidence ] [ Data Health & DQ ] [ Entitlements ] [ Execution Telemetry ] │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ END-TO-END DETERMINISTIC LINEAGE CHAIN                                               │
│ → SRC-INV: Event SE-9931 (DS041, SKU-2207 Stockout Flag = True)                     │
│ → DSR-DS041: Aggregated Daily Stockout Transformation                                │
│ → KPI-zone_gmv-Z003: Evaluated Variance (-7.8%)                                      │
│ → FIND-01: Registered C1 Lineage Finding                                             │
│ → DEC-01: Policy-Admitted Decision Directive                                         │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ DATA QUALITY GATE STATUS                                                             │
│ 🟢 Completeness: 100% | 🟢 Schema Conformance: Valid | 🟢 Stream Latency: 220ms      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 13. Comprehensive Component State Specifications

To guarantee behavioral robustness, every primary component defines an explicit visual appearance across all possible system states:

### 13.1 Hero KPI Card States
* **Critical**: Top border `crimson-600` (4px), soft red ambient shadow, white card background, red chevron, bold negative delta (`↓ 7.8%`), primary red status pill (`🔴 Action Required`).
* **Warning**: Top border `amber-600` (4px), amber status pill (`🟡 Review Caveat`), delta colored amber, explanatory caveat subtext.
* **Healthy**: Top border `emerald-600` (2px), calm green status pill (`🟢 On Track`), green delta arrow (`↑ 1.2%`), standard elevation-1.
* **No Data / Cold**: Muted gray border (`neutral-200`), gray dashed accent, clear empty state icon (`○`), text: *"Diagnostic telemetry awaiting initial stream ingest."*
* **Loading / Refreshing**: Card dimensions fully reserved with an animated subtle gradient shimmer (`neutral-100` to `neutral-200`, 1.5s wave), eliminating layout shift.
* **Low Confidence / Abstain**: Amber border with diagonal hatch watermark, badge: `⊘ Praxis Abstains`, body copy explaining ambiguous driver distribution.

### 13.2 Action Directive Card States
* **Pending Approval**: Solid white surface, royal violet left accent bar (4px), active `Approve` (violet fill) and `Reject` (outlined) buttons enabled.
* **Approved**: Emerald border (`emerald-600`), soft green header tint, status pill: `✓ Approved by Zone Head`, timestamp displayed, buttons replaced by `Dispatched to Fleet OMS`.
* **Rejected / Escalated**: Crimson border (`crimson-600`), status pill: `✗ Escalated to Central Supply Chain`, note field recording reason for rejection.
* **Executing**: Violet border with soft pulsing sync dot, status pill: `⏳ Stock Transfer In Transit (ETA: 14:00 IST)`.
* **Completed / Confirmed**: Muted border, status pill: `✓ Reallocation Landed · Outcome Verified`, outcome feedback metrics visible.

### 13.3 Confidence Gauge States
* **High Confidence (≥70 pts)**: Track fill colored vibrant `emerald-600`, score displayed large in dark obsidian, status text: *"Strong empirical evidence from multiple independent sources."*
* **Medium Confidence (40–69 pts)**: Track fill colored `amber-600`, status text: *"Attribution supported by primary driver; unobserved market factors remain."*
* **Low Confidence (15–39 pts)**: Track fill colored `crimson-600`, status text: *"Signal detected but secondary drivers conflict. Cautious evaluation advised."*
* **Abstain (<15 pts / Multi-Driver Ambiguity)**: Track grayed out, hatch pattern, badge: `⊘ Inconclusive Evidence`, explicit guidance that Praxis will not guess.

### 13.4 Memory Precedent Card States
* **Cold Start**: Subtle neutral container, status pill: `⚪ Cold Start`, text: *"No prior precedent exists in corporate memory. This decision will establish the baseline."*
* **Matched Precedent**: Deep royal violet surface (`violet-800`), radial violet glow, white display typography, bold `+12 pts` callout, active precedent link.
* **Strengthened**: Double-border violet highlight, badge: `✓ Repeatedly Confirmed (3x)`, confidence boost maximized (+25 pts cap).
* **Superseded**: Gray background, strike-through on prior driver hypothesis, orange badge: `⚠ Superseded by New Data`, explanation of updated belief.
* **Retired**: Muted gray outline, badge: `Archived`, note: *"Policy retired following supply chain network re-zoning."*

---

## 14. Motion, Feedback & Micro-Interaction Guidelines

Praxis employs motion with utmost discipline. Motion is never decorative; it is purely functional, providing spatial orientation and interaction confirmation:

### 14.1 Micro-Interaction Behaviors
* **Hover Affordance**: Hovering over an actionable card triggers a subtle 1px vertical lift and expands the shadow from `elevation-1` to `elevation-2` over a `150ms ease-out` curve. Cards that are non-actionable do not lift.
* **Button Press Feedback**: On mouse-down, buttons compress slightly (`transform: scale(0.98)`) and deepen background color by 8% over `80ms`, providing immediate tactile feedback.
* **Page Transitions**: When transitioning between workflow stages (e.g. Briefing → Investigation), the outgoing content fades out over `100ms` while the incoming content translates 8px upward and fades in over `200ms ease-out`. There are zero sliding horizontal carousels.
* **Collapsible Accordions (Layer 4 Drawers)**: Expand smoothly over `240ms cubic-bezier(0.16, 1, 0.3, 1)`. The disclosure chevron rotates cleanly through 180 degrees.
* **Loading Skeleton Shimmer**: Skeleton placeholders pulse with a gentle, linear opacity wave (from 40% to 100% opacity) on a `1.5s` infinite loop. No spinning circular loaders in primary content areas.
* **Success Toast Confirmations**: Slide in smoothly from top-right, pause for 3.5 seconds, and dissolve over `200ms`. Accompanied by a crisp green checkmark.

### 14.2 Timing Curves & Philosophy
* **Fast Micro-Transitions**: `100ms – 150ms` (hover states, button clicks, color shifts).
* **Macro Content Transitions**: `200ms – 250ms` (accordion open, modal fade, drawer slide).
* **Easing Function**: Standard enterprise cubic bezier (`cubic-bezier(0.16, 1, 0.3, 1)` — swift entrance with a gentle, natural deceleration). Elastic, bouncy, or overshoot animations are strictly prohibited.

---

## 15. System Anti-Patterns ("Things Praxis Must Never Do")

These 15 cardinal constraints act as absolute guardrails for all interface decisions:

1. **Never Place Technical Plumbing Above Business Insights**: Mathematical indices (Z-scores, p-values, loss functions) must never appear before the monetary deficit and causal diagnosis.
2. **Never Show More Than One Primary Call-to-Action**: Every viewport has exactly one primary button (`violet-800` fill). All other actions are secondary outlines or text links.
3. **Never Exceed Three Hero Metrics**: Packing five or six big numbers onto a card destroys visual hierarchy. The eye must lock onto no more than three numbers simultaneously.
4. **Never Nest Cards Inside Cards Inside Cards**: Limit card nesting to exactly one level (a recessed well inside a primary surface). Triple nesting creates visual claustrophobia.
5. **Never Overload the Executive with Multiple Competing Alerts**: If four KPIs moved, Praxis prioritizes the single most severe deviation as the hero incident. Secondary KPIs are listed calmly below.
6. **Never Require Reading Paragraphs to Understand an Anomaly**: An executive must understand the problem from the headline and metric trio without reading prose.
7. **Never Expose Uncollapsed Telemetry**: Token usage, query execution times, and server latency belong in Layer 4 drawers, never in primary decision cards.
8. **Never Mix More Than Two Accent Colors on a Screen**: Restrict the palette to Obsidian (structure), Royal Violet (brand/action), and exactly one semantic color (Red for alert, Green for stable).
9. **Never Rely on Color Alone to Communicate State**: Every color-coded element must be accompanied by explicit text labels or standard directional iconography (↑ / ↓ / ✓ / ⊘).
10. **Never Guess When Data Is Inconclusive**: If multi-driver conflict exists, Praxis must boldly state `⊘ Abstain`. It must never fabricate a confident recommendation.
11. **Never Break the Workflow Storytelling Flow**: Never trap an executive on a dead-end page. Every screen must end with a clear handoff to the next logical operational stage.
12. **Never Present Unactionable Findings**: Never tell an executive a KPI dropped without stating what lever exists to fix it, who owns the lever, and the recovery timeline.
13. **Never Allow Unvalidated Feedback to Overwrite Memory Directly**: User feedback must pass through the C5 Gateway validation checks. The UI must never pretend human clicks instantly rewrite algorithmic truth.
14. **Never Use Consumer AI Tropes**: No sparkling stars, magic wands, glowing chatbot bubbles, or futuristic sci-fi terminology.
15. **Never Truncate Financial Precision Imprecisely**: Quantified gaps must always state currency units clearly (e.g. `₹3.5L`, `₹450K`), never raw unformatted floating-point integers (`350124.892`).

---

## 16. The 4-Layer Progressive Disclosure Matrix

To prevent executive cognitive overload, every screen strictly organizes content across four discrete cognitive layers:

| Layer | Temporal Budget | User Activity | Information Exposed | Visual Form |
|---|---|---|---|---|
| **Layer 1** | **0 – 5 Seconds** | Unconscious scan | The primary business verdict, financial stakes, dominant cause, and main action CTA. | Large hero display metrics, high-contrast verdict cards, bold primary action buttons. |
| **Layer 2** | **5 – 15 Seconds** | Deliberate scan | Visual decomposition, ranked causal drivers, store location rankings, stable operations grid. | Horizontal contribution bars, clean status chips, structured operational tables. |
| **Layer 3** | **15 – 30 Seconds** | Focused reading | Confidence scoring breakdown, historical memory precedents, operational decision memos, uncertainty bounds. | Memory boost highlight cards, confidence track gauges, executive memo panels. |
| **Layer 4** | **On Demand (Deep Dive)** | Technical audit | Granular transaction records, telemetry metrics (ms, tokens), lineage DAGs, gateway rules, data health monitors. | Clean collapsible accordions, dedicated audit drawers, monospaced lineage logs. |

---

## 17. Visual Hierarchy & Cognitive Weight Allocation

Visual hierarchy is not about decorative styling; it is the deliberate orchestration of the user's attention. Every visual element in Praxis is assigned a strict tier of visual prominence:

```
TIER 1: HERO METRICS (Maximum Visual Weight)
├── Financial Deficit / Business Stakes (e.g., -₹3.5L)
├── Dominant Root Cause (e.g., Dark Store DS041 Stockout)
├── Recommended Operational Action (e.g., L2 Inventory Transfer)
└── Expected Business Recovery (e.g., ₹3.2L Recovered)
    └── Treated with: Largest typography (2.25rem+), bold weights, high contrast, hero cards.

TIER 2: STRATEGIC CONTEXT (High Visual Weight)
├── Confidence Band & Score (e.g., HIGH · 72/100)
├── Driver Contribution Decomposition (e.g., 76.2% share)
├── Memory Boost Proof Indicator (e.g., +12 pts from Aug 15)
└── Primary Operational Directives & Authority Rights
    └── Treated with: Structured cards, clean horizontal bars, distinct semantic badges.

TIER 3: OPERATIONAL DETAIL (Medium Visual Weight)
├── Stable KPI Status Chips (e.g., Order Fulfillment: 98.4%)
├── Location Segmentation & Exclusions (e.g., DS042, DS043)
├── Executive Role Memos & Narratives
└── Downstream Temporal Risk Disclaimers
    └── Treated with: Calm neutral cards, subtle borders, standard body typography (0.9375rem).

TIER 4: TECHNICAL & AUDIT METADATA (Low Visual Weight — Collapsed)
├── Data Freshness Timestamps & Window Baselines
├── Pipeline Execution Latency, LLM Token Usage, Cost ($0.0004)
├── Finding IDs, Lineage Hashes, DAG Step Identifiers
└── Raw Transaction Tables & Telemetry Inspector
    └── Treated with: Muted grays, compact typography (0.6875rem), placed inside collapsible drawers.
```

---

## 18. Master Component Inventory

Every screen in Praxis is constructed from an intentional catalog of purpose-built enterprise components:

| Component Name | Primary Purpose | Information Displayed | Importance Tier | Interaction / Behavior | Primary Screen Placement |
|---|---|---|---|---|---|
| **Incident Hero Card** | Immediately communicate the day's primary business emergency. | KPI name, deficit amount, variance %, plain-English root cause, financial risk, operational scope. | **Tier 1 (Maximum)** | Anchors the top of the morning brief; houses direct button to enter investigation. | Morning Briefing (Top) |
| **Verdict Trio** | Deliver the complete 5-second answer to an investigation. | 3 pillars: 1. Business Deficit, 2. Dominant Root Cause, 3. Recommended Fix. | **Tier 1 (Maximum)** | Dominates the investigation header; sets up the entire narrative arc. | Active Investigation (Top) |
| **Driver Waterfall Bar** | Quantify causal attribution with mathematical precision. | Ranked horizontal contribution bars (name, % share, ₹ value, driver type). | **Tier 2 (High)** | Scannable visual ranking; clearly isolates dominant driver from residual noise. | Active Investigation (Why) |
| **Memory Boost Card** | Highlight the compounding power of organizational intelligence. | Prior confidence score, boosted confidence score, net points (+12), matched precedent date, scope. | **Tier 2 (High)** | Features deep violet gradient with subtle radial glow; visual anchor of the memory engine. | Active Investigation & Memory |
| **Confidence Gauge** | Honestly communicate analytical certainty and bounds. | Numerical confidence score (0–100), confidence band pill (HIGH/MED/LOW), track progress bar. | **Tier 2 (High)** | Visually transparent; pairs score with explicit list of what data could alter the finding. | Active Investigation (Confidence) |
| **Action Directive Card** | Deliver an unambiguous operational command. | Primary driver, controllable business lever, specific action text, action owner, decision authority. | **Tier 1 (Maximum)** | Clear operational card with distinct visual styling for primary lever. | Active Investigation & Decisions |
| **Executive Decision Memo** | Present tailored narrative prose for the active persona. | Role-specific memo header, operational context, execution mandate, SLA timeline. | **Tier 3 (Medium)** | Structured executive memo format; automatically tailors prose to Business Leader vs Ops Manager. | Decisions & Investigation |
| **Stable KPI Chip Grid** | Reassure the leader that non-deviant operations are stable. | Metric name, current value, variance status, live freshness indicator. | **Tier 3 (Medium)** | Compact 2-column or 3-column chip grid; eliminates bloated table rows. | Morning Briefing |
| **Compounding Proof Box** | Prove that memory improves decision confidence over time. | Decision 1 (Cold Start: 60) vs. Decision 2 (Boosted: 72), boost delta (+12 pts), precedent link. | **Tier 1 (Maximum)** | Clean side-by-side comparative box demonstrating the core value proposition. | Memory & Learning (Hero) |
| **Precedent Case Card** | Display verified institutional experience. | Driver type, store grain, action taken, empirical recovery verified, admission timestamp. | **Tier 3 (Medium)** | Expandable case card representing an admitted `DecisionMemory` / `OutcomeMemory` pair. | Memory & Learning |
| **Outcome Feedback Form** | Capture empirical execution results to close the loop. | Observed outcome input, hypothesis confirmed/rejected radio, submit action button. | **Tier 2 (High)** | Submits real-world results to C5 Gateway; triggers confidence updates for future runs. | Actions & Decisions (History) |
| **Technical Audit Drawer** | House deep compliance, lineage, and telemetry data. | Lineage DAG step trace, customer review text matches, token counts, latency profiles, DQ status. | **Tier 4 (Low)** | Collapsed by default (`st.expander`); fully accessible on demand for auditors and engineers. | Investigation & Governance |

---

## 19. Phased Implementation Roadmap v1.0

To execute this vision methodically and ensure zero regressions in backend logic or deterministic calculations, the redesign will follow a disciplined 6-phase engineering lifecycle:

### Phase 1: Information Architecture & Workflow Routing
* **Phase Objective**: Consolidate global navigation to 5 workflow stages, decouple routing from backend calculation logic, and enforce session state persistence.
* **Deliverables**:
  * Clean 5-item sidebar navigation structure (Morning Briefing, Investigation, Decisions, Memory, Governance).
  * Persona switching toggle (Zone Business Head vs Dark Store Ops Manager) with instant semantic recalculation.
  * Context persistence across scenario switching.
* **Dependencies**: Existing `pipeline.py` and session state schema.
* **Completion Criteria**: User can navigate between all 5 stages and switch personas in under 100ms without triggering pipeline recalculations.
* **Validation Checklist**:
  * [ ] Sidebar contains exactly 5 navigation items + 1 persona selector + 1 live demo trigger.
  * [ ] Switching persona immediately updates displayed data scoping without page reload.
  * [ ] Back and forward browser navigation does not crash session state.
* **Success Metric**: 100% routing stability; zero lost session state during navigation.

### Phase 2: Design System Tokens & Global Layout Skeleton
* **Phase Objective**: Establish the universal page skeleton, typography hierarchy, and spacing tokens across the application.
* **Deliverables**:
  * Centralized design token library implementing Section 7 scales.
  * Universal page layout wrapper (1140px max width, 8pt vertical spacing rhythm, sticky header).
  * Elimination of all remaining default framework chrome, unstyled margins, and harsh borders.
* **Dependencies**: Phase 1 completion.
* **Completion Criteria**: Every page inherits identical margin, padding, typographic, and background tokens.
* **Validation Checklist**:
  * [ ] Canvas width locked to 1140px on desktop screens.
  * [ ] Plus Jakarta Sans active for all display numerals; Inter active for all body text.
  * [ ] Zero nested card boxes across all screens.
* **Success Metric**: 100% visual consistency across screens; zero unmapped CSS styles.

### Phase 3: Morning Briefing Overhaul
* **Phase Objective**: Transform the home screen into a 5-second executive situation briefing.
* **Deliverables**:
  * Urgent Incident Hero Card displaying the primary anomaly, financial deficit, and root cause.
  * Stable Operations Grid rendering healthy KPIs as clean, non-intrusive status chips.
  * Direct action button linking into the active investigation.
* **Dependencies**: Phase 2 layout skeleton.
* **Completion Criteria**: Executive can identify the single primary problem in under 5 seconds.
* **Validation Checklist**:
  * [ ] Critical deviation dominates the viewport above the fold.
  * [ ] Monitored healthy KPIs occupy compact, peaceful status chips.
  * [ ] Single click on the hero CTA navigates seamlessly to the Investigation workspace.
* **Success Metric**: User comprehension of the operational incident in under 10 seconds.

### Phase 4: Investigation Workspace Elevation (The Flagship Experience)
* **Phase Objective**: Build the single-scroll executive forensic narrative arc.
* **Deliverables**:
  * Executive Verdict Trio hero grid at the top of the investigation.
  * Horizontal driver decomposition waterfall bars and store segmentation ranking.
  * Prominent Memory Boost Card showcasing validated historical precedents and confidence delta.
  * Honest Confidence Gauge with explicit uncertainty boundaries and alternative hypothesis testing.
  * Encapsulation of raw telemetry and lineage DAGs into collapsible Layer 4 drawers.
* **Dependencies**: Phase 3 completion.
* **Completion Criteria**: A user can scroll from verdict to root cause to precedent to recommendation in under 60 seconds.
* **Validation Checklist**:
  * [ ] Top Verdict Trio communicates Deficit, Cause, and Fix above the fold.
  * [ ] Driver waterfall clearly displays percentage contribution and rupee values.
  * [ ] Memory Boost card prominently highlights the Aug 15 precedent (+12 pts).
  * [ ] Technical telemetry is 100% hidden inside collapsible drawers.
* **Success Metric**: Full executive understanding of causality and confidence within 45 seconds.

### Phase 5: Actions, Decisions & Closed-Loop Memory Polish
* **Phase Objective**: Streamline operational intervention dispatch and empirical outcome capture.
* **Deliverables**:
  * Executive Action Directive Card with quantified recovery expectations and decision rights.
  * Role-tailored Operational Decision Memo for Business Leader vs Operations Manager.
  * One-click approval and escalation controls.
  * Streamlined outcome feedback form writing directly to the C5 DuckDB memory gateway.
  * Compounding Value Proof Card on the Memory & Learning page (60 pts → 72 pts comparison).
* **Dependencies**: Phase 4 completion.
* **Completion Criteria**: Executive can approve an action in 1 click and verify outcome admission into DuckDB.
* **Validation Checklist**:
  * [ ] Action card explicitly states physical lever, owner, and recovery timeline.
  * [ ] Clicking Approve generates a valid `DecisionMemory` record in DuckDB.
  * [ ] Submitting outcome feedback updates future confidence boost calculations.
* **Success Metric**: Complete decision loop closed in under 3 minutes.

### Phase 6: Executive Polish, Accessibility & Benchmark Verification
* **Phase Objective**: Achieve Accenture/Apple-grade visual perfection, flawless responsive adaptation, and audit sign-off.
* **Deliverables**:
  * Micro-interaction refinement (card hover elevation, button press feedback, smooth drawer slide).
  * Full regression test verification (all 76 unit tests passing).
  * Comprehensive end-to-end user testing against the Accenture Executive Benchmark.
* **Dependencies**: Phases 1–5 completion.
* **Completion Criteria**: 100% passing test suite; flawless executive walkthrough without hesitation or confusion.
* **Validation Checklist**:
  * [ ] All 76 backend unit tests pass without failure or deprecation warnings.
  * [ ] 20-second executive scan test successfully passed by independent reviewer.
  * [ ] Zero visual glitches or text truncations across standard resolutions.
* **Success Metric**: 100% executive presentation readiness.

---

## 20. Summary: The Benchmark for Success

When this redesign is complete, Praxis will satisfy the **Accenture Executive Benchmark**:

* **Within 20 Seconds**: A visiting executive or competition judge will look at the Morning Briefing and immediately understand the business problem, the financial stakes, and the primary driver without reading a paragraph of documentation.
* **Within 60 Seconds**: The user will navigate through the Investigation, absorb the Verdict Trio, inspect the Driver Decomposition, and witness the Memory Boost card prove that the organization learned from prior experience.
* **Within 3 Minutes**: The user will approve the operational action directive, verify the closed-loop outcome, and be able to confidently explain the entire value proposition of Praxis to another executive.
