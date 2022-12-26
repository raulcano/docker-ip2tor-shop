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
MIICNTCCAdqgAwIBAgIRAMdJJa0NLUnyPaecfMOaXB4wCgYIKoZIzj0EAwIwPzEf
MB0GA1UEChMWbG5kIGF1dG9nZW5lcmF0ZWQgY2VydDEcMBoGA1UEAxMTbGV4aW5l
bS5kdWNrZG5zLm9yZzAeFw0yMjEyMjQxNTI1MjVaFw0yNDAyMTgxNTI1MjVaMD8x
HzAdBgNVBAoTFmxuZCBhdXRvZ2VuZXJhdGVkIGNlcnQxHDAaBgNVBAMTE2xleGlu
ZW0uZHVja2Rucy5vcmcwWTATBgcqhkjOPQIBBggqhkjOPQMBBwNCAARByngkKSsf
QoTnG9RvhIfxd8mvghDuY5shWZ3AiQXAiocAY9DZ0tElrV4y9V0+O8JFbUJyF9+t
sBOFO4/FW8Bjo4G2MIGzMA4GA1UdDwEB/wQEAwICpDATBgNVHSUEDDAKBggrBgEF
BQcDATAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQWBBTgGew6I1RrkR0SmeXloPQn
x31usTBcBgNVHREEVTBTgglsb2NhbGhvc3SCE2xleGluZW0uZHVja2Rucy5vcmeC
BHVuaXiCCnVuaXhwYWNrZXSCB2J1ZmNvbm6HBH8AAAGHEAAAAAAAAAAAAAAAAAAA
AAEwCgYIKoZIzj0EAwIDSQAwRgIhAPdi2rwkOucMSNwXarys5nhPJAVu/EZKYT1i
oAO4C6njAiEA02zmNqGDgurqJjW8456/Z7HREHCZGzcwAd9Lox0daE0=
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
