"""
ephemeris-service — AGPL-3.0

A minimal, generic HTTP wrapper around Swiss Ephemeris.

IMPORTANT: this file must never contain real business logic tied to the
domain this service's clients happen to be used for (see this repo's CI
boundary check for the exact watched terms). Anything domain-specific
belongs in the separate `panchanga-core` repository instead.  # boundary-check-ignore
"""

import os
from datetime import datetime, timezone

import swisseph as swe
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

# SE_EPHE_PATH is optional: without it (or without the .se1 files it points
# to) swisseph automatically falls back to its built-in Moshier ephemeris,
# which needs no data files and is accurate to within a few arcseconds for
# the sun/moon — plenty for this service's tolerances. Set SE_EPHE_PATH to
# a directory of downloaded .se1 files for full Swiss Ephemeris precision.
_SE_EPHE_PATH = os.environ.get("SE_EPHE_PATH")
if _SE_EPHE_PATH:
    swe.set_ephe_path(_SE_EPHE_PATH)

app = FastAPI(
    title="ephemeris-service",
    description="Generic raw astronomical position service (AGPL-3.0). "
                 "See module docstring for scope restrictions.",
    version="0.0.1",
)

PUBLIC_REPO_URL = "https://REPLACE-ME.example/ephemeris-service"  # TODO: set before publishing


class PositionRequest(BaseModel):
    datetime_utc: datetime = Field(
        ...,
        description="UTC datetime for the calculation; must include a UTC offset "
                    "(e.g. a trailing 'Z' or '+00:00')",
    )
    lat: float = Field(..., ge=-90, le=90, description="Observer latitude, degrees")
    lon: float = Field(..., ge=-180, le=180, description="Observer longitude, degrees")

    @field_validator("datetime_utc")
    @classmethod
    def _reject_naive_datetime(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError(
                "datetime_utc must include a UTC offset (e.g. trailing 'Z' or "
                "'+00:00'); a naive datetime would silently be treated as UTC "
                "even if the caller meant local time"
            )
        return value


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


def _to_julian_day_ut(dt: datetime) -> float:
    if dt.tzinfo is not None:
        dt = dt.astimezone(timezone.utc)
    hour = dt.hour + dt.minute / 60 + dt.second / 3600 + dt.microsecond / 3_600_000_000
    return swe.julday(dt.year, dt.month, dt.day, hour)


def _from_julian_day_ut(jd_ut: float) -> datetime:
    year, month, day, hour = swe.revjul(jd_ut)
    hour_int = int(hour)
    minute_float = (hour - hour_int) * 60
    minute_int = int(minute_float)
    second_float = (minute_float - minute_int) * 60
    second_int = int(second_float)
    microsecond = round((second_float - second_int) * 1_000_000)
    if microsecond >= 1_000_000:
        microsecond -= 1_000_000
        second_int += 1
    return datetime(year, month, day, hour_int, minute_int, second_int, microsecond, tzinfo=timezone.utc)


@app.post("/position", response_model=PositionResponse)
def position(req: PositionRequest):
    """
    Returns raw sun/moon ecliptic longitude and sunrise/sunset for the given
    UTC datetime and observer location.

    Sunrise/sunset are the next rising/setting after `datetime_utc` (per
    `swe.rise_trans` semantics), not necessarily on the same calendar day.
    """
    jd_ut = _to_julian_day_ut(req.datetime_utc)

    sun_longitude_deg = swe.calc_ut(jd_ut, swe.SUN)[0][0] % 360
    moon_longitude_deg = swe.calc_ut(jd_ut, swe.MOON)[0][0] % 360

    geopos = (req.lon, req.lat, 0.0)
    rise_flag, rise_data = swe.rise_trans(jd_ut, swe.SUN, swe.CALC_RISE, geopos)
    set_flag, set_data = swe.rise_trans(jd_ut, swe.SUN, swe.CALC_SET, geopos)
    if rise_flag < 0 or set_flag < 0:
        raise HTTPException(
            status_code=422,
            detail="Could not compute sunrise/sunset for this date/location "
                   "(e.g. polar day/night).",
        )

    return PositionResponse(
        sun_longitude_deg=sun_longitude_deg,
        moon_longitude_deg=moon_longitude_deg,
        sunrise_utc=_from_julian_day_ut(rise_data[0]),
        sunset_utc=_from_julian_day_ut(set_data[0]),
    )
