from django.contrib import admin

from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'transaction_id',
        'user',
        'card',
        'amount',
        'status',
        'created_at',
    )

    list_filter = (
        'status',
        'created_at',
    )

    search_fields = (
        'transaction_id',
        'user__username',
        'user__email',
        'card__last_four_digits',
    )

    ordering = (
        '-created_at',
    )