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

    async def mark_rented(self):
        self.status = "rented"
        await self.save()

    async def mark_available(self):
        self.status = "available"
        await self.save()

    async def update_status(self, status: str):
        self.status = status
        await self.save()


class Customer(Document):
    name: str
    email: str
    phone: Optional[str] = None
    driver_license_number: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "customers"

    async def update_info(self, name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None):
        if name is not None:
            self.name = name
        if email is not None:
            self.email = email
        if phone is not None:
            self.phone = phone
        await self.save()


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

    def calculate_total(self) -> float:
        delta_days = max(1, (self.end_date.date() - self.start_date.date()).days + 1)
        return float(self.daily_rate) * delta_days

    async def mark_returned(self):
        self.status = "returned"
        self.returned_at = datetime.utcnow()
        await self.save()

    def is_active(self) -> bool:
        return self.status == "ongoing"


class Payment(Document):
    rental_id: PydanticObjectId
    amount: float
    method: str = "cash"
    status: str = "pending"
    paid_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "payments"

    async def process(self, method: str):
        self.method = method
        self.status = "paid"
        self.paid_at = datetime.utcnow()
        await self.save()
        return self

    async def mark_paid(self):
        self.status = "paid"
        self.paid_at = datetime.utcnow()
        await self.save()
