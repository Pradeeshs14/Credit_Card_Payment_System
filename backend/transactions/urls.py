from django.urls import path

from .views import (
    TransactionCreateView,
    TransactionListView,
    TransactionCSVExportView,
    AdminPaymentSummaryView,
    PaymentSyncView,
)

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('export-csv/', TransactionCSVExportView.as_view(), name='transaction-export-csv'),
    path('admin/summary/',AdminPaymentSummaryView.as_view(),name='admin-payment-summary'),
    path('sync/', PaymentSyncView.as_view(), name='payment-sync'),
]