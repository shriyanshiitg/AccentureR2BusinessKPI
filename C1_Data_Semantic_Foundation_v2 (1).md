# Praxis — C1: Data & Semantic Foundation (v2, Build-Ready)
**Owner:** Data & Semantic Engineer
**Scope unchanged from v1:** dark-store quick-commerce domain, 5 KPIs, 3 source families (OMS; Dark-Store Inventory & Delivery Fleet; Customer Voice), 2 personas (Zone Business Head, Dark-Store Ops Manager). C1 remains the semantic/data trust boundary — everything downstream treats this document as ground truth.
**What changed from v1:** nothing architectural. This revision converts v1's narrative decisions into a schema-exact, executable contract, and separates every decision into LOCKED / PROTOTYPE ASSUMPTION / OPEN so C2 can start without re-deciding anything.
**Not in scope here (owned by C2+):** anomaly/materiality detection, statistical thresholds, PVM decomposition, hypothesis generation, confidence scoring, causal inference, recommendations.

---

## 1. Decision Classification Ledger

Every consequential decision in this document is tagged inline with one of:

- 🔒 **LOCKED** — implement exactly as specified; not open for reinterpretation.
- 🧪 **PROTOTYPE ASSUMPTION** — a deliberate simplification for a synthetic-data demo; would need revisiting for production.
- ❓ **OPEN / REQUIRES DECISION** — cannot be resolved from the Business Brief or the C1 task brief; someone (product/team) must decide before an engineer can build against it.

Master list, grouped by the areas flagged in the task brief:

| Area | Decision | Class |
|---|---|---|
| Source cadence | App Session stream is hourly batch | 🧪 PROTOTYPE ASSUMPTION |
| Source cadence | Inventory stream ≤15 min, OMS ≤24h, Customer Voice ≤7 days | 🔒 LOCKED |
| Timestamps | All source timestamps captured in IST at origin | 🧪 PROTOTYPE ASSUMPTION |
| Timestamps | Day boundary = IST calendar day; delivery events attributed to dispatch day | 🔒 LOCKED |
| Zone attribution | Order/GMV zone = `dark_store.zone_id`, not `customer.home_zone_id` | 🔒 LOCKED |
| Order/session relationship | App Session is a 4th structured source, distinct grain from Order | 🔒 LOCKED |
| Order/session relationship | Guest sessions (`customer_id` null) count in the conversion denominator | 🧪 PROTOTYPE ASSUMPTION |
| Delivery/order relationship | 1:1 Order↔Delivery Event, no split shipments | 🧪 PROTOTYPE ASSUMPTION |
| Repeat Purchase Rate | Computed directly at month grain, not rolled up from weeks | 🔒 LOCKED |
| Repeat Purchase Rate | Store-level view for Ops Manager is a non-authoritative proxy | 🧪 PROTOTYPE ASSUMPTION |
| Repeat Purchase Rate | Minimum history required before a customer counts as "active" in a month | ❓ OPEN |
| Customer Voice granularity | Zone-level only, no `dark_store_id` field | 🔒 LOCKED (source fact, not a choice) |
| Customer Voice granularity | Ops Manager sees zone-wide records filtered by text-match to their store, labeled unverified | 🧪 PROTOTYPE ASSUMPTION |
| Access restrictions | Row-level filtering enforced at semantic layer, not UI | 🔒 LOCKED |
| Cross-grain lag rule | Min 1-day lag, max 45-day lookback, customer-level precedence required | 🧪 PROTOTYPE ASSUMPTION (tunable parameter, stated as such) |
| Discount representation | `discount_applied` is a fraction in [0,1] | 🧪 PROTOTYPE ASSUMPTION |
| Conflicting-definition handling | Praxis surfaces conflicts explicitly rather than silently merging | 🔒 LOCKED |

Anything not in this table but referenced elsewhere in the document inherits the classification stated at first mention.

---

## 2. Source Catalogue

Four structured/semi-structured sources feed C1. App Session is included as the 4th because the Conversion Rate resolution requires it (see §9 rationale, unchanged from v1) — 🔒 **LOCKED**, not an optional addition.

### 2.1 OMS (Order Management System)

| Field | Value |
|---|---|
| Source ID | `SRC-OMS` |
| Business purpose | System of record for orders, line items, GMV, discounts |
| Format | Structured (relational batch export) |
| Grain | Order-level, with nested line items |
| Refresh cadence | Hourly/daily batch — 🔒 LOCKED (source-given) |
| Historical coverage | Full order history from go-live — ❓ OPEN (exact retention not specified; assume unlimited for prototype, flagged) |
| Primary key | `order_id` |
| Foreign keys | `zone_id → Zone`, `dark_store_id → Dark Store`, `customer_id → Customer`, `session_id → App Session` (nullable) |
| Source-of-truth status | Authoritative for orders, GMV, discounts, order status |
| Timestamp field | `order_ts` (event time = business time; no separate ingestion-time field modeled) |
| Access classification | Zone-scoped / Store-scoped per persona (§16) |
| Expected DQ issues | Late-arriving batches; duplicate `order_id` on re-export; discount field unit ambiguity (fraction vs %) |
| Used for | KPI computation (Zone GMV, Order Conversion Rate numerator, Repeat Purchase Rate) |

**Exact fields:**

| Field | Type | Nullable | Description |
|---|---|---|---|
| `order_id` | string | NOT NULL | Natural key |
| `zone_id` | string | NOT NULL | Denormalized from `dark_store.zone_id` at write time |
| `dark_store_id` | string | NOT NULL | Fulfilling store |
| `customer_id` | string | NOT NULL | Order requires a resolved customer (guest checkout not modeled at order stage) |
| `session_id` | string | NULLABLE | Traceability to originating App Session |
| `order_ts` | timestamp | NOT NULL | IST, event time |
| `sku_line_items[]` | array | NOT NULL (≥1 element) | Normalized into Order Line Item entity (§3) |
| `units_sold` | int | NOT NULL | Order-level total, derivable from line items — kept as a redundant field for validation cross-check |
| `gmv_value` | decimal | NOT NULL | Order-level total, must equal `SUM(line_gmv)` — DQ check §12 |
| `discount_applied` | decimal [0,1] | NOT NULL | Fraction — 🧪 assumption |
| `order_status` | enum | NOT NULL | `completed \| cancelled \| failed` |
| `source_version` | string | NOT NULL | |
| `ingested_at` | timestamp | NOT NULL | |

### 2.2 Dark-Store Inventory & Delivery Fleet (two streams, one source family)

**Inventory stream**

| Field | Value |
|---|---|
| Source ID | `SRC-INV` |
| Business purpose | SKU-level stock availability per store |
| Format | Structured, near-real-time event stream |
| Grain | `dark_store_id × sku_id × ts` |
| Refresh cadence | Minutes — 🔒 LOCKED |
| Historical coverage | ❓ OPEN — retention window not specified |
| Primary key | `stock_event_id` (surrogate — raw stream has none) |
| Foreign keys | `dark_store_id → Dark Store`, `sku_id → SKU` |
| Source-of-truth status | Authoritative for stock level and stockout status |
| Timestamp field | `ts` (event time) |
| Access classification | Store-scoped (Ops Manager) / Zone-aggregated (Zone Head) |
| Expected DQ issues | Duplicate events at the same `(dark_store_id, sku_id, ts)`; sensor/API gaps producing missing intervals; negative stock levels from write-back races |
| Used for | KPI computation (Dark-Store Stockout Rate), driver analysis (feeds GMV, Conversion Rate, Repeat Purchase Rate as a driver, not a KPI source) |

