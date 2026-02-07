# Phase 4: Visualization - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Real-time intelligence dashboard displaying all six panels via Supabase realtime subscriptions: interactive map, event feeds, narrative timeline, threat indicator, and intelligence brief. Built with Lovable (React) connecting to existing Supabase backend from Phases 1-3. Demo playback control and offline reliability are Phase 5.

</domain>

<decisions>
## Implementation Decisions

### Map panel
- Clean minimal base map (Mapbox Light style) — data is the star, geography is context
- Directional ship/arrow icons for vessel positions showing heading and type (AIS-style)
- Semi-transparent shaded regions overlaid for narrative geographic focus areas (where state media is mentioning)
- Fixed view locked to Taiwan Strait — no panning or zooming (clean demo, no risk of user getting lost)

### Dashboard layout
- Map dominates the center/top — takes ~50% of screen space
- Left panel: stacking event cards (articles, movement posts) that pop in as new data arrives
- Bottom panel: narrative timeline showing how the coordination story is building over time (replaces separate dual-axis correlation chart — bottom panel covers this)
- Right sidebar: intelligence brief panel, always visible
- Top: full-width threat status banner
- Light theme throughout — modern SaaS analytics feel, not dark command center

### Real-time update behavior
- Left panel cards pop/appear in a stack as new items arrive — auto-insert, no "new items" banner
- Vessel position updates are instant snap with a brief pulse effect — no smooth gliding animation
- Narrative timeline in bottom panel updates as new correlations form
- Threat banner transitions color when level escalates — noticeable, attention-grabbing

### Threat indicator
- Full-width colored status banner at top of dashboard
- Shows threat level + confidence score (e.g., "THREAT LEVEL: AMBER — 67% confidence")
- GREEN/AMBER/RED background color on the banner
- No evidence summary in the banner itself — brief panel on right covers the evidence chain

### Intelligence brief panel
- Lives in the right sidebar, always visible alongside the map
- Clean prose format — well-formatted text, professional, no classification-style markings
- Structured sections (assessment, evidence, timeline, collection priorities) but without "UNCLASSIFIED // OSINT" theater
- Updates when new briefs are generated

### Claude's Discretion
- Specific mapping library choice (Mapbox, Leaflet, deck.gl, etc.)
- Exact card design for left panel event cards
- Narrative timeline visualization approach in bottom panel
- Typography, spacing, and color palette within light theme
- Responsive breakpoint handling
- How Lovable scaffolding integrates with custom map/chart components
- Loading states and error handling

</decisions>

<specifics>
## Specific Ideas

- Map should feel clean and minimal — let the intelligence data (vessel icons, shaded regions, cards) tell the story
- Event cards on the left should stack/pop in — feels alive, analyst sees the flow of incoming intelligence
- Vessel position updates should pulse briefly on snap — instant but with a visual cue
- The threat banner should be impossible to miss when it escalates — it's the headline of the whole dashboard
- Bottom narrative panel replaces the dual-axis correlation chart — the timeline IS the correlation visualization
- Lovable generates the React frontend connected to Supabase; the data pipeline (Phases 1-3) feeds the tables that the dashboard subscribes to

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope

</deferred>

---

*Phase: 04-visualization*
*Context gathered: 2026-02-07*
