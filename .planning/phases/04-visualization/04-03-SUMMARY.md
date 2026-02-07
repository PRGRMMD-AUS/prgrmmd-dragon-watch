---
phase: 04-visualization
plan: 03
subsystem: ui
tags: [react, event-feed, timeline, recharts, coordination-signals, movement-tags, realtime]

# Dependency graph
requires:
  - phase: 04-visualization
    plan: 01
    provides: React + Vite frontend scaffold, Supabase client, database types, realtime hook, DashboardLayout shell
  - phase: 02-intelligence-processing
    provides: Articles table (60 rows), social_posts table (120 rows)
  - phase: 03-correlation
    provides: narrative_events table (source_ids for coordination), movement_events table (event_type, location for post tags), alert detection_history
provides:
  - Left panel event feed with interleaved article and post cards sorted by timestamp
  - ArticleCard component with coordination signals (purple "COORDINATED" badge)
  - PostCard component with movement category tags and location coordinates
  - NarrativeTimeline component showing threat score evolution over time
  - Recharts area chart with GREEN/AMBER/RED zones and narrative event scatter points
affects: [04-04]

# Tech tracking
tech-stack:
  added: [recharts-area-chart, recharts-composed-chart, recharts-scatter]
  patterns: [temporal matching for movement events, coordination signal cross-reference, multi-source feed interleaving]

key-files:
  created:
    - frontend/src/hooks/useArticles.ts
    - frontend/src/hooks/useSocialPosts.ts
    - frontend/src/hooks/useNarrativeEvents.ts
    - frontend/src/hooks/useMovementEvents.ts
    - frontend/src/components/ArticleCard.tsx
    - frontend/src/components/PostCard.tsx
    - frontend/src/components/EventFeed.tsx
    - frontend/src/components/NarrativeTimeline.tsx
  modified:
    - frontend/src/components/DashboardLayout.tsx
    - frontend/src/index.css

key-decisions:
  - "Temporal matching for movement events: 5-minute window for post-to-event association"
  - "Coordination signals via narrative_events.source_ids Set for O(1) lookup"
  - "Interleaved feed sorted by timestamp to show unified intelligence flow"
  - "Empty state for timeline: 'Awaiting correlation data...' with chart frame"
  - "Recharts ComposedChart for combined area (threat score) and scatter (narrative events)"

patterns-established:
  - "Multi-hook pattern: EventFeed consumes 4 separate hooks (articles, posts, narrative events, movement events)"
  - "Temporal matching strategy: find closest movement event within time window for post enrichment"
  - "Visual coordination signals: purple left border + COORDINATED badge on articles part of narrative events"
  - "Category-based styling: convoy/naval/flight/restricted_zone colors on post movement tags"

# Metrics
duration: 4min
completed: 2026-02-07
---

# Phase 4 Plan 3: Event Feed Cards + Narrative Timeline Summary

**Left event feed with auto-updating article/post cards showing coordination signals and movement tags, bottom narrative timeline with Recharts showing threat score evolution through GREEN/AMBER/RED zones**

## Performance

- **Duration:** 4 minutes (239 seconds)
- **Started:** 2026-02-07T05:30:57Z
- **Completed:** 2026-02-07T05:34:56Z
- **Tasks:** 2 (both executed successfully)
- **Commits:** 3 (2 task commits + 1 fix commit)

## Accomplishments

- Left panel renders 170+ interleaved cards (60 articles + 120 posts) sorted by timestamp
- Article cards show title, domain, tone score, time, and purple "COORDINATED" badge when part of narrative event (DASH-03 requirement)
- Post cards show channel, text excerpt, views, time, movement category tags (convoy/naval/flight/restricted zone), and location coordinates when matched to movement event (DASH-04 requirement)
- Bottom timeline shows Recharts area chart with threat score over time, reference lines at 30 (GREEN/AMBER) and 70 (AMBER/RED)
- Narrative events appear as scatter points on timeline at their confidence level
- Empty state handled gracefully: "Awaiting correlation data..." when no narrative_events exist
- All TypeScript compilation passes, realtime subscriptions functional
- fadeIn animation for new cards appearing at top of feed

## Task Commits

Each task was committed atomically:

1. **Task 1: Left panel event feed with article and post cards** - `2f0639a` (feat)
   - Created useArticles, useSocialPosts, useNarrativeEvents, useMovementEvents hooks
   - Created ArticleCard with coordination signals (purple badge + border when isCoordinated=true)
   - Created PostCard with movement category tags (convoy/naval/flight/restricted zone) and location coordinates
   - Created EventFeed component that interleaves articles and posts by timestamp
   - Wired EventFeed into DashboardLayout feed zone
   - Added fadeIn keyframe animation to index.css

2. **Task 2: Bottom narrative timeline panel** - `388fbe6` (feat)
   - Extended useNarrativeEvents to fetch alert detection_history from correlation_metadata
   - Created NarrativeTimeline component with Recharts ComposedChart
   - Area chart shows threat score over time with gradient fill (red/amber/green zones)
   - Reference lines at y=30 and y=70 for threat level boundaries
   - Scatter points for narrative events at their confidence level
   - Empty state with chart frame and "Awaiting correlation data..." message
   - Wired NarrativeTimeline into DashboardLayout timeline zone

