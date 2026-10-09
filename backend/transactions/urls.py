from django.urls import path # type: ignore
from .health_views import SystemHealthView
from .views import (
    AdminFraudReviewView,
    TransactionCreateView,
    TransactionListView,
    TransactionCSVExportView,
    AdminPaymentSummaryView,
    PaymentSyncView,
    MonthlyStatementPDFView,
    AdminCardActivityView,
    MonthlySpendingAnalyticsView,
    CategorySpendingAnalyticsView,
    CreditUtilizationAnalyticsView,
    AnalyticsCSVExportView,
    AnalyticsPDFExportView,
)

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),
    path('create/', TransactionCreateView.as_view(), name='transaction-create'),
    path('export-csv/', TransactionCSVExportView.as_view(), name='transaction-export-csv'),
    path('monthly-statement/', MonthlyStatementPDFView.as_view(), name='monthly-statement'),
    path('admin/summary/',AdminPaymentSummaryView.as_view(),name='admin-payment-summary'),
    path('sync/', PaymentSyncView.as_view(), name='payment-sync'),
    path('admin/card/<int:card_id>/activity/',AdminCardActivityView.as_view(),name='admin-card-activity'),
    path('admin/fraud/<int:pk>/review/',AdminFraudReviewView.as_view(), name='admin-fraud-review',),
    path('analytics/monthly-spending/', MonthlySpendingAnalyticsView.as_view(), name='monthly-spending-analytics'),
    path('analytics/category-spending/', CategorySpendingAnalyticsView.as_view(), name='category-spending-analytics'),
    path('analytics/credit-utilization/', CreditUtilizationAnalyticsView.as_view(), name='credit-utilization-analytics'),
    path('analytics/export-csv/', AnalyticsCSVExportView.as_view(), name='analytics-export  -csv'),
    path('analytics/export-pdf/', AnalyticsPDFExportView.as_view(), name='analytics-export-pdf'),
    path('admin/health/', SystemHealthView.as_view(), name='system-health'),
]