Fields: `stock_event_id` (string, NOT NULL, surrogate), `dark_store_id` (string, NOT NULL), `sku_id` (string, NOT NULL), `ts` (timestamp, NOT NULL), `stock_level` (int, NOT NULL, ≥0), `stockout_flag` (bool, NOT NULL).

**Delivery stream**

| Field | Value |
|---|---|
| Source ID | `SRC-DEL` |
| Business purpose | Dispatch/delivery timing and SLA outcome per order |
| Format | Structured, near-real-time event stream |
| Grain | Delivery-event-level (1:1 with `order_id` — 🧪 assumption) |
| Refresh cadence | Minutes — 🔒 LOCKED |
| Historical coverage | ❓ OPEN |
| Primary key | `delivery_event_id` (= `order_id`) |
| Foreign keys | `order_id → Order`, `dark_store_id → Dark Store` |
| Source-of-truth status | Authoritative for SLA adherence |
| Timestamp field | `dispatch_ts` (day-attribution anchor, §7); `delivered_ts` (resolution time, may arrive late) |
| Access classification | Store-scoped / Zone-aggregated |
| Expected DQ issues | `delivered_ts` arriving after the dispatch day has already been "closed" for reporting (late-arrival, handled per §7); missing `delivered_ts` on stuck/lost orders |
| Used for | KPI computation (Delivery SLA Adherence), driver analysis (feeds Conversion Rate, Repeat Purchase Rate) |

Fields: `delivery_event_id` (string, NOT NULL), `order_id` (string, NOT NULL, FK), `dark_store_id` (string, NOT NULL), `rider_id` (string, NOT NULL), `dispatch_ts` (timestamp, NOT NULL), `delivered_ts` (timestamp, NULLABLE), `sla_target_mins` (int, NOT NULL, >0), `sla_met` (bool, NULLABLE — null while in transit).

### 2.3 Customer Voice

| Field | Value |
|---|---|
| Source ID | `SRC-CV` |
| Business purpose | Unstructured contextual evidence (reviews, chat, social, CSAT) |
| Format | Unstructured/semi-structured, free text |
| Grain | Zone-level, per record — 🔒 LOCKED (source fact) |
| Refresh cadence | Weekly, irregular |
| Historical coverage | ❓ OPEN |
| Primary key | `record_id` |
| Foreign keys | `zone_id → Zone` (required), `customer_id → Customer` (nullable) |
| Source-of-truth status | **Not** authoritative for any quantitative KPI. Evidence-only (§13). |
| Timestamp field | `ts` |
| Access classification | Zone-scoped; store-level access is a filtered, unverified subset (§16) |
| Expected DQ issues | No store attribution at source (structural gap, not a data error); duplicate near-identical text from repost/cross-post; sentiment/language variance not normalized |
| Used for | Contextual evidence only — never KPI computation, never driver analysis in the quantitative sense |

Fields: `record_id` (string, NOT NULL), `zone_id` (string, NOT NULL), `customer_id` (string, NULLABLE), `ts` (timestamp, NOT NULL), `source_type` (enum: `review\|chat\|social\|csat`, NOT NULL), `text` (string, NOT NULL), `matched_day` (date, derived, NOT NULL), `matched_week` (string ISO week, derived, NOT NULL).

### 2.4 App Session & Engagement Stream *(4th source — Conversion Rate resolution, §9)*

| Field | Value |
|---|---|
| Source ID | `SRC-SESS` |
| Business purpose | Capture cart-add events independent of whether they convert, so the Conversion Rate denominator is not truncated to converting sessions only |
| Format | Structured event stream |
| Grain | Session-level |
| Refresh cadence | Hourly batch — 🧪 PROTOTYPE ASSUMPTION (§1) |
| Historical coverage | ❓ OPEN |
| Primary key | `session_id` |
| Foreign keys | `customer_id → Customer` (nullable), `zone_id → Zone`, `dark_store_id → Dark Store` (nullable), `converted_order_id → Order` (nullable) |
| Source-of-truth status | Authoritative for cart-add events and abandoned-session evidence |
| Timestamp field | `session_start_ts`, `cart_add_ts` (nullable) |
| Access classification | Store-scoped / Zone-aggregated |
| Expected DQ issues | Duplicate `cart_add` events from client retries; sessions that never resolve `dark_store_id` (pre-store-selection abandonment); `converted_order_id` set but referencing a non-existent order (referential break) |
| Used for | KPI computation (Order Conversion Rate denominator), driver analysis |

Fields: `session_id` (string, NOT NULL), `customer_id` (string, NULLABLE), `zone_id` (string, NOT NULL), `dark_store_id` (string, NULLABLE), `session_start_ts` (timestamp, NOT NULL), `cart_add_flag` (bool, NOT NULL), `cart_add_ts` (timestamp, NULLABLE — required if `cart_add_flag=true`), `converted_order_id` (string, NULLABLE, FK), `source_version` (string, NOT NULL), `ingested_at` (timestamp, NOT NULL).

---

## 3. Canonical Entity Model

Unchanged entity set from v1, plus App Session. Each entity below states purpose, PK, key attributes/types, relationships, and source mapping.

| Entity | Purpose | PK | Key attributes (type) | Relationships | Source mapping |
|---|---|---|---|---|---|
| **Zone** | Top-level geography/reporting unit | `zone_id` (string) | `zone_name` (string), `city` (string) | 1:N Dark Store | Reference dimension (no live source; maintained as a dimension table) |
| **Dark Store** | Fulfillment unit | `dark_store_id` (string) | `zone_id` (string, NOT NULL FK), `store_name` (string), `lat/long` (float), `go_live_date` (date), `status` (enum) | N:1 Zone; 1:N Inventory/Stock Event, Delivery Event | Reference dimension |
| **SKU** | Product unit | `sku_id` (string) | `sku_name` (string), `category` (string), `list_price` (decimal), `active_flag` (bool) | N:M Dark Store via Inventory events | Reference dimension |
| **Customer** | Individual customer | `customer_id` (string) | `home_zone_id` (string, nullable), `signup_ts` (timestamp), `customer_status` (enum) | 1:N Order, 1:N App Session, 1:N Customer Voice Record | Reference dimension, enriched from OMS on first order |
| **App Session** | Cart-add / engagement event, independent of conversion | `session_id` (string) | `customer_id` (nullable), `zone_id`, `dark_store_id` (nullable), `session_start_ts`, `cart_add_flag`, `cart_add_ts` (nullable), `converted_order_id` (nullable) | N:1 Customer (nullable); 0:1 Order | `SRC-SESS` |
| **Order** | Completed/attempted transaction | `order_id` (string) | `zone_id`, `dark_store_id`, `customer_id`, `session_id` (nullable), `order_ts`, `gmv_value` (decimal), `discount_applied` (decimal), `order_status` (enum) | N:1 Zone, Dark Store, Customer; 0:1 App Session; 1:N Order Line Item; 1:1 Delivery Event | `SRC-OMS` |
| **Order Line Item** | Normalized SKU line within an order | `order_line_id` (string, surrogate) | `order_id`, `sku_id`, `units_sold` (int), `unit_price_at_sale` (decimal), `line_gmv` (decimal) | N:1 Order; N:1 SKU | `SRC-OMS` (`sku_line_items[]`, normalized) |
| **Delivery Event** | Dispatch → delivery outcome for one order | `delivery_event_id` (string, = `order_id`) | `order_id`, `dark_store_id`, `rider_id`, `dispatch_ts`, `delivered_ts` (nullable), `sla_target_mins`, `sla_met` (nullable) | 1:1 Order; N:1 Dark Store | `SRC-DEL` |
| **Inventory/Stock Event** | Point-in-time stock observation | `stock_event_id` (string, surrogate) | `dark_store_id`, `sku_id`, `ts`, `stock_level` (int), `stockout_flag` (bool) | N:1 Dark Store; N:1 SKU | `SRC-INV` |
| **Customer Voice Record** | Unstructured evidence record | `record_id` (string) | `zone_id`, `customer_id` (nullable), `ts`, `source_type` (enum), `text`, `matched_day`, `matched_week` (derived) | N:1 Zone; N:1 Customer (nullable) | `SRC-CV` |

