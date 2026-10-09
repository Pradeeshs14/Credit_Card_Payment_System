
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field # type: ignore


class PaymentCategory(str, Enum):
    SHOPPING = "SHOPPING"
    FOOD = "FOOD"
    TRAVEL = "TRAVEL"
    BILLS = "BILLS"
    ENTERTAINMENT = "ENTERTAINMENT"
    HEALTH = "HEALTH"
    OTHER = "OTHER"


class PaymentCreate(BaseModel):
    user_id: int
    card_id: int
    amount: Decimal = Field(gt=0)
    category: PaymentCategory = PaymentCategory.OTHER
    location: str = ""
    device_id: str = ""


class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    user_id: int
    card_id: int
    amount: Decimal
    status: str

    class Config:
        from_attributes = True