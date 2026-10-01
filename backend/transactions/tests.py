from datetime import date

from django.contrib.auth import get_user_model # type: ignore
from rest_framework import status # type: ignore
from rest_framework.test import APITestCase # type: ignore

from cards.models import Card
from .models import Transaction


User = get_user_model()


class TransactionManagementTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='transactiontest',
            email='transactiontest@example.com',
            password='Test@12345'
        )

        self.admin = User.objects.create_superuser(
            username='transactionadmin',
            email='transactionadmin@example.com',
            password='Admin@12345'
        )

        self.card = Card.objects.create(
            user=self.user,
            card_type='CREDIT',
            masked_card_number='**** **** **** 1111',
            last_four_digits='1111',
            expiry_month=12,
            expiry_year=2030
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.transactions_url = '/api/transactions/'

        self.transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=150.00,
            status='SUCCESS',
            transaction_id='TXN-TEST-0001'
        )

        self.failed_transaction = Transaction.objects.create(
            user=self.user,
            card=self.card,
            amount=500.00,
            status='FAILED',
            transaction_id='TXN-TEST-0002'
        )

    def test_view_transaction_history(self):
        response = self.client.get(
            self.transactions_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    def test_filter_by_status(self):
        response = self.client.get(
            self.transactions_url,
            {'status': 'SUCCESS'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            response.data[0]['status'],
            'SUCCESS'
        )

    def test_filter_by_amount(self):
        response = self.client.get(
            self.transactions_url,
            {'amount': '500'}
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            1
        )

        self.assertEqual(
            float(response.data[0]['amount']),
            500.00
        )

    def test_filter_by_date(self):
        today = date.today().isoformat()

        response = self.client.get(
            self.transactions_url,
            {
                'start_date': today,
                'end_date': today
            }
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            len(response.data),
            2
        )

    def test_create_transaction(self):
        response = self.client.post(
            '/api/transactions/create/',
            {
                'card': self.card.id,
                'amount': 250.00,
                'status': 'PENDING'
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            response.data['transaction_id'].startswith('TXN-')
        )

        self.assertEqual(
            response.data['status'],
            'PENDING'
        )

    def test_admin_csv_export(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            '/api/transactions/export-csv/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response['Content-Type'],
            'text/csv'
        )

        content = response.content.decode()

        self.assertIn(
            'Transaction ID',
            content
        )

        self.assertIn(
            'TXN-TEST-0001',
            content
        )

        self.assertIn(
            '**** **** **** 1111',
            content
        )

        self.assertNotIn(
            '4111111111111111',
            content
        )

    def test_admin_payment_summary(self):
        self.client.force_authenticate(
            user=self.admin
        )

        response = self.client.get(
            '/api/transactions/admin/summary/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['total_payments'],
            2
        )

        self.assertEqual(
            response.data['successful_payments'],
            1
        )

        self.assertEqual(
            response.data['failed_payments'],
            1
        )

        self.assertEqual(
            float(response.data['total_amount']),
            650.00
        )

        self.assertEqual(
            float(response.data['successful_amount']),
            150.00
        )

