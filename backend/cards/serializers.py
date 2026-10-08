from rest_framework import serializers # type: ignore

from .models import Card


class CardSerializer(serializers.ModelSerializer):
    card_number = serializers.CharField(
        write_only=True,
        min_length=13,
        max_length=19
    )

    cvv = serializers.CharField(
        write_only=True,
        min_length=3,
        max_length=4
    )

    class Meta:
        model = Card
        fields = [
            'id',
            'card_type',
            'card_number',
            'cvv',
            'masked_card_number',
            'last_four_digits',
            'expiry_month',
            'expiry_year',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'masked_card_number',
            'last_four_digits',
            'created_at',
        ]

    def validate_card_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError(
                'Card number must contain only digits.'
            )

        if not 13 <= len(value) <= 19:
            raise serializers.ValidationError(
                'Card number must be between 13 and 19 digits.'
            )

        return value

    def validate_expiry_month(self, value):
        if value < 1 or value > 12:
            raise serializers.ValidationError(
                'Expiry month must be between 1 and 12.'
            )

        return value

    def create(self, validated_data):
        card_number = validated_data.pop('card_number')
        validated_data.pop('cvv')

        last_four_digits = card_number[-4:]
        masked_card_number = f"**** **** **** {last_four_digits}"

        validated_data['user'] = self.context['request'].user
        validated_data['last_four_digits'] = last_four_digits
        validated_data['masked_card_number'] = masked_card_number

        return Card.objects.create(**validated_data)

class AdminCardBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['is_blocked']

class AdminCardSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        source='user.username',
        read_only=True
    )

    email = serializers.EmailField(
        source='user.email',
        read_only=True
    )

    class Meta:
        model = Card
        fields = [
            'id',
            'username',
            'email',
            'card_type',
            'masked_card_number',
            'last_four_digits',
            'credit_limit',
            'is_blocked',
            'expiry_month',
            'expiry_year',
            'created_at',
        ]

        read_only_fields = fields

class AdminCreditLimitSerializer(serializers.ModelSerializer):
    class Meta:
        model = Card
        fields = ['credit_limit']

    def validate_credit_limit(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                'Credit limit must be greater than zero.'
            )

        if value > 10000000:
            raise serializers.ValidationError(
                'Credit limit cannot exceed Rs. 1,00,00,000.'
            )

        return value                