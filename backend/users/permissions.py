
from rest_framework.permissions import BasePermission  # type: ignore


def get_user_role(user):
    if not user or not user.is_authenticated:
        return None

    # Preserve existing Django administrator access.
    if user.is_staff or user.is_superuser:
        return "Admin"

    try:
        return user.user_role.role.name
    except Exception:
        return None


class IsAdminRole(BasePermission):
    message = "Admin role required."

    def has_permission(self, request, view):
        return get_user_role(request.user) == "Admin"


class IsAdminOrSupport(BasePermission):
    message = "Admin or Support role required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in {"Admin", "Support"}


class CanViewAllCards(BasePermission):
    message = "An assigned Admin, Support, or Read-Only role is required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in {
            "Admin",
            "Support",
            "Read-Only",
        }


class CanManageOwnCards(BasePermission):
    message = "Authentication is required; Read-Only users cannot modify cards."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return get_user_role(request.user) != "Read-Only"


class CanViewAdminTransactionData(BasePermission):
    message = "Admin, Support, or Read-Only role required."

    def has_permission(self, request, view):
        return get_user_role(request.user) in {
            "Admin",
            "Support",
            "Read-Only",
        }


class CanCreateTransaction(BasePermission):
    message = "Authentication is required; Read-Only users cannot create transactions."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        return get_user_role(request.user) != "Read-Only"