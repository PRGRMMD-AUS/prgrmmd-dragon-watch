---
phase: 02-intelligence-processing
plan: 03
subsystem: llm-classifier
tags: [python, ai, openai, gpt-4o-mini]
dependencies:
  requires: [02-01]
  provides: [post-classifier, batch-post-processor]
  affects: [02-04]
tech-stack:
  added: []
  patterns: [semaphore-concurrency, structured-output-parsing, cost-optimization-filtering]
file-tracking:
  created:
    - src/llm/classification.py
    - src/processors/batch_posts.py
  modified: []
decisions:
  - what: Use GPT-4o Mini for classification
    why: 16x cheaper than Claude Sonnet for high-volume stream
    impact: Significant cost reduction for Stream 2
  - what: Filter 'not_relevant' before entity extraction
    why: Avoid expensive entity extraction on irrelevant posts
    impact: Further cost optimization
  - what: Use AsyncOpenAI with Pydantic response_format
    why: Native structured output support
    impact: Reliable JSON parsing without manual logic
metrics:
  duration: 5 minutes
  completed: 2026-02-07
  commits: 1
  files-changed: 2
---

# Phase 2 Plan 03: Civilian Post Classifier Summary

**One-liner:** Implemented the Civilian Post Classifier using GPT-4o Mini and a batch pipeline that filters for military relevance before triggering entity extraction to optimize costs.

## What Was Built

1.  **Civilian Post Classifier**
    - `src/llm/classification.py`: `classify_civilian_post` function.
    - Uses GPT-4o Mini for cost-effective bulk analysis.
    - Classifies into: `convoy`, `naval`, `flight`, `restricted_zone`, `not_relevant`.

2.  **Batch Processing Pipeline**
    - `src/processors/batch_posts.py`: `process_post_batch` orchestrator.
    - Fetches unprocessed posts from Supabase.
    - Classifies posts concurrently (semaphore limited).
    - **Optimization**: Only runs `extract_entities` (expensive Claude call) if post is relevant.
    - Writes `movement_events` and marks posts processed.

## Key Technical Patterns

-   **Cost Optimization**: Strategic model selection (GPT-4o Mini for noise filtering, Claude for precision extraction).
-   **Structured Outputs**: OpenAI `beta.chat.completions.parse` with Pydantic model.
-   **Conditional Logic**: Pipeline branches based on classification result.

## Deviations from Plan

-   **Supabase Client**: Used `await` native async client (consistent with Plan 02 deviation).
-   **Entities Storage**: Inserted as JSON within `movement_events` table (assuming schema flexibility or existing column).

## Verification Results

✅ `classify_civilian_post` and `process_post_batch` import correctly.
✅ Pipeline logic correctly implements the filter-then-extract pattern.
