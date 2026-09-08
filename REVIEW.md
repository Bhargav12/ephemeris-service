# Review instructions

## Licensing context

This repo is AGPL-3.0 and public (final decision — see docs/product-plan.md
§11 in panchanga-core). Real Swiss Ephemeris calls are expected here now —
do not flag implementing them as premature.

## What Important means here

- Any change to `LICENSE` that isn't the full, unmodified official AGPL-3.0
  text — flag hand-written or paraphrased license text as Important.
- Panchanga-specific terms (tithi, nakshatra, yoga, karana, rahu kalam,
  yamaganda, gulika, muhurta, ayanamsa) introduced into this repo's code —
  treat as Nit (🟡) now, not Important; it's an architecture-convention
  deviation, not a licensing issue, since both repos are AGPL/public.

## Do not report

- Anything CI already enforces: lint, formatting, type errors
- Real pyswisseph implementation work — this is expected now, not a
  licensing gate

## Summary shape

Lead with whether the LICENSE file is correct/unmodified, then general
code quality notes.

