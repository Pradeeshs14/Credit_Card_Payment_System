import logging

logger = logging.getLogger("system_monitoring")

import csv
from calendar import monthrange
from datetime import datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO

from django.conf import settings  # type: ignore
from django.db.models import Sum, Count  # type: ignore
from django.db.models.functions import TruncMonth  # type: ignore
from django.http import HttpResponse  # type: ignore
from django.shortcuts import get_object_or_404  # type: ignore
from django.utils import timezone  # type: ignore

from reportlab.lib import colors  # type: ignore
from reportlab.lib.enums import TA_CENTER, TA_RIGHT  # type: ignore
from reportlab.lib.pagesizes import A4  # type: ignore
from reportlab.lib.styles import (  # type: ignore
    getSampleStyleSheet,
    ParagraphStyle,
)
from reportlab.lib.units import mm  # type: ignore
from reportlab.platypus import (  # type: ignore
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from rest_framework import generics  # type: ignore
from rest_framework.pagination import PageNumberPagination  # type: ignore
from rest_framework.permissions import IsAuthenticated, AllowAny  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework.views import APIView  # type: ignore

from admin_logs.services import create_admin_log
from cards.models import Card
from email_service.services import (
    send_large_transaction_alert,
    send_low_credit_alert,
    send_fraud_alert,
)
from users.models import AuditLog
from users.permissions import (  # type: ignore
    IsAdminRole,
    CanViewAdminTransactionData,
    CanCreateTransaction,
)

from .fraud_service import detect_fraud
from .models import Transaction
from .serializers import TransactionSerializer


def get_client_ip(request):
    return request.META.get("REMOTE_ADDR")


def filter_transactions_by_date(queryset, request):
    start_date = request.query_params.get("start_date")
    end_date = request.query_params.get("end_date")

    try:
        if start_date:
            parsed_start = datetime.strptime(
                start_date, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                created_at__date__gte=parsed_start
            )

        if end_date:
            parsed_end = datetime.strptime(
                end_date, "%Y-%m-%d"
            ).date()
            queryset = queryset.filter(
                created_at__date__lte=parsed_end
            )

        if start_date and end_date and parsed_start > parsed_end:
            raise ValueError("Start date must not be after end date.")

    except ValueError as exc:
        raise ValueError(
            "Dates must use YYYY-MM-DD, and start_date must not "
            "be after end_date."
        ) from exc

    return queryset
class TransactionPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = TransactionPagination

    def get_queryset(self):
        queryset = (
            Transaction.objects.filter(user=self.request.user)
            .select_related("card")
            .order_by("-created_at")
        )

        params = self.request.query_params
        status_value = params.get("status")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        min_amount = params.get("min_amount")
        max_amount = params.get("max_amount")
        amount = params.get("amount")
        card_number = params.get("card_number")
        category = params.get("category")
        ordering = params.get("ordering", "-created_at")

        if status_value:
            queryset = queryset.filter(status=status_value.upper())

        if category:
            queryset = queryset.filter(category=category.upper())

        if start_date:
            queryset = queryset.filter(created_at__date__gte=start_date)

        if end_date:
            queryset = queryset.filter(created_at__date__lte=end_date)

        try:
            if amount:
                queryset = queryset.filter(amount=Decimal(amount))

            if min_amount:
                queryset = queryset.filter(amount__gte=Decimal(min_amount))

            if max_amount:
                queryset = queryset.filter(amount__lte=Decimal(max_amount))
        except (InvalidOperation, TypeError, ValueError):
            return queryset.none()

        if card_number:
            queryset = queryset.filter(
                card__masked_card_number__icontains=card_number
            )

        allowed_ordering = {
            "created_at",
            "-created_at",
            "amount",
            "-amount",
            "status",
            "-status",
            "category",
            "-category",
        }

        if ordering in allowed_ordering:
            queryset = queryset.order_by(ordering)

        return queryset


class TransactionCreateView(generics.CreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated, CanCreateTransaction]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TransactionCSVExportView(generics.GenericAPIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        transactions = Transaction.objects.select_related(
            "user", "card"
        ).order_by("-created_at")

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="transactions.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            "ID",
            "Transaction ID",
            "Username",
            "Card",
            "Amount",
            "Category",
            "Status",
            "Fraud Status",
            "Created At",
        ])

        for transaction in transactions.iterator():
            writer.writerow([
                transaction.id,
                transaction.transaction_id,
                transaction.user.username,
                transaction.card.masked_card_number,
                transaction.amount,
                transaction.category,
                transaction.status,
                transaction.fraud_status,
                transaction.created_at,
            ])

        create_admin_log(
            request.user,
            "CSV_EXPORT",
            "Admin exported transaction data as CSV.",
        )

        return response