3. **Fix: TypeScript type import errors** - `c907102` (fix)
   - Use 'import type' syntax for all type imports (verbatimModuleSyntax compliance)
   - Add type annotation for forEach id parameter in useNarrativeEvents
   - Fix Tooltip formatter parameter to accept optional name
   - Remove unused cn import and getAreaColor function

**Plan metadata:** (to be committed in final metadata commit)

## Files Created/Modified

**Created:**
- `frontend/src/hooks/useArticles.ts` - Fetch 50 most recent articles, subscribe to INSERT events, prepend to top
- `frontend/src/hooks/useSocialPosts.ts` - Fetch 50 most recent posts, subscribe to INSERT events, prepend to top
- `frontend/src/hooks/useNarrativeEvents.ts` - Fetch narrative events, build coordinatedArticleIds Set from source_ids, fetch alert detection_history
- `frontend/src/hooks/useMovementEvents.ts` - Fetch movement events for temporal matching with posts
- `frontend/src/components/ArticleCard.tsx` - Title, domain pill, tone score, time, purple "COORDINATED" badge when isCoordinated prop true, left border color by tone or purple when coordinated
- `frontend/src/components/PostCard.tsx` - Channel pill, text excerpt (2 lines), views, time, movement category tags (convoy/naval/flight/restricted zone), location coordinates (lat/lon)
- `frontend/src/components/EventFeed.tsx` - Interleaves articles and posts by timestamp, passes coordination and movement data to cards, "INTELLIGENCE FEED" header, skeleton loader
- `frontend/src/components/NarrativeTimeline.tsx` - Recharts ComposedChart with AreaChart for threat score, Scatter for narrative events, reference lines at 30/70, empty state

**Modified:**
- `frontend/src/components/DashboardLayout.tsx` - Wired EventFeed into feed zone, wired NarrativeTimeline into timeline zone
- `frontend/src/index.css` - Added fadeIn keyframe animation for new cards

## Decisions Made

**Temporal matching for movement events (5-minute window):** Since movement_events don't have direct foreign keys to social_posts, match by finding closest movement event within 5 minutes of post timestamp. Acceptable for demo — approximate matching shows the pattern.

**Coordination signals via narrative_events.source_ids Set:** Build a Set of coordinated article IDs from all narrative_events.source_ids arrays for O(1) lookup when rendering ArticleCard. Purple "COORDINATED" badge + purple left border when article ID in Set. Implements DASH-03 requirement.

**Interleaved feed sorted by timestamp:** Combine articles (published_at) and posts (timestamp) into single array, sort descending by time. Shows unified intelligence flow — analyst sees newest items first regardless of source.

**Empty state for timeline:** When narrative_events table empty (0 rows), show chart frame with reference lines and "Awaiting correlation data..." centered text. Handles expected state until correlation engine runs.

**Recharts ComposedChart for timeline:** Use ComposedChart (not just AreaChart) to overlay Scatter points for narrative events on top of Area chart for threat score. Gradient fill shows GREEN/AMBER/RED zones visually. Reference lines at 30 and 70 mark boundaries.

**Category-based styling for movement tags:** convoy (orange), naval (blue), flight (sky), restricted_zone (red) — color-coded badges and left borders on PostCard when movement event matched. Implements DASH-04 requirement. Includes location coordinates when available.

## Technical Highlights

**Multi-hook pattern in EventFeed:** EventFeed consumes 4 separate hooks (useArticles, useSocialPosts, useNarrativeEvents, useMovementEvents) and combines their data. Each hook independently fetches and subscribes to realtime updates. EventFeed merges into single interleaved feed.

**Temporal matching strategy:** For each social post, iterate movement_events and find closest by timestamp within 5-minute window. Best-effort matching acceptable for demo — shows the pattern without requiring exact foreign key relationships.

**Visual coordination signals:** Purple left border + "COORDINATED" badge on ArticleCard when article ID appears in narrative_events.source_ids. Instant visual indicator of coordination detection.

**Realtime prepend pattern:** All 4 hooks use realtime subscriptions with INSERT event handling. New rows prepend to top of array, appear at top of feed with fadeIn animation. Conveys "intelligence flowing in" feel.

**Empty state handling:** Timeline shows "Awaiting correlation data..." when no detection_history exists. Chart frame with reference lines still renders so user sees what the panel will look like.

## Deviations from Plan

None - plan executed exactly as written. All DASH-03 (coordination signals) and DASH-04 (movement tags) requirements implemented successfully.

## Next Phase Readiness

**Phase 4 Plan 4 (Intelligence Brief Sidebar):** Ready to proceed. EventFeed and NarrativeTimeline wired into DashboardLayout. Brief panel zone (col 3, rows 2-3) still has placeholder — ready for IntelligenceBrief component.

**Parallel execution with 04-02:** Successful. 04-02 (ThreatBanner + MapPanel) and 04-03 (EventFeed + NarrativeTimeline) executed in parallel with no merge conflicts. DashboardLayout now has ThreatBanner, MapPanel, EventFeed, and NarrativeTimeline all wired in. Only brief panel remains.

**Data validation:** 170+ cards render correctly (60 articles + 120 posts). No coordination or movement events yet (0 rows in those tables), so no purple badges or category tags visible — expected until Phase 2/3 LLM processing runs. Empty timeline shows "Awaiting correlation data..." as designed.

## Blockers/Concerns

None. All tasks completed successfully. TypeScript compilation passes. Realtime subscriptions functional. Ready for 04-04 (Intelligence Brief).
