from datetime import datetime
import uuid

cars: dict = {}
customers: dict = {}
rentals: dict = {}
payments: dict = {}


def _gen_id() -> str:
    return str(uuid.uuid4())


async def list_cars():
    return list(cars.values())


async def get_car(car_id: str):
    return cars.get(car_id)


async def create_car(data: dict):
    cid = _gen_id()
    car = data.copy()
    car["id"] = cid
    car.setdefault("status", "available")
    car.setdefault("created_at", datetime.utcnow().isoformat())
    cars[cid] = car
    return car


async def update_car(car_id: str, update: dict):
    car = cars.get(car_id)
    if not car:
        return None
    car.update(update)
    cars[car_id] = car
    return car


async def delete_car(car_id: str):
    return cars.pop(car_id, None)


async def list_customers():
    return list(customers.values())


async def get_customer(customer_id: str):
    return customers.get(customer_id)


async def create_customer(data: dict):
    cid = _gen_id()
    customer = data.copy()
    customer["id"] = cid
    customer.setdefault("created_at", datetime.utcnow().isoformat())
    customers[cid] = customer
    return customer


async def update_customer(customer_id: str, update: dict):
    customer = customers.get(customer_id)
    if not customer:
        return None
    customer.update(update)
    customers[customer_id] = customer
    return customer


async def delete_customer(customer_id: str):
    return customers.pop(customer_id, None)


async def create_rental(customer_id: str, car_id: str, start_date, end_date):
    car = cars.get(car_id)
    if not car or car.get("status") != "available":
        return None

    daily_rate = float(car.get("daily_rate", 0.0))
    delta_days = max(1, (end_date.date() - start_date.date()).days + 1)
    total_amount = daily_rate * delta_days

    rid = _gen_id()
    rental = {
        "id": rid,
        "car_id": car_id,
        "customer_id": customer_id,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily_rate": daily_rate,
        "total_amount": total_amount,
        "status": "ongoing",
        "created_at": datetime.utcnow().isoformat(),
    }
    rentals[rid] = rental
    car["status"] = "rented"
    cars[car_id] = car
    return rental


async def return_rental(rental_id: str):
    rental = rentals.get(rental_id)
    if not rental:
        return None
    if rental.get("status") != "ongoing":
        return rental

    car = cars.get(rental.get("car_id"))
    if car and car.get("status") == "rented":
        car["status"] = "available"
        cars[car["id"]] = car

    rental["status"] = "returned"
    rental["returned_at"] = datetime.utcnow().isoformat()
    rentals[rental_id] = rental
    return rental


async def reset_all():
    cars.clear()
    customers.clear()
    rentals.clear()
    payments.clear()


async def list_rentals():
    return list(rentals.values())


async def get_rental(rental_id: str):
    return rentals.get(rental_id)
