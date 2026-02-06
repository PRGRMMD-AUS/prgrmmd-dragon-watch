# Pitfalls Research

**Domain:** OSINT data fusion + LLM analysis + real-time correlation
**Researched:** 2026-02-07
**Confidence:** HIGH (based on known patterns in data pipelines, LLM integrations, and hackathon constraints)

## Critical Pitfalls

### Pitfall 1: LLM API Dependency for Live Demo

**What goes wrong:**
The demo fails mid-presentation because Claude/GPT API hits rate limits, returns 429 errors, or experiences downtime. The dashboard shows blank panels or error messages in front of judges. Without cached responses, the entire demo collapses.

**Why it happens:**
Teams build the full pipeline assuming live API access will "just work" during the demo. They don't cache LLM responses during development. When demo day arrives, the API is slower due to network conditions, account limits kick in after repeated testing, or the provider has an outage.

**How to avoid:**
- Cache ALL demo scenario LLM responses during Phase 3.4 (testing)
- Build a fallback layer: if API call fails, serve cached response keyed by input hash
- Pre-generate every response the demo will need and store in Supabase `cached_responses` table
- Add a `--offline` flag to demo playback engine that uses cached-only mode
- Never call live APIs during the actual judge presentation — use pre-computed results

**Warning signs:**
- API calls in demo playback engine that aren't wrapped in try/except with cache fallback
- No cached responses committed to the repo or pre-loaded in Supabase
- Demo rehearsals depend on live API calls succeeding
- Response time variability during testing (300ms one run, 5000ms the next)

**Phase to address:**
Phase 3.4 (End-to-end testing) — pre-cache all demo responses
Phase 3.5 (Fallback/offline mode) — implement cached response fallback

**Recovery cost if it happens:**
HIGH — If discovered during demo, recovery is impossible without cached responses. If discovered during Phase 4 rehearsal, requires 2-4 hours to cache all responses.

---

### Pitfall 2: Correlation False Positives from Noisy Data

**What goes wrong:**
The correlation engine fires constantly on unrelated events. Every spike in state media articles (routine news cycle) triggers an AMBER alert. Every fishing forum post about naval vessels (common in coastal regions) gets flagged as military movement. The system cries wolf so often that the RED alert in the demo scenario has no impact — judges assume it's just more noise.

**Why it happens:**
Correlation logic uses naive thresholds without baseline calibration. "More than 3 outlets publishing about Taiwan" fires an alert, but 3 outlets publish about Taiwan every week. "More than 5 posts mentioning military" fires, but military posts are baseline in OSINT channels. No statistical anomaly detection — just raw counts against arbitrary thresholds.

**How to avoid:**
- Establish baseline activity rates during Phase 0 data collection: average articles/day per outlet, average military posts/day per channel
- Use statistical anomaly detection: alert when activity is 2+ standard deviations above rolling 7-day baseline
- Implement phrase novelty scoring in narrative detector: "restoration of necessary order" (novel) should score higher than "one China principle" (routine)
- Add temporal clustering requirement: coordination requires multiple outlets within 6-hour window, not just same day
- Test correlation logic against 7 days of real data before demo — tune thresholds to minimize false positives

**Warning signs:**
- Correlation engine uses hardcoded thresholds (e.g., `if article_count > 5`)
- No baseline comparison in logic (only absolute counts, no "compared to what?")
- Demo scenario testing shows multiple AMBER alerts before the intended one
- Narrative detector flags routine diplomatic language as coordination
- Movement detector flags normal port activity as anomalous

**Phase to address:**
Phase 1.1 (Narrative coordination detector) — implement phrase novelty scoring
Phase 1.4 (Correlation engine) — add baseline calibration and statistical thresholds
Phase 3.4 (End-to-end testing) — tune thresholds against real data

**Recovery cost if it happens:**
MEDIUM — Fixable with 2-3 hours of threshold tuning if discovered in Phase 3. If discovered during demo, can be explained away as "system tuned for high sensitivity," but undermines credibility.

---

### Pitfall 3: Real-time Supabase Subscription Race Conditions

