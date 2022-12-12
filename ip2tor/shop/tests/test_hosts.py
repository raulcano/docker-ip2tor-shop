from rest_framework import status
from model_bakery import baker
from shop.models import Host
import pytest


@pytest.mark.django_db
class TestRetrieveHost():
    def test_if_user_is_anonymous_returns_200(self, api_client):
        response = api_client.get('/api/v1/public/hosts/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_only_host_that_is_enabled_and_alive(self, api_client):
        hostEnabledAlive = baker.make(Host, is_enabled=True, is_alive=True)
        hostEnabledNotAlive = baker.make(Host, is_enabled=True, is_alive=False)
        hostNotEnabledAlive = baker.make(Host, is_enabled=False, is_alive=True)
        hostNotEnabledNotAlive = baker.make(Host, is_enabled=False, is_alive=False)
        
        response = api_client.get('/api/v1/public/hosts/')
        print(response.data)

        assert False

    # Test retrieve a single Host by ID
    def test_if_host_exists_returns_200(self, api_client):
        assert True