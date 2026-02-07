

**DRAGON WATCH**

Pre-Conflict Narrative & Movement Detection

48-Hour Prototype Development Report

**Team Panop**

UNCLASSIFIED // FOR EXERCISE USE ONLY

February 2026

| Project Name | Dragon Watch |
| :---- | :---- |
| **Team** | Panop |
| **Build Window** | 48 hours |
| **Concept** | Narrative-to-physical-domain correlation for pre-conflict I\&W |
| **Demo Scenario** | Taiwan Strait — PLA exercise preparation detected via coordinated state media \+ civilian movement posts |
| **Data Approach** | Simulated/seeded data for demo, live Telegram \+ GDELT for technical proof |
| **Classification** | UNCLASSIFIED // FOR EXERCISE USE ONLY |

# **1\. Project Overview**

Dragon Watch is a 48-hour hackathon prototype that demonstrates a capability no existing OSINT vendor provides: the automated correlation of state media narrative coordination with civilian social media movement indicators to generate pre-conflict warnings. The system runs two independent detection streams in parallel and alerts when they converge, providing intelligence analysts with hours of advance warning before a military operation commences.

# **2\. The Core Concept**

The system operates on a simple but powerful principle: when a state decides to conduct a military operation, two things happen in sequence. First, the propaganda apparatus coordinates — multiple state media outlets begin using the same unusual phrases simultaneously, indicating a centralised directive. Second, civilians in the operational area begin inadvertently posting about unusual military activity. Either signal alone is noisy and ambiguous. The correlation of both signals is diagnostic.

## **Detection Architecture**

**Stream 1 — Narrative Coordination Detection:** Continuously monitor Chinese state media outlets (Xinhua, Global Times, CCTV, People’s Daily) via GDELT. Use LLM analysis to detect when multiple outlets simultaneously adopt identical unusual phrasing, doctrinal language shifts, or coordinated theme escalation. The signal is synchronisation across outlets, not the content of any single article. Score each detected coordination event by outlet count, phrase novelty, temporal clustering, and topic severity.

**Stream 2 — Civilian Movement Anomaly Detection:** Continuously monitor public Telegram channels and simulated social media feeds for civilian posts that inadvertently reveal military activity: truck convoys, naval vessel sightings, unusual flight activity, restricted zone announcements, military personnel in transit. Use LLM classification to identify military-relevant posts, extract geolocation data, and cluster by region and time window. The signal is a spike in military-relevant civilian posts in a specific region compared to baseline activity.

**Correlation Engine:** Cross-reference Stream 1 and Stream 2 outputs. If a narrative coordination spike occurred within the previous 72 hours targeting a geographic region where civilian movement anomalies are now clustering, the system escalates to a threat warning. Confidence scoring considers: number of coordinating outlets, intensity of phrase novelty, volume of civilian movement reports, geographic proximity between narrative focus and movement cluster, and temporal sequence (narrative should precede movement by 24–72 hours).

**Alert Output:** Generate a structured intelligence brief with threat level (GREEN/AMBER/RED), confidence score, supporting evidence from both streams, a timeline of indicator convergence, and recommended collection priorities. Designed for human-in-the-loop validation — the system recommends, the analyst decides.

# **3\. Technology Stack**

The stack is optimised for a 48-hour build with a 4-person team working in parallel. The architecture separates backend data processing (Python) from the frontend dashboard (React via Lovable), connected through Supabase’s real-time Postgres database. This decoupling means backend developers and the frontend developer can work independently from hour one.

## **Architecture Overview**

Python backend scripts (GDELT fetcher, Telegram scraper, LLM analyser, correlation engine) process data and write results to Supabase Postgres tables. The Lovable-generated React frontend subscribes to those tables via Supabase real-time, so the dashboard updates automatically as new data flows in. No polling, no WebSocket boilerplate — Supabase handles the real-time layer.

