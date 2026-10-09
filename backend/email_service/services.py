from decimal import Decimal

from django.conf import settings # type: ignore
from django.core.mail import send_mail # type: ignore
from django.db.models import Sum # type: ignore


def send_large_transaction_alert(transaction):
    if transaction.amount <= Decimal("5000"):
        return

    user = transaction.user
    card = transaction.card

    send_mail(
        subject="Credit Card Payment Alert",
        message=(
            f"Hello {user.username},\n\n"
            f"A successful transaction above Rs. 5,000 was detected "
            f"on your credit card.\n\n"
            f"Transaction ID: {transaction.transaction_id}\n"
            f"Amount: Rs. {transaction.amount}\n"
            f"Card: {card.masked_card_number}\n"
            f"Date: {transaction.created_at}\n\n"
            f"If you did not authorize this transaction, please "
            f"contact your bank immediately."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_low_credit_alert(transaction):
    card = transaction.card

    if card.credit_limit <= 0:
        return

    successful_spending = (
        card.transactions
        .filter(status="SUCCESS")
        .aggregate(total=Sum("amount"))
        .get("total")
        or Decimal("0")
    )

    available_credit = card.credit_limit - successful_spending
    threshold = card.credit_limit * Decimal("0.10")

    if available_credit >= threshold:
        return

    user = transaction.user

    send_mail(
        subject="Low Credit Limit Alert",
        message=(
            f"Hello {user.username},\n\n"
            f"Your available credit limit has fallen below 10%.\n\n"
            f"Card: {card.masked_card_number}\n"
            f"Credit Limit: Rs. {card.credit_limit}\n"
            f"Available Credit: Rs. {available_credit}\n\n"
            f"Please review your credit card usage."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )


def send_card_blocked_alert(card):
    user = card.user

    send_mail(
        subject="Credit Card Blocked",
        message=(
            f"Hello {user.username},\n\n"
            f"Your credit card has been blocked.\n\n"
            f"Card: {card.masked_card_number}\n\n"
            f"If you did not request this action, please contact "
            f"your bank immediately."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )



def send_fraud_alert(transaction):
    user = transaction.user
    card = transaction.card

    reason = (
        getattr(transaction, "fraud_reason", None)
        or "Suspicious transaction activity was detected."
    )

    send_mail(
        subject="URGENT: Suspicious Credit Card Transaction",
        message=(
            f"Hello {user.username},\n\n"
            "Our system has flagged a transaction as potentially fraudulent.\n\n"
            f"Transaction ID: {transaction.transaction_id}\n"
            f"Amount: Rs. {transaction.amount}\n"
            f"Card: {card.masked_card_number}\n"
            f"Reason: {reason}\n"
            f"Date: {transaction.created_at}\n\n"
            "If you did not authorize this transaction, please contact "
            "your bank immediately."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email] if user.email else [],
        fail_silently=False,
    )