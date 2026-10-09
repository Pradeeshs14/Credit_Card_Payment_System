
from rest_framework import generics # type: ignore
from rest_framework.permissions import IsAuthenticated # type: ignore

from .models import Card
from .serializers import (
    CardSerializer,
    AdminCardBlockSerializer,
    AdminCardSerializer,
    AdminCreditLimitSerializer,
)
from email_service.services import send_card_blocked_alert
from users.models import AuditLog
from users.permissions import (
    IsAdminRole,
    IsAdminOrSupport,
    CanViewAllCards,
    CanManageOwnCards,
)


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")


class CardListCreateView(generics.ListCreateAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated, CanManageOwnCards]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class CardDeleteView(generics.DestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated, CanManageOwnCards]

    def get_queryset(self):
        return Card.objects.filter(user=self.request.user)


class AdminCardBlockView(generics.UpdateAPIView):
    serializer_class = AdminCardBlockSerializer
    permission_classes = [IsAdminOrSupport]
    queryset = Card.objects.all()

    def perform_update(self, serializer):
        old_value = serializer.instance.is_blocked
        card = serializer.save()

        if old_value != card.is_blocked:
            AuditLog.objects.create(
                actor=self.request.user,
                action="CARD_BLOCKED" if card.is_blocked else "CARD_UNBLOCKED",
                target_type="Card",
                target_id=str(card.pk),
                details={
                    "previous_is_blocked": old_value,
                    "new_is_blocked": card.is_blocked,
                },
                ip_address=get_client_ip(self.request),
            )

        if card.is_blocked and not old_value:
            send_card_blocked_alert(card)


class AdminCardListView(generics.ListAPIView):
    serializer_class = AdminCardSerializer
    permission_classes = [CanViewAllCards]
    queryset = Card.objects.select_related("user").all().order_by("-created_at")


class AdminCreditLimitUpdateView(generics.UpdateAPIView):
    serializer_class = AdminCreditLimitSerializer
    permission_classes = [IsAdminRole]
    queryset = Card.objects.all()

    def perform_update(self, serializer):
        old_limit = serializer.instance.credit_limit
        card = serializer.save()

        if old_limit != card.credit_limit:
            AuditLog.objects.create(
                actor=self.request.user,
                action="CREDIT_LIMIT_UPDATED",
                target_type="Card",
                target_id=str(card.pk),
                details={
                    "previous_credit_limit": str(old_limit),
                    "new_credit_limit": str(card.credit_limit),
                },
                ip_address=get_client_ip(self.request),
            )