**What goes wrong:**
During demo playback, the dashboard updates out of sequence. The threat gauge shows RED before any articles appear in the narrative feed. The intelligence brief displays before the correlation event that generated it. Movement posts appear on the map but with stale timestamps. Judges notice the timeline doesn't make sense.

**Why it happens:**
Demo playback engine inserts multiple related records (articles, posts, correlation event, alert, brief) into Supabase in rapid sequence. React frontend has separate realtime subscriptions for each table. Network latency varies per subscription. Record B (the brief) arrives at the frontend before record A (the correlation event that triggered it). No ordering guarantees across tables.

**How to avoid:**
- Demo playback engine should insert records in story-logical order with 200-500ms delays between related records
- Use Supabase RPC functions to insert related records atomically (e.g., correlation + alert + brief in single transaction)
- Add sequence numbers to all demo records: article.sequence, post.sequence, event.sequence
- Frontend sorts received records by sequence number before rendering
- Test demo playback at various speeds (1x, 5x, 10x) to expose race conditions

**Warning signs:**
- Demo playback inserts bulk records with `for` loop and no delays
- Frontend components each have independent `useEffect` hooks subscribing to different tables
- No sequence numbers or timestamps used for ordering
- Demo rehearsals show inconsistent order of events (different each run)
- Network tab shows realtime messages arriving out of order

**Phase to address:**
Phase 3.2 (Demo playback engine) — add sequencing and delays
Phase 2.1 (Dashboard Supabase connection) — implement sequence-based rendering
Phase 3.4 (End-to-end testing) — test at multiple playback speeds

**Recovery cost if it happens:**
MEDIUM — If discovered during Phase 4 rehearsal, 2-3 hours to add sequencing. If discovered during demo, no recovery — best to slow down manual playback.

---

### Pitfall 4: GDELT Data Quality Assumptions

**What goes wrong:**
The GDELT pipeline breaks or returns incomplete data. Article URLs are 404'd. Tone scores are missing. Timestamps are malformed. Chinese state media articles are misclassified or missing from results. The narrative detector receives garbage data and produces garbage output. Demo scenario relies on GDELT-sourced articles that don't exist.

**Why it happens:**
GDELT is free and comprehensive, but data quality is inconsistent. URLs break after 24-48 hours as articles move or sites restructure. Not all Chinese outlets are reliably indexed. Tone scoring fails on non-English text. The GDELT DOC API is eventually consistent — same query 5 minutes later returns different results. Teams assume GDELT is "production-quality" because it's popular in academia.

**How to avoid:**
- Pre-download 7 days of Chinese state media articles during Phase 0 and store in Supabase
- Demo dataset uses hand-crafted synthetic articles, NOT live GDELT data
- GDELT pipeline should have field validation: check for required fields (url, title, tone), discard incomplete records
- Add null checks everywhere GDELT data is accessed
- Live GDELT feed is separate "technical proof" tab, not part of core demo
- Demo works entirely with pre-loaded data in offline mode

**Warning signs:**
- Demo scenario references specific GDELT articles by expected content (articles may not exist)
- No validation on GDELT response fields before writing to Supabase
- Pipeline assumes every article has tone score, URL, and clean text
- No offline fallback — demo requires live GDELT API access
- Testing discovers inconsistent results from same query over time

**Phase to address:**
Phase 0.3 (GDELT ingestion pipeline) — add field validation and error handling
Phase 0.5 (Simulated demo dataset) — use synthetic articles, not GDELT-sourced
Phase 3.5 (Fallback/offline mode) — ensure demo works without GDELT API

**Recovery cost if it happens:**
HIGH — If demo relies on live GDELT and data is incomplete during presentation, no recovery path. If discovered during Phase 3 testing, 2-4 hours to create synthetic fallback dataset.

---

### Pitfall 5: Telegram FloodWait Rate Limiting

**What goes wrong:**
The Telegram scraper hits FloodWait errors during Phase 0 data collection. Telethon raises `FloodWaitError: A wait of 3600 seconds is required`. Pipeline stops for an hour. Team can't scrape enough channel history to build the demo dataset. Live Telegram feed during demo gets rate limited and displays "waiting 30 minutes..." message.