class AdminPaymentSummaryView(generics.GenericAPIView):
    permission_classes = [CanViewAdminTransactionData]

    def get(self, request):
        date_filter = request.query_params.get("date")
        queryset = Transaction.objects.all()

        if date_filter:
            queryset = queryset.filter(created_at__date=date_filter)

        total_amount = (
            queryset.aggregate(total=Sum("amount"))["total"] or Decimal("0")
        )
        successful_amount = (
            queryset.filter(status="SUCCESS")
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0")
        )

        create_admin_log(
            request.user,
            "PAYMENT_SUMMARY_VIEW",
            f"Admin viewed payment summary for date: "
            f"{date_filter or 'all dates'}.",
        )

        return Response({
            "date": date_filter,
            "total_payments": queryset.count(),
            "successful_payments": queryset.filter(status="SUCCESS").count(),
            "failed_payments": queryset.filter(status="FAILED").count(),
            "pending_payments": queryset.filter(status="PENDING").count(),
            "total_amount": total_amount,
            "successful_amount": successful_amount,
        })



class PaymentSyncView(generics.CreateAPIView):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        internal_key = request.headers.get("X-Internal-Key")
        expected_key = getattr(settings, "INTERNAL_API_KEY", None)

        if (
            not expected_key
            or not internal_key
            or internal_key != expected_key
        ):
            logger.warning(
                "Payment sync unauthorized request | path=%s",
                request.path,
            )
            return Response({"detail": "Unauthorized"}, status=401)

        user_id = request.data.get("user_id")
        card_id = request.data.get("card_id")
        amount_value = request.data.get("amount")
        category = request.data.get("category", "OTHER")
        status_value = request.data.get("status")
        transaction_id = request.data.get("transaction_id")
        location = request.data.get("location", "")
        device_id = request.data.get("device_id", "")

        if not all([
            user_id,
            card_id,
            amount_value is not None,
            status_value,
            transaction_id,
        ]):
            logger.warning("Payment sync rejected | reason=missing_required_data")
            return Response(
                {"detail": "Missing required payment data."},
                status=400,
            )

        if status_value not in {"SUCCESS", "FAILED", "PENDING"}:
            logger.warning("Payment sync rejected | reason=invalid_status")
            return Response(
                {"detail": "Invalid transaction status."},
                status=400,
            )

        valid_categories = {
            choice[0] for choice in Transaction.CATEGORY_CHOICES
        }

        if category not in valid_categories:
            logger.warning("Payment sync rejected | reason=invalid_category")
            return Response(
                {"detail": "Invalid transaction category."},
                status=400,
            )

        try:
            amount = Decimal(str(amount_value))

            if not amount.is_finite() or amount <= 0:
                logger.warning("Payment sync rejected | reason=invalid_amount")
                return Response(
                    {"detail": "Amount must be a positive number."},
                    status=400,
                )

        except (InvalidOperation, TypeError, ValueError):
            logger.warning("Payment sync rejected | reason=invalid_amount")
            return Response(
                {"detail": "Invalid transaction amount."},
                status=400,
            )

        from django.contrib.auth import get_user_model  # type: ignore

        User = get_user_model()
        user = get_object_or_404(User, id=user_id)
        card = get_object_or_404(Card, id=card_id, user=user)

        transaction, created = Transaction.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                "user": user,
                "card": card,
                "amount": amount,
                "category": category,
                "status": status_value,
                "location": location,
                "device_id": device_id,
            },
        )

        if transaction.status == "FAILED":
            logger.warning(
                "Payment failure recorded | transaction_id=%s | user_id=%s",
                transaction.transaction_id,
                user.id,
            )

        elif transaction.status == "PENDING":
            logger.info(
                "Payment pending | transaction_id=%s | user_id=%s",
                transaction.transaction_id,
                user.id,
            )

        elif transaction.status == "SUCCESS":
            logger.info(
                "Payment successful | transaction_id=%s | user_id=%s",
                transaction.transaction_id,
                user.id,
            )

        if created and transaction.status == "SUCCESS":
            detect_fraud(transaction)

            transaction.refresh_from_db(
                fields=["fraud_status", "fraud_reason"]
            )

            if transaction.fraud_status == "FLAGGED" and user.email:
                send_fraud_alert(transaction)

            send_large_transaction_alert(transaction)
            send_low_credit_alert(transaction)

        return Response({
            "id": transaction.id,
            "transaction_id": transaction.transaction_id,
            "status": transaction.status,
            "category": transaction.category,
            "fraud_status": transaction.fraud_status,
            "fraud_reason": transaction.fraud_reason,
            "created": created,
        })





class MonthlySpendingAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = filter_transactions_by_date(
                Transaction.objects.filter(
                    user=request.user,
                    status="SUCCESS",
                ),
                request,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        monthly = (
            queryset
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                total_spending=Sum("amount"),
                transaction_count=Count("id"),
            )
            .order_by("month")
        )

        return Response([
            {
                "month": row["month"].strftime("%Y-%m"),
                "total_spending": row["total_spending"],
                "transaction_count": row["transaction_count"],
            }
            for row in monthly
        ])


class CategorySpendingAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            queryset = filter_transactions_by_date(
                Transaction.objects.filter(
                    user=request.user,
                    status="SUCCESS",
                ),
                request,
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        results = (
            queryset
            .values("category")
            .annotate(
                total_spending=Sum("amount"),
                transaction_count=Count("id"),
            )
            .order_by("-total_spending")
        )

        return Response(list(results))


class CreditUtilizationAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cards = Card.objects.filter(user=request.user).order_by("id")

        spending_by_card = (
            Transaction.objects.filter(
                user=request.user,
                status="SUCCESS",
            )
            .values("card_id")
            .annotate(total=Sum("amount"))
        )

        spending_lookup = {
            row["card_id"]: row["total"] or Decimal("0")
            for row in spending_by_card
        }

        results = []

        for card in cards:
            limit = card.credit_limit

            if limit is None or limit <= 0:
                continue

            spending = spending_lookup.get(
                card.id,
                Decimal("0"),
            )

            results.append({
                "card_id": card.id,
                "masked_card_number": card.masked_card_number,
                "credit_limit": limit,
                "total_successful_spending": spending,
                "utilization_percentage": min(
                    Decimal("100"),
                    round(
                        spending / limit * Decimal("100"),
                        2,
                    ),
                ),
            })

        return Response(results)


class AnalyticsCSVExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            transactions = filter_transactions_by_date(
                Transaction.objects.filter(
                    user=request.user,
                    status="SUCCESS",
                ),
                request,
            ).order_by("created_at")
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            'attachment; filename="my_spending_analytics.csv"'
        )

        writer = csv.writer(response)
        writer.writerow([
            "Month",
            "Category",
            "Transaction ID",
            "Amount",
            "Status",
        ])

        for transaction in transactions.iterator():
            writer.writerow([
                transaction.created_at.strftime("%Y-%m"),
                transaction.category,
                transaction.transaction_id,
                transaction.amount,
                transaction.status,
            ])

        return response


class AnalyticsPDFExportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            transactions = list(
                filter_transactions_by_date(
                    Transaction.objects.filter(
                        user=request.user,
                        status="SUCCESS",
                    ),
                    request,
                )
                .select_related("card")
                .order_by("-created_at")
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)

        total_spending = sum(
            (transaction.amount for transaction in transactions),
            Decimal("0"),
        )

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
        )

        styles = getSampleStyleSheet()

        story = [
            Paragraph("Spending Analytics Summary", styles["Title"]),
            Paragraph(
                f"Customer: {request.user.username}",
                styles["Normal"],
            ),
            Paragraph(
                f"Total successful spending: Rs. {total_spending:,.2f}",
                styles["Heading2"],
            ),
            Spacer(1, 12),
        ]

        rows = [
            ["Date", "Transaction ID", "Category", "Amount"]
        ]

        for transaction in transactions:
            rows.append([
                transaction.created_at.strftime("%d-%m-%Y"),
                transaction.transaction_id,
                transaction.category,
                f"Rs. {transaction.amount:,.2f}",
            ])

        table = Table(rows, repeatRows=1)

        table.setStyle(TableStyle([
            (
                "BACKGROUND",
                (0, 0),
                (-1, 0),
                colors.HexColor("#1e293b"),
            ),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))

        story.append(table)
        document.build(story)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/pdf",
        )

        response["Content-Disposition"] = (
            'attachment; filename="my_spending_analytics.pdf"'
        )

        return response