| Layer | Technology | Rationale |
| :---- | :---- | :---- |
| Frontend / Dashboard | Lovable (React) \+ Mapbox/Leaflet \+ Recharts | AI-generated React app with professional UI. Dramatically better visual quality than Streamlit. Lovable generates the split-screen layout, map components, charts, and intelligence brief panel in a fraction of hand-coded React time. |
| Backend Pipeline | Python \+ FastAPI | Data ingestion, LLM analysis, and correlation logic. FastAPI endpoints for any direct API calls. Writes results to Supabase. |
| Database | Supabase (Postgres \+ Realtime) | Managed Postgres with built-in real-time subscriptions. Frontend auto-updates when backend writes new rows. Auth, storage, and edge functions available if needed. Free tier sufficient for hackathon. |
| Data Processing | Pandas \+ NumPy | In-memory time-series analysis, correlation calculations, anomaly detection baselines. |
| LLM Analysis | Claude Sonnet 4.5 API | Propaganda pattern detection, entity extraction, cross-language analysis, intelligence summary generation. \~$3/$15 per M tokens I/O. |
| Bulk Classification | GPT-4o Mini / Gemini 2.5 Flash | High-volume post classification at $0.15–$0.60 per M tokens. Cost-effective for Stream 2 civilian post processing. |
| Mapping | Mapbox GL JS or Leaflet (via Lovable) | Interactive map with heatmap layers, marker clustering, and bounding box filtering for movement data. Integrated directly into the React frontend. |
| Charting | Recharts (via Lovable) | Dual-axis time-series charts for narrative volume vs. movement indicator correlation visualisation. Native React component. |
| Version Control | Git / GitHub | Standard collaborative development workflow. |

## **Why Lovable Instead of Streamlit**

Streamlit is the standard hackathon recommendation because it’s the fastest Python-to-UI path. However, for this project Lovable is the better choice for three reasons. First, the architecture becomes cleaner: Python scripts write to Supabase, the React frontend reads from Supabase via real-time subscriptions, and each layer is fully decoupled. Second, the demo looks dramatically better — judges see many Streamlit dashboards, but a polished React UI with proper maps, animated threat gauges, and a professional intelligence-product aesthetic stands out. Third, the 4-person team can parallelise more effectively: the frontend developer works entirely in Lovable while backend developers work in Python, with Supabase as the contract between them.

The tradeoff is that if Lovable generates buggy React code, someone on the team needs to be able to read React/TypeScript to debug it. For a dashboard that’s primarily displaying data from Supabase, this risk is low.

# **4\. Data Sources**

| Source | Purpose | Setup | Cost | Notes |
| :---- | :---- | :---- | :---- | :---- |
| GDELT DOC 2.0 | State media narrative tracking (Xinhua, Global Times, CCTV, People’s Daily) | 5 min | Free | No API key needed. Domain filtering, tone scoring, 15-min updates. Python gdeltdoc package. |
| Telethon (Telegram) | OSINT channel monitoring, civilian post scraping | 30 min | Free | Register at my.telegram.org for api\_id/api\_hash. Full access to public channels. \~20–30 req/sec. |
| AISstream.io | Real-time vessel position tracking (WebSocket) | 30 min | Free | JSON via WebSocket. Filter by bounding box (SCS: 0–25°N, 100–125°E). MMSI, position, speed, heading. |
| Global Fishing Watch | Maritime domain awareness, dark fleet detection | 30 min | Free | Fishing activity, AIS-disabling detection, loitering events. Python SDK available. |
| ACLED | Conflict event data (ground truth / validation) | 30 min | Free | Free API after registration. Weekly updates since 1997\. Good for historical validation. |
| Simulated Dataset | Demo scenario data (Taiwan Strait exercise) | 2–4 hrs | Free | Team-generated synthetic Weibo-style posts, coordinated media articles, vessel movements for scripted demo. |

Sources deliberately excluded: X/Twitter API ($200+/month), TikTok Research API (academic-only, weeks to approve), Weibo API (requires Chinese SIM), MarineTraffic API (no free tier). These are out of scope for the 48-hour build window.

# **5\. Open-Source Repos and Building Blocks**

The narrative-to-movement correlation engine is the novel piece — no existing open-source project builds this. However, each individual data pipeline component has solid open-source implementations that save an estimated 6–8 hours of pipeline work. The following repos should be cloned and adapted rather than built from scratch.

## **GDELT Ingestion**

| Repository | URL | Use For |
| :---- | :---- | :---- |
| gdeltPyR | github.com/linwoodc3/gdeltPyR | Python framework for pulling GDELT v1 and v2 data into Pandas DataFrames. Fastest path to getting state media articles flowing. Use to query domain:xinhuanet.com, domain:globaltimes.cn etc. |
| gdelt-doc-api (gdeltdoc) | github.com/alex9smith/gdelt-doc-api | Python wrapper specifically for the GDELT DOC 2.0 API. Article-level queries with tone scoring. This is the primary library for Stream 1\. |
| GDELT sentiment analysis | github.com/t4f1d/sentiment-analysis | Indonesia-focused but the GDELT → BigQuery → sentiment pipeline pattern is the exact architecture needed. Good reference for the data flow. |
| GDELT news dashboard | github.com/albertovpd/analysing\_world\_news\_with\_Gdelt | Full ETL pipeline from GDELT to dashboard with sentiment analysis. Shows how to build the automated news monitoring loop. |

