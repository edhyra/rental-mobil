from fastapi import APIRouter, HTTPException, Response
from typing import List
from beanie import PydanticObjectId
import os

from app.models import Customer
from app.schemas import CustomerCreate, CustomerUpdate
from app.services import in_memory

TESTING = bool(os.getenv("TESTING"))

router = APIRouter()


@router.get("/")
async def list_customers():
    if TESTING:
        return await in_memory.list_customers()
    return await Customer.find_all().to_list()


@router.get("/{customer_id}")
async def get_customer(customer_id: str):
    if TESTING:
        customer = await in_memory.get_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    customer = await Customer.get(PydanticObjectId(customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.post("/", status_code=201)
async def create_customer(c_in: CustomerCreate):
    if TESTING:
        data = c_in.model_dump() if hasattr(c_in, "model_dump") else c_in.dict()
        customer = await in_memory.create_customer(data)
        return customer

    customer = Customer(**c_in.dict())
    await customer.insert()
    return customer


@router.put("/{customer_id}")
async def update_customer(customer_id: str, c_in: CustomerUpdate):
    if TESTING:
        update_data = c_in.model_dump(exclude_unset=True) if hasattr(c_in, "model_dump") else c_in.dict(exclude_unset=True)
        customer = await in_memory.update_customer(customer_id, update_data)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer

    customer = await Customer.get(PydanticObjectId(customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    update_data = c_in.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(customer, k, v)
    await customer.save()
    return customer


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(customer_id: str):
    if TESTING:
        customer = await in_memory.delete_customer(customer_id)
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        return Response(status_code=204)

    customer = await Customer.get(PydanticObjectId(customer_id))
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    await customer.delete()
    return Response(status_code=204)
