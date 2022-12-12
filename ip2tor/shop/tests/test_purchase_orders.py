from model_bakery import baker
from rest_framework import status
from shop.models import Host, ShopPurchaseOrder
from charged.lnpurchase.models import PurchaseOrder
import pytest

@pytest.fixture
def create_purchase_order(api_client):
    def do_create_purchase_order():
        host = baker.make(Host, is_enabled=True, is_alive=True, name="bridge")
        product = 'tor_bridge'
        target = 'myonionaddresherewithaport.onion:80'
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
    yield do_create_purchase_order

@pytest.mark.django_db
class TestCreatePurchaseOrder():
    def test_create_empty_po_returns_400(self, create_purchase_order):
        response = create_purchase_order()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_create_purchase_order_for_TorBridge(self, create_purchase_order):
        response = create_purchase_order()
        # po = ShopPurchaseOrder.objects.get(pk=response.data['id'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        assert response.data['id'] == po.id

@pytest.mark.django_db
class TestRetrievePurchaseOrder():
    def test_retrieve_purchase_order(self, create_purchase_order, api_client):
        response_po = create_purchase_order()

        response = api_client.get(f'/api/v1/public/pos/{response_po.data["id"]}/')
        # print(response.data)
        assert response.status_code == status.HTTP_200_OK
        assert 'item_details' in response.data
        assert 'ln_invoices' in response.data
        