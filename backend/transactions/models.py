from django.conf import settings # type: ignore
from django.db import models # type: ignore


class Transaction(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    CATEGORY_CHOICES = [
        ("SHOPPING", "Shopping"),
        ("FOOD", "Food"),
        ("TRAVEL", "Travel"),
        ("BILLS", "Bills"),
        ("ENTERTAINMENT", "Entertainment"),
        ("HEALTH", "Health"),
        ("OTHER", "Other"),
    ]

    FRAUD_STATUS_CHOICES = [
        ("CLEAR", "Clear"),
        ("FLAGGED", "Flagged"),
        ("REVIEWED", "Reviewed"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    card = models.ForeignKey(
        "cards.Card",
        on_delete=models.CASCADE,
        related_name="transactions",
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default="OTHER",
        db_index=True,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    transaction_id = models.CharField(
        max_length=100,
        unique=True,
    )

    fraud_status = models.CharField(
        max_length=20,
        choices=FRAUD_STATUS_CHOICES,
        default="CLEAR",
        db_index=True,
    )

    fraud_reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    location = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    device_id = models.CharField(
        max_length=255,
        blank=True,
        default="",
        db_index=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return f"{self.transaction_id} - {self.status}"