## **AIS Vessel Tracking**

| Repository | URL | Use For |
| :---- | :---- | :---- |
| aisstream (official) | github.com/aisstream/aisstream | Official AISstream.io repo with WebSocket connection examples. Free API, real-time global vessel positions. Start here for Stream 2 maritime data. |
| vessel\_research | github.com/followthemoney/vessel\_research | Bellingcat-sourced maritime OSINT investigation code with Global Fishing Watch API integration. Events: fishing, loitering, encounters, AIS gaps. |
| MultitaskAIS | github.com/dnguyengithub/MultitaskAIS | Academic ML model for anomalous vessel behaviour detection from AIS streams. Overkill for hackathon but excellent reference for what “anomaly” means in maritime context. |

## **Telegram Scraping**

| Repository | URL | Use For |
| :---- | :---- | :---- |
| Telethon | github.com/LonamiWebs/Telethon | The standard Python library for Telegram API. Working scraper in under an hour. Full access to public channel history, media, forwarding info, reactions. |
| awesome-osint | github.com/jivoi/awesome-osint | Massive curated OSINT tool list including Telegram-specific tools (TGCollector, Telerecon, GroupDa, Maltego Telegram transforms). |

## **OSINT Frameworks & Reference**

| Repository | URL | Use For |
| :---- | :---- | :---- |
| OSINT-Framework | github.com/lockfale/OSINT-Framework | Reference architecture for organising OSINT data sources. Useful for understanding the data source taxonomy. |
| Flight-And-Marine-OSINT | github.com/The-Osint-Toolbox/Flight-And-Marine-OSINT | Curated collection of flight and marine tracking tools and resources. Quick reference for additional data sources. |
| awesome-intelligence | github.com/ARPSyndicate/awesome-intelligence | Comprehensive OSINT resource list including vessel tracking, flight tracking, news, and social media tools. |

## **Recommended Clone Strategy**

During Phase 0 (Hours 0–6), clone gdeltdoc and aisstream repos first. These two provide the core data pipelines for Stream 1 and Stream 2\. The gdeltdoc library wraps the GDELT DOC 2.0 API cleanly and returns Pandas DataFrames ready for analysis. The aisstream repo has working WebSocket connection code that can be adapted to filter for the South China Sea bounding box in minutes. Telethon is pip-installable and needs no repo clone — just pip install telethon and register at my.telegram.org for credentials. Use the vessel\_research repo as reference for Global Fishing Watch API integration if time permits.

# **6\. Phase Rollout Plan — 48-Hour Build**

The build is structured into five phases. Each phase has a clear deliverable that the next phase depends on. If the team falls behind, Phase 4 (Polish) is the buffer — cut polish, not core functionality.

## **PHASE 0: Environment & Data Pipeline Setup \[Hours 0–6\]**

**Goal:** Every team member has a working dev environment, all API accounts are created, data is flowing from GDELT and Telegram into Supabase, the Lovable project is initialised with the dashboard skeleton, and the simulated demo dataset is ready.

