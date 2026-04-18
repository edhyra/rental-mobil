from fastapi import FastAPI
from app.routers import cars, customers, rentals, payments
from app.db import init_db

app = FastAPI(title="Rental Mobil API", version="0.1.0")

app.include_router(cars.router, prefix="/cars", tags=["cars"])
app.include_router(customers.router, prefix="/customers", tags=["customers"])
app.include_router(rentals.router, prefix="/rentals", tags=["rentals"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])


@app.on_event("startup")
async def startup_event():
    await init_db()


@app.get("/")
async def root():
    return {"message": "Rental Mobil API"}
