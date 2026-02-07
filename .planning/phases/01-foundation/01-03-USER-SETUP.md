# Phase 1 Plan 03: User Setup Required

**Generated:** 2026-02-07
**Phase:** 01-foundation
**Status:** Incomplete

This plan requires manual configuration of external services that cannot be automated.

---

## Environment Variables

| Status | Variable | Source | Add to |
|--------|----------|--------|--------|
| [ ] | `AISSTREAM_API_KEY` | https://aisstream.io → Sign up → Dashboard → API Key | `.env` |

---

## Setup Instructions

### 1. AISstream.io API Key

**What it's for:** Real-time AIS vessel position data via WebSocket

**Steps:**

1. Visit https://aisstream.io
2. Click "Sign Up" (free tier available)
3. Verify email address
4. Log in to dashboard
5. Navigate to "API Keys" section
6. Copy your API key
7. Add to `.env`:
   ```bash
   AISSTREAM_API_KEY=your_api_key_here
   ```

**Free tier limits:**
- 1,000 messages per day
- Single bounding box filter
- No historical data access

**Sufficient for:** Taiwan Strait monitoring with narrow bounding box (23-26N, 118-122E)

**Verification:**

```bash
# Test AIS tracker connects successfully
python -c "
import asyncio
from src.fetchers.ais import connect_ais_stream

async def test():
    print('Testing AIS connection...')
    # Will fail with clear error if AISSTREAM_API_KEY not set
    async for position in connect_ais_stream():
        print(f'Received position: {position}')
        break  # Exit after first message
    print('Connection successful!')

asyncio.run(test())
"
```

Expected output:
```
Testing AIS connection...
Received position: {'mmsi': 412345678, 'latitude': 24.5, ...}
Connection successful!
```

---

## Notes

**Demo dataset does NOT require AISstream:**
- Demo data is pre-generated and self-contained
- Run `python scripts/load_demo_data.py` without any external APIs
- AIS tracker only needed for LIVE vessel tracking beyond demo

**When you need this:**
- Phase 3 integration testing with live data
- Production deployment with real-time monitoring
- Development of AIS-based movement detection

**When you DON'T need this:**
- Phase 2 LLM wrapper development (uses demo articles/posts)
- Phase 3 correlation engine testing (uses demo positions)
- Phase 4 frontend development (uses demo data)

---

**Once all items complete:** Update status to "Complete" and check all boxes.
