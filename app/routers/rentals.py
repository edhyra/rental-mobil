from fastapi import APIRouter, HTTPException
from typing import List
from beanie import PydanticObjectId

from app.models import Rental
from app.schemas import RentalCreate
from app.services.rental_service import create_rental

router = APIRouter()


@router.get("/", response_model=List[Rental])
async def list_rentals():
    return await Rental.find_all().to_list()


@router.get("/{rental_id}", response_model=Rental)
async def get_rental(rental_id: str):
    rental = await Rental.get(PydanticObjectId(rental_id))
    if not rental:
        raise HTTPException(status_code=404, detail="Rental not found")
    return rental


@router.post("/", response_model=Rental, status_code=201)
async def create_rental_endpoint(r_in: RentalCreate):
    rental = await create_rental(r_in.customer_id, r_in.car_id, r_in.start_date, r_in.end_date)
    if not rental:
        raise HTTPException(status_code=400, detail="Unable to create rental - car may be unavailable")
    return rental
