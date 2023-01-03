import os
from datetime import timedelta
from os.path import abspath, dirname

import pytest
import requests
from charged.lnpurchase.models import PurchaseOrder
from charged.tests.conftest import global_data
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from shop.models import Bridge, TorBridge
from shop.tasks import (delete_due_tor_bridges,
                        set_needs_delete_on_initial_tor_bridges,
                        set_needs_delete_on_suspended_tor_bridges,
                        set_needs_suspend_on_expired_tor_bridges)
from shop.utils import remove_utc_offset_string_from_time_isoformat


@pytest.mark.django_db
class TestTorBridges():
    
    def test_sample_hidden_service_is_responding_behind_tor(self, global_data):

        session = requests.session()
        session.proxies = {'http':  'socks5h://localhost:9050',
                        'https': 'socks5h://localhost:9050'}
        
        response = session.get('http://' + global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])

        assert 'Hello world!' in response.text
        assert response.status_code == status.HTTP_200_OK
    
    
    def test_create_purchase_order_for_TorBridge_with_specific_onion_target(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        _, host, owner = create_node_host_and_owner()
        
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        assert response.data['id'] == po.id
        assert response.data['url'].endswith('/api/v1/public/pos/' + str(po.id) + '/')
        
        
        response_po = api_client.get(f'/api/v1/public/pos/{response.data["id"]}/')
        # PO data
        assert po.status == PurchaseOrder.INITIAL
        assert response_po.data['url'].endswith('/api/v1/public/pos/' + str(po.id) + '/')
        assert response_po.data['status'] == po.status
        assert response_po.data['message'] == po.message
        
        bridge = po.item_details.first().product
        assert bridge.status == TorBridge.INITIAL

        # Item details data
        assert response_po.data['item_details'][0]['product_id'] == str(bridge.id)
        assert response_po.data['item_details'][0]['price'] == host.tor_bridge_price_initial
        assert response_po.data['item_details'][0]['quantity'] == 1
        assert response_po.data['item_details'][0]['po'].endswith('/api/v1/public/pos/' + str(po.id) + '/')

        # # Tor bridge data
        assert response_po.data['item_details'][0]['product']['url'].endswith('/api/v1/tor_bridges/' + str(bridge.id) + '/')
        assert response_po.data['item_details'][0]['product']['id'] == str(bridge.id)
        assert response_po.data['item_details'][0]['product']['comment'] == bridge.comment
        assert response_po.data['item_details'][0]['product']['status'] == bridge.status
        assert response_po.data['item_details'][0]['product']['host']['name'] == host.name
        assert response_po.data['item_details'][0]['product']['port'] == bridge.port
        assert response_po.data['item_details'][0]['product']['target'] == bridge.target
        assert response_po.data['item_details'][0]['product']['suspend_after'] == remove_utc_offset_string_from_time_isoformat(bridge.suspend_after.isoformat("T", "seconds")) + 'Z'
        
    def test_authorized_access_to_tor_bridge_page_is_accepted(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        _, host, owner = create_node_host_and_owner()
        token = Token.objects.filter(user=host.token_user).first()

        # create a bridge with the PO
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product

        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = api_client.get(f'/api/v1/tor_bridges/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        response = api_client.get(f'/api/v1/tor_bridges/?host=' + str(host.id))
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        
        response = api_client.get(f'/api/v1/tor_bridges/{str(bridge.id)}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['url'].endswith('/api/v1/tor_bridges/' + str(bridge.id) + '/')
        assert response.data['id'] == str(bridge.id)
        assert response.data['comment'] == bridge.comment
        assert response.data['status'] == bridge.status
        assert response.data['host']['name'] == host.name
        assert response.data['port'] == bridge.port
        assert response.data['target'] == bridge.target
        assert response.data['suspend_after'] == remove_utc_offset_string_from_time_isoformat(bridge.suspend_after.isoformat("T", "seconds")) + 'Z'

    def test_unauthorized_access_to_tor_bridge_page_is_rejected(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        _, host, owner = create_node_host_and_owner()

        invalid_token = '4bcdc4948e4a741291e038fecc0efc7dbb205df7'


        # create a bridge with the PO
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product

        api_client.credentials(HTTP_AUTHORIZATION='Token ' + invalid_token)

        response = api_client.get(f'/api/v1/tor_bridges/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
        response = api_client.get(f'/api/v1/tor_bridges/?host=' + str(host.id))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        response = api_client.get(f'/api/v1/tor_bridges/{str(bridge.id)}/')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        
    @pytest.mark.parametrize('bridge_status', [TorBridge.NEEDS_ACTIVATE, TorBridge.NEEDS_SUSPEND])
    def test_list_and_patch_tor_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client, bridge_status):
        
        _, host, owner = create_node_host_and_owner()
        token = Token.objects.filter(user=host.token_user).first()
        
        # create a bridge with the PO
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge1 = po.item_details.first().product

        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge2 = po.item_details.first().product

        api_client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        response = api_client.get(f'/api/v1/tor_bridges/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        response = api_client.get(f'/api/v1/tor_bridges/?host=' + str(host.id) + '&status=' + TorBridge.INITIAL )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        payload = { 'status': bridge_status}
        api_client.patch(f'/api/v1/tor_bridges/{str(bridge1.id)}/', payload)


        response = api_client.get(f'/api/v1/tor_bridges/?host=' + str(host.id) + '&status=' + TorBridge.INITIAL )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

        response = api_client.get(f'/api/v1/tor_bridges/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

        response = api_client.get(f'/api/v1/tor_bridges/?host=' + str(host.id) + '&status=' +  bridge_status)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['id'] == str(bridge1.id)

    def test_extend_tor_bridge_produces_purchase_order_with_extension_price(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        
        _, host, owner = create_node_host_and_owner()
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product


        response = api_client.post(f'/api/v1/public/tor_bridges/{str(bridge.id)}/extend/')
        po_ext = PurchaseOrder.objects.get(pk=response.data['po_id'])
        assert response.status_code == status.HTTP_200_OK
        assert int(host.tor_bridge_price_extension) == int(po_ext.total_price_msat)
    
    @pytest.mark.parametrize('bridge_status', [TorBridge.ACTIVE, TorBridge.SUSPENDED, TorBridge.NEEDS_SUSPEND])
    def test_extend_not_expired_tor_bridge_after_successful_payment_extends_bridge_deadline(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client, lninvoice_paid_handler_mockup, bridge_status):
        
        _, host, owner = create_node_host_and_owner()
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product

        original_deadline = bridge.suspend_after
        bridge.status = bridge_status
        bridge.save()

        response = api_client.post(f'/api/v1/public/tor_bridges/{str(bridge.id)}/extend/')
        po_ext = PurchaseOrder.objects.get(pk=response.data['po_id'])

        # simulate the payment
        bridge = lninvoice_paid_handler_mockup("TestSender", po.item_details.first())

        assert response.status_code == status.HTTP_200_OK
        assert str(bridge.suspend_after) == str(original_deadline + timedelta(seconds=host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME'))) 

    @pytest.mark.parametrize('bridge_status', [TorBridge.ACTIVE, TorBridge.SUSPENDED, TorBridge.NEEDS_SUSPEND])
    def test_extend_expired_tor_bridge_after_successful_payment_extends_bridge_deadline(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client, lninvoice_paid_handler_mockup, bridge_status):
        
        _, host, owner = create_node_host_and_owner()
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product

        bridge.status = bridge_status
        bridge.suspend_after = timezone.now() - timedelta(seconds=172800) # set to expired 2 days ago

        bridge.save()

        response = api_client.post(f'/api/v1/public/tor_bridges/{str(bridge.id)}/extend/')
        po_ext = PurchaseOrder.objects.get(pk=response.data['po_id'])

        # simulate the payment
        bridge = lninvoice_paid_handler_mockup("TestSender", po.item_details.first())

        assert response.status_code == status.HTTP_200_OK
        assert str(bridge.suspend_after) >= str(timezone.now() + timedelta(seconds=host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME')) - timedelta(seconds=1))       
        assert str(bridge.suspend_after) <= str(timezone.now() + timedelta(seconds=host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME')))       
    
    def test_status_change_from_active_to_needs_suspend_on_expired_tor_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        
        _, host, owner = create_node_host_and_owner()
        
        # create 2 bridges
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge1 = po.item_details.first().product

        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge2 = po.item_details.first().product

        # We set them as active
        bridge1.status = TorBridge.ACTIVE
        bridge1.save()
        bridge2.status = TorBridge.ACTIVE
        bridge2.save()
        
        
        # We'll set bridge2 to expire
        bridge2.suspend_after = timezone.now() - timedelta(seconds=1)
        bridge2.save()

        # We run the task to suspend expired bridges
        set_needs_suspend_on_expired_tor_bridges()
        assert bridge1.status == TorBridge.ACTIVE
        assert bridge2.status == TorBridge.NEEDS_SUSPEND


    def test_status_change_to_needs_delete_on_suspended_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        # set_needs_delete_on_suspended_tor_bridges()
        pass

    def test_status_change_to_needs_delete_on_initial_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        # set_needs_delete_on_initial_tor_bridges()
        pass

    def test_delete_due_tor_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        # delete_due_tor_bridges()
        pass

    # not sure how to test this
    @pytest.mark.skip
    def test_bridge_in_initial_status_wont_redirect_to_target(self, create_purchase_order_via_api, create_node_host_and_owner, global_data):
        _, host, owner = create_node_host_and_owner()
        
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product
        
        assert bridge.status == TorBridge.INITIAL
        
        session = requests.session()
        response = session.get('http://' + str(host.ip) + ':' + str(bridge.port))
        
        assert 'Hello world!' not in response.text
        assert response.status_code == status.HTTP_200_OK
        

        
