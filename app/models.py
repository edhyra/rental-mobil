from beanie import Document, PydanticObjectId
from pydantic import Field
from typing import Optional
from datetime import datetime


class Car(Document):
    plate_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    daily_rate: float
    status: str = "available"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "cars"


class Customer(Document):
    name: str
    email: str
    phone: Optional[str] = None
    driver_license_number: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customers"


class Rental(Document):
    car_id: PydanticObjectId
    customer_id: PydanticObjectId
    start_date: datetime
    end_date: datetime
    daily_rate: float
    total_amount: float
    status: str = "ongoing"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    returned_at: Optional[datetime] = None

    class Settings:
        name = "rentals"


class Payment(Document):
    rental_id: PydanticObjectId
    amount: float
    method: str = "cash"
    status: str = "pending"
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "payments"
