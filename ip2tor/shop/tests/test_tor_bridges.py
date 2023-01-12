import datetime
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
from freezegun import freeze_time
from model_bakery import baker
from rest_framework import status
from rest_framework.authtoken.models import Token
from shop.models import Bridge, TorBridge
from shop.signals import lninvoice_paid_handler
from shop.tasks import (delete_due_tor_bridges,
                        set_needs_delete_on_initial_tor_bridges,
                        set_needs_delete_on_suspended_tor_bridges,
                        set_needs_suspend_on_expired_tor_bridges)
from shop.utils import remove_utc_offset_string_from_time_isoformat


@freeze_time("2023-01-14 12:00:01", tz_offset=0)
def test_fake_datetime():
    assert timezone.now() == datetime.datetime(2023, 1, 14, 12, 0, 1, tzinfo=datetime.timezone.utc)

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
    def test_extend_not_expired_tor_bridge_after_successful_payment_extends_bridge_deadline(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client, bridge_status):
        
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
        lninvoice_paid_handler("TestSender", po.item_details.first())

        # Not sure why I need to reload the item, but if I don't do this, the data won't be persisted in the object
        bridge = TorBridge.objects.get(pk=bridge.id)

        assert response.status_code == status.HTTP_200_OK
        assert str(bridge.suspend_after) == str(original_deadline + timedelta(seconds=host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME'))) 

    @freeze_time("2023-01-05 09:00:01", tz_offset=0)
    @pytest.mark.parametrize('bridge_status', [TorBridge.ACTIVE, TorBridge.SUSPENDED, TorBridge.NEEDS_SUSPEND])
    def test_extend_expired_tor_bridge_after_successful_payment_extends_bridge_deadline(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client, bridge_status):
        
        _, host, owner = create_node_host_and_owner()
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge = po.item_details.first().product

        bridge.status = bridge_status
        bridge.suspend_after = timezone.now() - timedelta(seconds=1) # set to expired 1 second ago

        bridge.save()

        response = api_client.post(f'/api/v1/public/tor_bridges/{str(bridge.id)}/extend/')
        po_ext = PurchaseOrder.objects.get(pk=response.data['po_id'])

        # simulate the payment
        lninvoice_paid_handler("TestSender", po.item_details.first())

        # Not sure why I need to reload the item, but if I don't do this, the data won't be persisted in the object
        bridge = TorBridge.objects.get(pk=bridge.id)

        assert response.status_code == status.HTTP_200_OK
        assert str(bridge.suspend_after) == str(timezone.now() + timedelta(seconds=host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME')))       
    
    
    def test_status_change_from_active_to_needs_suspend_on_expired_tor_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data):
        
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
        bridge2.suspend_after = timezone.now() - timedelta(seconds=100000)
        bridge2.save()

        # We run the task to suspend expired bridges
        print(set_needs_suspend_on_expired_tor_bridges())

        # Not sure why I need to reload the item, but if I don't do this, the data won't be persisted in the object
        bridge2 = TorBridge.objects.get(pk=bridge2.id)

        assert bridge1.status == TorBridge.ACTIVE
        assert bridge2.status == TorBridge.NEEDS_SUSPEND

    def test_status_change_to_needs_delete_on_suspended_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data):
        _, host, owner = create_node_host_and_owner()
        
        # create 2 bridges
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge1 = po.item_details.first().product

        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge2 = po.item_details.first().product

        # We set them as suspended
        bridge1.status = TorBridge.SUSPENDED
        bridge1.save()
        
        # We'll set bridge2 modified_at date to a long enough TO BE DELETED
        # we need to freeze time in the past we want to test, because save() will set "modified_at" with the now()
        freezer = freeze_time(timezone.now() - timedelta(days=getattr(settings, 'DELETE_SUSPENDED_AFTER_THESE_DAYS'))) 
        freezer.start()
        bridge2.status = TorBridge.SUSPENDED
        bridge2.save()
        freezer.stop()

        # We run the task to set needs delete on suspended bridges
        print(set_needs_delete_on_suspended_tor_bridges())

        # Not sure why I need to reload the item, but if I don't do this, the data won't be persisted in the object
        bridge2 = TorBridge.objects.get(pk=bridge2.id)

        assert bridge1.status == TorBridge.SUSPENDED
        assert bridge2.status == TorBridge.NEEDS_DELETE

    def test_status_change_to_needs_delete_on_initial_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data):
        _, host, owner = create_node_host_and_owner()
        
        # create 2 bridges
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge1 = po.item_details.first().product

        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge2 = po.item_details.first().product
        
        # We'll set bridge2 modified_at date to a long enough TO BE DELETED
        freezer = freeze_time(timezone.now() - timedelta(minutes=getattr(settings, 'DELETE_INITIAL_AFTER_THESE_MINUTES'))) 
        freezer.start()
        bridge2.save() # save() updates modified_at with the now() time
        freezer.stop()
        
        print(set_needs_delete_on_initial_tor_bridges())

        # Not sure why I need to reload the item, but if I don't do this, the data won't be persisted in the object
        bridge2 = TorBridge.objects.get(pk=bridge2.id)

        assert bridge1.status == TorBridge.INITIAL
        assert bridge2.status == TorBridge.NEEDS_DELETE

    def test_delete_due_tor_bridges(self, create_purchase_order_via_api, create_node_host_and_owner, global_data, api_client):
        _, host, owner = create_node_host_and_owner()
        
        # create 2 bridges
        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge1 = po.item_details.first().product

        response = create_purchase_order_via_api(host=host, owner=owner, target=global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        bridge2 = po.item_details.first().product

        # We set one as Needs to be deleted, regardless of the dates (modified_at, suspend_after)
        bridge2.status = TorBridge.NEEDS_DELETE
        bridge2.save()
        bridge2_id = bridge2.id #since we will delete the bridge, we need to recover the id to check later it does not exist

        # We run the task to set needs delete on suspended bridges
        print(delete_due_tor_bridges())

        # Not sure why I need to reload the item, but if I don't do this, the data won't be persisted in the object

        assert bridge1.status == TorBridge.INITIAL
        assert False == TorBridge.objects.filter(pk=bridge2_id).exists()
        

        
