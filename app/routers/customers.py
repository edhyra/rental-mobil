from fastapi import APIRouter, HTTPException
from typing import List
from beanie import PydanticObjectId

from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate

router = APIRouter()


@router.get("/", response_model=List[Customer])
async def list_customers():
    return await Customer.find_all().to_list()


@router.get("/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    customer = await Customer.get(PydanticObjectId(customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", response_model=Customer, status_code=201)
async def create_customer(c_in: CustomerCreate):
    customer = Customer(**c_in.dict())
    await customer.insert()
    return customer


@router.put("/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, c_in: CustomerUpdate):
    customer = await Customer.get(PydanticObjectId(customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_data = c_in.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(customer, k, v)
    await customer.save()
    return customer
