from rest_framework import generics # type: ignore
from rest_framework.permissions import IsAdminUser # type: ignore
from rest_framework.serializers import ModelSerializer # type: ignore

from .models import AdminLog


class AdminLogSerializer(ModelSerializer):
    class Meta:
        model = AdminLog
        fields = [
            'id',
            'admin',
            'action',
            'description',
            'created_at',
        ]


class AdminLogListView(generics.ListAPIView):
    serializer_class = AdminLogSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return AdminLog.objects.select_related(
            'admin'
        ).order_by('-created_at')

