

import pytest
from charged.tests.conftest import create_node, global_data
from django.contrib.auth.models import User
from django.db import connection

from model_bakery import baker
from rest_framework.test import APIClient
from shop.models import Host


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
        return node, host, owner
    

    # When the fixture is torn down, there is an error because the django_admin_log has a pending trigger event
    # This is a dirty solution for the time being. We are testing anyway and I am not checking the admin logs
    cursor = connection.cursor()
    cursor.execute("ALTER TABLE django_admin_log DISABLE TRIGGER ALL")
    
    yield do_create_node_host_and_owner

    # cursor.execute("TRUNCATE TABLE django_admin_log")
    # cursor.execute("ALTER TABLE django_admin_log ENABLE TRIGGER ALL")

@pytest.fixture
def create_purchase_order_via_api(api_client):
    def do_create_purchase_order_via_api(po=None, owner=None, host=None):
        if po == None:
            host = baker.make(Host, is_enabled=True, is_alive=True, owner=owner) if None == host else host
            product = 'tor_bridge'
            target = 'myonionaddresherewithaport.onion:8333' # IMPORTANT: for the sake of tests, make sure the port is in the whitelisted_service_ports (see lnpurchase/tasks.py)
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
