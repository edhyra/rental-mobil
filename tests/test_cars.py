import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.mark.asyncio
async def test_create_and_get_car():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        car_data = {
            "plate_number": "B1234CD",
            "make": "Toyota",
            "model": "Avanza",
            "year": 2020,
            "color": "white",
            "daily_rate": 250000.0,
        }
        r = await ac.post("/cars/", json=car_data)
        assert r.status_code == 201
        body = r.json()
        assert body["plate_number"] == "B1234CD"
        car_id = body.get("id") or body.get("_id")
        assert car_id

        r2 = await ac.get(f"/cars/{car_id}")
        assert r2.status_code == 200
        body2 = r2.json()
        assert body2["plate_number"] == "B1234CD"
