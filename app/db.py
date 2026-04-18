import os
import motor.motor_asyncio
from beanie import init_beanie

from app.models import Car, Customer, Rental, Payment

client = None
DATABASE_NAME = os.getenv("MONGO_DB", "rental_db")
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")


async def init_db():
    """Initialize Motor client and Beanie ODM."""
    global client
    client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URI)
    db = client[DATABASE_NAME]
    # register document models
    await init_beanie(database=db, document_models=[Car, Customer, Rental, Payment])


def get_db():
    return client[DATABASE_NAME]
