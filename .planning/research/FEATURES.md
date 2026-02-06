# Feature Research

**Domain:** OSINT Pre-Conflict Early Warning Systems
**Researched:** 2026-02-07
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| Real-time data ingestion | Early warning = speed critical; users expect live feeds not batch updates | MEDIUM | For 48hr demo: simulate real-time with scheduled batches (every 15-30min) |
| Multi-source aggregation | No single source provides complete picture; credibility requires cross-referencing | LOW-MEDIUM | Stream 1: 4 state media outlets. Stream 2: Telegram + simulated social |
| Threat level visualization | Users need instant situation assessment without reading raw data | LOW | GREEN/AMBER/RED traffic light system with clear thresholds |
| Geographic context | Geopolitical threats are location-specific; map visualization expected | MEDIUM | Taiwan Strait region map with event markers. Simple Leaflet/Mapbox implementation |
| Temporal filtering | Users need to see "what's happening now" vs "what happened yesterday" | LOW | 72-hour rolling window with timeline scrubber |
| Alert notifications | Passive monitoring isn't enough; users expect push notifications on escalation | MEDIUM | For demo: visual alerts on dashboard. Production would need email/SMS/webhook |
| Source attribution | Intelligence professionals need to trace claims to sources | LOW | Every event links back to original social post or media article |
| Confidence scoring | Users need to know reliability of each signal | MEDIUM | Per-event confidence based on source credibility, geolocation accuracy, corroboration |
| Export/reporting | Analysts need to brief stakeholders; export intelligence briefs as PDF/JSON | LOW-MEDIUM | Generate markdown brief on threshold breach, allow PDF export |
| Historical playback | Understanding current situation requires reviewing recent escalation | MEDIUM | Timeline replay of last 72hrs. Not critical for MVP but judges may expect |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Dual-stream correlation** | CORE VALUE: Detects what narrative-only or movement-only systems miss | HIGH | This IS the product. Synchronised narrative + ground activity = earlier warning |
| Centralized directive detection | Identifies state propaganda coordination via synchronized phrasing across outlets | HIGH | LLM analyzes Xinhua, Global Times, CCTV, People's Daily for identical talking points |
| Civilian OSINT for movement | Crowdsourced military activity detection before official announcements | MEDIUM | Telegram channels where civilians post convoy/naval sightings |
| Geolocation extraction from text | Automatically maps unstructured social posts to coordinates | MEDIUM | LLM extracts "near Taipei" or "Route 101 convoy" → lat/long |
| Temporal clustering analysis | Identifies coordinated activity across time (72hr correlation window) | MEDIUM | Narrative spike Monday + movement cluster Tuesday = correlated threat |
| Regional cross-referencing | Correlates narrative theme (Taiwan) with movement geography (Taiwan Strait) | MEDIUM | Semantic matching: "Taiwan reunification" narrative + Taiwan Strait naval activity |
| Novelty detection | New phrasing in state media = fresh directive vs recycled rhetoric | HIGH | Compare current Xinhua phrasing to historical corpus to detect novel talking points |
| Preemptive warning timeline | Provides 24-48hr advance warning before traditional intelligence | HIGH | Key metric: how much earlier than CNN/official sources |
| Intelligence brief auto-generation | LLM synthesizes narrative + movement into executive summary | MEDIUM | "On 2026-02-05, state media began synchronized 'reunification readiness' messaging. 12 hours later, naval activity increased near..." |
| Explainable AI scoring | Shows WHY threat level changed (which signals triggered it) | MEDIUM | Transparency for intelligence analysts: "AMBER because 3/4 outlets + 8 movement clusters" |

