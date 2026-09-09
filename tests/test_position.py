from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_position_includes_valid_jupiter_longitude():
    response = client.post(
        "/position",
        json={
            "datetime_utc": "2026-09-07T12:00:00Z",
            "lat": 13.0827,
            "lon": 80.2707,
        },
    )

    assert response.status_code == 200
    body = response.json()

    assert "jupiter_longitude_deg" in body
    jupiter_longitude_deg = body["jupiter_longitude_deg"]
    assert isinstance(jupiter_longitude_deg, (int, float))
    assert 0 <= jupiter_longitude_deg < 360
