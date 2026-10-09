
from django.contrib.auth.models import AbstractUser # type: ignore
from django.conf import settings # type: ignore
from django.db import models # type: ignore


class User(AbstractUser):
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username


class Role(models.Model):
    name = models.CharField(max_length=30, unique=True)
    description = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_role",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        related_name="assigned_users",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
    )
    action = models.CharField(max_length=100)
    target_type = models.CharField(max_length=50)
    target_id = models.CharField(max_length=100, blank=True)
    details = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} - {self.created_at}"