



import time

import pytest
from charged.lnpurchase.models import PurchaseOrder
from charged.lnpurchase.tasks import process_initial_purchase_order
from django.db.models import signals
from rest_framework import status


# @pytest.mark.skip
@pytest.mark.django_db
class TestCreatePurchaseOrder():
    def test_create_empty_po_returns_400(self, create_purchase_order_via_api):
        response = create_purchase_order_via_api({})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
    def test_create_purchase_order_for_TorBridge_returns_id_and_url(self, create_purchase_order_via_api):
        response = create_purchase_order_via_api()
        # po = ShopPurchaseOrder.objects.get(pk=response.data['id'])
        po = PurchaseOrder.objects.get(pk=response.data['id'])
        assert response.data['id'] == po.id
        assert response.data['url'].endswith('/api/v1/public/pos/' + str(po.id) + '/')

# @pytest.mark.skip
@pytest.mark.django_db
class TestRetrievePurchaseOrder():
    
    # @pytest.mark.skip
    def test_retrieve_purchase_order_includes_item_details_and_ln_invoices(self, create_purchase_order_via_api, api_client, create_node_host_and_owner):
        
        _, host, owner = create_node_host_and_owner()

        response_po = create_purchase_order_via_api(owner=owner, host=host)
        response = api_client.get(f'/api/v1/public/pos/{response_po.data["id"]}/')
        
        print(response_po.data)
        assert response.status_code == status.HTTP_200_OK
        assert 'item_details' in response.data
        assert 'ln_invoices' in response.data

    # @pytest.mark.skip
    def test_retrieve_purchase_order_includes_one_invoice(self, create_purchase_order_via_api, api_client, create_node_host_and_owner):
        
        node, host, owner = create_node_host_and_owner(node_is_alive=True)

        invoice_received = False
        iterations = 3
        delay = 2 # seconds
                
        response_po = create_purchase_order_via_api(owner=owner, host=host)
        po = PurchaseOrder.objects.get(pk=response_po.data['id'])
        process_initial_purchase_order(po.id)
        i = 0
        while (i < iterations) & (not invoice_received): 
            response = api_client.get(f'/api/v1/public/pos/{po.id}/')
            invoice_received = True if len(response.data['ln_invoices']) > 0 else False
            time.sleep(delay)
            i = i + 1
        
        print(response.data)
        assert invoice_received
        