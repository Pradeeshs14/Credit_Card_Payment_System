from django.contrib.auth import get_user_model # type: ignore
from rest_framework import status # type: ignore
from rest_framework.test import APITestCase # type: ignore


User = get_user_model()


class UserAuthenticationTests(APITestCase):

    def setUp(self):
        self.register_url = '/api/users/register/'
        self.login_url = '/api/users/login/'
        self.me_url = '/api/users/me/'
        self.logout_url = '/api/users/logout/'

        self.user_data = {
            'username': 'testauth',
            'email': 'testauth@example.com',
            'password': 'Test@12345',
        }

    def test_user_registration(self):
        response = self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )

        self.assertTrue(
            User.objects.filter(
                username='testauth'
            ).exists()
        )

    def test_password_is_encrypted(self):
        self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        user = User.objects.get(
            username='testauth'
        )

        self.assertNotEqual(
            user.password,
            'Test@12345'
        )

        self.assertTrue(
            user.check_password('Test@12345')
        )

    def test_user_login_returns_jwt(self):
        self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        response = self.client.post(
            self.login_url,
            {
                'username': 'testauth',
                'password': 'Test@12345',
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertIn(
            'access',
            response.data
        )

        self.assertIn(
            'refresh',
            response.data
        )

    def test_protected_me_endpoint_without_token(self):
        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

    def test_protected_me_endpoint_with_token(self):
        self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        login_response = self.client.post(
            self.login_url,
            {
                'username': 'testauth',
                'password': 'Test@12345',
            },
            format='json'
        )

        access_token = login_response.data['access']

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        response = self.client.get(
            self.me_url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

        self.assertEqual(
            response.data['username'],
            'testauth'
        )

    def test_logout(self):
        self.client.post(
            self.register_url,
            self.user_data,
            format='json'
        )

        login_response = self.client.post(
            self.login_url,
            {
                'username': 'testauth',
                'password': 'Test@12345',
            },
            format='json'
        )

        access_token = login_response.data['access']
        refresh_token = login_response.data['refresh']

        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )

        response = self.client.post(
            self.logout_url,
            {
                'refresh': refresh_token
            },
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )

