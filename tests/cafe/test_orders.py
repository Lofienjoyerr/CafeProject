import datetime
from urllib.parse import urlencode

import pytest
from django.urls import reverse
from django.test import override_settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient

from cafe.models import Item, Order
from tests.factories import EmailAddressAdminFactory

User = get_user_model()


class TestOrders:
    @override_settings(CACHES={
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    })
    def test_order_list_filter(self, client: APIClient) -> None:
        user = User.objects.first()
        client.force_authenticate(user=user)
        url = reverse('order-list')
        url = f"{url}?{urlencode({'status': 'PAID'})}"

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response_data
        assert response_data['results'][0]['table_number'] == 6
        assert len(response_data['results']) == 3
        assert len(response_data['results'][0]['items']) == 3
        assert response_data['results'][0]['total_price'] == 1400

    def test_order_list(self, client: APIClient) -> None:
        user = User.objects.first()
        client.force_authenticate(user=user)
        url = reverse('order-list')

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response_data
        assert response_data['results'][0]['table_number'] == 6
        assert len(response_data['results']) == 5
        assert len(response_data['results'][0]['items']) == 3
        assert response_data['results'][0]['total_price'] == 1400

    def test_order_retrieve(self, client: APIClient) -> None:
        user = User.objects.first()
        order = Order.objects.first()
        client.force_authenticate(user=user)
        url = reverse('order-detail', args=[order.id])

        response = client.get(url, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['id'] == order.id
        assert response_data['table_number'] == order.table_number
        assert response_data['total_price'] == order.total_price
        assert len(response_data) == 7

    def test_order_create(self, client: APIClient) -> None:
        user = User.objects.first()
        client.force_authenticate(user=user)
        url = reverse('order-list')

        response = client.post(url, {'table_number': 1, 'items': [Item.objects.first().id]}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_201_CREATED
        assert response_data['table_number'] == 1
        assert len(response_data) == 7
        assert len(response_data['items']) == 1

    def test_order_destroy(self, client: APIClient) -> None:
        user = User.objects.first()
        order = Order.objects.first()
        client.force_authenticate(user=user)
        url = reverse('order-detail', args=[order.id])

        response = client.delete(url, format='json')

        assert response.status_code == status.HTTP_204_NO_CONTENT

        url = reverse('order-detail', args=[order.id])

        response = client.get(url, format='json')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_order_update(self, client: APIClient) -> None:
        user = User.objects.first()
        order = Order.objects.first()
        client.force_authenticate(user=user)
        url = reverse('order-detail', args=[order.id])
        old_number = order.table_number

        response = client.patch(url, {'table_number': old_number + 1}, format='json')
        response_data = response.json()
        order.refresh_from_db()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['id'] == order.id
        assert old_number + 1 == order.table_number
        assert response_data['total_price'] == order.total_price
        assert len(response_data) == 7

    def test_calc_revenue(self, client: APIClient) -> None:
        user = User.objects.first()
        client.force_authenticate(user=user)
        url = reverse('calc_revenue')
        response = client.post(url, {'date': datetime.date.today()}, format='json')
        response_data = response.json()

        assert response.status_code == status.HTTP_200_OK
        assert response_data['revenue'] == 4200
        assert len(response_data) == 1

    @pytest.fixture(scope='function', autouse=True, name='setup_admin_db')
    def create_admin_users(self, db) -> None:
        EmailAddressAdminFactory.create_batch(1)

    # не использую фабрики, тк не получилось состыковать с кастомным менеджером
    # (передача списка items и расчёт total_price)
    @pytest.fixture(scope='function', autouse=True, name='setup_db')
    def create_orders(self, db) -> None:
        Item.objects.bulk_create([
            Item(name='Паста', price=500),
            Item(name='Суп', price=600),
            Item(name='Пиво', price=300),
        ])
        Order.objects.create(table_number=1, items=list(Item.objects.all()))
        Order.objects.create(table_number=2, items=list(Item.objects.all()))
        Order.objects.create(table_number=3, items=list(Item.objects.all()))
        Order.objects.create(table_number=4, items=list(Item.objects.all()), status='PAID')
        Order.objects.create(table_number=5, items=list(Item.objects.all()), status='PAID')
        Order.objects.create(table_number=6, items=list(Item.objects.all()), status='PAID')
