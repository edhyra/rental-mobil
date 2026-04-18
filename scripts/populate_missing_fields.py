#!/usr/bin/env python3
import os
import asyncio
from datetime import datetime, timedelta
import random
from motor.motor_asyncio import AsyncIOMotorClient
import string

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("MONGO_DB", "rental_db")


def rand_datetime_within_days(days: int = 365) -> datetime:
    days_back = random.randint(0, days)
    seconds_back = random.randint(0, 86400)
    return datetime.utcnow() - timedelta(days=days_back, seconds=seconds_back)


def rand_plate_number():
    # Pattern: 1 uppercase letter + 4 digits + 2 uppercase letters (e.g. B1234CD)
    prefix = random.choice(string.ascii_uppercase)
    digits = f"{random.randint(0, 9999):04d}"
    suffix = ''.join(random.choice(string.ascii_uppercase) for _ in range(2))
    return f"{prefix}{digits}{suffix}"


async def main():
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]

    # Cars: ensure created_at and status exist
    cursor = db["cars"].find({"$or": [{"created_at": {"$exists": False}}, {"status": {"$exists": False}}]})
    async for car in cursor:
        update = {}
        if "created_at" not in car:
            update["created_at"] = rand_datetime_within_days()
        if "status" not in car:
            update["status"] = "available"
        if update:
            await db["cars"].update_one({"_id": car["_id"]}, {"$set": update})
            print(f"Updated car {_id_to_str(car['_id'])}: {update}")

    # Cars: ensure plate_number exists (handle separately so we cover cars that already had created_at/status)
    cursor = db["cars"].find({"$or": [{"plate_number": {"$exists": False}}, {"plate_number": None}, {"plate_number": ""}]})
    async for car in cursor:
        update = {}
        # generate a unique plate_number
        plate = None
        for _ in range(10):
            candidate = rand_plate_number()
            exists = await db["cars"].find_one({"plate_number": candidate})
            if not exists:
                plate = candidate
                break
        if plate is None:
            plate = rand_plate_number()
        update["plate_number"] = plate
        await db["cars"].update_one({"_id": car["_id"]}, {"$set": update})
        print(f"Added plate_number for car {_id_to_str(car['_id'])}: {update}")

    # Customers: created_at and address
    cursor = db["customers"].find({"$or": [{"created_at": {"$exists": False}}, {"address": {"$exists": False}}]})
    async for cust in cursor:
        update = {}
        if "created_at" not in cust:
            update["created_at"] = rand_datetime_within_days()
        if "address" not in cust:
            update["address"] = f"{random.randint(100,999)} Example St, City"
        if update:
            await db["customers"].update_one({"_id": cust["_id"]}, {"$set": update})
            print(f"Updated customer {_id_to_str(cust['_id'])}: {update}")

    # Rentals: created_at and returned_at for returned rentals
    cursor = db["rentals"].find({"created_at": {"$exists": False}})
    async for rent in cursor:
        update = {"created_at": rand_datetime_within_days()}
        if rent.get("status") == "returned" and not rent.get("returned_at"):
            # try to use end_date if present
            end_date = rent.get("end_date")
            if isinstance(end_date, str):
                try:
                    rd = datetime.fromisoformat(end_date)
                except Exception:
                    rd = rand_datetime_within_days()
            elif isinstance(end_date, datetime):
                rd = end_date
            else:
                rd = rand_datetime_within_days()
            update["returned_at"] = rd
        await db["rentals"].update_one({"_id": rent["_id"]}, {"$set": update})
        print(f"Updated rental {_id_to_str(rent['_id'])}: {update}")

    # Payments: created_at and paid_at for paid payments
    cursor = db["payments"].find({"created_at": {"$exists": False}})
    async for pay in cursor:
        update = {"created_at": rand_datetime_within_days()}
        if pay.get("status") == "paid" and not pay.get("paid_at"):
            update["paid_at"] = update["created_at"]
        await db["payments"].update_one({"_id": pay["_id"]}, {"$set": update})
        print(f"Updated payment {_id_to_str(pay['_id'])}: {update}")

    client.close()


def _id_to_str(_id):
    try:
        return str(_id)
    except Exception:
        return repr(_id)


if __name__ == "__main__":
    asyncio.run(main())
