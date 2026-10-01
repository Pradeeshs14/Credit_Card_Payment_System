from django.urls import path # type: ignore

from .views import AdminLogListView


urlpatterns = [
    path('', AdminLogListView.as_view(), name='admin-log-list'),
]