**Why it happens:**
Telegram API has aggressive rate limits: ~20-30 requests/second for new accounts, lower for recent sign-ups. Scraping 10 channels of 1000 messages each in a tight loop triggers FloodWait. No exponential backoff implemented. Team tries to "speed up" scraping by removing delays, making the problem worse.

**How to avoid:**
- Add exponential backoff wrapper around all Telethon calls: catch FloodWaitError, sleep for requested duration, retry
- Pre-scrape target channels during Phase 0 setup (first 6 hours) — don't wait until Phase 1
- Use `messages.search()` with `limit=100, offset` pagination instead of iterating all messages
- Add 2-3 second delays between channel switches
- For demo, use pre-scraped messages stored in Supabase — never scrape live during demo
- Have 2-3 Telegram API accounts (different phone numbers) as backup

**Warning signs:**
- No FloodWait exception handling in Telegram scraper code
- Scraper runs in tight loop with no delays
- Planning to scrape channels "right before the demo" for fresh data
- Using brand-new Telegram account created same day as development
- No pre-scraped message cache in Supabase

**Phase to address:**
Phase 0.4 (Telegram scraper) — implement FloodWait handling and delays
Phase 3.5 (Fallback/offline mode) — use pre-scraped messages for demo

**Recovery cost if it happens:**
HIGH — FloodWait requires waiting (no technical workaround). If hit during demo, can switch to pre-loaded data if it exists. If hit during Phase 0 without pre-loaded data, blocks progress for 30-60 minutes per occurrence.

---

### Pitfall 6: LLM Prompt Output Format Drift

**What goes wrong:**
The narrative coordination detector expects LLM to return JSON with `{score, phrases, outlets, geo_focus, themes}`. During demo, Claude returns a markdown table instead. The Python parser breaks. The correlation engine receives malformed data. Threat assessment fails to generate. Dashboard shows blank panels.

**Why it happens:**
LLM prompts don't enforce output format strictly. Prompt says "return as JSON" but doesn't show an example. During testing, Claude happens to return valid JSON. During demo (different input, different random seed, API load), Claude returns prose or markdown. JSON parsing raises `ValueError`. No fallback handling.

**How to avoid:**
- Use structured output format in prompts: provide exact JSON schema example with "respond ONLY with valid JSON, no markdown formatting"
- Add JSON validation after every LLM call: `try: json.loads(response)` with fallback to regex extraction
- Use Claude's structured output features if available (constrained decoding)
- Cache all demo LLM responses — known good outputs, no parsing risk
- Add unit tests for LLM response parsing with 5-10 real examples
- If parsing fails, return default safe values (e.g., score=0, phrases=[], outlets=[]) rather than crashing

**Warning signs:**
- Prompts don't include JSON schema examples
- No try/except around `json.loads()` in LLM response handling
- Testing only done with 2-3 example inputs (insufficient to see format variation)
- No unit tests for LLM response parsing
- No fallback behavior when parsing fails

**Phase to address:**
Phase 1.1, 1.2 (LLM analysis modules) — strict JSON output prompts with examples
Phase 1.6 (Pipeline integration test) — test with 10+ varied inputs, validate output formats
Phase 3.4 (End-to-end testing) — add error handling for malformed LLM outputs

**Recovery cost if it happens:**
LOW if caching is implemented (use cached responses). MEDIUM if parsing breaks during live testing (2-3 hours to add robust parsing + fallbacks). HIGH if it breaks during demo with no cache (no recovery).

---

### Pitfall 7: Lovable-Generated React Code Integration Bugs

**What goes wrong:**
Lovable generates React components that don't correctly integrate with Supabase realtime. The subscription code looks correct but never fires updates. Map component doesn't render markers. Chart component expects different data shape than Supabase provides. Frontend developer spends 6+ hours debugging generated TypeScript/React code they didn't write.

**Why it happens:**
Lovable generates high-quality UI but integration code quality varies. Supabase realtime subscription setup is complex (channels, filters, callbacks). Generated code may use outdated Supabase client patterns or incorrect table names. Lovable doesn't know the exact schema from Phase 0.6. Frontend dev can't quickly debug React/TypeScript if they're primarily a Python developer.

