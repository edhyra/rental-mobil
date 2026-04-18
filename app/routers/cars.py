from fastapi import APIRouter, HTTPException, Response
from typing import List
from beanie import PydanticObjectId
import os

from app.models import Car
from app.schemas import CarCreate, CarUpdate
from app.services import in_memory

TESTING = bool(os.getenv("TESTING"))

router = APIRouter()


@router.get("/")
async def list_cars():
    if TESTING:
        return await in_memory.list_cars()
    return await Car.find_all().to_list()


@router.get("/{car_id}")
async def get_car(car_id: str):
    if TESTING:
        car = await in_memory.get_car(car_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return car

    car = await Car.get(PydanticObjectId(car_id))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    return car


@router.post("/", status_code=201)
async def create_car(car_in: CarCreate):
    if TESTING:
        data = car_in.model_dump() if hasattr(car_in, "model_dump") else car_in.dict()
        car = await in_memory.create_car(data)
        return car

    car = Car(**car_in.dict())
    await car.insert()
    return car


@router.put("/{car_id}")
async def update_car(car_id: str, car_in: CarUpdate):
    if TESTING:
        update_data = car_in.model_dump(exclude_unset=True) if hasattr(car_in, "model_dump") else car_in.dict(exclude_unset=True)
        car = await in_memory.update_car(car_id, update_data)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return car

    car = await Car.get(PydanticObjectId(car_id))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    update_data = car_in.dict(exclude_unset=True)
    for k, v in update_data.items():
        setattr(car, k, v)
    await car.save()
    return car


@router.delete("/{car_id}", status_code=204)
async def delete_car(car_id: str):
    if TESTING:
        car = await in_memory.delete_car(car_id)
        if not car:
            raise HTTPException(status_code=404, detail="Car not found")
        return Response(status_code=204)

    car = await Car.get(PydanticObjectId(car_id))
    if not car:
        raise HTTPException(status_code=404, detail="Car not found")
    await car.delete()
    return Response(status_code=204)
