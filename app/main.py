"""
ephemeris-service — AGPL-3.0

A minimal, generic HTTP wrapper around Swiss Ephemeris.

IMPORTANT: this file must never contain real business logic tied to the
domain this service's clients happen to be used for (see this repo's CI
boundary check for the exact watched terms). Anything domain-specific
belongs in the separate `panchanga-core` repository instead.  # boundary-check-ignore

Real Swiss Ephemeris (`pyswisseph`) calls are wired up below. All returned
longitudes are raw tropical ecliptic longitudes — no sidereal conversion
happens here; that is the responsibility of downstream consumers such as
`panchanga-core`.
"""

import os
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import swisseph as swe

if "SE_EPHE_PATH" in os.environ:
    swe.set_ephe_path(os.environ["SE_EPHE_PATH"])

app = FastAPI(
    title="ephemeris-service",
    description="Generic raw astronomical position service (AGPL-3.0). "
                 "See module docstring for scope restrictions.",
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
    jupiter_longitude_deg: float
    sunrise_utc: datetime
    sunset_utc: datetime


def _julday_ut(dt: datetime) -> float:
    hour = dt.hour + dt.minute / 60 + dt.second / 3600
    return swe.julday(dt.year, dt.month, dt.day, hour)


def _jd_ut_to_datetime(jd_ut: float) -> datetime:
    year, month, day, hour = swe.revjul(jd_ut)
    hour_int = int(hour)
    minute_full = (hour - hour_int) * 60
    minute_int = int(minute_full)
    second_int = round((minute_full - minute_int) * 60)
    return datetime(year, month, day, hour_int, minute_int, second_int, tzinfo=timezone.utc)


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
    Returns raw sun/moon/Jupiter ecliptic longitude and sunrise/sunset for
    the given UTC datetime and observer location.
    """
    jd_ut = _julday_ut(req.datetime_utc)

    sun_longitude_deg = swe.calc_ut(jd_ut, swe.SUN)[0][0]
    moon_longitude_deg = swe.calc_ut(jd_ut, swe.MOON)[0][0]
    jupiter_longitude_deg = swe.calc_ut(jd_ut, swe.JUPITER)[0][0]

    rise_rsmi = swe.CALC_RISE | swe.BIT_DISC_CENTER
    set_rsmi = swe.CALC_SET | swe.BIT_DISC_CENTER
    try:
        _, rise_tret = swe.rise_trans(
            jd_ut, swe.SUN, lon=req.lon, lat=req.lat, alt=0, rsmi=rise_rsmi
        )
        _, set_tret = swe.rise_trans(
            jd_ut, swe.SUN, lon=req.lon, lat=req.lat, alt=0, rsmi=set_rsmi
        )
    except Exception as exc:  # pragma: no cover - polar day/night edge cases
        raise HTTPException(
            status_code=422,
            detail=f"Could not compute sunrise/sunset for this location/date: {exc}",
        )

    return PositionResponse(
        sun_longitude_deg=sun_longitude_deg,
        moon_longitude_deg=moon_longitude_deg,
        jupiter_longitude_deg=jupiter_longitude_deg,
        sunrise_utc=_jd_ut_to_datetime(rise_tret[0]),
        sunset_utc=_jd_ut_to_datetime(set_tret[0]),
    )
