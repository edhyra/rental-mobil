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


# Output / response models reflecting stored attributes
class CarOut(CarCreate):
    id: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class CustomerOut(CustomerCreate):
    id: Optional[str] = None
    address: Optional[str] = None
    created_at: Optional[datetime] = None


class RentalOut(BaseModel):
    id: Optional[str] = None
    car_id: str
    customer_id: str
    start_date: datetime
    end_date: datetime
    daily_rate: float
    total_amount: float
    status: str
    created_at: Optional[datetime] = None
    returned_at: Optional[datetime] = None


class PaymentOut(BaseModel):
    id: Optional[str] = None
    rental_id: str
    amount: float
    method: str
    status: str
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
