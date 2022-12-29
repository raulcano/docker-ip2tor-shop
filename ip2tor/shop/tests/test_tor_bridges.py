import os
from os.path import abspath, dirname

import pytest
import requests
from charged.lnpurchase.models import PurchaseOrder
from charged.tests.conftest import global_data
from rest_framework import status
from shop.models import Bridge, TorBridge
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
        
    def test_bridge_in_initial_status_wont_redirect_to_target(self, create_purchase_order_via_api, create_node_host_and_owner, global_data):
        _, host, owner = create_node_host_and_owner()
        
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product
        
        assert bridge.status == TorBridge.INITIAL
        
        session = requests.session()
        response = session.get('http://' + str(host.ip) + ':' + str(bridge.port))
        
        assert 'Hello world!' in response.text
        assert response.status_code == status.HTTP_200_OK
        
        
