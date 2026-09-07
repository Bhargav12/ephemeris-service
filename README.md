# ephemeris-service

**License: AGPL-3.0** (see `LICENSE`)

A minimal, generic HTTP service exposing raw astronomical positions
(sun/moon ecliptic longitude, sunrise/sunset) computed via Swiss Ephemeris.

## Why this service is deliberately generic

This API returns raw astronomical facts only — no tithi, nakshatra, rahu
kalam, or any other panchanga-specific term appears here. That's intentional:
the service should look like something any astronomy project could use, not
something carved out of the app purely to route around copyleft. See the
product plan's Phase 0 / AGPL architecture section for the reasoning.

**Do not add panchanga business logic to this repo.** If you find yourself
writing "tithi" or "nakshatra" anywhere in this codebase, it belongs in
`panchanga-core` instead, calling this service as a client.

## API

### `POST /position`
Request:
```json
{ "datetime_utc": "2026-09-07T12:00:00Z", "lat": 13.0827, "lon": 80.2707 }
```
Response:
```json
{
  "sun_longitude_deg": 165.32,
  "moon_longitude_deg": 201.77,
  "sunrise_utc": "2026-09-07T00:28:00Z",
  "sunset_utc": "2026-09-07T12:41:00Z"
}
```

### `GET /source`
Returns the public repository URL and license text location, satisfying
AGPL §13's "offer source to network users" clause defensively — even though
today the only caller is our own internal orchestrator.

### `GET /health`
Basic liveness check.

## Setup

```bash
pip install -r requirements.txt
# Requires Swiss Ephemeris data files (.se1) — download separately from
# https://www.astro.com/ftp/swisseph/ephe/ and set SE_EPHE_PATH.
export SE_EPHE_PATH=/path/to/ephe
uvicorn app.main:app --reload
```

## Before going to production

- [ ] Confirm AGPL applies as intended for this batch-only usage pattern
      (see clarification email in the main product plan)
- [ ] Publish this repo publicly BEFORE first production deployment
- [ ] Add full AGPL-3.0 text + Astrodienst/Koch/Treindl copyright notices
      to `LICENSE` (currently a placeholder)
- [ ] Do not use Astrodienst's or the authors' names in product marketing
