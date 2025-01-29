import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from cafe.models import Item
from tests.factories import EmailAddressAdminFactory, ItemFactory

User = get_user_model()


class TestItems:
    def test_item_list(self, client: APIClient) -> None:
        user = User.objects.first()
        client.force_authenticate(user=user)
        url = reverse('item-list')

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response_data
        assert response_data['results'][0]['id'] == Item.objects.first().id
        assert len(response_data['results']) == 5

    def test_item_retrieve(self, client: APIClient) -> None:
        user = User.objects.first()
        item = Item.objects.first()
        client.force_authenticate(user=user)
        url = reverse('item-detail', args=[item.id])

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['id'] == item.id
        assert response_data['name'] == item.name
        assert response_data['price'] == item.price
        assert len(response_data) == 4

    def test_item_create(self, client: APIClient) -> None:
        user = User.objects.first()
        client.force_authenticate(user=user)
        url = reverse('item-list')

        response = client.post(url, {'name': 'Салат Цезарь', 'price': 350}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert response_data['price'] == 350
        assert len(response_data) == 4

    def test_item_destroy(self, client: APIClient) -> None:
        user = User.objects.first()
        item = Item.objects.last()
        client.force_authenticate(user=user)
        url = reverse('item-detail', args=[item.id])

        response = client.delete(url, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        url = reverse('item-detail', args=[item.id])

        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_item_update(self, client: APIClient) -> None:
        user = User.objects.first()
        item = Item.objects.last()
        client.force_authenticate(user=user)
        url = reverse('item-detail', args=[item.id])
        old_price = item.price

        response = client.patch(url, {'price': old_price + 777}, format='json')
        response_data = response.json()
        item.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['id'] == item.id
        assert old_price + 777 == item.price
        assert len(response_data) == 4

    @pytest.fixture(scope='function', autouse=True, name='setup_admin_db')
    def create_admin_users(self, db) -> None:
        EmailAddressAdminFactory.create_batch(1)

    @pytest.fixture(scope='function', autouse=True, name='setup_db')
    def create_items(self, db) -> None:
        ItemFactory.create_batch(6)
