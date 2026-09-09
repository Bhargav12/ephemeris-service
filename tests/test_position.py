from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_position_response_shape_and_ranges():
    # Chosen so local time (UTC+5:30) is 01:30 -- well before that day's
    # sunrise -- so the next-rise/next-set pair returned by swe.rise_trans
    # falls on the same local day, in rise-then-set order.
    resp = client.post(
        "/position",
        json={"datetime_utc": "2026-06-14T20:00:00Z", "lat": 13.0827, "lon": 80.2707},
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


def test_position_sunrise_sunset_matches_published_reference():
    # Published reference for Chennai (timeanddate.com, 2026-06-15):
    # sunrise 05:42 IST, sunset 18:36 IST (IST = UTC+5:30), i.e.
    # 2026-06-15T00:12:00Z and 2026-06-15T13:06:00Z.
    resp = client.post(
        "/position",
        json={"datetime_utc": "2026-06-14T20:00:00Z", "lat": 13.0827, "lon": 80.2707},
    )
    assert resp.status_code == 200
    body = resp.json()

    sunrise = datetime.fromisoformat(body["sunrise_utc"])
    sunset = datetime.fromisoformat(body["sunset_utc"])

    expected_sunrise = datetime(2026, 6, 15, 0, 12, tzinfo=timezone.utc)
    expected_sunset = datetime(2026, 6, 15, 13, 6, tzinfo=timezone.utc)

    # Generous tolerance: covers the published time's minute-level rounding
    # and the lower precision of the Moshier ephemeris fallback used when no
    # .se1 data files are installed.
    assert abs((sunrise - expected_sunrise).total_seconds()) <= 120
    assert abs((sunset - expected_sunset).total_seconds()) <= 120


def test_position_rejects_naive_datetime():
    resp = client.post(
        "/position",
        json={"datetime_utc": "2026-06-15T12:00:00", "lat": 13.0827, "lon": 80.2707},
    )
    assert resp.status_code == 422
    assert "datetime_utc must include a UTC offset" in resp.text