### Anti-Features (Commonly Requested, Often Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Predict exact conflict timing | "When will invasion happen?" | Impossible and legally/ethically risky; creates false precision | Probabilistic threat levels (AMBER = "elevated risk next 72hrs" not "attack Tuesday 3pm") |
| 100% automation (no human review) | "AI should decide everything" | False positives could trigger panic; intelligence requires human judgment | AI recommends, human confirms before external alerts |
| Real-time global coverage | "Monitor all conflicts everywhere" | Scope explosion; demo needs focus | Demo: Taiwan Strait only. Show architecture scales to other regions |
| Social media firehose ingestion | "Connect to Twitter/X API for millions of posts" | Cost, noise, rate limits; 48hrs insufficient to build filtering | Simulated social feed + Telegram (manageable volume) |
| Historical data analysis | "Train on 20 years of GDELT" | Distraction from core demo; judges evaluate real-time capability | Use last 7 days of GDELT as baseline for novelty detection |
| Custom LLM training | "Fine-tune model on classified intelligence" | No access to training data; inference-only approach faster | Use prompt engineering with GPT-4/Claude for analysis |
| Blockchain/cryptocurrency tracking | "Follow money flows for threat finance" | Tangential to core value; different problem domain | Focus on open-source narrative + movement signals |
| Dark web monitoring | "Scan Tor forums" | Technical complexity, legal gray areas, low signal in 48hrs | Stick to Telegram (accessible, high-signal for OSINT community) |

## Feature Dependencies

```
[Data Ingestion Layer]
    ├──requires──> [GDELT API integration] (Narrative Stream)
    ├──requires──> [Telegram scraping] (Movement Stream)
    └──requires──> [Simulated social feed generator] (Movement Stream)

[LLM Analysis Pipeline]
    ├──requires──> [Data Ingestion Layer]
    ├──requires──> [Prompt engineering for directive detection]
    ├──requires──> [Prompt engineering for movement classification]
    └──requires──> [Geolocation extraction]

[Correlation Engine]
    ├──requires──> [LLM Analysis Pipeline]
    ├──requires──> [Temporal clustering (72hr window)]
    ├──requires──> [Geographic matching]
    └──requires──> [Threat level calculation algorithm]

[Visualization Dashboard]
    ├──requires──> [Correlation Engine]
    ├──requires──> [Map component (Leaflet/Mapbox)]
    ├──requires──> [Timeline component]
    └──requires──> [Traffic light threat indicator]

[Intelligence Brief Generation]
    ├──requires──> [Correlation Engine]
    └──enhances──> [Visualization Dashboard]

[Alert System]
    ├──requires──> [Correlation Engine]
    └──optional──> [Email/SMS integration] (defer to post-demo)
```

### Dependency Notes

- **LLM Analysis requires Data Ingestion:** Can't analyze what you haven't ingested. Build ingestion first.
- **Correlation Engine requires LLM Analysis:** Correlation operates on structured events (narrative signals + movement events) not raw text. LLM must classify/extract first.
- **Dashboard requires Correlation Engine:** Shows threat levels which come from correlation algorithm.
- **Brief Generation enhances Dashboard:** Not required for visualization but makes demo compelling for non-technical judges.
- **Historical playback conflicts with MVP timeline:** Requires storing/indexing all events. For 48hr demo, show only current 72hr window.

## MVP Definition

### Launch With (48hr Hackathon Demo)

Minimum viable product — what's needed to validate the concept.

- [ ] **Dual-stream data ingestion** — Core differentiator requires both streams operational
- [ ] **GDELT narrative monitoring** — Stream 1: Xinhua, Global Times, CCTV, People's Daily via GDELT
- [ ] **Simulated movement feed** — Stream 2: Generate realistic social posts for Taiwan Strait scenario (Telegram scraping optional if time)
- [ ] **LLM directive detection** — Analyze state media for synchronized phrasing
- [ ] **LLM movement classification** — Extract relevant military activity from social posts
- [ ] **Geolocation extraction** — Convert text mentions to map coordinates
- [ ] **Correlation algorithm** — 72hr window: narrative spike + movement cluster = threat escalation
- [ ] **Threat level calculation** — GREEN/AMBER/RED based on correlation strength
- [ ] **Dashboard visualization** — Map + timeline + threat indicator
- [ ] **Taiwan Strait demo scenario** — Simulated 72hr escalation with ~24-48hr warning time
- [ ] **Intelligence brief generation** — LLM synthesizes findings into executive summary

### Add After Validation (Post-Hackathon v1.x)

Features to add once core is working.

