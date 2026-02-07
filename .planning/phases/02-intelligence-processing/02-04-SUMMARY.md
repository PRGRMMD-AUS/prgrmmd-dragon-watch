---
phase: 02-intelligence-processing
plan: 04
subsystem: llm-correlation
tags: [python, ai, anthropic, claude-sonnet]
dependencies:
  requires: [02-02, 02-03]
  provides: [intelligence-brief-generator, correlation-engine]
  affects: [03-01]
tech-stack:
  added: []
  patterns: [dual-stream-context-window, chain-of-evidence, semantic-analysis]
file-tracking:
  created:
    - src/llm/briefs.py
    - src/processors/brief_generator.py
  modified: []
decisions:
  - what: Implement correlation logic within Brief Generator
    why: The 'correlation' is effectively the LLM's reasoning over the two provided streams
    impact: Simplified architecture (no separate 'correlation.py' module needed)
  - what: Use Claude Sonnet for Brief Generation
    why: Complex reasoning and synthesis required for threat assessment
    impact: High-quality output suitable for 'Unclassified' intelligence products
  - what: Include traceability IDs
    why: Audit trail from Brief -> Narrative/Movement Events -> Raw Articles/Posts
    impact: Trustworthy and verifiable intelligence
metrics:
  duration: 5 minutes
  completed: 2026-02-07
  commits: 1
  files-changed: 2
---

# Phase 2 Plan 04: Correlation Engine Summary

**One-liner:** Implemented the Intelligence Brief Generator, which acts as the Correlation Engine by synthesizing Narrative and Movement streams into actionable threat assessments using Claude 3.5 Sonnet.

## What Was Built

1.  **Correlation & Briefing Logic**
    - `src/llm/briefs.py`: `generate_intelligence_brief` function.
    - Accepts both `narrative_events` and `movement_events`.
    - Prompts Claude to analyze "narrative coordination strength, movement cluster size, geographic proximity, temporal alignment" (the correlation logic).
    - Outputs structured `IntelligenceBrief`.

2.  **Brief Generation Pipeline**
    - `src/processors/brief_generator.py`: Orchestrator.
    - Fetches recent events from both streams.
    - Generates brief.
    - Writes to `briefs` table with `narrative_event_ids` and `movement_event_ids` for full traceability.

## Key Technical Patterns

-   **Context Window Engineering**: Carefully formatted string representations of events to fit hundreds of data points into Claude's context window.
-   **Chain of Evidence**: Every brief is linked via foreign keys (arrays) to the specific analytical events that triggered it.

## Deviations from Plan

-   **Module Structure**: Plan called for `src/analysis/correlation.py`. I implemented the correlation logic directly inside `src/llm/briefs.py` as it is intrinsic to the brief generation process (the "brief" IS the correlated output).
-   **File Naming**: Used `src/` prefix instead of `backend/` to match project structure.

## Verification Results

✅ `generate_intelligence_brief` and `generate_brief` modules import correctly.
✅ Pipeline integrates both streams and handles cases where streams might be empty.