**How to avoid:**
- Define Supabase schema in Phase 0.6 BEFORE starting Lovable development — give Lovable exact table names and column types
- Start Lovable integration early (Phase 2.1, hour 16) — don't wait until hour 40 to discover integration bugs
- Ensure at least one team member can read React/TypeScript code
- Use Lovable's simplest components first — single table subscription, no complex joins
- Test each dashboard panel immediately after generation — don't build all panels then test
- Keep Supabase realtime subscriptions simple: one table per component, minimal filtering
- Have working Supabase + React example from official docs as reference

**Warning signs:**
- Team has no React/TypeScript experience
- Planning to build all Lovable components then test integration at the end
- Supabase schema undefined when starting Lovable development
- Complex multi-table joins required in realtime subscriptions
- Generated code uses deprecated Supabase client methods (check docs for v2 patterns)

**Phase to address:**
Phase 0.6 (Supabase schema) — finalize schema before Lovable work starts
Phase 2.1 (Dashboard Supabase connection) — test realtime subscriptions immediately
Phase 3.4 (End-to-end testing) — validate all dashboard panels update correctly

**Recovery cost if it happens:**
MEDIUM-HIGH — Debugging unfamiliar generated code is slow. 4-8 hours if discovered in Phase 3. If discovered in Phase 4, may require cutting dashboard features. Mitigation: have working Supabase + React example to copy patterns from.

---

### Pitfall 8: Demo Scenario Narrative Not Compelling

**What goes wrong:**
The demo technically works (GREEN → AMBER → RED) but judges don't care. The Taiwan Strait scenario feels generic or implausible. The intelligence brief reads like lorem ipsum. Judges see the correlation math working but don't understand why it matters. Team loses points for "interesting tech demo but unclear value."

**Why it happens:**
Team focuses on building the pipeline and neglects the story. Demo scenario is written last-minute as afterthought. The script shows technical capabilities ("system detected 3 coordinated outlets!") but doesn't explain operational value ("this gave analysts 48 hours to reposition assets before the exercise began"). Intelligence brief is auto-generated by LLM without editorial review and contains generic recommendations.

**How to avoid:**
- Write demo scenario script in Phase 3.1 BEFORE building playback engine — story drives implementation, not reverse
- Frame the demo around the analyst's problem: "How do I get warning before a surprise military exercise?"
- Use concrete, realistic details: "8 posts from Fujian fishing forums report restricted zones near Pingtan" not "movement indicators increased"
- Intelligence brief should read like actual intelligence: specific evidence, confidence qualifiers, collection gaps, actionable recommendations
- Rehearse the demo narrative separately from the technical flow — practice explaining value, not just features
- Show the timeline: "Hour 24: coordination detected. Hour 48: movement surge. Hour 72: official PLA announcement. System gave 48 hours advance warning."

**Warning signs:**
- Demo scenario script has technical details (API calls, table names) but no story
- Intelligence brief is generic LLM output without human editing
- Presentation focuses on "how we built it" not "what problem this solves"
- Demo rehearsals run through screens but team can't explain operational context
- No specific numbers in demo script (e.g., "multiple outlets" instead of "5 major outlets")

**Phase to address:**
Phase 3.1 (Demo scenario script) — write compelling narrative FIRST
Phase 1.5 (Intelligence brief generator) — ensure brief format is realistic, edit examples
Phase 4.3 (Demo rehearsal) — practice explaining value and operational context

**Recovery cost if it happens:**
MEDIUM — If discovered during Phase 4 rehearsals, 2-3 hours to rewrite script and brief. If discovered during actual demo, can adjust presentation framing, but weaker impact.

---

### Pitfall 9: Python Backend / React Frontend Schema Mismatch

**What goes wrong:**
Backend writes `article_count` to Supabase. Frontend expects `articleCount` (camelCase). Chart shows blank. Backend writes timestamps as Unix integers. Frontend expects ISO strings. Map expects `{ lat, lon }` objects. Backend writes `latitude, longitude` columns. Every dashboard panel shows "No data available."

**Why it happens:**
Backend and frontend teams work in parallel from hour 1 (correct strategy) but don't establish data contract first. Schema defined quickly in Phase 0.6 without review. Backend developer uses snake_case (Python convention). Frontend developer assumes camelCase (JavaScript convention). No integration testing until Phase 3.4 (hour 28+). By then, both sides have hardcoded assumptions.

