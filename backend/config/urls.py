from django.contrib import admin # type: ignore
from django.urls import include, path # type: ignore

from drf_spectacular.views import ( # type: ignore
    SpectacularAPIView,
    SpectacularSwaggerView,
)


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/users/', include('users.urls')),
    path('api/cards/', include('cards.urls')),
    path('api/transactions/', include('transactions.urls')),
    path('api/admin-logs/', include('admin_logs.urls')),

    path(
        'api/schema/',
        SpectacularAPIView.as_view(),
        name='schema',
    ),

    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='schema'
        ),
        name='swagger-ui',
    ),
]

