# Phase 3: Correlation Engine - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Two independent intelligence streams (narrative coordination events + civilian movement events) converge to produce time-windowed, geographically-scoped threat-level alerts. The engine detects when narrative spikes and movement clusters co-occur, calculates a composite threat score with sub-factor breakdown, and writes correlation events and alerts to Supabase. The demo scenario covers a single geographic region (Taiwan Strait) with monotonic escalation from GREEN to RED.

</domain>

<decisions>
## Implementation Decisions

### Geographic Proximity
- **Claude's discretion** on matching approach (predefined zones, bounding boxes, or hybrid) — choose what best fits the existing demo data structure
- **Single-region focus** — Taiwan Strait only for this phase; no multi-hotspot capability needed
- **Claude's discretion** on trigger mode (event-driven vs batch on demand) — pick what fits the demo playback architecture best
- **Claude's discretion** on no-match behavior (record non-correlations or skip) — decide based on what the dashboard and brief generator need

### Threat Scoring Formula
- **Monotonic escalation only** — once AMBER, stays AMBER or goes RED; never de-escalates. This is a design decision, not a limitation.
- **Composite score (0-100) with visible sub-scores** — overall threat level plus breakdown of contributing factors (outlet count, phrase novelty, post volume, geographic proximity). The dashboard will show WHY the level changed.
- **Claude's discretion on threshold values** — tune GREEN/AMBER/RED cutoffs so the demo data produces compelling transitions. Fixed thresholds preferred but exact numbers are flexible.
- **Confidence score required** — each threat assessment includes a confidence percentage alongside the threat level (e.g., "RED — 87% confidence")

### Evidence Chain Linking
- **Claude's discretion on evidence organization** — choose between by-stream grouping, chronological, or hybrid based on what works best for the brief generator downstream
- **Claude's discretion on evidence storage** — decide between foreign key references only vs denormalized snapshots based on brief generator and dashboard query needs
- **Claude's discretion on alert narrative** — decide whether correlation events include a plain-English summary or leave that entirely to the brief generator
- **Consolidate into single escalating alert** — multiple correlation events over time merge into one living alert that escalates, rather than separate stacked events. Cleaner for the threat gauge.

### Claude's Discretion
- Geographic matching approach (zones, bounding boxes, or hybrid)
- Correlation trigger mode (event-driven vs batch)
- Non-correlation recording behavior
- Exact GREEN/AMBER/RED threshold values
- Evidence storage format (references vs denormalized)
- Evidence organization (by stream vs chronological)
- Whether correlation events include plain-English summaries

</decisions>

<specifics>
## Specific Ideas

- The 72-hour correlation window from the roadmap success criteria should be the primary matching parameter
- Sub-scores should feel like an intelligence product — analysts want to see what's driving the assessment, not just a number
- Consolidating alerts means the threat gauge on the dashboard shows one clear, escalating status rather than a confusing list of separate events

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-correlation-engine*
*Context gathered: 2026-02-07*
