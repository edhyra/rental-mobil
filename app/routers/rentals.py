from fastapi import APIRouter, HTTPException
from typing import List
from beanie import PydanticObjectId
import os

from app.models import Rental
from app.schemas import RentalCreate
from app.services.rental_service import create_rental, return_rental
from app.services import in_memory

TESTING = bool(os.getenv("TESTING"))

router = APIRouter()


@router.get("/")
async def list_rentals():
    if TESTING:
        return await in_memory.list_rentals()
    return await Rental.find_all().to_list()


@router.get("/{rental_id}")
async def get_rental(rental_id: str):
    if TESTING:
        rental = await in_memory.get_rental(rental_id)
        if not rental:
            raise HTTPException(status_code=404, detail="Rental not found")
        return rental

    rental = await Rental.get(PydanticObjectId(rental_id))
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental


@router.post("/", status_code=201)
async def create_rental_endpoint(r_in: RentalCreate):
    rental = await create_rental(r_in.customer_id, r_in.car_id, r_in.start_date, r_in.end_date)
    if not rental:
        raise HTTPException(status_code=400, detail="Unable to create rental - car may be unavailable")
    return rental


@router.post("/{rental_id}/return")
async def return_rental_endpoint(rental_id: str):
    rental = await return_rental(rental_id)
    if not rental:
        raise HTTPException(status_code=400, detail="Unable to return rental or rental not found")
    return rental
