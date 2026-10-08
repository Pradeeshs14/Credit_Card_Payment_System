import csv
from calendar import monthrange
from datetime import datetime
from io import BytesIO

from django.conf import settings  # type: ignore
from django.db.models import Sum  # type: ignore
from django.http import HttpResponse  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore
from django.utils import timezone  # type: ignore

from reportlab.lib import colors  # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_RIGHT  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.styles import ( # type: ignore
    getSampleStyleSheet,
    ParagraphStyle,
)  # type: ignore
from reportlab.lib.units import mm  # type: ignore
from reportlab.platypus import (  # type: ignore
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from rest_framework import generics  # type: ignore
from rest_framework.permissions import (  # type: ignore
    IsAuthenticated,
    IsAdminUser,
    AllowAny,
)  # type: ignore
from rest_framework.response import Response  # type: ignore

from admin_logs.services import create_admin_log
from cards.models import Card
from email_service.services import (
    send_large_transaction_alert,
    send_low_credit_alert,
)

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
            f'Admin viewed payment summary for date: '
            f'{date or "all dates"}.'
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

        from django.contrib.auth import get_user_model  # type: ignore

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

        if transaction.status == 'SUCCESS':
            send_large_transaction_alert(transaction)
            send_low_credit_alert(transaction)

        return Response({
            'id': transaction.id,
            'transaction_id': transaction.transaction_id,
            'status': transaction.status,
            'created': created,
        })


class MonthlyStatementPDFView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get('year'))
            month = int(request.query_params.get('month'))
        except (TypeError, ValueError):
            return Response(
                {'detail': 'Year and month are required.'},
                status=400
            )

        if month < 1 or month > 12:
            return Response(
                {'detail': 'Month must be between 1 and 12.'},
                status=400
            )

        start_date = datetime(year, month, 1)

        last_day = monthrange(year, month)[1]

        end_date = datetime(
            year,
            month,
            last_day,
            23,
            59,
            59
        )

        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)

        transactions = Transaction.objects.filter(
            user=request.user,
            created_at__gte=start_date,
            created_at__lte=end_date,
            status='SUCCESS',
        ).select_related(
            'card'
        ).order_by(
            'created_at'
        )

        total_spending = sum(
            transaction.amount
            for transaction in transactions
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm,
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'StatementTitle',
            parent=styles['Title'],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=8,
        )

        right_style = ParagraphStyle(
            'Right',
            parent=styles['Normal'],
            alignment=TA_RIGHT,
        )

        story = []

        story.append(
            Paragraph(
                'Credit Card Payment System',
                title_style
            )
        )

        story.append(
            Paragraph(
                f'Monthly Statement - {month:02d}/{year}',
                styles['Heading2']
            )
        )

        story.append(
            Spacer(1, 8)
        )

        story.append(
            Paragraph(
                f'<b>Customer:</b> {request.user.username}',
                styles['Normal']
            )
        )

        story.append(
            Paragraph(
                f'<b>Email:</b> {request.user.email}',
                styles['Normal']
            )
        )

        story.append(
            Spacer(1, 8)
        )

        card_numbers = sorted({
            transaction.card.masked_card_number
            for transaction in transactions
        })

        if card_numbers:
            card_text = ', '.join(card_numbers)
        else:
            card_text = 'No transactions'

        story.append(
            Paragraph(
                f'<b>Card:</b> {card_text}',
                styles['Normal']
            )
        )

        story.append(
            Spacer(1, 12)
        )

        summary_data = [
            [
                'Statement Month',
                f'{month:02d}/{year}'
            ],
            [
                'Successful Transactions',
                str(len(transactions))
            ],
            [
                'Total Spending',
                f'Rs. {total_spending:,.2f}'
            ],
        ]

        summary_table = Table(
            summary_data,
            colWidths=[
                65 * mm,
                65 * mm
            ]
        )

        summary_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, -1),
                    colors.whitesmoke
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (0, -1),
                    'Helvetica-Bold'
                ),
                (
                    'ALIGN',
                    (1, 0),
                    (1, -1),
                    'RIGHT'
                ),
                (
                    'PADDING',
                    (0, 0),
                    (-1, -1),
                    7
                ),
            ])
        )

        story.append(summary_table)

        story.append(
            Spacer(1, 15)
        )

        transaction_data = [
            [
                'Date',
                'Transaction ID',
                'Card',
                'Amount',
                'Status',
            ]
        ]

        for transaction in transactions:
            transaction_data.append([
                transaction.created_at.strftime(
                    '%d-%m-%Y'
                ),
                transaction.transaction_id,
                transaction.card.masked_card_number,
                f'Rs. {transaction.amount:,.2f}',
                transaction.status,
            ])

        if len(transaction_data) == 1:
            transaction_data.append([
                '-',
                'No transactions',
                '-',
                'Rs. 0.00',
                '-',
            ])

        transaction_table = Table(
            transaction_data,
            repeatRows=1,
            colWidths=[
                25 * mm,
                45 * mm,
                35 * mm,
                30 * mm,
                20 * mm,
            ],
        )

        transaction_table.setStyle(
            TableStyle([
                (
                    'BACKGROUND',
                    (0, 0),
                    (-1, 0),
                    colors.HexColor('#1e293b')
                ),
                (
                    'TEXTCOLOR',
                    (0, 0),
                    (-1, 0),
                    colors.white
                ),
                (
                    'FONTNAME',
                    (0, 0),
                    (-1, 0),
                    'Helvetica-Bold'
                ),
                (
                    'FONTSIZE',
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    'GRID',
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    'ALIGN',
                    (3, 1),
                    (3, -1),
                    'RIGHT'
                ),
                (
                    'VALIGN',
                    (0, 0),
                    (-1, -1),
                    'MIDDLE'
                ),
                (
                    'PADDING',
                    (0, 0),
                    (-1, -1),
                    5
                ),
            ])
        )

        story.append(transaction_table)

        story.append(
            Spacer(1, 15)
        )

        story.append(
            Paragraph(
                f'<b>Total Monthly Spending: '
                f'Rs. {total_spending:,.2f}</b>',
                right_style
            )
        )

        story.append(
            Spacer(1, 20)
        )

        story.append(
            Paragraph(
                'This statement contains successful transactions '
                'recorded during the selected month.',
                styles['Normal']
            )
        )

        document.build(story)

        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type='application/pdf'
        )

        response['Content-Disposition'] = (
            f'attachment; '
            f'filename="monthly_statement_{year}_{month:02d}.pdf"'
        )

        return response


class AdminCardActivityView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        card_id = self.kwargs['card_id']

        return Transaction.objects.filter(
            card_id=card_id
        ).select_related(
            'user',
            'card'
        ).order_by(
            '-created_at'
        )