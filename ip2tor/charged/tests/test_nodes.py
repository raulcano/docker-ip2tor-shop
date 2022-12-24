import pytest


@pytest.mark.skip
@pytest.mark.django_db
class TestCheckAliveNodes():
    def test_grpc_node_alive_without_tls_verification_cert_OK(self, create_node, global_data):
        node = create_node('LndGRpcNode', tls_cert_verification=False)
        status, info = node.check_alive_status()
        assert status == True
        assert node.is_alive == True

    def test_grpc_node_alive_without_tls_verification_cert_NOK(self, create_node, global_data):
        node = create_node('LndGRpcNode', tls_cert_verification=False, tls_cert=global_data['invalid_cert'])
        status, info = node.check_alive_status()
        assert status == True
        assert node.is_alive == True

    def test_grpc_node_alive_with_tls_verification_cert_OK(self, create_node, global_data):
        node = create_node('LndGRpcNode', tls_cert_verification=True)
        status, info = node.check_alive_status()
        assert status == True
        assert node.is_alive == True

    def test_grpc_node_alive_with_tls_verification_cert_NOK(self, create_node, global_data):
        node = create_node('LndGRpcNode', tls_cert_verification=True, tls_cert=global_data['invalid_cert'])
        status, info = node.check_alive_status()
        assert status == False
        assert node.is_alive == False

    def test_rest_node_alive_without_tls_verification_cert_OK(self, create_node, global_data):
        node = create_node('LndRestNode', tls_cert_verification=False)
        status, info = node.check_alive_status()
        assert status == True
        assert node.is_alive == True

    def test_rest_node_alive_without_tls_verification_cert_NOK(self, create_node, global_data):
        node = create_node('LndRestNode', tls_cert_verification=False, tls_cert=global_data['invalid_cert'])
        status, info = node.check_alive_status()
        assert status == True
        assert node.is_alive == True

    def test_rest_node_alive_with_tls_verification_cert_OK(self, create_node, global_data):
        node = create_node('LndRestNode', tls_cert_verification=True)
        status, info = node.check_alive_status()
        assert status == True
        assert node.is_alive == True

    def test_rest_node_alive_with_tls_verification_cert_NOK(self, create_node, global_data):
        node = create_node('LndRestNode', tls_cert_verification=True, tls_cert=global_data['invalid_cert'])
        status, info = node.check_alive_status()
        assert status == False
        assert node.is_alive == False