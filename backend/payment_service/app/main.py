from fastapi import FastAPI # type: ignore
from fastapi.middleware.cors import CORSMiddleware # type: ignore

from app.database import Base, engine # type: ignore
from app.models.payment import Payment # type: ignore
from app.routers import payments # type: ignore

INTERNAL_API_KEY = "credit-payment-internal-2026"

app = FastAPI(
    title="Credit Card Payment System - Payment API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
	"http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(
    payments.router,
    prefix="/api/payments",
    tags=["Payments"]
)

@app.get("/")
def root():
    return {
        "message": "Payment API is running"
    }