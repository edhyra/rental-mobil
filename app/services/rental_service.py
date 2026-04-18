from datetime import datetime
from bson import ObjectId
from pymongo import ReturnDocument
import os

from app.db import client, DATABASE_NAME
from app.models import Rental
from app.services import in_memory
from typing import Optional
from beanie import PydanticObjectId


async def create_rental(customer_id: str, car_id: str, start_date: datetime, end_date: datetime):
    """Create a rental if the car is available. This uses an atomic find_one_and_update on the cars collection.

    Returns the Rental document or None if car wasn't available.
    """
    # If TESTING env var is set, use the in-memory backend
    if os.getenv("TESTING"):
        return await in_memory.create_rental(customer_id, car_id, start_date, end_date)

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


async def return_rental(rental_id: str):
    """Mark a rental as returned and set the car status back to 'available'.

    Returns the updated Rental or None if not found.
    """
    # Use in-memory backend during testing
    if os.getenv("TESTING"):
        return await in_memory.return_rental(rental_id)

    if client is None:
        raise RuntimeError("DB client is not initialized. Ensure app startup has run init_db().")

    rental = await Rental.get(PydanticObjectId(rental_id))
    if not rental:
        return None

    if rental.status != "ongoing":
        return rental

    db = client[DATABASE_NAME]
    try:
        car_obj_id = ObjectId(str(rental.car_id))
    except Exception:
        car_obj_id = rental.car_id

    await db["cars"].find_one_and_update(
        {"_id": car_obj_id, "status": "rented"},
        {"$set": {"status": "available"}},
        return_document=ReturnDocument.AFTER,
    )

    rental.status = "returned"
    rental.returned_at = datetime.utcnow()
    await rental.save()
    return rental
