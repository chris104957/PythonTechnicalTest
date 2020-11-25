import pytest
from bonds.models import Currency
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture(autouse=True)
def currencies():
    for code in ['EUR', 'USD', 'GBP']:
        Currency.objects.create(code=code)


@pytest.fixture
def client():
    User.objects.create_user('admin', password='test')
    client = APIClient()
    client.login(username='admin', password='test')
    return client


@pytest.fixture
def alt_user_client():
    User.objects.create_user('alt_user', password='test')
    client = APIClient()
    client.login(username='alt_user', password='test')
    return client
