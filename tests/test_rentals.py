import pytest
from httpx import AsyncClient
from datetime import datetime, timedelta
from app.main import app


@pytest.mark.asyncio
async def test_rental_flow():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # create customer
        customer = {"name": "Test User", "email": "test@example.com"}
        rc = await ac.post("/customers/", json=customer)
        assert rc.status_code == 201
        cbody = rc.json()
        customer_id = cbody.get("id") or cbody.get("_id")

        # create car
        car = {"plate_number": "B9999XX", "make": "Honda", "model": "Jazz", "year": 2019, "daily_rate": 200000.0}
        rcar = await ac.post("/cars/", json=car)
        assert rcar.status_code == 201
        carbody = rcar.json()
        car_id = carbody.get("id") or carbody.get("_id")

        # create rental
        start = datetime.utcnow().isoformat()
        end = (datetime.utcnow() + timedelta(days=2)).isoformat()
        rental_req = {"car_id": car_id, "customer_id": customer_id, "start_date": start, "end_date": end}
        rr = await ac.post("/rentals/", json=rental_req)
        assert rr.status_code == 201
        rbody = rr.json()
        assert rbody["status"] == "ongoing"

        # verify car is now rented
        rcar2 = await ac.get(f"/cars/{car_id}")
        assert rcar2.status_code == 200
        assert rcar2.json()["status"] == "rented"