**How to avoid:**
- Define Supabase schema as formal contract in Phase 0.6 — BOTH teams review and sign off
- Document exact column names, types, and examples in `.planning/SUPABASE_SCHEMA.md`
- Use snake_case for Supabase columns (Postgres convention) — frontend adapts with Supabase client camelCase conversion
- Add sample data insertion + retrieval test in Phase 0.6: backend writes, frontend reads, verify match
- Schedule integration checkpoint at hour 20 (after Phase 2.1) — test minimal dashboard + backend integration
- Use TypeScript interfaces on frontend side generated from Supabase schema (Supabase can auto-generate types)

**Warning signs:**
- No written schema documentation — "we'll figure it out"
- Backend and frontend developers haven't discussed data format
- First integration test planned for hour 28+ (after both sides mostly complete)
- Backend writes timestamps without timezone, frontend expects timezone-aware
- No sample data in Supabase for frontend to develop against

**Phase to address:**
Phase 0.6 (Supabase schema) — define schema as contract, both teams review
Phase 2.1 (Dashboard Supabase connection) — test basic integration early
Phase 3.4 (End-to-end testing) — validate all data flows match schema

**Recovery cost if it happens:**
MEDIUM-HIGH — Discovered late (Phase 3-4), requires backend or frontend rewrites. 3-6 hours to fix column names, types, and all references. Avoid by testing integration early.

---

### Pitfall 10: Map Geolocation Data Quality

**What goes wrong:**
The movement stream panel shows posts classified as military-relevant, but 40% have no location data. The map shows 5 markers but the feed lists 50 posts. LLM extraction returns "Fujian province" (500km ambiguity) or "near the coast" (useless for map). Heatmap is empty. Judges ask "where are the movement indicators?" and see nearly blank map.

**Why it happens:**
Civilian social media posts rarely include precise GPS coordinates. LLM prompt asks for location extraction but doesn't enforce format. Extraction returns "Xiamen" (city name, no lat/lon), "south of Fuzhou" (relative location), or nothing. Post classification prompt focuses on detecting military relevance, treats geolocation as secondary. No geocoding service to convert place names to coordinates.

**How to avoid:**
- LLM post classifier prompt should return structured location: `{raw_text: "near Xiamen port", place_name: "Xiamen", lat: 24.48, lon: 118.08, confidence: "medium"}`
- Use geocoding service (Nominatim free tier, or Mapbox Geocoding API) to convert place names to coordinates during Phase 1.2
- Demo dataset includes explicit lat/lon in synthetic posts (fake but precise)
- Add location confidence scores: only show "high confidence" locations on map, list others in feed without markers
- If real-world location data is sparse, don't pretend — show this as information gap in intelligence brief
- Consider using region-level heatmap (province/city aggregation) rather than precise markers if data is ambiguous

**Warning signs:**
- LLM extraction prompt returns free-text location descriptions
- No geocoding step in post processing pipeline
- Map component expects precise lat/lon but data contains place names
- Demo testing shows empty or nearly-empty map despite posts in feed
- No location confidence filtering (showing "somewhere in China" on map)

**Phase to address:**
Phase 1.2 (Civilian post classifier) — structured location extraction + geocoding
Phase 0.5 (Simulated demo dataset) — include precise lat/lon in synthetic posts
Phase 2.2 (Interactive map panel) — add location confidence filtering

