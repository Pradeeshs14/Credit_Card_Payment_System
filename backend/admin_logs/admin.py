from django.contrib import admin # type: ignore

from .models import AdminLog


@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'admin',
        'action',
        'description',
        'created_at',
    )

    list_filter = (
        'action',
        'created_at',
    )

    search_fields = (
        'admin__username',
        'admin__email',
        'description',
    )

    ordering = (
        '-created_at',
    )

