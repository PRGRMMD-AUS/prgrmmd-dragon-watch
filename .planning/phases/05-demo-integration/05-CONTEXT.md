# Phase 5: Demo Integration - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Demo playback engine that steps through the Taiwan Strait escalation scenario GREEN-to-RED in ~5 minutes, using pre-computed results inserted into Supabase. Frontend dashboard reacts via existing realtime subscriptions. Includes demo controls in the dashboard UI and a pre-recorded video fallback. No live API dependencies required.

</domain>

<decisions>
## Implementation Decisions

### Playback mechanics
- Continuous drip pacing — items trickle in one-by-one with small random delays, feels like live intelligence flow (not batch waves)
- Pre-computed results only — no LLM API calls during demo. All narrative_events, movement_events, alerts, and briefs are pre-generated and inserted directly
- Prompt before reset — demo asks user whether to clear tables or layer on top before each run
- 72 simulated hours compressed into ~5 minutes real time

### Scenario narrative
- 5-beat story arc: baseline → first signals → coordination detected → movement confirmed → full alert
- Climax moment: threat banner flipping RED with high confidence — simple, visual, unmistakable
- Extend existing Phase 1 demo dataset (60 articles, 120 posts, 180 vessel positions) — add corresponding narrative_events, movement_events, alerts, and briefs
- Current simulated text is good enough — focus on system behavior, not content polish

### Offline & fallback mode
- Supabase connection required — demo always needs internet (hackathon venue has WiFi)
- No full offline/local fallback needed
- Pre-recorded video as backup — record a perfect demo run, switch to video if live demo breaks
- No live LLM API keys needed (pre-computed results)

### Demo controls & UX
- Controls live in the dashboard UI — small visible control bar, audience can see the presenter controlling it
- Preset speed buttons: Normal (~5 min), Fast (~2 min), Slow (~10 min)
- Simulated clock display showing scenario time advancing (e.g., "T+24h") — audience sees the 72-hour compression
- Start, pause, reset controls in the control bar

### Claude's Discretion
- Engine location (Python backend script vs frontend-driven) — pick what fits the architecture best
- Exact timing intervals for continuous drip pacing
- Control bar positioning and styling within the dashboard
- How to structure the pre-computed demo data files
- Video recording approach for fallback

</decisions>

<specifics>
## Specific Ideas

- The banner flipping RED should be the dramatic peak — build tension through the 5 beats leading up to it
- Continuous drip should feel like watching a real intelligence feed — items appearing naturally, not in obvious batches
- The simulated clock (T+0h → T+72h) helps the audience understand the time compression
- Preset speeds let the presenter speed through boring parts or slow down to explain key moments

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 05-demo-integration*
*Context gathered: 2026-02-07*
