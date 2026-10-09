
from django.contrib import admin # type: ignore
from .models import User, Role, UserRole, AuditLog

admin.site.register(User)
admin.site.register(Role)
admin.site.register(UserRole)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "actor",
        "action",
        "target_type",
        "target_id",
        "created_at",
    )
    list_filter = ("action", "target_type", "created_at")
    search_fields = ("actor__username", "action", "target_id")
    readonly_fields = (
        "actor",
        "action",
        "target_type",
        "target_id",
        "details",
        "ip_address",
        "created_at",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False