**Recovery cost if it happens:**
MEDIUM — If discovered during Phase 3 testing, 2-4 hours to add geocoding or adjust demo data. If discovered during demo, can explain as "limited geolocation data" but weakens visual impact.

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Hardcoded thresholds (e.g., `if article_count > 3`) | Fast to implement, no calibration needed | High false positive rate, brittle to data changes | Never — use baseline-relative thresholds (2σ above mean) |
| No error handling around API calls | Clean code, faster to write | Demo crashes on transient errors (rate limit, timeout, 500) | Never — wrap ALL external API calls in try/except with fallback |
| Single LLM for all tasks (Claude for everything) | Simpler code, one API key | 10x higher cost ($15/M tokens for bulk classification) | MVP only — migrate to GPT-4o Mini for classification in Phase 1.2 |
| Loading all data client-side from Supabase | No backend API needed, direct DB access | Slow dashboard loads (1000+ rows), no pagination | Acceptable for hackathon with <500 demo records |
| Mock data in frontend without backend | Frontend dev unblocked, parallel work | Integration bugs discovered late | Acceptable IF schema is formal contract (Phase 0.6) |
| No database indexes | Faster initial setup, no schema design | Slow queries when demo dataset grows past 100 rows | Acceptable if demo uses <200 records total |
| Storing LLM responses as text blobs | Easy to implement, no schema design | Can't query or filter by extracted fields (e.g., find all posts mentioning "Type 055 destroyer") | Acceptable for hackathon — no complex queries needed |
| No authentication on Supabase | Faster setup, no auth code | Anyone with public URL can modify demo data | Acceptable for localhost demo, NOT if deployed |
| Inline SQL queries in Python (no ORM) | Fast to write, no ORM learning curve | Brittle to schema changes, SQL injection risk if dynamic queries | Acceptable for hackathon IF queries are static, no user input |
| No unit tests | More time for features | Regression bugs when changing prompts or correlation logic | Acceptable for 48-hour build — focus on integration testing instead |

---

## Integration Gotchas

Common mistakes when connecting to external services.

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Claude/GPT API | No timeout specified → hangs forever if API is slow | Set 30-second timeout: `client.messages.create(..., timeout=30)` |
| GDELT DOC API | Assuming results are complete immediately | GDELT is eventually consistent — wait 5 min, query again for complete results |
| Telegram Telethon | Using `client.get_messages(limit=1000)` in single call | Paginate with `async for message in client.iter_messages(limit=1000)` |
| Supabase realtime | Not unsubscribing from channels on component unmount | Memory leak — use `useEffect` cleanup or `subscription.unsubscribe()` |
| AISstream WebSocket | Not handling reconnection on disconnect | WebSocket drops after 10 min idle — implement reconnect logic with exponential backoff |
| LLM JSON parsing | Using `json.loads()` without validation | Validate schema: `assert 'score' in data and 0 <= data['score'] <= 100` |
| Mapbox/Leaflet | Loading all 1000+ markers at once | Use marker clustering (Leaflet.markercluster) for >50 markers |
| Pandas/NumPy | Loading full dataset into memory for correlation | Stream data in chunks if >10K rows: `pd.read_sql(..., chunksize=1000)` |
| Supabase queries | Fetching all rows with `select('*')` | Add limit + pagination: `select('*').limit(100).range(0, 99)` |
| Geocoding APIs | Sending raw user text to geocoding → fails on ambiguous input | Clean text first: extract place names, add country context ("Xiamen, China") |

---

## Performance Traps

Patterns that work at small scale but fail as usage grows.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| N+1 LLM API calls (classify posts one-by-one) | Slow pipeline, high cost, rate limits | Batch processing: classify 50 posts per prompt | >100 posts (10x slower, 10x cost) |
| Loading all articles into React state | Slow dashboard render, browser lag | Pagination or virtualized lists (react-window) | >500 articles (5+ second render) |
| No database indexes on timestamp columns | Slow time-range queries for correlation | Add indexes on `created_at`, `timestamp` columns | >1000 rows (queries >2 seconds) |
| Realtime subscription to all tables without filters | High bandwidth, slow updates, memory leak | Filter subscriptions: `supabase.channel().on('postgres_changes', {table: 'articles', filter: 'score=gt.70'})` | >100 realtime events/sec |
| Storing full article HTML in Supabase | Database bloat, slow inserts | Store URL + metadata only, fetch full text on demand | >5000 articles (>500MB DB) |
| Rendering all map markers without clustering | Map unresponsive, browser crash | Marker clustering (groups nearby markers) | >200 markers |
| LLM prompt with 50K token context | Slow response (30+ sec), high cost | Chunk text, summarize first, or use focused prompts | >20K tokens input (>10 sec response) |
| No caching of geocoding results | Repeated API calls for same locations, rate limits | Cache place_name → lat/lon mapping in Supabase | >500 geocoding requests (hit rate limit) |

---

## Security Mistakes

Domain-specific security issues beyond general web security.

