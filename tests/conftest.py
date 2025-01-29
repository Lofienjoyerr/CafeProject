import pytest
from rest_framework.test import APIClient


@pytest.fixture(scope="function", name='client')
def api_client() -> APIClient:
    return APIClient()
