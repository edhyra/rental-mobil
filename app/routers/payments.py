from fastapi import APIRouter, HTTPException
from typing import List
from beanie import PydanticObjectId

from app.models import Payment
from app.schemas import PaymentCreate

router = APIRouter()


@router.get("/", response_model=List[Payment])
async def list_payments():
    return await Payment.find_all().to_list()


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(payment_id: str):
    payment = await Payment.get(PydanticObjectId(payment_id))
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.post("/", response_model=Payment, status_code=201)
async def create_payment(p_in: PaymentCreate):
    payment = Payment(**p_in.dict())
    await payment.insert()
    return payment
