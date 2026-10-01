from django.conf import settings # type: ignore
from django.db import models # type: ignore


class AdminLog(models.Model):
    ACTION_CHOICES = [
        ('USER_VIEW', 'User View'),
        ('CARD_VIEW', 'Card View'),
        ('TRANSACTION_VIEW', 'Transaction View'),
        ('CSV_EXPORT', 'CSV Export'),
        ('PAYMENT_SUMMARY_VIEW', 'Payment Summary View'),
    ]

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_logs'
    )

    action = models.CharField(
        max_length=50,
        choices=ACTION_CHOICES
    )

    description = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.admin.username} - {self.action}"