| \# | Task | Detail | Deliverable | Hrs |
| :---- | :---- | :---- | :---- | :---- |
| 0.1 | Dev environment setup | Python 3.11+, venv, install core deps (fastapi, pandas, anthropic, telethon, gdeltdoc, httpx, supabase-py). Git repo init. Shared .env for API keys. Lovable project created and connected to Supabase. | All team members can run Python pipeline scripts and Lovable project loads in browser. | 1 |
| 0.2 | API account creation | Create accounts: Supabase (new project with Postgres), AISstream.io, Telegram (my.telegram.org), Anthropic API, ACLED. GDELT needs no account. Store all keys in shared .env. Configure Supabase tables and enable realtime. | All API keys verified working. Supabase project live with realtime enabled. | 1.5 |
| 0.3 | GDELT ingestion pipeline | Build Python module using gdeltdoc library that queries GDELT DOC 2.0 API filtered to Chinese state media domains (xinhuanet.com, globaltimes.cn, chinadaily.com.cn, ecns.cn). Fetch articles, tone scores, themes, timestamps. Write to Supabase articles table. | Running script that fetches last 7 days of Chinese state media articles and stores in Supabase. | 2 |
| 0.4 | Telegram scraper | Build Telethon-based scraper targeting 5–10 public OSINT/military channels. Extract message text, timestamps, forwarding info, media presence, reactions. Write to Supabase social\_posts table. | Running script that pulls recent messages from target channels and stores in Supabase. | 2 |
| 0.5 | Simulated demo dataset | Create synthetic dataset for Taiwan Strait scenario: (a) 50+ fake state media articles showing coordinated phrase adoption over 72hrs, (b) 100+ fake civilian social media posts showing military movement sightings in Fujian/Taiwan Strait area, (c) simulated AIS vessel position data showing PLA Navy activity increase. Load into Supabase demo tables. | Complete demo dataset in Supabase that tells the Taiwan Strait escalation story across both streams. | 3 |
| 0.6 | Supabase schema design | Supabase Postgres tables: articles (source, url, title, tone, themes, timestamp), social\_posts (source, text, lat, lon, timestamp, classification), vessel\_positions (mmsi, lat, lon, speed, heading, timestamp), alerts (level, confidence, evidence, timestamp), correlation\_events (narrative\_id, movement\_cluster\_id, score, timestamp). Enable realtime on all tables. | Schema created, demo data loadable, realtime subscriptions working. | 0.5 |

**Phase 0 Gate:** Team can run a script that queries GDELT, pulls Telegram messages, and loads demo data into Supabase. Lovable project connects to Supabase and displays placeholder data. All data visible in both Supabase dashboard and frontend.

## **PHASE 1: LLM Analysis Engine \[Hours 6–16\]**

**Goal:** The AI brain of the system is working. LLM prompts can classify state media articles for coordination signals, classify civilian posts for military relevance, and generate intelligence summaries. The correlation logic connects both streams and writes results to Supabase.

| \# | Task | Detail | Deliverable | Hrs |
| :---- | :---- | :---- | :---- | :---- |
| 1.1 | Narrative coordination detector | Build prompt pipeline that takes a batch of state media articles (same time window) and asks Claude to: (a) identify repeated phrases/framing across multiple outlets, (b) score coordination likelihood (0–100), (c) extract key themes and geographic focus, (d) flag doctrinal language shifts. Use DISARM framework TTPs as few-shot reference. | Python function: detect\_narrative\_coordination(articles) → {score, phrases, outlets, geo\_focus, themes}. Results written to Supabase. | 3 |
| 1.2 | Civilian post classifier | Build prompt pipeline (GPT-4o Mini for cost efficiency) that classifies individual social media posts as: military-relevant (vehicle sighting, personnel movement, restricted zone, naval activity) or not. Extract: location mentions, equipment types, estimated timestamp, confidence. Batch process. | Python function: classify\_posts(posts) → \[{is\_military, category, location, equipment, confidence}\]. Results written to Supabase. | 3 |
| 1.3 | Entity extraction module | Build prompt that extracts structured entities from both article and post text: military unit designations, equipment types (PLA nomenclature), geographic locations (with lat/lon where possible), temporal references, named individuals. | Python function: extract\_entities(text) → {units, equipment, locations, timestamps, people} | 2 |
| 1.4 | Correlation engine | Build rule-based correlation logic: (a) time-window matching (narrative spike within 72hrs of movement cluster), (b) geographic proximity scoring, (c) severity weighting (more outlets \+ more movement posts \= higher confidence), (d) output threat level: GREEN (\<30), AMBER (30–70), RED (\>70). Write to Supabase alerts table. | Python function: correlate(narrative\_events, movement\_events) → {threat\_level, confidence, evidence\_chain, timeline}. Alert appears in Supabase in realtime. | 2 |
| 1.5 | Intelligence brief generator | Build prompt that takes correlation output and generates a formatted intelligence brief: situation summary, indicator timeline, confidence assessment, information gaps, recommended collection priorities. UNCLASSIFIED//FOR EXERCISE USE ONLY header. | Python function: generate\_brief(correlation) → formatted\_brief\_text. Written to Supabase briefs table. | 1.5 |
| 1.6 | Pipeline integration test | Wire 1.1–1.5 together: feed demo dataset through full pipeline. Articles → narrative detection → correlation with classified posts → threat assessment → intelligence brief. Verify end-to-end output in Supabase. | Full pipeline runs against demo data and produces coherent threat assessment visible in Supabase. | 1 |

