from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    user_id: int
    card_id: int
    amount: Decimal = Field(gt=0)


class PaymentResponse(BaseModel):
    id: int
    transaction_id: str
    user_id: int
    card_id: int
    amount: Decimal
    status: str

    class Config:
        from_attributes = True

