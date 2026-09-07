"""
ephemeris-service — AGPL-3.0

A minimal, generic HTTP wrapper around Swiss Ephemeris.

IMPORTANT: this file must never contain panchanga-specific terms (tithi,
nakshatra, yoga, karana, rahu kalam, muhurta, etc). Those belong in the
separate `panchanga-core` repository, which calls this service as a client.

NOTE: the actual `swisseph` import and calls are stubbed out below with
clearly marked TODOs. Do not wire up real Swiss Ephemeris calls until the
licensing decision (product plan §11) is finalized and this repo has been
split out and published as its own public, AGPL-3.0 repository.
"""

from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# TODO: once licensing is confirmed, uncomment and use the real library.
# import swisseph as swe
# swe.set_ephe_path(os.environ["SE_EPHE_PATH"])

app = FastAPI(
    title="ephemeris-service",
    description="Generic raw astronomical position service (AGPL-3.0). "
                 "No panchanga-specific logic lives here.",
    version="0.0.1",
)

PUBLIC_REPO_URL = "https://REPLACE-ME.example/ephemeris-service"  # TODO: set before publishing


class PositionRequest(BaseModel):
    datetime_utc: datetime = Field(..., description="UTC datetime for the calculation")
    lat: float = Field(..., ge=-90, le=90, description="Observer latitude, degrees")
    lon: float = Field(..., ge=-180, le=180, description="Observer longitude, degrees")


class PositionResponse(BaseModel):
    sun_longitude_deg: float
    moon_longitude_deg: float
    sunrise_utc: datetime
    sunset_utc: datetime


@app.get("/health")
def health():
    return {"status": "ok", "time_utc": datetime.now(timezone.utc).isoformat()}


@app.get("/source")
def source():
    """
    AGPL-3.0 §13 defensive compliance: point network users of this service
    at the corresponding source, even though today the only caller is our
    own internal orchestrator.
    """
    return {
        "license": "AGPL-3.0",
        "source_repository": PUBLIC_REPO_URL,
        "note": "Replace PUBLIC_REPO_URL before production deployment.",
    }


@app.post("/position", response_model=PositionResponse)
def position(req: PositionRequest):
    """
    Returns raw sun/moon ecliptic longitude and sunrise/sunset for the given
    UTC datetime and observer location.

    STUB IMPLEMENTATION — replace with real Swiss Ephemeris calls, e.g.:

        jd = swe.julday(req.datetime_utc.year, req.datetime_utc.month,
                         req.datetime_utc.day,
                         req.datetime_utc.hour + req.datetime_utc.minute / 60)
        sun = swe.calc_ut(jd, swe.SUN)[0][0]
        moon = swe.calc_ut(jd, swe.MOON)[0][0]
        sunrise, sunset = swe.rise_trans(...)  # see swisseph docs
    """
    raise HTTPException(
        status_code=501,
        detail=(
            "Not implemented: wire up real Swiss Ephemeris calls here once "
            "the licensing decision is finalized (see product plan §11)."
        ),
    )
