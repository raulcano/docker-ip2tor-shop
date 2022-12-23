from charged.utils import dynamic_import_class
from dotenv import load_dotenv
from model_bakery import baker
import os
from os.path import dirname, abspath
import pytest

# In this test module, we assume that the cert loaded from the .env file is a correct one
# if it isn't, the corresponding tests will fail

@pytest.fixture
def global_data():
    return {
        'invalid_cert': '''-----BEGIN CERTIFICATE-----
MIIDKTCCAhGgAwIBAgIUHqZn0ZKwEWfOI+1W/SBNfyxfW34wDQYJKoZIhvcNAQEL
BQAwJzElMCMGA1UEAwwcdGhpcy1pcy1hLW1hZGUtdXAtZG9tYWluLmNvbTAeFw0y
MjEyMjExNjE3MDlaFw0yMzAxMjAxNjE3MDlaMCcxJTAjBgNVBAMMHHRoaXMtaXMt
YS1tYWRlLXVwLWRvbWFpbi5jb20wggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEK
AoIBAQDREaXSVUd4YPzp1znjjG64dh10coZHDFSZn133kZbDputCI1nqs914jxdz
zTIluGFYfzUnLTDz4eaeeMDf8LzlGJG18sWq4wqQEME8RJSyRiDJreVX1irEd3/0
lQCgpUGoXeG+DuydVZE/N+VpzQ3yQjPK+OSnYdeIFHTH+IrZJTdo4KIgWJuLRTm8
ZtRze49Zq4QmxgKjSbCatkvq6d3GlqfVZPGfC7e8TXrwSvFZk2+UAX+u6J9q/qIg
BRZ++8szRuxihP9SFjv22LjYO2dBj0Vo7TW6jljKXbIntOgBVErRnyEjtEFKJwjE
RxnP3Mm7Qrsxzb+HcBVUX1qovW7LAgMBAAGjTTBLMCcGA1UdEQQgMB6CHHRoaXMt
aXMtYS1tYWRlLXVwLWRvbWFpbi5jb20wCwYDVR0PBAQDAgeAMBMGA1UdJQQMMAoG
CCsGAQUFBwMBMA0GCSqGSIb3DQEBCwUAA4IBAQBpG7XGoFb76KAWUSU/BpkWaTUI
lP8aShvySZ9bFGQwxJN7RSpg3PH3XDgMVTAYh06Scfq+U9MxJYtpCc8cToFQWEzK
hGR4wDQ0sAzDsx2EJu91p5RFMO7wU1RY0uXdc3TxK8uMZgu5gTNXgzMfhQ7b1aEl
LfcoTcHPM66xGe7oX5n4T1sfzusoOCArG+X/uAPByjbSlJKN/wqXUDXTxgykJFul
tkDbmcW31ImITf8vVNaywDjhmLBOEquS6NK0LZdxuoZqCukx/pxScBGjFdWDn4ge
d5812LflhkGeSpvDPk+0QtPKTv/rHmXY99oSf2ZiXhtVB1vegU4Lh8QHJuOE
-----END CERTIFICATE-----'''
    }

@pytest.fixture
def create_node():
    def do_create_node(nodeclass, tls_cert_verification=True, tls_cert=None):
        path = dirname(abspath(__file__)) + '/../../../.env'
        load_dotenv(path)

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
            is_enabled=True, priority=0, tls_cert_verification=tls_cert_verification)

    yield do_create_node