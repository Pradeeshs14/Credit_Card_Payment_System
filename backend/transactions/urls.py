from django.urls import path # type: ignore

from .views import (
    TransactionCreateView,
    TransactionListView,
    TransactionCSVExportView,
    AdminPaymentSummaryView,
    PaymentSyncView,
    MonthlyStatementPDFView,
    AdminCardActivityView,
)

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('export-csv/', TransactionCSVExportView.as_view(), name='transaction-export-csv'),
    path('monthly-statement/', MonthlyStatementPDFView.as_view(), name='monthly-statement'),
    path('admin/summary/',AdminPaymentSummaryView.as_view(),name='admin-payment-summary'),
    path('sync/', PaymentSyncView.as_view(), name='payment-sync'),
    path(
    'admin/card/<int:card_id>/activity/',AdminCardActivityView.as_view(),name='admin-card-activity'  
),
]