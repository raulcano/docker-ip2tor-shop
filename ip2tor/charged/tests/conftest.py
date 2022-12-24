import os
from os.path import abspath, dirname

import pytest
from charged.lnpurchase.models import PurchaseOrder
from charged.utils import dynamic_import_class
from django.contrib.auth.models import User
from dotenv import load_dotenv
from model_bakery import baker
# In this test module, we assume that the cert loaded from the .env file is a correct one (if it isn't, the corresponding tests will fail)
# Also, we add a fixture with a syntactically correct certificate, but which is invalid for our node

@pytest.fixture
def global_data():
    return {
        'invalid_cert': '''-----BEGIN CERTIFICATE-----
MIICMjCCAdmgAwIBAgIQVNGjQ2zwqC+5A/PUefa87jAKBggqhkjOPQQDAjA/MR8wHQYDVQQKExZsbmQgYXV0b2dlbmVyYXRlZCBjZXJ0MRwwGgYDVQQDExNsZXhpbmVtLmR1Y2tkbnMub3JnMB4XDTIyMTIxMjEyMzYyNVoXDTI0MDIwNjEyMzYyNVowPzEfMB0GA1UEChMWbG5kIGF1dG9nZW5lcmF0ZWQgY2VydDEcMBoGA1UEAxMTbGV4aW5lbS5kdWNrZG5zLm9yZzBZMBMGByqGSM49AgEGCCqGSM49AwEHA0IABAxYaLPTfhM14GLmmMddALB/ACwfzPqJNwmBUHOPNuqDeZv1M/VxiHErehcgZadukQXaPP8/Bl+A8i9i3o4zyIqjgbYwgbMwDgYDVR0PAQH/BAQDAgKkMBMGA1UdJQQMMAoGCCsGAQUFBwMBMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFPKLtcFAb6SAacBj5U783/LvA2knMFwGA1UdEQRVMFOCCWxvY2FsaG9zdIITbGV4aW5lbS5kdWNrZG5zLm9yZ4IEdW5peIIKdW5peHBhY2tldIIHYnVmY29ubocEfwAAAYcQAAAAAAAAAAAAAAAAAAAAATAKBggqhkjOPQQDAgNHADBEAiBEbi4HZv77cLyexF4UnZkMVCiu0BBLPXF7qjjxWVMK0wIgbNxD0WyqAEdivNEZu5S7HOzEG7ziESM4xIWMxmO0EMo=
-----END CERTIFICATE-----'''
    }

@pytest.fixture
def create_node():
    def do_create_node(nodeclass='LndGRpcNode', tls_cert_verification=True, tls_cert=None, owner=None, is_alive=False):
        path = dirname(abspath(__file__)) + '/../../../.env'
        load_dotenv(path)
        
        owner = baker.make(User) if None == owner else owner
        host = os.getenv('CHARGED_LND_HOST')
        port = ""
        if ('LndGRpcNode' == nodeclass):
            port = os.getenv('CHARGED_LND_PORT_GRPC')
        elif ('LndRestNode' == nodeclass):
            port = os.getenv('CHARGED_LND_PORT_REST')
        
        macaroon_invoice = os.getenv('CHARGED_LND_MACAROON_INVOICE')
        macaroon_readonly = os.getenv('CHARGED_LND_MACAROON_READONLY')
        
        tls_cert = os.getenv('CHARGED_LND_TLS_CERTIFICATE') if None == tls_cert else tls_cert
        
        name = 'test_' + os.getenv('CHARGED_LND_NAME')

        Node = dynamic_import_class('charged.lnnode.models', nodeclass)
        return baker.make(Node, name=name, port=port, hostname=host, tls_cert=tls_cert, 
            macaroon_invoice=macaroon_invoice, macaroon_readonly=macaroon_readonly,
            is_enabled=True, priority=0, tls_cert_verification=tls_cert_verification, is_alive=is_alive, owner=owner)

    yield do_create_node




@pytest.fixture
def create_po():
    def do_create_po():
        return baker.make(PurchaseOrder)
    yield do_create_po