**Phase 1 Gate:** Run demo dataset through pipeline. System correctly detects narrative coordination, classifies military-relevant posts, correlates them, and outputs a RED threat assessment with a coherent intelligence brief. All results visible in Supabase tables and updating in realtime.

## **PHASE 2: Dashboard & Visualisation \[Hours 16–28\]**

**Goal:** A working Lovable-generated React dashboard that visually tells the story. Split-screen showing narrative stream and movement stream converging. Map with movement indicators. Threat level gauge. Timeline chart. Intelligence brief panel. All powered by Supabase realtime subscriptions.

| \# | Task | Detail | Deliverable | Hrs |
| :---- | :---- | :---- | :---- | :---- |
| 2.1 | Dashboard layout and navigation | Build React app skeleton in Lovable: sidebar for controls (date range, scenario selector, threat level filter), main area split into panels. Tab-based navigation: Overview, Narrative Stream, Movement Stream, Correlation, Intelligence Brief. Connect to Supabase with realtime subscriptions on all relevant tables. | React app runs with navigable tabs and live Supabase connection showing placeholder content. | 2 |
| 2.2 | Interactive map panel | Build map component (Mapbox GL JS or Leaflet) centred on Taiwan Strait. Layers: (a) civilian movement post locations as clustered markers (colour-coded by confidence), (b) vessel positions as ship icons, (c) heatmap overlay showing post density, (d) narrative geographic focus as shaded regions. | Map displays demo data from Supabase with all four layers toggleable. | 3 |
| 2.3 | Dual-axis correlation chart | Build Recharts component with: left Y-axis \= narrative coordination score over time, right Y-axis \= civilian movement post count over time, X-axis \= timeline. Shaded regions where correlation exceeds threshold. Clickable data points. | Chart shows clear visual correlation between narrative spike and movement spike. | 2 |
| 2.4 | Narrative stream panel | Real-time feed of state media articles from Supabase: source outlet, headline, tone score, detected coordinated phrases highlighted, coordination score badge. Sortable by time and score. Summary statistics at top. | Scrollable feed of articles with highlighted coordination signals, auto-updating via Supabase realtime. | 2 |
| 2.5 | Movement stream panel | Real-time feed of classified civilian posts from Supabase: text, inferred location, military category tag, confidence score, source platform. Map mini-view showing post locations. Summary statistics. | Scrollable feed of classified posts with location data and category tags, auto-updating. | 2 |
| 2.6 | Threat level and alert panel | Large threat level indicator (GREEN/AMBER/RED gauge), current confidence score, time since last correlation event, evidence summary from both streams. Alert history log. Subscribes to Supabase alerts table. | Visual threat gauge that updates in realtime based on pipeline output. | 1.5 |
| 2.7 | Intelligence brief display | Formatted display of LLM-generated intelligence brief from Supabase briefs table. Classification markings, section headers (Situation, Assessment, Indicators, Gaps, Recommendations), confidence callouts. | Intelligence brief renders cleanly with proper formatting, auto-updates when new brief is generated. | 1.5 |

**Phase 2 Gate:** Dashboard loads demo scenario from Supabase and displays all panels with real data. Map shows movement indicators. Chart shows correlation. Threat gauge shows RED. Brief is readable and looks like an intelligence product. All panels update in realtime.

## **PHASE 3: Demo Scenario & Integration \[Hours 28–40\]**

**Goal:** The demo tells a compelling story. A scripted Taiwan Strait scenario plays through the dashboard showing escalation from GREEN to RED over a simulated 72-hour period in \~5 minutes. Live data feeds demonstrate technical capability alongside the seeded demo.

