# Phase 1 Plan 02: User Setup Required

**Generated:** 2026-02-06
**Phase:** 01-foundation
**Status:** Incomplete

## Environment Variables

| Status | Variable | Source | Add to |
|--------|----------|--------|--------|
| [ ] | TELEGRAM_API_ID | https://my.telegram.org/apps -> App api_id | .env |
| [ ] | TELEGRAM_API_HASH | https://my.telegram.org/apps -> App api_hash | .env |

## Account Setup

- [ ] Create Telegram app at https://my.telegram.org/apps (if not done)
  - Log in with your Telegram phone number
  - Click "API development tools"
  - Fill out the form (app title/short name can be anything)
  - Copy the `api_id` and `api_hash` values

## Verification

Once credentials are added to `.env`, verify Telegram scraper can initialize:

```bash
python3 -c "from src.fetchers.telegram import scrape_channel; print('Telegram credentials OK')"
```

---
**Once all items complete:** Mark status as "Complete"
