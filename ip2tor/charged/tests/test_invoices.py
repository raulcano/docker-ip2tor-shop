
import datetime
from decimal import Decimal
from charged.lninvoice.models import PurchaseOrderInvoice

import pytest
import random

@pytest.mark.skip
@pytest.mark.django_db
class TestInvoices():
    def test_invoice_is_created_on_node_via_grpc(self, create_node, create_po):
        node = create_node('LndGRpcNode', tls_cert_verification=False)
        po = create_po()

        label = datetime.datetime.now().strftime("%I:%M%p on %B %d, %Y") + " | Test invoice"
        msatoshi = random.randrange(1000,10000)
        invoice = PurchaseOrderInvoice(
                    label=label,
                    msatoshi=msatoshi,
                    tax_rate=Decimal.from_float(1.0),
                    tax_currency_ex_rate=1,
                    info_currency_ex_rate=1,
                    lnnode=node,
                    po=po)
        invoice.lnnode_create_invoice()

        

        # now we retrieve the invoce from the node to check it exists and that the data is consistent

        # invoice_from_node = node.get_invoice(r_hash=invoice.payment_hash)
        # print(invoice_from_node)
        # assert invoice_from_node

        assert False
    
    
    @pytest.mark.skip
    def test_invoice_is_created_on_node_via_rest(self, create_node):
        node = create_node('LndRestNode', tls_cert_verification=False)
        assert True