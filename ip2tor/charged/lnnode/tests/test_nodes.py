
from charged.utils import dynamic_import_class
from dotenv import load_dotenv
from model_bakery import baker
import os
from os.path import dirname, abspath
import pytest


@pytest.fixture
def create_node():
    def do_create_node(nodeclass):
        path = dirname(abspath(__file__)) + '/../../../../.env'
        load_dotenv(path)

        host = os.getenv('CHARGED_LND_HOST')
        port = ""
        if ('LndGRpcNode' == nodeclass):
            port = os.getenv('CHARGED_LND_PORT_GRPC')
        elif ('LndRestNode' == nodeclass):
            port = os.getenv('CHARGED_LND_PORT_REST')
        
        macaroon_invoice = os.getenv('CHARGED_LND_MACAROON_INVOICE')
        macaroon_readonly = os.getenv('CHARGED_LND_MACAROON_READONLY')
        cert = os.getenv('CHARGED_LND_TLS_CERTIFICATE')
        name = 'test_' + os.getenv('CHARGED_LND_NAME')

        Node = dynamic_import_class('charged.lnnode.models', nodeclass)
        return baker.make(Node, name=name, port=port, hostname=host, tls_cert=cert, 
            macaroon_invoice=macaroon_invoice, macaroon_readonly=macaroon_readonly,
            is_enabled=True, priority=0)

    yield do_create_node

@pytest.mark.django_db
class TestCheckAliveNodes():
    def test_grpc_node_alive_without_tls_verification(self, create_node):
        node = create_node('LndGRpcNode')
        port = 10009
        print(node.id)
        assert False
    def test_grpc_node_alive_with_tls_verification(self, create_node):
        node = create_node('LndGRpcNode')
        port = 10009
        assert True
    def test_grpc_node_alive_with_tls_verification(self, create_node):
        node = create_node('LndRestNode')
        port = 8080
        assert True
    def test_rest_node_alive_without_tls_verification(self, create_node):
        node = create_node('LndRestNode')
        assert True
    