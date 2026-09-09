# ephemeris-service

**License: AGPL-3.0-only. This repo is public.** See `LICENSE` and `NOTICE`.

This is a deliberate, final decision (not the earlier isolation-architecture
attempt, which was ruled out by Astrodienst's own clarification — see
`docs/product-plan.md` §11 in the `panchanga-core` repo for the full history).
Proceeding under AGPL means this repo's complete source is public, and per
Astrodienst's stated interpretation, `panchanga-core`'s rule layer is also
public/AGPL-licensed as a consequence — see that repo directly.

A minimal, generic HTTP service exposing raw astronomical positions
(sun/moon ecliptic longitude, sunrise/sunset) computed via Swiss Ephemeris.

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
AGPL-3.0 §13 compliance: points network users of this service at the
corresponding source. Keep this pointed at the real public repo URL.

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

### Getting the `.se1` ephemeris data files

`pyswisseph` needs Swiss Ephemeris's `.se1` data files for full precision.
They're large binary files and are **not** committed to this repo. To get
them:

- **Local dev:** download the files you need (at minimum the planetary
  file covering your date range, e.g. `sepl_18.se1`) from
  https://www.astro.com/ftp/swisseph/ephe/ into a local directory, then
  `export SE_EPHE_PATH=/path/to/that/directory` before running the service.
- **CI:** add a step before running tests that downloads the same files
  into a cache directory and sets `SE_EPHE_PATH`, e.g.:
  ```yaml
  - name: Cache Swiss Ephemeris data
    uses: actions/cache@v4
    with:
      path: ephe
      key: swisseph-ephe-v1
  - name: Fetch Swiss Ephemeris data files
    run: |
      mkdir -p ephe
      cd ephe
      for f in sepl_18.se1 semo_18.se1; do
        [ -f "$f" ] || curl -fsSL -O "https://www.astro.com/ftp/swisseph/ephe/$f"
      done
  - name: Run tests
    run: pytest
    env:
      SE_EPHE_PATH: ${{ github.workspace }}/ephe
  ```
- **If `SE_EPHE_PATH` is unset or the files aren't found**, `pyswisseph`
  automatically falls back to its built-in Moshier ephemeris (no data files
  needed), which is accurate to within a few arcseconds for sun/moon —
  good enough for local testing, but the real `.se1` files should be used
  in production for full precision.

## Status

The `pyswisseph` integration in `app/main.py` is implemented: `/position`
computes real sun/moon ecliptic longitudes and sunrise/sunset via Swiss
Ephemeris (falling back to Moshier when `.se1` files aren't available, see
above).

## Before this repo is considered fully compliant

- [ ] Replace `LICENSE` with the real, unmodified AGPL-3.0 text (see that file)
- [ ] Fill in the project-specific copyright line in `NOTICE`
- [ ] Update `PUBLIC_REPO_URL` in `app/main.py`'s `/source` endpoint to the real repo URL
- [ ] Confirm the repo is actually public on GitHub
