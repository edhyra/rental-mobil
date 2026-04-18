from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CarCreate(BaseModel):
    plate_number: str
    make: str
    model: str
    year: int
    color: Optional[str] = None
    daily_rate: float


class CarUpdate(BaseModel):
    color: Optional[str] = None
    daily_rate: Optional[float] = None
    status: Optional[str] = None


class CustomerCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    driver_license_number: Optional[str] = None
    address: Optional[str] = None


class CustomerUpdate(BaseModel):
    phone: Optional[str] = None
    address: Optional[str] = None


class RentalCreate(BaseModel):
    car_id: str
    customer_id: str
    start_date: datetime
    end_date: datetime


class PaymentCreate(BaseModel):
    rental_id: str
    amount: float
    method: str
