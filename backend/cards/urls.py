from django.urls import path # type: ignore

from .views import (
    CardListCreateView,
    CardDeleteView,
    AdminCardBlockView,
    AdminCardListView,
    AdminCreditLimitUpdateView,
)


urlpatterns = [
    path(
        '',
        CardListCreateView.as_view(),
        name='card-list-create'
    ),
    path(
        '<int:pk>/',
        CardDeleteView.as_view(),
        name='card-delete'
    ),
    path(
        '<int:pk>/block/',
        AdminCardBlockView.as_view(),
        name='admin-card-block'
    ),
    path(
    'admin/',
    AdminCardListView.as_view(),
    name='admin-card-list'
    ),

    path(
    '<int:pk>/credit-limit/',
    AdminCreditLimitUpdateView.as_view(),
    name='admin-credit-limit-update'
),    
]