class MonthlyStatementPDFView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            year = int(request.query_params.get("year"))
            month = int(request.query_params.get("month"))
        except (TypeError, ValueError):
            return Response(
                {"detail": "Year and month are required."},
                status=400,
            )

        if month < 1 or month > 12:
            return Response(
                {"detail": "Month must be between 1 and 12."},
                status=400,
            )

        try:
            start_date = datetime(year, month, 1)
            last_day = monthrange(year, month)[1]
            end_date = datetime(year, month, last_day, 23, 59, 59)
        except ValueError:
            return Response(
                {"detail": "Invalid year or month."},
                status=400,
            )

        start_date = timezone.make_aware(start_date)
        end_date = timezone.make_aware(end_date)

        transactions = list(
            Transaction.objects.filter(
                user=request.user,
                created_at__gte=start_date,
                created_at__lte=end_date,
                status="SUCCESS",
            ).select_related("card").order_by("created_at")
        )

        total_spending = sum(
            (transaction.amount for transaction in transactions),
            Decimal("0"),
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
            "StatementTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=20,
            spaceAfter=8,
        )
        right_style = ParagraphStyle(
            "Right",
            parent=styles["Normal"],
            alignment=TA_RIGHT,
        )

        story = [
            Paragraph("Credit Card Payment System", title_style),
            Paragraph(
                f"Monthly Statement - {month:02d}/{year}",
                styles["Heading2"],
            ),
            Spacer(1, 8),
            Paragraph(
                f"<b>Customer:</b> {request.user.username}",
                styles["Normal"],
            ),
            Paragraph(
                f"<b>Email:</b> {request.user.email}",
                styles["Normal"],
            ),
            Spacer(1, 8),
        ]

        card_numbers = sorted({
            transaction.card.masked_card_number
            for transaction in transactions
        })
        card_text = (
            ", ".join(card_numbers) if card_numbers else "No transactions"
        )

        story.extend([
            Paragraph(f"<b>Card:</b> {card_text}", styles["Normal"]),
            Spacer(1, 12),
        ])

        summary_data = [
            ["Statement Month", f"{month:02d}/{year}"],
            ["Successful Transactions", str(len(transactions))],
            ["Total Spending", f"Rs. {total_spending:,.2f}"],
        ]

        summary_table = Table(summary_data, colWidths=[65 * mm, 65 * mm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.whitesmoke),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("PADDING", (0, 0), (-1, -1), 7),
        ]))

        story.extend([summary_table, Spacer(1, 15)])

        transaction_data = [[
            "Date", "Transaction ID", "Card", "Category", "Amount", "Status"
        ]]

        for transaction in transactions:
            transaction_data.append([
                transaction.created_at.strftime("%d-%m-%Y"),
                transaction.transaction_id,
                transaction.card.masked_card_number,
                transaction.category,
                f"Rs. {transaction.amount:,.2f}",
                transaction.status,
            ])

        if len(transaction_data) == 1:
            transaction_data.append([
                "-", "No transactions", "-", "-", "Rs. 0.00", "-"
            ])

        transaction_table = Table(
            transaction_data,
            repeatRows=1,
            colWidths=[
                22 * mm, 38 * mm, 30 * mm, 30 * mm, 28 * mm, 18 * mm
            ],
        )
        transaction_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (4, 1), (4, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))

        story.extend([
            transaction_table,
            Spacer(1, 15),
            Paragraph(
                f"<b>Total Monthly Spending: Rs. {total_spending:,.2f}</b>",
                right_style,
            ),
            Spacer(1, 20),
            Paragraph(
                "This statement contains successful transactions "
                "recorded during the selected month.",
                styles["Normal"],
            ),
        ])

        document.build(story)
        buffer.seek(0)

        response = HttpResponse(
            buffer.getvalue(),
            content_type="application/pdf",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="monthly_statement_{year}_{month:02d}.pdf"'
        )
        return response


class AdminCardActivityView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [CanViewAdminTransactionData]
    pagination_class = TransactionPagination

    def get_queryset(self):
        card_id = self.kwargs["card_id"]
        return Transaction.objects.filter(
            card_id=card_id
        ).select_related(
            "user", "card"
        ).order_by("-created_at")


class AdminFraudReviewView(generics.GenericAPIView):
    permission_classes = [IsAdminRole]

    def post(self, request, pk):
        transaction = get_object_or_404(Transaction, pk=pk)

        if transaction.fraud_status != "FLAGGED":
            return Response(
                {
                    "detail": (
                        "Only flagged transactions can be marked as reviewed."
                    )
                },
                status=400,
            )

        transaction.fraud_status = "REVIEWED"
        transaction.reviewed_at = timezone.now()
        transaction.save(update_fields=["fraud_status", "reviewed_at"])

        AuditLog.objects.create(
            actor=request.user,
            action="FRAUD_TRANSACTION_REVIEWED",
            target_type="Transaction",
            target_id=str(transaction.pk),
            details={
                "transaction_id": transaction.transaction_id,
                "fraud_reason": transaction.fraud_reason,
                "new_fraud_status": transaction.fraud_status,
            },
            ip_address=get_client_ip(request),
        )

        return Response({
            "detail": "Fraud transaction marked as reviewed.",
            "transaction_id": transaction.transaction_id,
            "fraud_status": transaction.fraud_status,
            "reviewed_at": transaction.reviewed_at,
        })