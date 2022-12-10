from rest_framework.test import APIClient
from rest_framework import status

class TestRetrieveHost():
    def test_if_user_is_anonymous_returns_200(self):
        client = APIClient()

        response = client.get('/api/v1/public/hosts/')

        assert response.status_code == status.HTTP_200_OK