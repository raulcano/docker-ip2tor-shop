from rest_framework import status
from model_bakery import baker
from shop.models import Host
import pytest


@pytest.mark.django_db
class TestRetrieveHosts ():
    def test_if_user_is_anonymous_returns_200(self, api_client):
        response = api_client.get('/api/v1/public/hosts/')
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_only_host_that_is_enabled_and_alive(self, api_client):
        hostEnabledAlive = baker.make(Host, is_enabled=True, is_alive=True, name="hostEA")
        hostEnabledNotAlive = baker.make(Host, is_enabled=True, is_alive=False, name="hostENA")
        hostNotEnabledAlive = baker.make(Host, is_enabled=False, is_alive=True, name="hostNEA")
        hostNotEnabledNotAlive = baker.make(Host, is_enabled=False, is_alive=False, name="hostNENA")
        
        response = api_client.get('/api/v1/public/hosts/')
        assert len(response.data) == 1
        assert response.data[0]['name'] == hostEnabledAlive.name