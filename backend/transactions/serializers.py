import uuid

from rest_framework import serializers # type: ignore

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    card_masked = serializers.CharField(
        source='card.masked_card_number',
        read_only=True
    )

    class Meta:
        model = Transaction
        fields = [
            'id',
            'transaction_id',
            'card',
            'card_masked',
            'amount',
            'status',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'transaction_id',
            'card_masked',
            'created_at',
        ]

    def create(self, validated_data):
        validated_data['transaction_id'] = (
            f"TXN-{uuid.uuid4().hex[:12].upper()}"
        )

        return Transaction.objects.create(**validated_data)

