---
phase: 02-intelligence-processing
plan: 02
subsystem: llm-narrative
tags: [python, ai, anthropic, processing-pipeline]
dependencies:
  requires: [02-01]
  provides: [narrative-detector, entity-extractor, batch-article-processor]
  affects: [02-04]
tech-stack:
  added: []
  patterns: [xml-tagged-prompts, tool-use-structured-output, semaphore-concurrency, async-pipeline]
file-tracking:
  created:
    - src/llm/narrative.py
    - src/llm/extraction.py
    - src/processors/batch_articles.py
  modified: []
decisions:
  - what: Use XML tags for prompt injection defense
    why: Hardens LLM against malicious content in articles
    impact: Safer processing of untrusted input
  - what: Distinct modules for Narrative vs Extraction
    why: Separation of concerns (document-level analysis vs span-level extraction)
    impact: Modular testing and maintenance
  - what: Batch pipeline with semaphore
    why: Respects API rate limits while maximizing throughput
    impact: Efficient processing of backlog
  - what: Use `await` for Supabase client instead of `asyncio.to_thread`
    why: `src/database/client.py` uses asynchronous `AsyncClient`
    impact: Native async/await pattern throughout pipeline
metrics:
  duration: 5 minutes
  completed: 2026-02-07
  commits: 1
  files-changed: 3
---

# Phase 2 Plan 02: Narrative Detector Summary

**One-liner:** Implemented the Narrative Coordination Detector and Entity Extractor using Claude 3.5 Sonnet, orchestrated by an async batch processor.

## What Was Built

1.  **Narrative Coordination Detector**
    - `src/llm/narrative.py`: `detect_narrative_coordination` function.
    - Analyzes batches of articles for synchronized phrasing and themes.
    - Uses XML-tagged prompts and Tool Use for structured `NarrativeCoordination` output.

2.  **Entity Extractor**
    - `src/llm/extraction.py`: `extract_entities` function.
    - Extracts military units, equipment, locations, and timestamps.
    - Enforces "ONLY entities present in text" rule to reduce hallucinations.

3.  **Batch Processing Pipeline**
    - `src/processors/batch_articles.py`: `process_article_batch` orchestrator.
    - Fetches unprocessed articles from Supabase.
    - Runs narrative detection (batch) and entity extraction (concurrent).
    - Writes results to `narrative_events` and marks articles processed.

## Key Technical Patterns

-   **Prompt Engineering**: XML tags (`<instructions>`, `<data>`) separate system logic from content.
-   **Structured Outputs**: Anthropic Tool Use guarantees Pydantic schema compliance.
-   **Concurrency Control**: `asyncio.Semaphore` limits parallel Entity Extraction calls.
-   **Observability**: Structured logs for tokens, cost, and duration per call.

## Deviations from Plan

-   **Supabase Async Client**: Used native `await client...` calls instead of wrapping in `asyncio.to_thread` because `src/database/client.py` provides an `AsyncClient`.
-   **Entities Storage**: Attempted to update source table with entities JSON since `entities` table schema was unconnected to the verified Phase 1 schema summary.

## Verification Results

✅ `detect_narrative_coordination` and `extract_entities` import correctly.
✅ `process_article_batch` imports and is valid async code.
✅ All modules integrate with `src.config.settings` and `src.llm.utils`.
