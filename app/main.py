from fastapi import FastAPI
from app.routers import cars, customers, rentals, payments
from app.db import init_db
import os
from app.services import in_memory

app = FastAPI(title="Rental Mobil API", version="0.1.0")

app.include_router(cars.router, prefix="/cars", tags=["cars"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(rentals.router, prefix="/rentals", tags=["rentals"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])


@app.on_event("startup")
async def startup_event():
    # If testing, reset in-memory stores instead of initializing DB
    if os.getenv("TESTING"):
        await in_memory.reset_all()
    else:
        await init_db()


@app.get("/")
async def root():
    return {"message": "Rental Mobil API"}
