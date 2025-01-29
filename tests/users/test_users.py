from typing import Dict

import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from tests.factories import EmailAddressFactory, EmailAddressAdminFactory

User = get_user_model()


class TestUsers:
    def test_user_list_as_anon(self, client: APIClient) -> None:
        url = reverse('users-list')

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response_data
        assert User.objects.first().email == response_data['results'][0]['email']
        assert len(response_data['results']) == 5
        assert 'is_staff' not in response_data['results'][0]

    def test_user_list_as_regular(self, client: APIClient, regular_token: Dict[str, str]) -> None:
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + regular_token['access'])
        url = reverse('users-list')

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response_data
        assert User.objects.first().email == response_data['results'][0]['email']
        assert len(response_data['results']) == 5
        assert 'is_staff' not in response_data['results'][0]

    def test_user_list_as_admin(self, client: APIClient, admin_token: Dict[str, str]) -> None:
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + admin_token['access'])
        url = reverse('users-list')

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response_data
        assert User.objects.first().email == response_data['results'][0]['email']
        assert len(response_data['results']) == 5
        assert 'is_staff' in response_data['results'][0]

    def test_get_user_detail_as_anon(self, client: APIClient) -> None:
        target_user = User.objects.filter(is_staff=False).first()
        url = reverse('user-detail', args=[target_user.id])

        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_user_detail_as_regular_foreign(self, client: APIClient) -> None:
        user = User.objects.filter(is_staff=False).last()
        target_user = User.objects.filter(is_staff=False).first()
        client.force_authenticate(user=user)
        url = reverse('user-detail', args=[target_user.id])

        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_get_user_detail_as_regular_owner(self, client: APIClient, regular_token: Dict[str, str]) -> None:
        user = User.objects.filter(is_staff=False).first()
        target_user = user
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + regular_token['access'])
        url = reverse('user-detail', args=[target_user.id])

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert target_user.email == response_data['email']
        assert 'is_staff' not in response_data

    def test_get_user_detail_as_admin(self, client: APIClient, admin_token: Dict[str, str]) -> None:
        target_user = User.objects.filter(is_staff=False).first()
        client.credentials(HTTP_AUTHORIZATION='Bearer ' + admin_token['access'])
        url = reverse('user-detail', args=[target_user.id])

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert target_user.email == response_data['email']
        assert 'is_staff' in response_data

    def test_put_user_detail_as_anon(self, client: APIClient) -> None:
        target_user = User.objects.filter(is_staff=False).first()
        url = reverse('user-detail', args=[target_user.id])

        response = client.put(url, {"phone": "+79618234567"}, format='json')

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_put_user_detail_as_regular_foreign(self, client: APIClient) -> None:
        user = User.objects.filter(is_staff=False).last()
        target_user = User.objects.filter(is_staff=False).first()
        client.force_authenticate(user=user)
        url = reverse('user-detail', args=[target_user.id])

        response = client.put(url, {"phone": "+79618234567"}, format='json')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_user_detail_as_regular_owner(self, client: APIClient) -> None:
        user = User.objects.filter(is_staff=False).first()
        target_user = user
        client.force_authenticate(user=user)
        url = reverse('user-detail', args=[target_user.id])

        old_email = target_user.email
        old_name = target_user.name
        response = client.put(url, {"phone": "+79618234567"}, format='json')
        response_data = response.json()
        target_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert target_user.phone == response_data['phone'] == "+79618234567"
        assert target_user.email == old_email and target_user.name == old_name
        assert 'is_staff' not in response_data and not target_user.is_staff

        response = client.put(url, {"zxc": "zxc", "is_staff": True}, format='json')
        response_data = response.json()
        target_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert target_user.phone == response_data['phone'] == "+79618234567"
        assert target_user.email == old_email and target_user.name == old_name
        assert 'zxc' not in response_data and 'zxc' not in target_user.__dict__
        assert 'is_staff' not in response_data and not target_user.is_staff

        response = client.put(url, {"phone": 'zxc'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_put_user_detail_as_admin(self, client: APIClient) -> None:
        user = User.objects.filter(is_staff=True).first()
        target_user = User.objects.filter(is_staff=False).first()
        client.force_authenticate(user=user)
        url = reverse('user-detail', args=[target_user.id])

        old_email = target_user.email
        old_name = target_user.name
        response = client.put(url, {"phone": "+79618234567"}, format='json')
        response_data = response.json()
        target_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert target_user.phone == response_data['phone'] == "+79618234567"
        assert target_user.email == old_email and target_user.name == old_name
        assert 'is_staff' in response_data and not target_user.is_staff

        response = client.put(url, {"zxc": "zxc", "is_staff": True}, format='json')
        response_data = response.json()
        target_user.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert target_user.phone == response_data['phone'] == "+79618234567"
        assert target_user.email == old_email and target_user.name == old_name
        assert 'zxc' not in response_data and 'zxc' not in target_user.__dict__
        assert 'is_staff' in response_data and target_user.is_staff

        response = client.put(url, {"phone": 'zxc'}, format='json')

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.fixture(scope='function', autouse=True, name='setup_db')
    def create_regular_users(self, db) -> None:
        EmailAddressFactory.create_batch(6)

    @pytest.fixture(scope='function', autouse=True, name='setup_admin_db')
    def create_admin_users(self, db) -> None:
        EmailAddressAdminFactory.create_batch(2)

    @pytest.fixture(scope='function', name='regular_token')
    def login_as_regular(self) -> Dict[str, str]:
        refresh = RefreshToken.for_user(User.objects.filter(is_staff=False).first())
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }

    @pytest.fixture(scope='function', name='admin_token')
    def login_as_admin(self) -> Dict[str, str]:
        refresh = RefreshToken.for_user(User.objects.filter(is_staff=True).first())
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
