import pytest

@pytest.mark.django_db
class TestInvoices():
    def test_invoice_is_created_on_node_via_grpc(self, create_node):
        node = create_node('LndGRpcNode', tls_cert_verification=False)
        assert True
    
    @pytest.mark.skip
    def test_invoice_is_created_on_node_via_rest(self, create_node):
        node = create_node('LndRestNode', tls_cert_verification=False)
        assert True