| \# | Task | Detail | Deliverable | Hrs |
| :---- | :---- | :---- | :---- | :---- |
| 3.1 | Demo scenario script | Write the narrative arc for the Taiwan Strait demo. Hour 0–24 (GREEN): baseline. Hour 24–48 (AMBER): coordination detected. Hour 48–72 (RED): civilian posts surge, correlation fires. Timestamps for both streams. | Written scenario document with timestamped events for both streams. | 2 |
| 3.2 | Demo playback engine | Build Python script that steps through the demo scenario by inserting time-sliced data into Supabase at controlled intervals. The React frontend auto-updates via realtime subscriptions. Speed control for presenter (fast forward / pause). | Dashboard auto-plays the scenario with visible escalation across all panels. | 3 |
| 3.3 | Live data integration | Wire live GDELT and Telegram feeds into Supabase as a separate data stream. Show real-time articles flowing in from Chinese state media. Show real Telegram channel messages being classified. Separate tab/mode in dashboard. | Live tab shows real data flowing through Supabase and being processed in real-time. | 3 |
| 3.4 | End-to-end testing | Run full demo scenario 5+ times. Fix: broken data transitions, LLM API failures (add retry \+ cached fallbacks), map rendering issues, chart scaling. Ensure demo works offline using pre-loaded Supabase data. | Demo runs reliably start-to-finish with no crashes or visual glitches. | 3 |
| 3.5 | Fallback/offline mode | Pre-load all demo data into Supabase so full demo can run without live API calls. Cache all LLM responses. If live feeds fail during demo, gracefully degrade with visual indicator. | Demo runs fully with pre-loaded data. Live feeds are a bonus, not a dependency. | 1.5 |

## **PHASE 4: Polish, Bug Fixes & Demo Prep \[Hours 40–48\]**

| \# | Task | Detail | Deliverable | Hrs |
| :---- | :---- | :---- | :---- | :---- |
| 4.1 | Visual polish | Consistent colour scheme. Clean typography. Loading spinners. Professional classification markings. Remove debug text. | Dashboard looks professional and intentional. | 2 |
| 4.2 | Error handling hardening | Try/catch around all API calls. Graceful error messages. Retry with exponential backoff. No unhandled exceptions. | No crash path exists in the demo flow. | 2 |
| 4.3 | Demo rehearsal | Run full demo 3+ times with team. Time it. Decide who drives, who explains, who handles questions. | Team runs demo confidently in under 7 minutes. | 2 |
| 4.4 | Documentation (README) | README with setup instructions, architecture diagram, data source list, key design decisions. Enough for judges to understand the system. | README.md in repo root. | 1 |
| 4.5 | Contingency testing | Test on actual presentation machine. Check screen resolution, projector, internet. Screen recording as backup. | Backup recording saved. Presentation environment verified. | 1 |

# **7\. Timeline Summary**

| Phase | Hours | Duration | Key Deliverable | Risk |
| :---- | :---- | :---- | :---- | :---- |
| Phase 0: Setup | 0–6 | 6 hrs | Dev env, API accounts, Supabase schema, data pipelines, Lovable project init, demo dataset | LOW |
| Phase 1: AI Engine | 6–16 | 10 hrs | Narrative detector, post classifier, correlation engine, brief generator — all writing to Supabase | MEDIUM |
| Phase 2: Dashboard | 16–28 | 12 hrs | Full Lovable React dashboard with map, charts, feeds, threat gauge, brief panel — all reading from Supabase realtime | MEDIUM |
| Phase 3: Integration | 28–40 | 12 hrs | Demo scenario playback via Supabase, live data integration, end-to-end testing, offline mode | HIGH |
| Phase 4: Polish | 40–48 | 8 hrs | Visual polish, error handling, demo rehearsal, documentation, contingency | LOW |

# **8\. Critical Risks & Mitigations**

| Risk | Impact | Likelihood | Mitigation |
| :---- | :---- | :---- | :---- |
| LLM API rate limits or downtime | HIGH | MEDIUM | Cache all demo scenario API responses during Phase 3\. Build offline fallback mode. Never depend on live API calls for the core demo. |
| GDELT API returns incomplete data | MEDIUM | LOW | Pre-download 7 days of historical data during Phase 0\. Use cached data as primary, live as supplement. |
| Telegram rate limiting (FloodWait) | MEDIUM | MEDIUM | Implement exponential backoff. Pre-scrape target channels during Phase 0\. Use cached messages for demo. |
| Lovable generates buggy React code | MEDIUM | MEDIUM | Ensure at least one team member can read React/TypeScript. Keep component complexity low. Test early in Phase 2\. |
| Supabase realtime latency or connection issues | HIGH | LOW | Pre-load all demo data into Supabase. Demo playback engine can work with pre-loaded data without requiring live realtime events. |
| Demo scenario not compelling | HIGH | LOW | Script the scenario in Phase 3.1 before building playback. The story matters more than the tech. |
| Integration bugs between Python backend and React frontend | HIGH | HIGH | Define Supabase table schemas as the contract in Phase 0\. Backend writes, frontend reads. Test the interface continuously. |
| Team member blocked/stuck | MEDIUM | MEDIUM | Each task is 1–3 hours. If stuck for \>1 hour, pair up. No one works alone for more than 3 hours. |
| Presentation environment issues | HIGH | LOW | Test on actual hardware in Phase 4.5. Screen recording backup. Demo works on localhost. |

