from django.contrib.auth import get_user_model # type: ignore
from rest_framework import status # type: ignore
from rest_framework.test import APITestCase # type: ignore

from .models import Card


User = get_user_model()


class CardManagementTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='cardtest',
            email='cardtest@example.com',
            password='Test@12345'
        )

        self.client.force_authenticate(
            user=self.user
        )

        self.cards_url = '/api/cards/'

        self.card_data = {
            'card_type': 'CREDIT',
            'card_number': '4111111111111111',
            'cvv': '123',
            'expiry_month': 12,
            'expiry_year': 2030,
        }

    def test_add_card(self):
        response = self.client.post(
            self.cards_url,
            self.card_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertEqual(
            response.data['last_four_digits'],
            '1111'
        )

        self.assertEqual(
            response.data['masked_card_number'],
            '**** **** **** 1111'
        )

        self.assertNotIn(
            '4111111111111111',
            str(response.data)
        )

        self.assertNotIn(
            '123',
            str(response.data)
        )

    def test_card_number_is_not_stored(self):
        self.client.post(
            self.cards_url,
            self.card_data,
            format='json'
        )

        card = Card.objects.get(
            user=self.user
        )

        self.assertEqual(
            card.last_four_digits,
            '1111'
        )

        self.assertEqual(
            card.masked_card_number,
            '**** **** **** 1111'
        )

        self.assertFalse(
            hasattr(card, 'card_number')
        )

        self.assertFalse(
            hasattr(card, 'cvv')
        )

    def test_view_saved_cards(self):
        self.client.post(
            self.cards_url,
            self.card_data,
            format='json'
        )

        response = self.client.get(
            self.cards_url
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
            response.data[0]['last_four_digits'],
            '1111'
        )

    def test_delete_card(self):
        create_response = self.client.post(
            self.cards_url,
            self.card_data,
            format='json'
        )

        card_id = create_response.data['id']

        response = self.client.delete(
            f'{self.cards_url}{card_id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT
        )

        self.assertFalse(
            Card.objects.filter(
                id=card_id
            ).exists()
        )

    def test_invalid_card_number(self):
        invalid_data = self.card_data.copy()

        invalid_data['card_number'] = '12345'

        response = self.client.post(
            self.cards_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_invalid_expiry_month(self):
        invalid_data = self.card_data.copy()

        invalid_data['expiry_month'] = 13

        response = self.client.post(
            self.cards_url,
            invalid_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

