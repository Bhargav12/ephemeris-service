from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_position_response_shape_and_ranges():
    resp = client.post(
        "/position",
        json={"datetime_utc": "2026-06-15T12:00:00Z", "lat": 13.0827, "lon": 80.2707},
    )
    assert resp.status_code == 200
    body = resp.json()

    assert set(body.keys()) == {
        "sun_longitude_deg",
        "moon_longitude_deg",
        "sunrise_utc",
        "sunset_utc",
    }
    assert 0.0 <= body["sun_longitude_deg"] < 360.0
    assert 0.0 <= body["moon_longitude_deg"] < 360.0

    sunrise = datetime.fromisoformat(body["sunrise_utc"])
    sunset = datetime.fromisoformat(body["sunset_utc"])
    assert sunrise < sunset


def test_position_sun_longitude_at_march_equinox():
    # Well-documented reference: the 2024 March equinox — the moment the
    # sun's apparent geocentric ecliptic longitude crosses 0 deg — fell on
    # 2024-03-20 03:06 UTC (widely published, e.g. timeanddate.com).
    resp = client.post(
        "/position",
        json={"datetime_utc": "2024-03-20T03:06:00Z", "lat": 0.0, "lon": 0.0},
    )
    assert resp.status_code == 200
    sun_longitude_deg = resp.json()["sun_longitude_deg"]

    # Generous tolerance: covers both the +/- few minute uncertainty in the
    # published equinox time and the lower precision of the Moshier
    # ephemeris fallback used when no .se1 data files are installed.
    distance_from_zero = min(sun_longitude_deg, 360.0 - sun_longitude_deg)
    assert distance_from_zero <= 1.0


def test_position_rejects_out_of_range_latitude():
    resp = client.post(
        "/position",
        json={"datetime_utc": "2026-06-15T12:00:00Z", "lat": 95.0, "lon": 0.0},
    )
    assert resp.status_code == 422
