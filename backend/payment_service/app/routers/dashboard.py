import jwt

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter()

JWT_SECRET = "django-insecure-dv#^g@+6b0-b$b=2&jg28r7%7y54)1w5b6w(5!m+h3xlj8*+r@"
JWT_ALGORITHM = "HS256"


def get_current_user_id(
    authorization: str = Header(...)
):
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header."
        )

    token = authorization.split(" ", 1)[1]

    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token."
            )

        return int(user_id)

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="JWT token has expired."
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid JWT token."
        )


@router.get("/summary")
def dashboard_summary(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    total_transactions = db.execute(
        text("""
            SELECT COUNT(*)
            FROM transactions_transaction
            WHERE user_id = :user_id
        """),
        {"user_id": user_id}
    ).scalar()

    total_amount_spent = db.execute(
        text("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions_transaction
            WHERE user_id = :user_id
              AND status = 'SUCCESS'
        """),
        {"user_id": user_id}
    ).scalar()

    current_month_spending = db.execute(
        text("""
            SELECT COALESCE(SUM(amount), 0)
            FROM transactions_transaction
            WHERE user_id = :user_id
              AND status = 'SUCCESS'
              AND YEAR(created_at) = YEAR(CURDATE())
              AND MONTH(created_at) = MONTH(CURDATE())
        """),
        {"user_id": user_id}
    ).scalar()

    available_credit_limit = db.execute(
    text("""
        SELECT GREATEST(
            COALESCE(
                SUM(
                    CASE
                        WHEN c.card_type = 'CREDIT'
                        THEN c.credit_limit
                        ELSE 0
                    END
                ),
                0
            )
            -
            COALESCE(
                (
                    SELECT SUM(t.amount)
                    FROM transactions_transaction t
                    WHERE t.user_id = :user_id
                      AND t.status = 'SUCCESS'
                ),
                0
            ),
            0
        )
        FROM cards_card c
        WHERE c.user_id = :user_id
    """),
    {"user_id": user_id}
).scalar()

    last_5_transactions = db.execute(
        text("""
            SELECT
                t.amount,
                t.status,
                t.created_at,
                c.masked_card_number
            FROM transactions_transaction t
            INNER JOIN cards_card c
                ON t.card_id = c.id
            WHERE t.user_id = :user_id
            ORDER BY t.created_at DESC
            LIMIT 5
        """),
        {"user_id": user_id}
    ).mappings().all()

    return {
        "total_transactions": total_transactions,
        "total_amount_spent": float(total_amount_spent),
        "current_month_spending": float(current_month_spending),
        "available_credit_limit": float(available_credit_limit),
        "last_5_transactions": [
            {
                "amount": float(transaction["amount"]),
                "masked_card_number": transaction["masked_card_number"],
                "date": transaction["created_at"],
                "status": transaction["status"],
            }
            for transaction in last_5_transactions
        ],
    }