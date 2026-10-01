from .models import AdminLog


def create_admin_log(admin, action, description):
    return AdminLog.objects.create(
        admin=admin,
        action=action,
        description=description,
    )

