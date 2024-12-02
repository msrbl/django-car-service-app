from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.user_data = {
            'phone': '+79822047803',
            'password': '111',
            'first_name': 'Admin',
            'last_name': 'Admin'
        }

    def test_register_user(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

    def test_login_user(self):
        self.client.post(self.register_url, self.user_data, format='json')
        response = self.client.post(self.login_url, {
            'phone': self.user_data['phone'],
            'password': self.user_data['password']
        }, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_access_protected_route(self):
        self.client.post(self.register_url, self.user_data, format='json')
        login_response = self.client.post(self.login_url, {
            'phone': self.user_data['phone'],
            'password': self.user_data['password']
        }, format='json')
        print(login_response.data) 
        access_token = login_response.data['access']

        protected_url = reverse('user_list')
        response = self.client.get(protected_url, HTTP_AUTHORIZATION=f'Bearer {access_token}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Проверка без токена
        response = self.client.get(protected_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)