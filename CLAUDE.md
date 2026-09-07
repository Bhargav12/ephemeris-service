# CLAUDE.md — ephemeris-service

## What this repo is

A minimal, generic HTTP service wrapping Swiss Ephemeris to return raw
astronomical positions (sun/moon ecliptic longitude, sunrise/sunset).
License: **AGPL-3.0**. This repo is (or will be) public.

## The one rule that overrides everything else

**This repo must never contain panchanga-specific business logic.**
No tithi, nakshatra, yoga, karana, rahu kalam, yamaganda, gulika, muhurta,
ayanamsa, or any other domain-specific term or calculation belongs here —
not in code, not in comments, not in variable names. If a task seems to
require adding one of these, stop and say so instead of implementing it;
that logic belongs in the separate `panchanga-core` repository, which
calls this service as an HTTP client.

This repo has a CI workflow (`.github/workflows/boundary-check.yml`) that
fails the build if these terms appear in any `.py` file. Don't try to work
around it — if it fires, the fix is to remove the logic, not to rename the
variable or add a suppression comment (except for genuine documentation
about the boundary itself, marked with `# boundary-check-ignore`).

## Why this boundary exists

Swiss Ephemeris is dual-licensed (AGPL vs. a paid Professional License).
Keeping this service generic and separate — a real, independently useful
program that just happens to be called by our own pipeline — is what lets
the proprietary rule layer in `panchanga-core` stay closed-source. See the
product plan (if available at `../panchanga-core/docs/product-plan.md` or
wherever it's been placed) section "Licensing Decision: Swiss Ephemeris"
and "Phase 0 Architecture — If Proceeding Under AGPL" for the full
reasoning. Treat that section as authoritative context before making
architectural changes here.

## Current state / what's stubbed

- `app/main.py` has the FastAPI app with `/position`, `/source`, `/health`.
- The actual Swiss Ephemeris calls (`swisseph`/`pyswisseph`) are **not yet
  wired up** — see the TODO comments in `main.py`. Do not uncomment or
  implement these until told the licensing decision (AGPL vs. Professional
  License) has been finalized. If asked to wire this up "for now" or
  "behind a flag," implement it but keep it opt-in/disabled by default.
- `LICENSE` is a placeholder. Do not replace it with the real AGPL-3.0 text
  or publish this repo without being explicitly asked to — that's a
  deliberate go/no-go decision point, not a routine cleanup task.

## Working conventions

- Python, FastAPI, Pydantic v2.
- Keep the API surface generic (raw positions in, raw positions out) —
  resist the temptation to add convenience fields that hint at panchanga
  use cases (e.g. don't add a `tithi_hint` field "just to save a round trip").
- Run `pip install -r requirements.txt` then `uvicorn app.main:app --reload`
  to run locally.
- Before committing, mentally check: does this diff introduce any of the
  forbidden terms? The CI check will catch it, but catching it yourself
  first saves a round trip.

## Do not do without being asked

- Do not make this repository public.
- Do not implement real Swiss Ephemeris calls.
- Do not add authentication/rate-limiting infra decisions unilaterally —
  flag them as open questions instead.