### 3.1 Source → Canonical Entity Mapping (explicit, no implicit joins)

| Source | Produces / updates entity |
|---|---|
| `SRC-OMS` | `Order` (1 row per order), `Order Line Item` (N rows per order, normalized from `sku_line_items[]`) |
| `SRC-INV` | `Inventory/Stock Event` (1 row per stream event) |
| `SRC-DEL` | `Delivery Event` (1 row per order, 1:1 by construction) |
| `SRC-CV` | `Customer Voice Record` (1 row per stream record) |
| `SRC-SESS` | `App Session` (1 row per session); back-fills `Order.session_id` when `converted_order_id` resolves |
| Reference dimension (no stream) | `Zone`, `Dark Store`, `SKU`, `Customer` (Customer is dimension-managed but enriched from first OMS/Session appearance) |

---

## 4. Grain & Join Contract

This table is the mechanism that stops technically-valid SQL from producing business-semantically-invalid results.

| Entity / Source | Native Grain | Canonical Grain (for KPI use) | Primary Join Keys | Cardinality | Required Pre-Aggregation | Temporal Rule | Double-Count Risk |
|---|---|---|---|---|---|---|---|
| Order | 1 row / order | Zone × Day (via `order_ts`) | `order_id`; `zone_id`, `dark_store_id` for rollups | 1:N to Order Line Item | None (Order itself is already order-grain) | Bucket by IST day of `order_ts` | Low — but joining Order directly to Order Line Item and then summing `Order.gmv_value` **and** `SUM(line_gmv)` together double-counts GMV. Use exactly one. |
| Order Line Item | 1 row / SKU per order | SKU × Order (rolls up to Zone × Day for GMV) | `order_id → Order`, `sku_id → SKU` | N:1 to Order | Pre-aggregate `SUM(line_gmv)` per `order_id` before joining to Delivery Event (1:1) — joining line items directly to Delivery Event first multiplies delivery rows by line-item count | Inherits `order_ts` from parent Order | **High** if joined to Delivery Event or App Session before aggregating to order grain — a 3-line-item order joined to its 1 delivery event produces 3 delivery rows |
| App Session | 1 row / session | Zone × Day | `session_id`; `converted_order_id → Order` (nullable) | 0:1 to Order | None for conversion numerator/denominator counts (both are session/order counts, not joined sums) | Bucket by IST day of `session_start_ts` (not `order_ts` — a session started late one day and converting after midnight still counts as that day's session) | Medium — joining App Session to Order Line Item to "enrich" session data with product detail multiplies session rows per line item. **Prohibited join** unless pre-aggregated. |
| Inventory/Stock Event | 1 row / SKU-store-timestamp | Dark Store × Day (via active/stockout interval logic, §8) | `dark_store_id`, `sku_id`; joined to Dark Store dimension for `zone_id` | N:1 to Dark Store, SKU | **Required**: collapse raw point-in-time events into per-SKU active/stockout intervals before computing the daily rate (§8) — the daily stockout rate is not a simple COUNT of raw events | Bucket interval boundaries by IST day; an interval spanning midnight is split at the boundary | High if raw events are joined to Order/GMV directly by `(dark_store_id, date)` without interval collapsing first — this can multiply GMV rows by however many stock pings occurred that day |
| Delivery Event | 1 row / order (1:1) | Zone × Day (via `dispatch_ts`) | `order_id → Order`, `dark_store_id → Dark Store` | 1:1 to Order | None (already order-grain) | Attributed to **dispatch day**, not delivered day (§7) — a delivery dispatched day D and delivered day D+1 is a day-D event | Low as a standalone join to Order (1:1). **High** if joined to Order Line Item before Order-level pre-aggregation (see above) |
| Customer Voice Record | 1 row / record | Zone × Day/Week (evidence window, §7) | `zone_id`; `customer_id` (nullable, weak join) | N:1 to Zone | None for retrieval; **prohibited** to join into any KPI aggregation (it is evidence-only, §13) | Matched via `matched_day`/`matched_week` window, not exact `ts` equality | N/A for KPI math (never joined into quantitative rollups). Risk instead is **misuse**: joining it as if it were a quantitative driver would silently fabricate a numeric signal from text |

**Valid joins:** `Order ↔ Order Line Item` (pre-aggregate before further joins); `Order ↔ Delivery Event` (1:1, safe directly); `Order ↔ App Session` (0:1, safe directly via `converted_order_id`); `Inventory/Stock Event → Dark Store → Zone` (dimension join, safe); `Customer Voice Record → Zone` (dimension join, safe, evidence-retrieval only).

**Prohibited joins (without pre-aggregation):** Order Line Item directly to Delivery Event or App Session; raw Inventory/Stock Event directly to Order/GMV by date without interval collapsing; Customer Voice Record into any KPI-value computation.

**Joins requiring temporal alignment:** any join across sources at day grain must first bucket each side to the same IST day using the timestamp field specified for that source (§2), not assume ingestion order implies same-day alignment.

---

## 5. KPI Semantic Contracts (5, complete)

```yaml
kpi_id: zone_gmv
name: Zone GMV
business_definition: >
  Total post-discount transaction value completed within a zone on a
  given day. The headline top-line performance metric for the Zone
  Business Head.
grain: [zone_id, date]
formula: "SUM(order_line_item.units_sold * order_line_item.unit_price_at_sale) for orders where order_status='completed'"
numerator: "SUM(line_gmv) across all completed-order line items in scope"
denominator: none (absolute measure, not a ratio)
dimensions: [zone_id, dark_store_id, sku_id, category, date]
source: SRC-OMS
authoritative_source: SRC-OMS (order_line_item.line_gmv is the single source of truth; order.gmv_value is a redundant cross-check field, not authoritative if the two disagree — see §6 reconciliation policy)
aggregation_rule: "Additive SUM across dark_store, sku, and date"
additivity: additive
non_additivity_notes: >
  GMV itself is additive. Average Selling Price (ASP), if displayed
  alongside GMV, is NOT additive — always recompute ASP as
  SUM(gmv)/SUM(units) at the target grain, never average pre-computed
  ASP values across a rollup.
unit: INR
calendar_basis: IST calendar day (§7)
comparison_windows: [day-over-day, week-over-week, same-day-last-week, month-to-date]
drivers: [dark_store_stockout_rate, delivery_sla_adherence, order_conversion_rate, discount_applied, competitor_dark_store_opening, demand_spike]
data_quality_prerequisites: "order.gmv_value reconciled against SUM(line_gmv) within tolerance (§12); no orphan order_line_items"
freshness_requirement: "≤24h (inherits SRC-OMS SLA)"
lineage: "SRC-OMS -> daily_zone_gmv -> KPI-zone_gmv-{zone_id}-{date} -> finding"
access:
  zone_business_head: "zone-level aggregate across all dark stores in their zone"
  dark_store_ops_manager: "own dark_store_id contribution to zone GMV only; no visibility into other stores or the zone total"
```

```yaml
kpi_id: order_conversion_rate
name: Order Conversion Rate
business_definition: >
  Share of cart-add sessions that result in a completed order,
  measured per zone per day. Denominator must include abandoned
  sessions — see §9.
grain: [zone_id, date]
formula: "COUNT(order.order_id WHERE order_status='completed' AND order.session_id IS NOT NULL) / COUNT(app_session.session_id WHERE cart_add_flag=true)"
numerator: "COUNT of completed orders traceable to a session"
denominator: "COUNT of ALL sessions with cart_add_flag=true, converted or not"
dimensions: [zone_id, dark_store_id, date]
source: SRC-SESS (denominator), SRC-OMS (numerator)
authoritative_source: SRC-SESS for cart-add events; SRC-OMS for completion status
aggregation_rule: "Pooled-ratio rollup: SUM(numerator), SUM(denominator) independently across the rollup grain, divide once"
additivity: non-additive (ratio)
non_additivity_notes: >
  Never average daily/store conversion rates to get a rollup rate.
  Rollup = SUM(completed orders) / SUM(cart-add sessions) at the
  target grain.
unit: percentage
calendar_basis: "Bucketed by session_start_ts day (§4), not order_ts day — a session begun late Day D that converts after midnight is still a Day-D session"
comparison_windows: [day-over-day, week-over-week, same-day-last-week]
drivers: [dark_store_stockout_rate, discount_applied, delivery_sla_predicted_at_checkout, price_sensitivity]
data_quality_prerequisites: "no duplicate cart_add events at same session_id+cart_add_ts; converted_order_id (if set) resolves to a real order"
freshness_requirement: "≤1h (SRC-SESS, 🧪 prototype assumption) blended with ≤24h (SRC-OMS)"
lineage: "SRC-SESS + SRC-OMS -> daily_zone_conversion_rate -> KPI-order_conversion_rate-{zone_id}-{date} -> finding"
access:
  zone_business_head: "zone-level aggregate across all dark stores in their zone"
  dark_store_ops_manager: "single dark_store_id = user.assigned_store, session/cart-add detail restricted to sessions resolved to that store"
```

```yaml
kpi_id: dark_store_stockout_rate
name: Dark-Store Stockout Rate
business_definition: >
  Share of active-SKU time at a dark store spent in a stockout state,
  per day. Defined precisely in §8.
grain: [dark_store_id, date]
formula: "COUNT(sku_intervals WHERE stockout_flag=true) / COUNT(total_active_sku_intervals)"
numerator: "sum of stockout-interval durations across active SKUs at the store on the day"
denominator: "sum of active-interval durations across all active SKUs at the store on the day"
dimensions: [dark_store_id, zone_id, sku_id, date]
source: SRC-INV
authoritative_source: SRC-INV
aggregation_rule: "Store -> zone rollup by weighted average (weighted by active_sku_intervals per store), never simple mean of store rates"
additivity: non-additive (ratio, interval-weighted)
non_additivity_notes: "See §8 for the full interval-collapsing procedure this depends on."
unit: percentage
calendar_basis: "IST day; an interval spanning midnight is split at the boundary (§4, §7)"
comparison_windows: [day-over-day, week-over-week]
drivers: [stockout, sla_breach, rider_capacity, competitor_dark_store_opening, demand_spike]
data_quality_prerequisites: "no duplicate events at (dark_store_id, sku_id, ts); stock_level >= 0; no gaps exceeding the freshness SLA without being marked stale"
freshness_requirement: "≤15 min (SRC-INV)"
lineage: "SRC-INV -> daily_store_stockout_rate -> KPI-dark_store_stockout_rate-{dark_store_id}-{date} -> finding"
access:
  zone_business_head: "zone-level aggregate across all dark stores in their zone"
  dark_store_ops_manager: "single dark_store_id = user.assigned_store, SKU-level detail"
```

```yaml
kpi_id: delivery_sla_adherence
name: Delivery SLA Adherence
business_definition: >
  Share of dispatched orders delivered within the promised SLA
  window, per zone per day, attributed to the dispatch day.
grain: [zone_id, date]
formula: "COUNT(delivery_event WHERE sla_met=true) / COUNT(delivery_event WHERE delivered_ts IS NOT NULL)"
numerator: "resolved deliveries meeting SLA"
denominator: "all resolved deliveries dispatched on the day (in-transit deliveries excluded until resolved, then back-attributed, §7)"
dimensions: [zone_id, dark_store_id, rider_id, date]
source: SRC-DEL
authoritative_source: SRC-DEL
aggregation_rule: "Store -> zone rollup by SUM(met)/SUM(total), not averaged per-store rates"
additivity: non-additive (ratio)
non_additivity_notes: "Same pooled-ratio rollup rule as order_conversion_rate."
unit: percentage
calendar_basis: "Attributed to dispatch_ts IST day, not delivered_ts day (§7 late-arrival rule)"
comparison_windows: [day-over-day, week-over-week]
drivers: [rider_capacity, dispatch_delay, catchment_density, weather, stockout_driven_order_complexity]
data_quality_prerequisites: "delivered_ts >= dispatch_ts when present; 1:1 order-to-delivery integrity"
freshness_requirement: "≤15 min (SRC-DEL)"
lineage: "SRC-DEL -> daily_store_sla_adherence -> daily_zone_sla_adherence -> KPI-delivery_sla_adherence-{zone_id}-{date} -> finding"
access:
  zone_business_head: "zone-level aggregate across all dark stores in their zone"
  dark_store_ops_manager: "single dark_store_id = user.assigned_store, rider-level detail"
```

```yaml
kpi_id: repeat_purchase_rate
name: Repeat Purchase Rate
business_definition: >
  Share of customers active in a zone during a calendar month who
  placed 2+ orders that month. Deliberately lagged/downstream KPI —
  see §11 for full semantic treatment.
grain: [zone_id, month]
formula: "COUNT(DISTINCT customer_id WHERE orders_in_month >= 2) / COUNT(DISTINCT customer_id WHERE active_in_month = true)"
numerator: "distinct customers with >=2 completed orders in the zone-month"
denominator: "distinct customers with >=1 completed order in the zone-month (active_in_month definition, §11)"
dimensions: [zone_id, month]
source: SRC-OMS (monthly rollup)
authoritative_source: SRC-OMS
aggregation_rule: >
  MUST be computed directly at month grain from underlying order
  records. Not derivable by combining weekly figures -- distinct
  customer sets overlap across weeks, so weekly rates are not additive
  into a month figure at all.
additivity: non-additive (distinct-count ratio; least additive KPI in the set)
non_additivity_notes: >
  Any rollup (store -> zone, or sub-month period -> month) requires
  recomputing the distinct-customer sets at the target grain, not
  combining pre-aggregated rates.
unit: percentage
calendar_basis: "Calendar month, IST"
comparison_windows: [month-over-month, same-month-last-year]
drivers: ["delivery_sla_adherence (lagged, subject to §7 precedence rule)", "dark_store_stockout_rate (lagged, subject to §7 precedence rule)", order_conversion_rate, "customer_voice_sentiment (qualitative evidence only, not a numeric driver, §12)"]
data_quality_prerequisites: "customer_id present and valid on all counted orders; no duplicate order_id"
freshness_requirement: "≤24h (inherits SRC-OMS); month figure is necessarily provisional until the month closes"
lineage: "SRC-OMS -> monthly_customer_order_counts -> monthly_zone_repeat_rate -> KPI-repeat_purchase_rate-{zone_id}-{month} -> finding"
access:
  zone_business_head: "zone-level aggregate across all dark stores in their zone"
  dark_store_ops_manager: >
    NOT natively available at store grain -- KPI is zone x month by
    business definition. Ops Manager sees a read-only, labeled
    non-authoritative proxy: repeat-rate contribution of customers
    whose most recent order was fulfilled by their store. (Prototype
    assumption, §1.)
```

---

## 6. Definition-Conflict Reconciliation Policy 🔒 LOCKED

**Principle: Praxis never silently merges conflicting definitions of the same business concept.**

Flow for every metric/concept with more than one candidate source of truth:

```
Source definition(s) → Canonical definition → Reconciliation rule → Authoritative definition
        → [if reconcilable: single value flows downstream]
        → [if NOT reconcilable: CONFLICT state, both values + provenance flow downstream, flagged]
```

**Worked examples:**

1. **"Completed order"** — OMS marks `order_status='completed'` at checkout; the Delivery stream implicitly treats an order as "real" once it has a `delivery_event_id`. Canonical definition: **an order is `completed` only per `OMS.order_status`**, independent of delivery outcome — a completed-but-failed-delivery order is still a completed order for GMV/conversion purposes, and separately scored for SLA. Reconciliation rule: OMS is authoritative for order status; Delivery stream is authoritative for delivery outcome; the two are never merged into one status field. No conflict state possible by construction — this is a scope separation, not a disagreement.

2. **GMV: `order.gmv_value` vs. `SUM(order_line_item.line_gmv)`** — both exist in OMS (§5, `zone_gmv` contract). Canonical definition: `SUM(line_gmv)` is authoritative (§5). Reconciliation rule: if `order.gmv_value` differs from `SUM(line_gmv)` by more than a defined tolerance (§12, DQ check), the order is flagged `CONFLICTING` (§13) — the line-item figure is still used for KPI computation, but the finding/lineage record carries the conflict flag so C2/C3 can see the source disagreed with itself, rather than presenting a silently-corrected number as clean.

3. **"Active SKU"** — the Inventory stream defines active implicitly (any SKU with a stock event that day); the SKU dimension has an explicit `active_flag`. Canonical definition: a SKU is active-for-stockout-rate purposes only if **both** `SKU.active_flag=true` **and** it has at least one stock event that day. Reconciliation rule stated explicitly rather than picking one source arbitrarily, because using stream presence alone would count SKUs the catalog has already discontinued, and using `active_flag` alone would count SKUs with no stock data (undefined stockout status) as active.

4. **Calendar definition** — see §7; IST is the single locked calendar basis, so this conflict is pre-empted rather than reconciled per-instance.

**Downstream behaviour on unreconcilable conflict:** the affected KPI instance or record is marked `CONFLICTING` (§13). C2/C3 receive the value(s), the conflict flag, and both source provenances — they decide how to handle it analytically (e.g., abstain, widen confidence interval). C1 does not resolve conflicts by picking a side when no rule justifies one.

---

## 7. Calendar & Cross-Grain Reconciliation (concrete)

### 7.1 Cross-cadence alignment

- **Timezone: IST (Asia/Kolkata), 🔒 LOCKED.** Business day = `00:00:00–23:59:59 IST`.
- **Timestamp normalization:** all source timestamps are assumed captured in IST at origin (🧪 assumption, §1). If a future source emits UTC, convert to IST before any day-bucketing step — never bucket on raw UTC.
- **Event time vs. ingestion time:** all KPI calendar bucketing uses **event time** (`order_ts`, `session_start_ts`, `dispatch_ts`, `ts`), never `ingested_at`. `ingested_at` is used only for freshness/staleness checks (§12–13), never for KPI day attribution.
- **Daily aggregation of near-real-time streams:** Inventory and Delivery events are bucketed into the IST day containing their event timestamp (§4 table).
- **Irregular Customer Voice records:** each record maps to `matched_day` (IST calendar day of `ts`) and `matched_week` (ISO week, Mon–Sun, IST). Evidence-matching window for a finding on day D: `record.ts ∈ [D − 7 days, D + 2 days]` — asymmetric and tunable (🧪 assumption, unchanged from v1), because complaints often precede formal detection of an issue and stop being useful evidence quickly after.
- **Late-arriving records:** a `delivered_ts`/`sla_met` value arriving after its dispatch day has already been reported is **back-attributed to the original dispatch day** and triggers a recompute of that day's SLA figure, not a new-day event. The same principle applies to any late-arriving OMS batch row: attribute by `order_ts`, recompute the affected day, flag the affected KPI instance as `Stale→Fresh (recomputed)` in lineage.

### 7.2 Day → Month temporal-eligibility rule (KPIs 1–4 vs. KPI 5)

This is a **semantic eligibility rule**, not a causal claim — it defines when a day-grain event is even a *candidate* explanation for a month-grain Repeat Purchase Rate movement; C2/C3 own whether it's actually causal.

A day-grain driver event (e.g., a stockout at store S on day D) is eligible as a candidate explanation for a Repeat Purchase Rate movement in month M only if:

1. **Customer-level linkage:** traceable to a specific `customer_id` affected by the event, who is also one of the customers counted in month M's repeat-purchase evaluation.
2. **Strict precedence:** for that customer, `driver_event_ts < subsequent_order_ts`.
3. **Minimum lag: 1 day.** Same-day association does not qualify.
4. **Maximum lookback: 45 days** prior to the start of month M's evaluation window. 🧪 Tunable parameter, not a fixed business rule.

Zone-level or store-level co-occurrence within the same calendar month, without customer-level precedence, **does not qualify** as eligible.

---

## 8. Dark-Store Stockout Rate — implementation detail

- **Active SKU interval:** the time span between two consecutive stock events for the same `(dark_store_id, sku_id)` where the SKU is catalog-active (`SKU.active_flag=true`, §6 reconciliation). An interval begins at one event's `ts` and ends at the next event's `ts` (or end-of-day, whichever is first).
- **Out-of-stock interval:** the sub-portion of an active-SKU interval during which `stockout_flag=true` held.
- **Daily store-level calculation:** for each store, on each day: `numerator = SUM(duration of out-of-stock intervals across all active SKUs)`; `denominator = SUM(duration of all active-SKU intervals)`. This is an interval-weighted rate, not a count of stockout *events*.
- **Store → zone aggregation:** weighted average, weighted by each store's `denominator` (total active-SKU-interval duration) that day. **Prohibited:** simple mean of store-level daily rates — this over-weights low-SKU-count or low-uptime stores.
- **Midnight-spanning intervals:** split at the IST day boundary; each resulting sub-interval is attributed to its own day (§7).

---

## 9. Order Conversion Rate — implementation detail

- **Resolution (restated, 🔒 LOCKED):** App Session/Cart Add is a **separate structured source** (`SRC-SESS`), not a field embedded in OMS.
- **Session:** one `App Session` row per app visit, `session_id` PK, resolved to a `zone_id` at session start and optionally to a `dark_store_id` once the app resolves a serviceable store.
- **Cart add:** `cart_add_flag=true` with a populated `cart_add_ts`. A session may have multiple cart-modification events at the raw client level; C1 collapses these to a single boolean+timestamp per session (first cart-add event) — duplicate raw events are deduplicated at ingestion, not represented as multiple sessions.
- **Conversion:** a session is "converted" if `converted_order_id` is non-null **and** that order has `order_status='completed'`. A session pointing to a cancelled/failed order is not counted as converted, but **remains in the denominator** as an abandoned-equivalent outcome.
- **Order–session relationship:** `Order.session_id` and `App Session.converted_order_id` are kept as a bidirectional pointer pair for traceability; the denominator computation reads from `App Session` directly, never by counting orders and inferring sessions — this is the mechanism that prevents the denominator from silently degrading to "sessions that converted."
- **Abandoned session representation:** a row in `App Session` with `cart_add_flag=true` and `converted_order_id=NULL`. No separate entity — abandonment is the absence of a link, not a distinct record type.
- **Duplicate event handling:** dedupe key `(session_id, cart_add_ts)`; a repeated event within a short client-retry window (assume ≤2 minutes, 🧪 assumption) is treated as one cart-add.
- **Denominator construction (explicit, restated):** `COUNT(DISTINCT session_id WHERE cart_add_flag=true)` for the zone-day — includes converted **and** abandoned sessions by construction, because both are rows in the same table with the same flag.

---

## 10. Customer Voice — evidence role (explicit)

- **Role:** Customer Voice can **support, challenge, or contextualize** a hypothesis produced from quantitative KPI/driver data. It **cannot independently establish quantitative contribution or causality** for any KPI. 🔒 LOCKED.
- **Consequence of zone-level grain:** no record can be attributed to a specific dark store at source. For the Zone Business Head this is a non-issue (their evidence scope is zone-wide anyway). For the Dark-Store Ops Manager, store-level evidence is a text-matched, **explicitly labeled unverified** subset of zone-wide records (§16) — this is a real structural gap in the source data, not a resolved design, and downstream UI/output must carry the "unverified, zone-wide" label whenever this subset is shown.
- **Freshness:** ≤7 days (§2.3).
- **Access classification:** zone-scoped by default; store view is the filtered subset above.

---

## 11. Repeat Purchase Rate — semantic complexity (explicit, C1 scope only)

- **Customer cohort:** all customers with `home_zone_id` = the zone in question OR at least one order in that zone during the month (zone attribution follows the order-level rule, §1) — 🧪 assumption: a customer is counted in whichever zone(s) they actually ordered from that month, not locked to `home_zone_id`, since `home_zone_id` may be stale or unset.
- **First purchase:** a customer's earliest `order_ts` with `order_status='completed'`, globally (not reset per month).
- **Repeat purchase:** any completed order by a customer who already has ≥1 prior completed order, evaluated within the same calendar month for this KPI's specific formula (§5 contract: ≥2 orders in the month, not "any order after the first ever").
- **Observation window:** calendar month, IST (§7).
- **Monthly calculation:** direct computation from `SRC-OMS`, not rolled up from weeks (§5, non-additivity notes).
- **Minimum history requirement:** ❓ **OPEN.** Neither source brief specifies whether a customer needs a minimum tenure (e.g., account age ≥30 days) before being eligible to count in the "active" denominator. Left undecided here rather than silently assumed, because it materially changes the denominator for new-zone launches.
- **Relationship to daily operational data:** only through the §7.2 eligibility rule — day-grain events are never summed or averaged into this KPI directly.
- **Temporal precedence requirement:** §7.2, restated by reference, not redefined here.
- **C1 vs. C2/C3 boundary (explicit):** C1 defines what the KPI *means*, its grain, its formula, and the eligibility rule for candidate day-grain drivers. C1 does **not** determine which specific stockout or SLA event actually explains a specific month's movement — that investigation is C2/C3's job entirely.

---

## 12. Data-Quality Gate (executable checks)

| # | Condition | Severity | Action |
|---|---|---|---|
| 1 | Record fails schema validation (wrong type, missing required field) | Critical | BLOCK |
| 2 | Required field null (per §2 field tables) | Critical | BLOCK |
| 3 | Duplicate primary key within a batch/stream (`order_id`, `session_id`, `stock_event_id`, `delivery_event_id`, `record_id`) | Critical | QUARANTINE (keep first by `ingested_at`, flag rest) |
| 4 | Referential integrity failure: `dark_store_id` not in Dark Store dimension, or its `zone_id` mismatches the referencing row's `zone_id` | Critical | BLOCK |
| 5 | Referential integrity failure: `sku_id` / `customer_id` not in respective dimension | High | QUARANTINE |
| 6 | `converted_order_id` set but does not resolve to an existing order | Medium | WARN, treat session as unconverted for KPI purposes |
| 7 | Range violation: `stock_level < 0` | High | QUARANTINE |
| 8 | Range violation: `discount_applied` outside [0,1] | High | QUARANTINE |
| 9 | Range violation: `units_sold < 0`, `gmv_value < 0`, `sla_target_mins <= 0` | Critical | BLOCK |
| 10 | `delivered_ts < dispatch_ts` | High | QUARANTINE |
| 11 | `order.gmv_value` vs `SUM(line_gmv)` mismatch beyond tolerance (e.g. >₹1 or >0.5%) | Medium | WARN + flag `CONFLICTING` (§6, §13) |
| 12 | Timestamp more than 5 minutes in the future (clock skew) | Medium | QUARANTINE |
| 13 | Source freshness SLA breached (§2 cadences) | Medium | WARN + mark `Stale` (§13), do not BLOCK — stale data still flows with a state flag |
| 14 | Unexpected categorical value (e.g. `order_status` outside the 3 defined enums) | High | QUARANTINE |
| 15 | Orphan record: `Order Line Item` with no parent `order_id`, or `Delivery Event` with no parent `Order` | Critical | BLOCK |
| 16 | Impossible business state: `order_status='completed'` but zero line items | Critical | BLOCK |
| 17 | Impossible business state: `App Session.cart_add_flag=true` with null `cart_add_ts` | High | QUARANTINE |
| 18 | Duplicate inventory event at exact `(dark_store_id, sku_id, ts)` | Medium | QUARANTINE (dedupe, keep one) |

BLOCK = record excluded from all downstream computation, error logged. QUARANTINE = record excluded from KPI computation but retained/visible for investigation, distinct from BLOCK. WARN = record included but flagged. PASS = no flag (implicit for anything not matching a rule above).

---

## 13. Data States (explicit representation, downstream contract)

| State | Trigger | What's passed downstream |
|---|---|---|
| **Fresh** | Within freshness SLA (§2), no DQ flags | Value + normal confidence-relevant metadata |
| **Stale** | Freshness SLA breached (§12 #13) | Value **is still passed**, tagged `state=STALE`, with `as_of_ts`. Never silently treated as fresh. |
| **Partially available** | Some but not all expected records for the grain/period have arrived (e.g., some stores' inventory feed lagging) | Partial value passed, tagged `state=PARTIAL`, with the set of `dark_store_id`s/sources actually represented |
| **Missing** | No data exists for the requested grain/period/source (including: user lacks access, §16) | **No value.** Tagged `state=MISSING`, with a reason code distinguishing "not yet arrived," "genuinely does not exist," and "access-restricted." 🔒 A missing/restricted source is never represented as a zero, a null-defaulted-to-negative, or absence-of-signal. |
| **Conflicting** | Two sources disagree on the same concept beyond reconciliation tolerance (§6, §12 #11) | Both values passed with provenance, tagged `state=CONFLICTING` |
| **Invalid** | Failed a BLOCK-severity check (§12) | Excluded from computation; tagged `state=INVALID` in the audit trail only, not surfaced as a usable value |

**Explicit non-negotiable rule (🔒 LOCKED), restated because it is easy to get wrong downstream:** if Customer Voice evidence is `MISSING` for a finding, the correct downstream representation is *"Customer Voice evidence is unavailable for this finding"* — never *"there is no customer complaint."* Absence of evidence is not evidence of absence, and C1's job is to make that distinction impossible to lose in the handoff.

---

## 14. Lineage (memory-ready ID scheme, unchanged principle from v1, made concrete)

| Stage | ID format | Worked example |
|---|---|---|
| Source record | native key | `order_id = ORD-88213` |
| Dataset/version | `{SRC_ID}-{batch_or_stream_version}` | `SRC-OMS-v2026-08-15-14h` |
| Transformation (materialized aggregate) | `{STAGE_PREFIX}-{grain_key}-{period}` | `DZG-Z003-20260815` (Daily Zone GMV) |
| Canonical record | entity PK (§3) | `dark_store_id = DS041` |
| KPI evaluation | `KPI-{kpi_id}-{grain_key}-{period}` | `KPI-dark_store_stockout_rate-DS041-20260815` |
| Finding | `FIND-{kpi_instance_id}-{seq}` | `FIND-KPI-dark_store_stockout_rate-DS041-20260815-01` |
| Timestamp/version | `created_at`, `source_version` on every stage | ISO-8601, IST |

**Worked example, end to end:**
`SRC-INV` stream event `stock_event_id=SE-9931` (`dark_store_id=DS041, sku_id=SKU-2207, ts=2026-08-15T11:40:00+05:30, stockout_flag=true`) → collapsed into an out-of-stock interval within transformation `DZG-INV-DS041-20260815`'s sibling stockout aggregate `DSR-DS041-20260815` → evaluated as `KPI-dark_store_stockout_rate-DS041-20260815` → flagged materially high, producing `FIND-KPI-dark_store_stockout_rate-DS041-20260815-01`. This `finding_id` is exactly what a future Memory-persona decision (`DEC-FIND-...-01-01`) and outcome (`OUT-DEC-...-01`) attach to, using the same deterministic ID scheme — no redesign needed. Decision/outcome records carry `validation_status ∈ {pending, approved, rejected, demo_preapproved}`; the seeded historical record for the signature demo uses `demo_preapproved`, entering through the same admission interface production memory would use.

Lineage is stored as a generic edge table: `lineage_edge(from_id, to_id, edge_type, created_at)` — not a hardcoded hierarchy — so later stages (decision, outcome) attach without schema change.

---

## 15. Entitlement Matrix & Partial-Evidence Behaviour

| Persona | Row scope | Detail level | Permitted dimensions | Restricted fields | Allowed aggregation | Evidence visibility |
|---|---|---|---|---|---|---|
| **Zone Business Head** | `zone_id = user.assigned_zone` | Zone-wide, all stores in zone | `dark_store_id, sku_id (aggregated), date, month` | Other zones' rows entirely; individual `rider_id`, raw `customer_id` lists | Zone-level SUM/ratio rollups per §5 rules | Full zone-wide Customer Voice; full zone-wide driver ranking |
| **Dark-Store Ops Manager** | `dark_store_id = user.assigned_store` | Single store, SKU-level, rider-level | `sku_id, rider_id, date` | Other stores' rows entirely; zone-level totals/rollups; raw customer PII beyond order linkage | Store-level only; no cross-store aggregation | Zone-wide Customer Voice, text-matched to store, **labeled unverified** (§10); Repeat Purchase Rate as labeled non-authoritative proxy (§5, §11) |

**Enforcement (🔒 LOCKED):** row-level security predicates at the semantic layer, evaluated before KPI aggregation or driver ranking — never a UI-level hide. This is what prevents a technically-permitted query from bypassing scope.

**Partial-evidence behaviour (🔒 LOCKED, applies regardless of persona):**

1. Analysis continues using whatever evidence the user is entitled to access — a missing/restricted source does not block the rest of the response.
2. Inaccessible information is never treated as negative evidence (§13 rule, restated in the access context).
3. The response must explicitly identify which evidence was unavailable and why (`MISSING — access-restricted` vs. `MISSING — not yet arrived`, §13).
4. An access-request/escalation path is represented for the prototype as a stub state (`evidence_state=RESTRICTED, escalation_available=true`) — the actual workflow is out of scope for C1/C2 and is a roadmap item, not built in the live demo.
5. Security is enforced before the analytical query runs, not by hiding fields in the response after the fact.

---

## 16. Semantic Query Contract (interface, not an NL agent)

For each supported query type: Input → Required context → Semantic resolution → Output → Validation → Failure state.

| Query type | Input | Required context | Semantic resolution | Output | Validation | Failure state |
|---|---|---|---|---|---|---|
| What does KPI X mean? | `kpi_id` | none | Look up §5 YAML contract | `business_definition, formula, unit, grain` | `kpi_id` exists in the 5 defined KPIs | `UNKNOWN_KPI` |
| What is the valid grain? | `kpi_id` | none | §5 contract `grain` field | grain tuple | as above | `UNKNOWN_KPI` |
| What is the valid aggregation? | `kpi_id`, target rollup grain | none | §5 `aggregation_rule` / §4 join contract | aggregation rule + additivity flag | target grain must be coarser-or-equal to native grain | `INVALID_ROLLUP_GRAIN` |
| What data sources support KPI X? | `kpi_id` | none | §5 `source`/`authoritative_source` | source ID(s) | as above | `UNKNOWN_KPI` |
| What dimensions can legitimately explain KPI X? | `kpi_id` | none | §5 `drivers` list | driver list with source | as above | `UNKNOWN_KPI` |
| What is the applicable comparison window? | `kpi_id`, requested window | none | §5 `comparison_windows` | valid window or nearest valid alternative | requested window must be in the allowed list | `UNSUPPORTED_COMPARISON_WINDOW` |
| What evidence is available to this user? | `user_id`, `finding_id` or `grain_key` | user's persona/scope (§15) | apply entitlement filter, resolve data state per source (§13) | list of `(source, state, value_or_reason)` tuples | user scope must resolve to exactly one persona | `UNRESOLVED_SCOPE` |
| What is the freshness/state of the evidence? | `source_id` or `kpi_instance_id` | none | §2 SLA + §13 state logic | `state ∈ {Fresh, Stale, Partial, Missing, Conflicting, Invalid}` + `as_of_ts` | source/instance must exist | `UNKNOWN_SOURCE_OR_INSTANCE` |
| What is the lineage of this KPI (instance)? | `kpi_instance_id` or `finding_id` | none | §14 lineage edge traversal | ordered chain of IDs, source → finding | ID must exist in lineage table | `LINEAGE_NOT_FOUND` |

This is a fixed, small interface — not a general-purpose NL agent. Any question outside this list is out of C1's scope by design.

---

## 17. C1 → C2 Handoff Contract

```
KPI definition (§5)
        ↓
canonical fields (§3)
        ↓
valid grain (§5, §4)
        ↓
valid dimensions (§5 drivers, §4 join contract)
        ↓
aggregation rules (§5, §4)
        ↓
calendar rules (§7)
        ↓
data-quality state (§13, per record/instance)
        ↓
freshness (§2, §13)
        ↓
lineage references (§14)
        ↓
access-filtered analytical dataset (§15)
```

**C2 owns:** anomaly/materiality detection, statistical thresholds, PVM decomposition methodology, hypothesis generation, confidence scoring, causal inference, recommendations — i.e., everything that decides *whether* a movement matters and *why*.

**C1 does not own any of the above.** C1's contract ends at: a correctly-scoped, correctly-stated, quality-flagged, lineage-traceable value (or explicit state) for a defined KPI at a defined grain. If C2 needs to distinguish signal from noise, it works entirely from what C1 hands off here — it does not need to re-derive grain, re-decide zone attribution, re-resolve the conversion-rate denominator, or re-invent the day/month lag eligibility rule.

---

## 18. C1 Acceptance Tests

1. **Given** abandoned sessions exist (`cart_add_flag=true`, `converted_order_id=NULL`), **when** Order Conversion Rate is calculated, **then** those sessions remain in the denominator.
2. **Given** an order has multiple line items, **when** Zone GMV is aggregated, **then** the order's GMV is counted exactly once (via `SUM(line_gmv)`, not multiplied by joining to Delivery Event pre-aggregation).
3. **Given** daily conversion rates exist for every day in a week, **when** weekly conversion is calculated, **then** numerator and denominator are summed independently before dividing — not averaged as daily rates.
4. **Given** store-level stockout rates exist for all stores in a zone, **when** zone stockout rate is calculated, **then** the interval-duration-weighted average is applied, not a simple mean of store rates.
5. **Given** a source has breached its freshness SLA, **when** C1 validates it, **then** the data is marked `Stale` and passed downstream with that flag — never silently treated as fresh.
6. **Given** `order.gmv_value` and `SUM(line_gmv)` disagree beyond tolerance, **when** reconciliation runs, **then** the order is flagged `CONFLICTING` and both values are retained with provenance.
7. **Given** a user's persona lacks access to a relevant source, **when** analysis runs, **then** that source is marked `MISSING — access-restricted`, not interpreted as negative evidence, and the rest of the analysis proceeds.
8. **Given** a delivery resolves (`delivered_ts` populated) after its dispatch day has already been reported, **when** SLA is recalculated, **then** the figure is back-attributed to the original dispatch day, not counted as a new-day event.
9. **Given** a candidate day-grain driver event and a month-grain Repeat Purchase Rate movement, **when** eligibility is checked, **then** the driver only qualifies if it satisfies customer-level precedence, ≥1-day lag, and ≤45-day lookback (§7.2) — same-month co-occurrence alone is rejected.
10. **Given** a Customer Voice record has no `dark_store_id`, **when** it is surfaced to a Dark-Store Ops Manager, **then** it is labeled as an unverified, zone-wide, text-matched record — never presented as store-verified evidence.
11. **Given** a duplicate `order_id` appears in an OMS batch, **when** ingestion runs, **then** the first record by `ingested_at` is kept and the duplicate is quarantined, not silently overwritten or double-counted.
12. **Given** a raw inventory event stream with multiple pings per SKU per day, **when** Dark-Store Stockout Rate is computed, **then** the calculation uses collapsed active/stockout intervals, not a raw count of stockout-flagged events.
13. **Given** an `App Session` row has `cart_add_flag=true` and a null `cart_add_ts`, **when** the record is validated, **then** it is quarantined as an impossible business state, not passed through with a null timestamp.
14. **Given** two zones' data are queried by a Zone Business Head scoped to one zone, **when** the query executes, **then** the semantic-layer row filter excludes the other zone's rows before any aggregation runs — not merely hidden in the UI.
15. **Given** a finding is generated from a KPI instance, **when** its lineage is requested, **then** the full chain from raw source record through transformation, KPI evaluation, and finding is returned as an ordered, ID-referenced trail (§14).

---

## C1 Handoff Status

### LOCKED FOR DOWNSTREAM
- Domain, 5 KPIs, 3 source families, 2 personas (unchanged, per instruction)
- App Session as a 4th structured source, and the exact denominator construction for Order Conversion Rate (§9)
- Canonical entity model, source→entity mapping, and the grain/join contract (§3, §4)
- All 5 KPI YAML contracts as the machine-readable semantic representation (§5)
- Zone attribution by fulfilling dark store (not customer home zone)
- IST as the single calendar basis; dispatch-day attribution for delivery events
- Day→month temporal eligibility rule structure (customer-level precedence, strict lag) — though its specific numeric parameters are a prototype assumption (see below)
- Conflict-surfacing policy (§6) and the six data states (§13), including the "missing ≠ negative evidence" rule
- Entitlement enforcement at the semantic layer, and the nested zone/store scope model (§15)
- Lineage ID scheme (§14) and the C1→C2 handoff boundary (§17)

### PROTOTYPE ASSUMPTIONS
- App Session stream cadence = hourly batch
- Guest (customer_id-null) sessions count in the conversion denominator
- 1:1 Order↔Delivery Event (no split shipments)
- `discount_applied` as a fraction in [0,1]
- All source timestamps assumed IST at origin
- Customer Voice evidence-matching window: `[D−7, D+2]` days
- Day→month lag rule parameters: 1-day minimum, 45-day maximum lookback
- Dark-Store Ops Manager's Repeat Purchase Rate view as a non-authoritative store-inferred proxy
- Dark-Store Ops Manager's Customer Voice access as a text-matched, unverified zone-wide subset
- Duplicate cart-add dedupe window of ≤2 minutes

### REQUIRES HUMAN / PRODUCT DECISION
- Minimum customer tenure/history requirement, if any, before counting toward the Repeat Purchase Rate "active" denominator (§11)
- Historical data retention window for each of the 4 sources (not specified in either source brief)
- GMV/line-item reconciliation tolerance threshold (a concrete number, not just "small") for the `CONFLICTING` flag in §6/§12
- Whether a customer's zone attribution for Repeat Purchase Rate should ever fall back to `home_zone_id` when they have zero orders in a given month but are still "assigned" to a zone (currently: not counted at all, per §11 assumption) — worth an explicit product call before C2 builds on it

**C2 can start now.** Everything C2 needs to build detection/investigation logic against is either LOCKED or a clearly-labeled PROTOTYPE ASSUMPTION it can build against as-is; the three OPEN items above affect edge-case precision, not the ability to begin implementation.
