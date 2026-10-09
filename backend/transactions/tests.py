from datetime import date

from django.contrib.auth import get_user_model # type: ignore
from rest_framework import status # type: ignore
from rest_framework.test import APITestCase # type: ignore

from cards.models import Card
from users.models import AuditLog
from .fraud_service import detect_fraud
from .models import Transaction

User = get_user_model()

class TransactionManagementTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
        username="transactiontest",
        email="[transactiontest@example.com](mailto:transactiontest@example.com)",
        password="Test@12345",
)


        self.admin = User.objects.create_superuser(
        username="transactionadmin",
        email="transactionadmin@example.com",
        password="Admin@12345",
    )

        self.card = Card.objects.create(
        user=self.user,
        card_type="CREDIT",
        masked_card_number="**** **** **** 1111",
        last_four_digits="1111",
        expiry_month=12,
        expiry_year=2030,
    )

        self.client.force_authenticate(user=self.user)
        self.transactions_url = "/api/transactions/"

        self.transaction = Transaction.objects.create(
        user=self.user,
        card=self.card,
        amount=150.00,
        status="SUCCESS",
        transaction_id="TXN-TEST-0001",
    )

        self.failed_transaction = Transaction.objects.create(
        user=self.user,
        card=self.card,
        amount=500.00,
        status="FAILED",
        transaction_id="TXN-TEST-0002",
    )

    def get_results(self, response):
        """Return result rows for either paginated or list responses."""
        data = response.data
        if isinstance(data, dict) and "results" in data:
            return data["results"]
        return data

    def test_view_transaction_history(self):
        response = self.client.get(self.transactions_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self.get_results(response)
        self.assertEqual(len(data), 2)

    def test_filter_by_status(self):
        response = self.client.get(
            self.transactions_url,
            {"status": "SUCCESS"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self.get_results(response)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["status"], "SUCCESS")

    def test_filter_by_amount(self):
        response = self.client.get(
            self.transactions_url,
            {"amount": "500"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self.get_results(response)
        self.assertEqual(len(data), 1)
        self.assertEqual(float(data[0]["amount"]), 500.00)

    def test_filter_by_date(self):
        today = date.today().isoformat()

        response = self.client.get(
            self.transactions_url,
            {"start_date": today, "end_date": today},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = self.get_results(response)
        self.assertEqual(len(data), 2)

    def test_create_transaction(self):
        response = self.client.post(
            "/api/transactions/create/",
            {
                "card": self.card.id,
                "amount": 250.00,
                "status": "PENDING",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )
        self.assertTrue(
            response.data["transaction_id"].startswith("TXN-")
        )
        self.assertEqual(response.data["status"], "PENDING")

    def test_admin_csv_export(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get("/api/transactions/export-csv/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "text/csv")

        content = response.content.decode()
        self.assertIn("Transaction ID", content)
        self.assertIn("TXN-TEST-0001", content)
        self.assertIn("**** **** **** 1111", content)
        self.assertNotIn("4111111111111111", content)

    def test_admin_payment_summary(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.get(
            "/api/transactions/admin/summary/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_payments"], 2)
        self.assertEqual(response.data["successful_payments"], 1)
        self.assertEqual(response.data["failed_payments"], 1)
        self.assertEqual(float(response.data["total_amount"]), 650.00)
        self.assertEqual(
            float(response.data["successful_amount"]),
            150.00,
        )

    def test_flags_three_high_value_transactions(self):
        Transaction.objects.filter(user=self.user).delete()

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=60000,
            status="SUCCESS",
            transaction_id="TXN-FRAUD-0001",
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=60000,
            status="SUCCESS",
            transaction_id="TXN-FRAUD-0002",
        )

        third = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=60000,
            status="SUCCESS",
            transaction_id="TXN-FRAUD-0003",
        )

        detect_fraud(third)
        third.refresh_from_db()

        self.assertEqual(third.fraud_status, "FLAGGED")
        self.assertIn("high-value transactions", third.fraud_reason)

    def test_flags_three_rapid_transactions(self):
        Transaction.objects.filter(user=self.user).delete()

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=100,
            status="SUCCESS",
            transaction_id="TXN-RAPID-0001",
        )

        Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=200,
            status="SUCCESS",
            transaction_id="TXN-RAPID-0002",
        )

        third = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=300,
            status="SUCCESS",
            transaction_id="TXN-RAPID-0003",
        )

        detect_fraud(third)
        third.refresh_from_db()

        self.assertEqual(third.fraud_status, "FLAGGED")
        self.assertIn("transactions within", third.fraud_reason)

    def test_admin_can_review_flagged_transaction(self):
        self.transaction.fraud_status = "FLAGGED"
        self.transaction.fraud_reason = "Suspicious transaction pattern"
        self.transaction.save(
            update_fields=["fraud_status", "fraud_reason"]
        )

        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/transactions/admin/fraud/{self.transaction.pk}/review/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.fraud_status, "REVIEWED")
        self.assertIsNotNone(self.transaction.reviewed_at)

        self.assertTrue(
            AuditLog.objects.filter(
                actor=self.admin,
                action="FRAUD_TRANSACTION_REVIEWED",
                target_type="Transaction",
                target_id=str(self.transaction.pk),
            ).exists()
        )

    def test_regular_user_cannot_review_flagged_transaction(self):
        self.transaction.fraud_status = "FLAGGED"
        self.transaction.save(update_fields=["fraud_status"])

        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            f"/api/transactions/admin/fraud/{self.transaction.pk}/review/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.fraud_status, "FLAGGED")
        self.assertIsNone(self.transaction.reviewed_at)

    def test_non_flagged_transaction_cannot_be_reviewed(self):
        self.client.force_authenticate(user=self.admin)

        response = self.client.post(
            f"/api/transactions/admin/fraud/{self.transaction.pk}/review/"
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.transaction.refresh_from_db()
        self.assertEqual(self.transaction.fraud_status, "CLEAR")
        self.assertIsNone(self.transaction.reviewed_at)

    def test_failed_payment_sync_logs_warning(self):
        from django.test import override_settings # type: ignore
        from unittest.mock import patch

        payload = {
            "user_id": self.user.id,
            "card_id": self.card.id,
            "amount": "125.00",
            "category": "OTHER",
            "status": "FAILED",
            "transaction_id": "TXN-FAIL-LOG-TEST",
        }

        with override_settings(INTERNAL_API_KEY="test-secret"):
            with self.assertLogs("system_monitoring", level="WARNING") as logs:
                response = self.client.post(
                    "/api/transactions/sync/",
                    payload,
                    format="json",
                    HTTP_X_INTERNAL_KEY="test-secret",
                )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            any(
                "Payment failure recorded" in message
                and "TXN-FAIL-LOG-TEST" in message
                for message in logs.output
            ),
            logs.output,
        )

