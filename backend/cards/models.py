from django.conf import settings
from django.db import models


class Card(models.Model):
    CARD_TYPES = [
        ('CREDIT', 'Credit Card'),
        ('DEBIT', 'Debit Card'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cards'
    )

    card_type = models.CharField(
        max_length=10,
        choices=CARD_TYPES
    )

    masked_card_number = models.CharField(
        max_length=19
    )

    last_four_digits = models.CharField(
        max_length=4
    )

    credit_limit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=50000.00
    )

    expiry_month = models.PositiveSmallIntegerField()

    expiry_year = models.PositiveSmallIntegerField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.card_type} **** {self.last_four_digits}"