from fastapi import APIRouter, HTTPException
from typing import List
from beanie import PydanticObjectId

from app.models import Car
from app.schemas import CarCreate, CarUpdate

router = APIRouter()


@router.get("/", response_model=List[Car])
async def list_cars():
    return await Car.find_all().to_list()


@router.get("/{car_id}", response_model=Car)
async def get_car(car_id: str):
    car = await Car.get(PydanticObjectId(car_id))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.post("/", response_model=Car, status_code=201)
async def create_car(car_in: CarCreate):
    car = Car(**car_in.dict())
    await car.insert()
    return car


@router.put("/{car_id}", response_model=Car)
async def update_car(car_id: str, car_in: CarUpdate):
    car = await Car.get(PydanticObjectId(car_id))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    update_data = car_in.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(car, k, v)
    await car.save()
    return car
