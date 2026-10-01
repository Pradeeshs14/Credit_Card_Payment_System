from sqlalchemy import Column, DateTime, Integer, Numeric, String
from datetime import datetime

from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    transaction_id = Column(
    String(100),
    unique=True,
    nullable=False
)

    user_id = Column(Integer, nullable=False)

    card_id = Column(Integer, nullable=False)

    amount = Column(Numeric(10, 2), nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