| Mistake | Risk | Prevention |
|---------|------|------------|
| Committing API keys to Git repo | Keys exposed publicly, API abuse, account takeover | Use `.env` file (excluded in `.gitignore`) + environment variables |
| Supabase anon key with RLS disabled | Anyone can read/write/delete all data | Enable Row-Level Security (RLS) OR keep localhost-only for hackathon |
| Storing Telegram api_id/api_hash in code | Account compromise, can't revoke without new phone number | `.env` file only, never commit |
| No rate limiting on FastAPI endpoints | API abuse, excessive LLM costs | Add rate limiting middleware (slowapi) if exposing endpoints |
| LLM prompt injection via user input | Attacker manipulates system prompts via malicious posts | Sanitize extracted text, don't concatenate user input directly into prompts |
| Exposing internal correlation logic in brief | Adversary learns detection signatures and evades | Generic brief language ("convergence of indicators") not specific thresholds |
| Using Supabase public URL with admin key | Full database access if key leaks | Use anon key + RLS for frontend, admin key only in backend scripts |
| No input validation on date ranges | SQL injection via malformed timestamps | Validate date format before query: `datetime.fromisoformat(date_str)` |

---

## UX Pitfalls

Common user experience mistakes in this domain.

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Showing raw JSON from LLM in intelligence brief | Unprofessional, hard to read, looks like a bug | Format as structured document with sections and bullet points |
| No loading indicators when data is processing | Dashboard looks broken ("where's my data?") | Spinner + "Analyzing articles..." message during LLM processing |
| Threat gauge jumps GREEN → RED instantly | Confusing, looks glitchy, no sense of escalation | Animated transition over 2-3 seconds, show intermediate AMBER |
| Displaying Unix timestamps (1738886400) | Meaningless to humans | Format as "2026-02-07 14:30 UTC" |
| Map zoomed to world view showing single marker | User must manually zoom to see data | Auto-fit map bounds to marker bounding box |
| Showing all 1000 posts in scrollable feed | Overwhelming, slow to render, hard to find signal | Show top 20 by confidence score, "Load more" button |
| No explanation of confidence scores | User doesn't know if 74 is good or bad | Color-coded + labels: 0-30 (LOW, green), 30-70 (MEDIUM, amber), 70-100 (HIGH, red) |
| Intelligence brief uses jargon without context | Non-expert judges don't understand value | Define terms on first use: "narrative coordination (multiple state media outlets using identical phrasing)" |
| Error messages show technical details | "JSONDecodeError line 42" is not helpful | User-friendly: "Unable to analyze articles. Using cached data." |
| No visual distinction between demo and live data | Judges don't know what's real vs simulated | Clear tab labels: "Demo Scenario" vs "Live Data (Technical Proof)" |

---

## "Looks Done But Isn't" Checklist

Things that appear complete but are missing critical pieces.

- [ ] **LLM analysis modules:** Often missing error handling when API returns non-JSON or times out — verify try/except + fallback responses exist
- [ ] **Demo playback engine:** Often missing sequence control (all data inserted at once) — verify time-sliced insertion with delays
- [ ] **Map component:** Often missing empty-state handling (no data message) — verify displays "No movement indicators yet" when empty
- [ ] **Intelligence brief:** Often missing realistic content (generic LLM output) — verify hand-edited example reads like real intelligence product
- [ ] **Correlation engine:** Often missing baseline calibration (hardcoded thresholds) — verify uses statistical thresholds (mean + 2σ)
- [ ] **Offline mode:** Often "implemented" but never tested — verify demo runs fully without internet connection
- [ ] **Supabase realtime:** Often subscribed but no updates visible — verify insert test record → appears in dashboard within 2 seconds
- [ ] **GDELT pipeline:** Often missing data validation (assumes all fields present) — verify null checks on tone, URL, title before writing
- [ ] **Telegram scraper:** Often missing FloodWait handling — verify catches `FloodWaitError` and sleeps
- [ ] **Dashboard responsive design:** Often works on dev laptop, breaks on projector resolution — verify test at 1920x1080 and 1280x720
- [ ] **Demo rehearsal timing:** Often "works" but takes 12 minutes — verify full demo runs in under 7 minutes
- [ ] **API cost tracking:** Often estimated but never measured — verify actual cost log from API dashboards <$25 total

