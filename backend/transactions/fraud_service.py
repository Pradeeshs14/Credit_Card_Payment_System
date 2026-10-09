from datetime import timedelta

from .models import Transaction


HIGH_VALUE_THRESHOLD = 50000
HIGH_VALUE_WINDOW_MINUTES = 10
HIGH_VALUE_TRANSACTION_LIMIT = 3

RAPID_TRANSACTION_WINDOW_MINUTES = 2
RAPID_TRANSACTION_LIMIT = 3


def detect_fraud(transaction):
    """Flag suspicious high-value, rapid, location, or device activity."""

    reasons = []
    transaction_time = transaction.created_at

    high_value_start = transaction_time - timedelta(
        minutes=HIGH_VALUE_WINDOW_MINUTES
    )

    high_value_count = Transaction.objects.filter(
        user=transaction.user,
        amount__gte=HIGH_VALUE_THRESHOLD,
        created_at__gte=high_value_start,
        created_at__lte=transaction_time,
    ).count()

    if high_value_count >= HIGH_VALUE_TRANSACTION_LIMIT:
        reasons.append(
            f"{high_value_count} high-value transactions within "
            f"{HIGH_VALUE_WINDOW_MINUTES} minutes."
        )

    rapid_start = transaction_time - timedelta(
        minutes=RAPID_TRANSACTION_WINDOW_MINUTES
    )

    recent_transactions = Transaction.objects.filter(
        user=transaction.user,
        created_at__gte=rapid_start,
        created_at__lte=transaction_time,
    ).exclude(pk=transaction.pk)

    rapid_count = recent_transactions.count() + 1

    if rapid_count >= RAPID_TRANSACTION_LIMIT:
        reasons.append(
            f"{rapid_count} transactions within "
            f"{RAPID_TRANSACTION_WINDOW_MINUTES} minutes."
        )

    if transaction.location and transaction.device_id:
        different_activity = recent_transactions.filter(
            created_at__gte=rapid_start,
        ).exclude(
            location=transaction.location,
            device_id=transaction.device_id,
        )

        if different_activity.exists():
            reasons.append(
                "Recent transaction activity used a different "
                "location or device identifier."
            )

    if reasons:
        transaction.fraud_status = "FLAGGED"
        transaction.fraud_reason = " ".join(reasons)[:255]
        transaction.save(
            update_fields=["fraud_status", "fraud_reason"]
        )
        return True

    return False

