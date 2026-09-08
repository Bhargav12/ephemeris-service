# CLAUDE.md — ephemeris-service

## What this repo is

A minimal, generic HTTP service wrapping Swiss Ephemeris to return raw
astronomical positions (sun/moon ecliptic longitude, sunrise/sunset).

## LICENSING DECISION: FINAL — AGPL-3.0, public repo

This was a deliberate choice, made with full awareness that it requires
`panchanga-core`'s rule layer to also be open-source (per Astrodienst's own
stated interpretation of AGPL's reach — see `docs/product-plan.md` §11 in
the `panchanga-core` repo). Do not second-guess or revert this without the
user explicitly asking to change the licensing decision again.

**Practical implications:**
- This repo is (or will be) public. Don't restrict visibility unilaterally.
- `LICENSE` must contain the full, unmodified AGPL-3.0 text — if you're ever
  asked to touch this file, do not paraphrase or hand-write license text;
  direct the user to download it from https://www.gnu.org/licenses/agpl-3.0.txt.
- `NOTICE` carries the Swiss Ephemeris copyright/attribution requirements —
  keep it separate from `LICENSE`, don't merge them.
- Real Swiss Ephemeris calls (`pyswisseph`) are **no longer blocked** — go
  ahead and implement the TODOs in `app/main.py` when asked.
- If asked to modify Swiss Ephemeris's own source code, remember any such
  modifications must also be released under AGPL-3.0.

## Current state / what's stubbed

- `app/main.py` has the FastAPI app with `/position`, `/source`, `/health`.
- The actual Swiss Ephemeris calls are not yet wired up — implement per
  the TODO comments when asked.
- `PUBLIC_REPO_URL` in `/source`'s response is a placeholder — needs the
  real repo URL once published.

## Working conventions

- Python, FastAPI, Pydantic v2.
- Run `pip install -r requirements.txt` then `uvicorn app.main:app --reload`
  to run locally.
- Keep the API surface generic (raw positions in, raw positions out) —
  this is now an architecture/separation-of-concerns preference rather
  than a legal requirement, but still worth maintaining so `panchanga-core`
  stays the one place domain logic lives.

## Do not do without being asked

- Do not hand-write or paraphrase AGPL license text.
- Do not make this repository private without being told the licensing
  decision has changed again.
- Do not add authentication/rate-limiting infra decisions unilaterally —
  flag them as open questions instead.
