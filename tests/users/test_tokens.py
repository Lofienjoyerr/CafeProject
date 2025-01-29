import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories import EmailAddressPasswordFactory

User = get_user_model()


class TestTokens:
    def test_login_passed(self, client: APIClient) -> None:
        user = User.objects.first()
        url = reverse('token_obtain_pair')

        response = client.post(url, {'login': user.email, 'password': 'asd'}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'refresh' in response_data and 'access' in response_data
        assert len(response_data) == 2

        user.phone = '+79615987654'
        user.save()
        response = client.post(url, {'login': user.phone, 'password': 'asd'}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'refresh' in response_data and 'access' in response_data
        assert len(response_data) == 2

    def test_login_failed(self, client: APIClient) -> None:
        user = User.objects.first()
        url = reverse('token_obtain_pair')

        response = client.post(url, {'login': user.email, 'password': 'asd', 'zxc': "zxc"}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'refresh' in response_data and 'access' in response_data
        assert len(response_data) == 2

        response = client.post(url, {'email': user.email, 'password': 'asd'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(url, {'zxc': 'zxc', 'password': 'asd'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

        response = client.post(url, {'login': 'a' + user.email, 'password': 'asd'}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_passed(self, client: APIClient) -> None:
        user = User.objects.first()
        url = reverse('token_obtain_pair')
        response = client.post(url, {'login': user.email, 'password': 'asd'}, format='json')
        response_data = response.json()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + response_data['access'])
        url = reverse('token_verify')

        response = client.post(url, format='json')
        response_data = response.json()
        user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert all([response_data[key] == user.__dict__[key] for key in response_data.keys() if
                    key not in ['avatar', 'date_joined', 'last_login']])

    def test_logout_passed(self, client: APIClient) -> None:
        user = User.objects.first()
        url = reverse('token_obtain_pair')
        response = client.post(url, {'login': user.email, 'password': 'asd'}, format='json')
        response_data = response.json()
        url = reverse('token_blacklist')

        response = client.post(url, {'refresh': response_data['refresh']}, format='json')

        assert response.status_code == status.HTTP_200_OK
        assert not len(response.json())

        url = reverse('token_refresh')

        response = client.post(url, {'refresh': response_data['refresh']}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data['code'] == 'token_not_valid'

    def test_logout_failed(self, client: APIClient) -> None:
        user = User.objects.first()
        url = reverse('token_obtain_pair')
        response = client.post(url, {'login': user.email, 'password': 'asd'}, format='json')
        response_data = response.json()
        url = reverse('token_blacklist')

        response = client.post(url, {'refresh': response_data['refresh'] + 'a'}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response_data['code'] == 'token_not_valid'

    @pytest.fixture(scope='function', autouse=True, name='setup_db')
    def create_regular_users(self, db) -> None:
        EmailAddressPasswordFactory.create_batch(2)
