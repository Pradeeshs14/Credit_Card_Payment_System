import time

from django.db import connection
from django.db.utils import DatabaseError
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView


class SystemHealthView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        start = time.perf_counter()
        database_status = "healthy"

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
        except DatabaseError:
            database_status = "unhealthy"

        response_time_ms = round(
            (time.perf_counter() - start) * 1000, 2
        )

        overall_status = (
            "healthy" if database_status == "healthy" else "degraded"
        )

        return Response(
            {
                "status": overall_status,
                "database": database_status,
                "response_time_ms": response_time_ms,
            },
            status=200 if overall_status == "healthy" else 503,
        )