---

## Recovery Strategies

When pitfalls occur despite prevention, how to recover.

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| LLM API fails during demo | LOW | Use cached responses (if implemented in Phase 3.5). Explain "pre-computed for reliability." |
| Correlation false positives flood dashboard | MEDIUM | Increase threshold live: edit `correlation_engine.py`, change `threshold=70` to `threshold=85`, restart script. 5 min fix. |
| Supabase realtime race conditions | LOW | Slow down demo playback to 0.5x speed. Manual control. |
| GDELT returns incomplete data | LOW | Use pre-loaded demo data (if fallback implemented). Switch to offline mode. |
| Telegram FloodWait during demo | HIGH | No recovery — don't scrape live during demo. Use pre-loaded data. |
| LLM output format parsing fails | MEDIUM | Modify prompt to be more explicit, re-cache responses. 30 min if discovered before demo. |
| Lovable React integration bugs | HIGH | Revert to working version from git. Cut broken feature if necessary. 1-2 hours. |
| Demo scenario not compelling | MEDIUM | Adjust presentation framing — focus on operational value. Add verbal context judges aren't getting from screens. 30 min preparation. |
| Backend/frontend schema mismatch | HIGH | Agree on column names, pick one side to change (usually frontend adapts). 2-4 hours + retest. |
| Map has no location data | MEDIUM | Show alternative view: table of posts without map, or province-level aggregation instead of precise markers. 1 hour. |

---

## Pitfall-to-Phase Mapping

How roadmap phases should address these pitfalls.

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| LLM API dependency | Phase 3.5 (Offline mode) | Demo runs fully with pre-cached responses, no live API calls |
| Correlation false positives | Phase 1.4 (Correlation engine) | Test against 7 days real data, tune to <5% false positive rate |
| Supabase race conditions | Phase 3.2 (Demo playback) | Demo runs 5x in a row with consistent event order |
| GDELT data quality | Phase 0.3 (GDELT pipeline) + Phase 3.5 | Validate all fields, demo works offline without GDELT API |
| Telegram FloodWait | Phase 0.4 (Telegram scraper) | Pre-scrape all channels in Phase 0, demo uses cached messages |
| LLM output format drift | Phase 1.1–1.2 (LLM modules) | Unit tests validate JSON parsing on 10+ examples |
| Lovable integration bugs | Phase 2.1 (Dashboard connection) | Test basic realtime subscription works by hour 18 |
| Demo scenario not compelling | Phase 3.1 (Scenario script) | Script reviewed by all team members before playback engine built |
| Backend/frontend schema mismatch | Phase 0.6 (Supabase schema) | Both teams review and sign off on schema doc before parallel work |
| Map geolocation quality | Phase 1.2 (Post classifier) + Phase 0.5 | Demo posts have explicit lat/lon, geocoding service tested |

---

## Sources

**OSINT Pipeline Patterns:**
- Known issues with GDELT data quality (eventual consistency, broken URLs, missing fields)
- Telegram rate limiting documentation (FloodWait, request limits)
- AISstream WebSocket connection patterns

**LLM Integration Patterns:**
- Anthropic Claude API documentation (timeouts, rate limits, structured output)
- OpenAI GPT-4o Mini rate limits and cost optimization
- Common prompt engineering mistakes (output format drift, no examples)

**Real-time Systems:**
- Supabase realtime subscription race conditions (multiple tables, ordering issues)
- WebSocket reconnection patterns for long-lived connections

**Hackathon Constraints:**
- Common mistakes in 48-hour builds (no caching, late integration, demo story neglected)
- API cost blow-ups from naive LLM usage (per-request instead of batching)

**Data Correlation:**
- False positive patterns in anomaly detection (hardcoded thresholds vs statistical baselines)
- Signal processing patterns (baseline calibration, novelty scoring)

**Geospatial Data:**
- Geocoding API integration (place name disambiguation, rate limits)
- Map rendering performance (marker clustering for >50 points)

---
*Pitfalls research for: Dragon Watch (OSINT narrative-to-movement correlation)*
*Researched: 2026-02-07*
