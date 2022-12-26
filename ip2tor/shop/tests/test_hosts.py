import pytest
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from shop.models import Host
from shop.tasks import host_alive_check
from shop.utils import remove_utc_offset_string_from_time_isoformat


# @pytest.mark.skip
@pytest.mark.django_db
class TestRetrieveHosts ():
    def test_if_user_is_anonymous_returns_200(self, api_client):
        response = api_client.get('/api/v1/public/hosts/')
        assert response.status_code == status.HTTP_200_OK

    def test_list_only_host_that_is_enabled_and_alive(self, api_client):
        hostEnabledAlive = baker.make(Host, is_enabled=True, is_alive=True, name="hostEA")
        hostEnabledNotAlive = baker.make(Host, is_enabled=True, is_alive=False, name="hostENA")
        hostNotEnabledAlive = baker.make(Host, is_enabled=False, is_alive=True, name="hostNEA")
        hostNotEnabledNotAlive = baker.make(Host, is_enabled=False, is_alive=False, name="hostNENA")
        
        response = api_client.get('/api/v1/public/hosts/')
        assert len(response.data) == 1
        assert response.data[0]['name'] == hostEnabledAlive.name

    def test_retrieve_single_host_enabled_and_alive_returns_200(self, api_client):
        host = baker.make(Host, is_enabled=True, is_alive=True,)
        response = api_client.get(f'/api/v1/public/hosts/{host.id}/')
        print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == str(host.id)
        assert response.data['site'] == host.site.domain
        assert response.data['created_at'] == remove_utc_offset_string_from_time_isoformat(host.created_at.isoformat("T", "seconds")) + 'Z'
        assert response.data['modified_at'] == remove_utc_offset_string_from_time_isoformat(host.modified_at.isoformat("T", "seconds")) + 'Z'
        assert response.data['ip'] == host.ip
        assert response.data['is_enabled'] == host.is_enabled
        assert response.data['is_alive'] == host.is_alive
        assert response.data['name'] == host.name
        assert response.data['is_testnet'] == host.is_testnet
        assert response.data['offers_tor_bridges'] == host.offers_tor_bridges
        assert response.data['tor_bridge_duration'] == host.tor_bridge_duration
        assert response.data['tor_bridge_price_initial'] == host.tor_bridge_price_initial
        assert response.data['tor_bridge_price_extension'] == host.tor_bridge_price_extension
        assert response.data['offers_rssh_tunnels'] == host.offers_rssh_tunnels
        assert response.data['rssh_tunnel_price'] == host.rssh_tunnel_price
        assert response.data['terms_of_service'] == host.terms_of_service
        assert response.data['terms_of_service_url'] == host.terms_of_service_url
        assert response.data['ci_date'] == host.ci_date
        assert response.data['ci_message'] == host.ci_message
        assert response.data['ci_status'] == host.ci_status
        assert response.data['owner'] == host.owner.id

    def test_retrieve_single_host_not_enabled_or_alive_returns_404(self, api_client):
        host1 = baker.make(Host, is_enabled=False, is_alive=True,name="hostNEA")
        host2 = baker.make(Host, is_enabled=True, is_alive=False,name="hostENA")
        host3 = baker.make(Host, is_enabled=False, is_alive=False, name="hostNENA")
        
        response1 = api_client.get(f'/api/v1/public/hosts/{host1.id}/')
        response2 = api_client.get(f'/api/v1/public/hosts/{host2.id}/')
        response3 = api_client.get(f'/api/v1/public/hosts/{host3.id}/')
        assert response1.status_code == status.HTTP_404_NOT_FOUND
        assert response2.status_code == status.HTTP_404_NOT_FOUND
        assert response3.status_code == status.HTTP_404_NOT_FOUND

    
    @pytest.mark.parametrize('is_alive', [False, True])
    @pytest.mark.parametrize('checkin_status', [Host.HELLO, Host.GOODBYE, Host.FAREWELL])
    def test_retrieve_host_data_after_status_checkin(self, api_client, checkin_status, is_alive):
        host = baker.make(Host, is_enabled=True, is_alive=is_alive)
        token = Token.objects.filter(user=host.token_user).first()
        
        response = api_client.get(f'/api/v1/public/hosts/{host.id}/')

        expected_status_code = status.HTTP_404_NOT_FOUND if not is_alive else status.HTTP_200_OK
        assert response.status_code == expected_status_code
        assert host.ci_status == 0
        assert host.ci_date == None
        assert host.ci_message == None


        payload = {
            'ci_message': 'This is a message of a test checkin with status ' + str(checkin_status),
            'ci_status': checkin_status
        }

        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = api_client.post(f'/api/v1/hosts/{host.id}/check_in/', payload)

        # The previous changes the host ci_date, ci_message and ci_status, but not the is_alive field.
        # For that, there is a periodic task that is checking on nodes.
        # We call that task manually to check on this node and update the alive status
        host_alive_check(host.id)

        response = api_client.get(f'/api/v1/public/hosts/{host.id}/')
        expected_status_code = status.HTTP_200_OK if Host.HELLO == checkin_status else status.HTTP_404_NOT_FOUND

        assert response.status_code == expected_status_code
    
        if Host.HELLO == checkin_status:
            assert response.data['id'] == str(host.id)
            assert response.data['ci_message'] == payload['ci_message']
            assert response.data['ci_status'] == payload['ci_status']
        else: 
            assert 'id' not in response.data
            assert 'ci_message' not in response.data
            assert 'ci_status' not in response.data
