import random
import uuid

import requests # type: ignore

from fastapi import APIRouter, Depends, HTTPException # type: ignore
from sqlalchemy.orm import Session # type: ignore

from app.database import get_db
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter()


DJANGO_TRANSACTION_SYNC_URL = (
    "http://django:8000/api/transactions/sync/"
)



INTERNAL_API_KEY = "credit-payment-internal-2026"


@router.post("/", response_model=PaymentResponse)
def make_payment(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db)
):
    payment = Payment(
        user_id=payment_data.user_id,
        card_id=payment_data.card_id,
        amount=payment_data.amount,
        status="PENDING",
        transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    # Simulate payment processing
    payment.status = random.choice(["SUCCESS", "FAILED"])

    db.commit()
    db.refresh(payment)

    # Sync payment result with Django transaction service
    try:
        sync_response = requests.post(
            DJANGO_TRANSACTION_SYNC_URL,
            headers={
                "X-Internal-Key": INTERNAL_API_KEY,
            },
            json={
                "user_id": payment.user_id,
                "card_id": payment.card_id,
                "amount": float(payment.amount),
                "status": payment.status,
                "transaction_id": payment.transaction_id,
            },
            timeout=5,
        )

        if sync_response.status_code != 200:
            raise HTTPException(
                status_code=500,
                detail="Payment processed but transaction sync failed."
            )

    except requests.RequestException:
        raise HTTPException(
            status_code=500,
            detail="Payment processed but Django transaction service is unavailable."
        )

    return payment


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db)
):
    payment = db.query(Payment).filter(
        Payment.id == payment_id
    ).first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found"
        )

    return payment