

import pytest
from charged.tests.conftest import create_node, global_data
from django.contrib.auth.models import User
from django.db import connection

from model_bakery import baker
from rest_framework.test import APIClient
from shop.models import Host, PortRange


######################################################
# All this is to mockup the lninvoice_paid_handler
# When I figure out a better way to simulate that, I'll delete this
#
from charged.utils import add_change_log_entry
from shop.models import TorBridge, RSshTunnel, Bridge
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
#
#
######################################################

@pytest.fixture
def api_client():

    # When the fixture is torn down, there is an error because the django_admin_log has a pending trigger event
    # This is a dirty solution for the time being. We are testing anyway and I am not checking the admin logs
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE django_admin_log DISABLE TRIGGER ALL")
    yield APIClient()

@pytest.fixture
def create_node_host_and_owner(create_node, global_data):
    def do_create_node_host_and_owner(nodeclass='LndGRpcNode', tls_cert_verification=False, tls_cert=global_data['invalid_cert'], owner=None, node_is_alive=False):
        owner = baker.make(User) if None == owner else owner
        node = create_node(nodeclass=nodeclass, tls_cert_verification=tls_cert_verification, tls_cert=tls_cert, owner=owner, is_alive=node_is_alive)
        
        
        host = baker.make(Host, is_enabled=True, is_alive=True, owner=owner)
        port_range = baker.make(PortRange, start=10000, end=20000, host=host, type=PortRange.TOR_BRIDGE)
        return node, host, owner
    

    # When the fixture is torn down, there is an error because the django_admin_log has a pending trigger event
    # This is a dirty solution for the time being. We are testing anyway and I am not checking the admin logs
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE django_admin_log DISABLE TRIGGER ALL")
    
    yield do_create_node_host_and_owner

    # cursor.execute("TRUNCATE TABLE django_admin_log")
    # cursor.execute("ALTER TABLE django_admin_log ENABLE TRIGGER ALL")

@pytest.fixture
def create_purchase_order_via_api(api_client, global_data):
    def do_create_purchase_order_via_api(po=None, owner=None, host=None, target=None):
        if po == None:
            if (None == host):
                host = baker.make(Host, is_enabled=True, is_alive=True, owner=owner, target=target)
                baker.make(PortRange, start=10000, end=20000, host=host, type=PortRange.TOR_BRIDGE) 
            product = 'tor_bridge'
            # IMPORTANT: for the sake of tests, make sure the port is in the whitelisted_service_ports (see lnpurchase/tasks.py)
            target = global_data['sample_onion_address'] + ':' + global_data['sample_onion_port'] if None == target else target
            comment = 'This is my Tor bridge in a new host'
            po = {
                'host_id': host.id,
                'product': product,
                'target': target,
                'public_key': '',
                'comment': comment,
                'tos_accepted': True,
            }

        return api_client.post('/api/v1/public/order/', po)
    # When the fixture is torn down, there is an error because the django_admin_log has a pending trigger event
    # This is a dirty solution for the time being. We are testing anyway and I am not checking the admin logs
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE django_admin_log DISABLE TRIGGER ALL")
    yield do_create_purchase_order_via_api

@pytest.fixture
def lninvoice_paid_handler_mockup():
    def do_lninvoice_paid_handler(sender, instance, **kwargs):
        print("received...!")
        print(f"received Sender: {sender}")
        print(f"received Instance: {instance}")

        shop_item_content_type = instance.po.item_details.first().content_type
        shop_item_id = instance.po.item_details.first().object_id

        if shop_item_content_type == ContentType.objects.get_for_model(TorBridge):
            shop_item = TorBridge.objects.get(id=shop_item_id)
        elif shop_item_content_type == ContentType.objects.get_for_model(RSshTunnel):
            shop_item = RSshTunnel.objects.get(id=shop_item_id)
        else:
            raise NotImplementedError

        if shop_item.status == Bridge.INITIAL:
            print(f"set to PENDING")
            shop_item.status = Bridge.NEEDS_ACTIVATE

        elif shop_item.status == Bridge.ACTIVE:
            print(f"is already ACTIVE - assume extend")
            if shop_item.suspend_after <= timezone.now():
                # rare cases where it's ACTIVE but expired (the scheduled task didn't update it yet)
                shop_item.suspend_after = timezone.now() + timedelta(seconds=shop_item.host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME', 600))
            else:
                shop_item.suspend_after = shop_item.suspend_after + timedelta(seconds=shop_item.host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME', 600))

        elif shop_item.status == Bridge.SUSPENDED or shop_item.status == Bridge.NEEDS_SUSPEND:
            print(f"is reactivate")
            shop_item.status = Bridge.NEEDS_ACTIVATE

            if shop_item.suspend_after <= timezone.now():
                shop_item.suspend_after = timezone.now() + timedelta(seconds=shop_item.host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME', 600))
            else:
                # rare cases where it's SUSPENDED/NEEDS_SUSPEND but it hasn't expired yet (not sure if we'll reach this state ever)
                shop_item.suspend_after = shop_item.suspend_after + timedelta(seconds=shop_item.host.tor_bridge_duration) + timedelta(seconds=getattr(settings, 'SHOP_BRIDGE_DURATION_GRACE_TIME', 600))

        shop_item.save()
        add_change_log_entry(shop_item, "ran lninvoice_paid_handler")
        
        return shop_item
    yield do_lninvoice_paid_handler