- [ ] **Real Telegram integration** — Replace simulated feed with live Telegram scraping (if demo proves concept)
- [ ] **Alert webhooks** — Push notifications to external systems on threat level change (trigger: when users want integration)
- [ ] **Historical playback** — Timeline replay of past escalations (trigger: users need training mode)
- [ ] **Multi-region support** — Beyond Taiwan Strait: South China Sea, Korean Peninsula (trigger: validated for one region first)
- [ ] **Confidence scoring per event** — Show reliability of each signal (trigger: users question accuracy)
- [ ] **Source credibility weighting** — Prioritize high-quality sources (trigger: noise problems emerge)
- [ ] **PDF export** — Generate printable intelligence briefs (trigger: users need offline sharing)
- [ ] **User authentication** — Multi-user access control (trigger: multiple organizations interested)

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Real-time Twitter/X ingestion** — Cost and rate limits prohibitive; assess after funding
- [ ] **Historical training corpus** — 20 years of GDELT for pattern learning (why defer: requires infrastructure investment)
- [ ] **Custom LLM fine-tuning** — Domain-specific model (why defer: need classified training data partnership)
- [ ] **Multi-language support** — Beyond English/Mandarin (why defer: focus on China threat first)
- [ ] **Mobile app** — Native iOS/Android (why defer: web dashboard sufficient for intelligence analysts)
- [ ] **Satellite imagery integration** — Verify movement claims with visual confirmation (why defer: API costs, complexity)

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Dual-stream correlation | HIGH | HIGH | P1 |
| GDELT narrative ingestion | HIGH | MEDIUM | P1 |
| LLM directive detection | HIGH | HIGH | P1 |
| LLM movement classification | HIGH | MEDIUM | P1 |
| Threat level visualization | HIGH | LOW | P1 |
| Map with event markers | HIGH | MEDIUM | P1 |
| Intelligence brief generation | MEDIUM | MEDIUM | P1 |
| Simulated social feed | HIGH | LOW | P1 |
| Geolocation extraction | HIGH | MEDIUM | P1 |
| Correlation algorithm | HIGH | HIGH | P1 |
| Timeline scrubber | MEDIUM | LOW | P2 |
| Real Telegram integration | MEDIUM | MEDIUM | P2 |
| Confidence scoring | MEDIUM | MEDIUM | P2 |
| Alert webhooks | MEDIUM | LOW | P2 |
| Historical playback | LOW | HIGH | P2 |
| PDF export | LOW | LOW | P2 |
| Multi-region support | MEDIUM | HIGH | P3 |
| Real-time Twitter ingestion | LOW | HIGH | P3 |
| Custom LLM training | LOW | VERY HIGH | P3 |
| Satellite imagery | LOW | VERY HIGH | P3 |

