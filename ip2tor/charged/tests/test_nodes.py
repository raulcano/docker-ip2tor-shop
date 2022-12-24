import pytest


@pytest.mark.skip
@pytest.mark.django_db
class TestCheckAliveNodes():

    @pytest.mark.parametrize('nodeclass', ['LndGRpcNode', 'LndRestNode'])
    @pytest.mark.parametrize('tls_cert_verification', [True, False])
    @pytest.mark.parametrize('tls_cert', [None, 'global_data']) # if None, we'll load the 'correct' cert as per the .env variable; otherwise, we load an invalid cert
    def test_node_alive(self, create_node, global_data, nodeclass, tls_cert_verification, tls_cert, request):
        
        # see this on how to use fixtures as arguments in 'parametrize': https://miguendes.me/how-to-use-fixtures-as-arguments-in-pytestmarkparametrize
        tls_cert = request.getfixturevalue(tls_cert)['invalid_cert'] if not None == tls_cert else None
        node = create_node(nodeclass=nodeclass, tls_cert_verification=tls_cert_verification, tls_cert=tls_cert)
        status, _ = node.check_alive_status()
        
        expected_status = True if (not tls_cert_verification) or (tls_cert_verification and None == tls_cert) else False

        assert status == expected_status
        assert node.is_alive == expected_status