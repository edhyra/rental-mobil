from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument

from app.db import client, DATABASE_NAME
from app.models import Rental


async def create_rental(customer_id: str, car_id: str, start_date: datetime, end_date: datetime):
    """Create a rental if the car is available. This uses an atomic find_one_and_update on the cars collection.

    Returns the Rental document or None if car wasn't available.
    """
    if client is None:
        raise RuntimeError("DB client is not initialized. Ensure app startup has run init_db().")

    db = client[DATABASE_NAME]
    # Attempt to atomically set car to 'rented' only if currently 'available'
    result = await db["cars"].find_one_and_update(
        {"_id": ObjectId(car_id), "status": "available"},
        {"$set": {"status": "rented"}},
        return_document=ReturnDocument.AFTER,
    )
    if not result:
        return None

    daily_rate = float(result.get("daily_rate", 0.0))
    # calculate inclusive days
    delta_days = max(1, (end_date.date() - start_date.date()).days + 1)
    total_amount = daily_rate * delta_days

    rental = Rental(
        car_id=ObjectId(car_id),
        customer_id=ObjectId(customer_id),
        start_date=start_date,
        end_date=end_date,
        daily_rate=daily_rate,
        total_amount=total_amount,
        status="ongoing",
    )
    await rental.insert()
    return rental