**Priority key:**
- P1: Must have for 48hr demo (judges evaluate completeness)
- P2: Should have if time permits (polish features)
- P3: Nice to have, future consideration (mention in presentation but don't build)

## Competitor Feature Analysis

| Feature | Janes Intelligence (Traditional) | Recorded Future (AI Threat Intel) | Dataminr (Real-time Alerts) | Dragon Watch (Our Approach) |
|---------|----------------------------------|-----------------------------------|----------------------------|----------------------------|
| Data sources | Classified + OSINT | Dark web + threat feeds | Social media firehose | GDELT (state media) + Telegram/social (civilian) |
| Narrative analysis | Human analysts read reports | AI entity extraction | Keyword alerts | LLM detects synchronized phrasing = directive |
| Movement detection | Satellite imagery + intel reports | None (cyber-focused) | Social media mentions | Civilian OSINT posts (convoy sightings, naval activity) |
| **Correlation capability** | Manual (analyst connects dots) | None (separate streams) | None (single stream alerts) | **AUTOMATED: Narrative + movement = threat** |
| Warning timeline | Days to weeks (human speed) | Hours (for cyber threats) | Minutes (breaking news) | **24-48hrs before official announcements** |
| Geographic focus | Global (expensive) | Cyber/digital (not physical) | Global (noisy) | **Region-specific: Taiwan Strait for demo** |
| Output format | PDF reports (slow) | Threat scores + dashboards | Alert emails | **Live dashboard + auto-generated intelligence briefs** |
| Cost | High (enterprise contracts) | Medium-High (SaaS) | Medium (SaaS) | **Open-source demo (hackathon project)** |

**Key differentiator:** No existing vendor automatically correlates state narrative propaganda with civilian-sourced military movement. Janes relies on human analysts. Recorded Future focuses on cyber threats. Dataminr is reactive (breaking news) not predictive. Dragon Watch's dual-stream approach provides earlier warning.

## Hackathon Judging Criteria Considerations

### Technical Execution (What Judges Look For)

| Judge Expectation | Our Implementation | Notes |
|-------------------|-------------------|-------|
| Working demo | Live dashboard showing Taiwan Strait scenario | Must be functional, not just slides |
| Novel approach | Dual-stream correlation is unique | Emphasize "no one else does this" |
| Real data | GDELT is real; social feed simulated | Acknowledge simulation, show architecture for production |
| AI/ML integration | LLM for directive detection + movement classification | Use GPT-4 or Claude API, show prompts |
| Scalability story | Architecture diagram showing multi-region expansion | Don't need to build it, show how it would work |
| Clear value prop | "24-48hr earlier warning than traditional intelligence" | Quantify the advantage |

### Table Stakes for Hackathon Demos

- Live demo (not video or slides only)
- Clear problem statement (judges understand the threat)
- Working code (repo with commit history)
- Visual polish (dashboard looks professional)
- Presentation clarity (non-technical judges can follow)

### Differentiators for Winning

- Novel technical approach (dual-stream correlation)
- Real-world impact story (Taiwan Strait crisis scenario)
- Scalability narrative (works for other regions/conflicts)
- Open-source ethos (code available, community could extend)
- Explainable AI (show why threat level changed)

## 48-Hour Build Strategy

### Hour 0-8: Foundation
- GDELT API integration + basic narrative ingestion
- Simulated social feed generator
- Database schema for events

### Hour 8-16: Intelligence Layer
- LLM prompt engineering for directive detection
- LLM prompt engineering for movement classification
- Geolocation extraction

### Hour 16-24: Correlation
- Temporal clustering algorithm (72hr window)
- Geographic matching logic
- Threat level calculation

### Hour 24-36: Visualization
- Map component with event markers
- Timeline component
- Traffic light threat indicator
- Basic dashboard layout

### Hour 36-44: Polish
- Intelligence brief auto-generation
- Demo scenario data (simulate 72hr escalation)
- UI/UX refinement

### Hour 44-48: Presentation
- Slides explaining architecture
- Practice demo walkthrough
- Backup plan if live demo fails

## Sources

**Confidence Level: MEDIUM** (based on domain knowledge + existing intelligence platform patterns)

### OSINT Platform Analysis
- GDELT Project documentation (real-time event database)
- Janes Intelligence services (traditional threat intelligence baseline)
- Recorded Future platform (AI-driven threat intelligence)
- Dataminr real-time alerting (social media monitoring)
- Bellingcat OSINT methodology (civilian intelligence gathering)

### Domain Knowledge
- Intelligence analysis workflows (analyst expectations for sourcing, confidence, geographic context)
- Geopolitical early warning systems (indicators of escalation)
- LLM capabilities for text analysis (directive detection, entity extraction, summarization)
- Hackathon demo best practices (working prototype > perfect architecture)

### Limitations
- Could not verify 2026 state-of-the-art via web search (permission denied)
- Feature list based on established intelligence platform patterns + domain expertise
- Competitor analysis reflects known capabilities as of training cutoff (January 2025)
- Hackathon-specific recommendations based on typical 48hr project constraints

### Verification Needed
- Current GDELT API rate limits and data freshness (check docs before building)
- LLM API costs for expected query volume (estimate before demo)
- Telegram scraping legal/technical feasibility (may need to stick with simulation)
- Map component library options (Leaflet vs Mapbox vs alternatives)

---
*Feature research for: Dragon Watch OSINT Pre-Conflict Early Warning System*
*Researched: 2026-02-07*
*Next step: Use this analysis to define roadmap phases and technical requirements*
