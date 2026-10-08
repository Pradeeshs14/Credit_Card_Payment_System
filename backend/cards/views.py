from rest_framework import generics  # type: ignore

from rest_framework.permissions import (  # type: ignore
    IsAuthenticated,
    IsAdminUser,
)

from .models import Card

from .serializers import (
    CardSerializer,
    AdminCardBlockSerializer,
    AdminCardSerializer,
    AdminCreditLimitSerializer,
)

from email_service.services import send_card_blocked_alert


class CardListCreateView(generics.ListCreateAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(
            user=self.request.user
        )


class CardDeleteView(generics.DestroyAPIView):
    serializer_class = CardSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Card.objects.filter(
            user=self.request.user
        )


class AdminCardBlockView(generics.UpdateAPIView):
    serializer_class = AdminCardBlockSerializer
    permission_classes = [IsAdminUser]
    queryset = Card.objects.all()

    def perform_update(self, serializer):
        card = serializer.save()

        if card.is_blocked:
            send_card_blocked_alert(card)

class AdminCardListView(generics.ListAPIView):
    serializer_class = AdminCardSerializer
    permission_classes = [IsAdminUser]
    queryset = Card.objects.select_related('user').all().order_by('-created_at')

class AdminCreditLimitUpdateView(generics.UpdateAPIView):
    serializer_class = AdminCreditLimitSerializer
    permission_classes = [IsAdminUser]
    queryset = Card.objects.all()    