# **9\. Demo Scenario: Taiwan Strait Escalation**

The demo walks the audience through a simulated 72-hour escalation in the Taiwan Strait. The dashboard starts at GREEN and escalates to RED as both streams detect converging indicators. The demo should take approximately 5–7 minutes to play through. The demo playback engine inserts time-sliced data into Supabase at controlled intervals, and the React frontend auto-updates via realtime subscriptions.

| Time | Threat | Stream 1 (Narrative) | Stream 2 (Movement) | System Response |
| :---- | :---- | :---- | :---- | :---- |
| Hour 0–12 | GREEN | Baseline: routine Xinhua/Global Times articles on economic policy, trade. Normal tone scores. | Baseline: 2–3 civilian posts from Fujian mentioning normal port activity. No anomalies. | System running. No correlation detected. Dashboard shows normal activity. |
| Hour 12–24 | GREEN | Subtle shift: Global Times publishes opinion on Taiwan “splittism.” Single outlet — not flagged as coordination. | Slight uptick: fishing forum mentions restricted zone near Pingtan. Single source — below threshold. | Narrative monitor logs the article. Movement monitor notes the post. No correlation yet. |
| Hour 24–36 | AMBER | Coordination detected: Xinhua, Global Times, and CCTV simultaneously use phrase “restoration of necessary order in the Taiwan Strait.” Score: 78/100. | Emerging cluster: 8 posts from Fujian/Xiamen reporting military truck convoys on G15. 3 posts about unusual fighter jet noise. | Correlation engine fires. Narrative spike (3 outlets, novel phrase) matches emerging movement cluster. Threat → AMBER. |
| Hour 36–48 | AMBER | Escalation: People’s Daily joins with editorial on “sacred duty to national reunification.” 4 outlets coordinating. CCTV leads evening news. | Growing cluster: 22 posts. Naval vessels departing Xiamen. Military vehicles near Fuzhou. Fishing ban announced for Taiwan Strait. | Confidence rising. 4-outlet coordination \+ 22 posts in same region. Score: 74\. Approaching RED. |
| Hour 48–60 | RED | Full coordination: All 5 major outlets running synchronised Taiwan coverage. WeChat public accounts amplifying. Unprecedented bellicosity. | Surge: 47 posts. Civilian photos of amphibious vehicles in Fuzhou harbour. Flights to Kinmen suspended. AIS shows vessel clustering. | 5-outlet sync \+ 47 posts \+ geographic convergence. Confidence: 91\. Threat → RED. Full brief generated. |
| Hour 60–72 | RED | Ultimatum-style language: “China reserves the right to all necessary measures.” All outlets amplifying. | PLA announces “routine military exercises.” Civilian posts confirm live fire visible from coast. | Brief updated. System provided \~24 hours advance warning before official announcement. |

**Key demo message:** The system detected the operation was being prepared approximately 24–48 hours before any public announcement, by correlating two independent indicator streams that no existing product fuses together.

# **10\. Estimated API Costs**

Total estimated cost for the entire 48-hour hackathon build, including development testing and demo runs:

| API | Usage Estimate | Rate | Est. Cost |
| :---- | :---- | :---- | :---- |
| Claude Sonnet 4.5 (narrative analysis, briefs) | \~500K input, \~100K output tokens | $3/$15 per M tokens | \~$3.00 |
| GPT-4o Mini (bulk post classification) | \~2M input, \~200K output tokens | $0.15/$0.60 per M tokens | \~$0.42 |
| Supabase (database \+ realtime) | Free tier: 500MB DB, 2GB bandwidth | Free | $0.00 |
| GDELT DOC 2.0 | Unlimited queries | Free | $0.00 |
| AISstream.io | WebSocket connection | Free | $0.00 |
| Telegram (Telethon) | Channel scraping | Free | $0.00 |
| ACLED | API queries | Free | $0.00 |
| Lovable | Free tier or Pro ($20/mo) | Free–$20 | $0–$20 |
|  |  | TOTAL | \< $25 |

# **11\. Definition of Done**

The prototype is complete when the following are all true:

