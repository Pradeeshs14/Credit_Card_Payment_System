import csv

from django.conf import settings # type: ignore
from django.db.models import Sum # type: ignore
from django.http import HttpResponse # type: ignore
from django.shortcuts import get_object_or_404 # type: ignore

from rest_framework import generics # type: ignore
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny # type: ignore
from rest_framework.response import Response # type: ignore

from admin_logs.services import create_admin_log
from cards.models import Card

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Transaction.objects.filter(
            user=self.request.user
        ).order_by('-created_at')

        status = self.request.query_params.get('status')
        amount = self.request.query_params.get('amount')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if status:
            queryset = queryset.filter(
                status=status.upper()
            )

        if amount:
            queryset = queryset.filter(
                amount=amount
            )

        if start_date:
            queryset = queryset.filter(
                created_at__date__gte=start_date
            )

        if end_date:
            queryset = queryset.filter(
                created_at__date__lte=end_date
            )

        return queryset


class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class TransactionCSVExportView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        transactions = Transaction.objects.select_related(
            'user',
            'card'
        ).order_by('-created_at')

        response = HttpResponse(
            content_type='text/csv'
        )

        response['Content-Disposition'] = (
            'attachment; filename="transactions.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            'ID',
            'Transaction ID',
            'Username',
            'Card',
            'Amount',
            'Status',
            'Created At',
        ])

        for transaction in transactions:
            writer.writerow([
                transaction.id,
                transaction.transaction_id,
                transaction.user.username,
                transaction.card.masked_card_number,
                transaction.amount,
                transaction.status,
                transaction.created_at,
            ])

        create_admin_log(
            request.user,
            'CSV_EXPORT',
            'Admin exported transaction data as CSV.'
        )

        return response


class AdminPaymentSummaryView(generics.GenericAPIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        date = request.query_params.get('date')

        queryset = Transaction.objects.all()

        if date:
            queryset = queryset.filter(
                created_at__date=date
            )

        total_payments = queryset.count()

        successful_payments = queryset.filter(
            status='SUCCESS'
        ).count()

        failed_payments = queryset.filter(
            status='FAILED'
        ).count()

        pending_payments = queryset.filter(
            status='PENDING'
        ).count()

        total_amount = queryset.aggregate(
            total=Sum('amount')
        )['total'] or 0

        successful_amount = queryset.filter(
            status='SUCCESS'
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        create_admin_log(
            request.user,
            'PAYMENT_SUMMARY_VIEW',
            f'Admin viewed payment summary for date: {date or "all dates"}.'
        )

        return Response({
            'date': date,
            'total_payments': total_payments,
            'successful_payments': successful_payments,
            'failed_payments': failed_payments,
            'pending_payments': pending_payments,
            'total_amount': total_amount,
            'successful_amount': successful_amount,
        })


class PaymentSyncView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        internal_key = request.headers.get('X-Internal-Key')

        if internal_key != getattr(
            settings,
            'INTERNAL_API_KEY',
            None
        ):
            return Response(
                {'detail': 'Unauthorized'},
                status=401
            )

        user_id = request.data.get('user_id')
        card_id = request.data.get('card_id')
        amount = request.data.get('amount')
        status = request.data.get('status')
        transaction_id = request.data.get('transaction_id')

        if not all([
            user_id,
            card_id,
            amount,
            status,
            transaction_id
        ]):
            return Response(
                {'detail': 'Missing required payment data.'},
                status=400
            )

        if status not in [
            'SUCCESS',
            'FAILED',
            'PENDING'
        ]:
            return Response(
                {'detail': 'Invalid payment status.'},
                status=400
            )

        from django.contrib.auth import get_user_model # type: ignore

        User = get_user_model()

        user = get_object_or_404(
            User,
            id=user_id
        )

        card = get_object_or_404(
            Card,
            id=card_id,
            user=user
        )

        transaction, created = Transaction.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                'user': user,
                'card': card,
                'amount': amount,
                'status': status,
            }
        )

        return Response({
            'id': transaction.id,
            'transaction_id': transaction.transaction_id,
            'status': transaction.status,
            'created': created,
        })