| \# | Criterion | Verification |
| :---- | :---- | :---- |
| 1 | Dashboard loads and is navigable across all tabs | Open Lovable React app, click through all tabs without errors |
| 2 | Demo scenario plays from GREEN to RED in \~5 minutes | Run demo playback engine, verify threat escalation is visible and logical |
| 3 | Map shows movement indicators with correct geolocation | Verify markers appear in Fujian/Taiwan Strait area during scenario |
| 4 | Dual-axis chart shows narrative-movement correlation | Chart clearly shows both lines rising with shaded correlation zone |
| 5 | Intelligence brief is generated and readable | Brief includes situation, assessment, indicators, gaps, recommendations |
| 6 | Threat level gauge updates based on correlation output | Gauge moves GREEN → AMBER → RED during scenario playback |
| 7 | Live data tab shows real GDELT/Telegram data flowing | Switch to live tab, see real articles/messages appearing via Supabase realtime |
| 8 | Offline/pre-loaded mode works without live API calls | Run demo with pre-loaded Supabase data — completes without errors |
| 9 | No unhandled exceptions in any demo path | Run demo 3 times consecutively without crashes |
| 10 | Team can explain every component of the system | Each member can describe their section and the overall concept |

# **12\. ClickUp Task Summary**

Below is a flat task list formatted for direct import into ClickUp. Each task includes phase, estimated hours, and dependencies. Updated to reflect Supabase \+ Lovable stack.

| Task ID | Task Name | Phase | Hrs | Depends On |
| :---- | :---- | :---- | :---- | :---- |
| 0.1 | Dev environment \+ Lovable project init | Phase 0: Setup | 1 | — |
| 0.2 | API accounts \+ Supabase project creation | Phase 0: Setup | 1.5 | — |
| 0.3 | GDELT ingestion pipeline (→ Supabase) | Phase 0: Setup | 2 | 0.1, 0.2 |
| 0.4 | Telegram scraper (→ Supabase) | Phase 0: Setup | 2 | 0.1, 0.2 |
| 0.5 | Simulated demo dataset (→ Supabase) | Phase 0: Setup | 3 | 0.6 |
| 0.6 | Supabase schema \+ realtime config | Phase 0: Setup | 0.5 | 0.2 |
| 1.1 | Narrative coordination detector | Phase 1: AI Engine | 3 | 0.3, 0.6 |
| 1.2 | Civilian post classifier | Phase 1: AI Engine | 3 | 0.4, 0.6 |
| 1.3 | Entity extraction module | Phase 1: AI Engine | 2 | 0.6 |
| 1.4 | Correlation engine | Phase 1: AI Engine | 2 | 1.1, 1.2 |
| 1.5 | Intelligence brief generator | Phase 1: AI Engine | 1.5 | 1.4 |
| 1.6 | Pipeline integration test | Phase 1: AI Engine | 1 | 1.1–1.5 |
| 2.1 | Dashboard layout \+ Supabase connection | Phase 2: Dashboard | 2 | 0.6 |
| 2.2 | Interactive map panel | Phase 2: Dashboard | 3 | 2.1 |
| 2.3 | Dual-axis correlation chart | Phase 2: Dashboard | 2 | 2.1 |
| 2.4 | Narrative stream panel | Phase 2: Dashboard | 2 | 2.1 |
| 2.5 | Movement stream panel | Phase 2: Dashboard | 2 | 2.1 |
| 2.6 | Threat level and alert panel | Phase 2: Dashboard | 1.5 | 2.1 |
| 2.7 | Intelligence brief display | Phase 2: Dashboard | 1.5 | 2.1 |
| 3.1 | Demo scenario script | Phase 3: Integration | 2 | 0.5 |
| 3.2 | Demo playback engine (→ Supabase) | Phase 3: Integration | 3 | 2.1–2.7, 3.1 |
| 3.3 | Live data integration | Phase 3: Integration | 3 | 0.3, 0.4, 2.1 |
| 3.4 | End-to-end testing | Phase 3: Integration | 3 | 3.2, 3.3 |
| 3.5 | Fallback/offline mode | Phase 3: Integration | 1.5 | 3.2 |
| 4.1 | Visual polish | Phase 4: Polish | 2 | 3.4 |
| 4.2 | Error handling hardening | Phase 4: Polish | 2 | 3.4 |
| 4.3 | Demo rehearsal | Phase 4: Polish | 2 | 4.1, 4.2 |
| 4.4 | Documentation (README) | Phase 4: Polish | 1 | 3.4 |
| 4.5 | Contingency testing | Phase 4: Polish | 1 | 4.3 |

*— End of Document —*