from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.viewsets import GenericViewSet

from charged.lninvoice.models import Invoice, PurchaseOrderInvoice
from charged.lninvoice.serializers import InvoiceSerializer, PurchaseOrderInvoiceSerializer
from charged.lnnode.models import LndGRpcNode
from charged.lnnode.serializers import LndGRpcNodeSerializer
from charged.lnpurchase.models import PurchaseOrder, PurchaseOrderItemDetail
from charged.utils import add_change_log_entry
from shop.models import TorBridge, Host, NostrAlias, BandwidthExtensionOption, BandwidthExtension
from . import serializers
import uuid
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

class PublicHostViewSet(mixins.RetrieveModelMixin,
                        mixins.ListModelMixin,
                        GenericViewSet):
    """
    API endpoint that allows **anybody** to `list` and `retrieve` hosts.
    `Create`, `edit` and `delete` is **not possible**.
    """
    queryset = Host.active.all()
    serializer_class = serializers.PublicHostSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['id', 'is_testnet', 'is_test_host', 'offers_tor_bridges', 'offers_rssh_tunnels', 'offers_nostr_aliases']


class PublicInvoiceViewSet(mixins.RetrieveModelMixin,
                           GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` lninvoice Invoices.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]


class PublicLndGRpcNodeViewSet(mixins.RetrieveModelMixin,
                               GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` lnnode LnNode.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = LndGRpcNode.objects.all()
    serializer_class = LndGRpcNodeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]


class PublicOrderViewSet(mixins.CreateModelMixin,
                         GenericViewSet):
    """
    API endpoint that allows **anybody** to `create` lnpurchase Purchase Orders.
    `Edit`, `list`, `delete` and `retrieve` is **not possible**.
    """
    queryset = Host.objects.all()  # ToDo(frennkie) check
    serializer_class = serializers.PublicOrderSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]


class PublicPurchaseOrderInvoiceViewSet(mixins.RetrieveModelMixin,
                                        GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` lninvoice Purchase Order Invoices.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = PurchaseOrderInvoice.objects.all()
    serializer_class = PurchaseOrderInvoiceSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]


class PublicPurchaseOrderItemDetailViewSet(mixins.RetrieveModelMixin,
                                           GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` lnpurchase Purchase Order Items.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = PurchaseOrderItemDetail.objects.all()
    serializer_class = serializers.PublicShopPurchaseOrderItemDetailSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]


class PublicPurchaseOrderViewSet(mixins.RetrieveModelMixin,
                                 GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` lnpurchase Purchase Orders.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = PurchaseOrder.objects.all()
    serializer_class = serializers.PublicShopPurchaseOrderSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]


class PublicTorBridgeViewSet(mixins.RetrieveModelMixin,
                             GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` tor bridges.
    Additional action `extend` allows **anybody** to extend an existing tor bridge.
    Additional action `extend_bandwidth` allows **anybody** to extend the bandwidth in an existing tor bridge.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = TorBridge.objects.all().order_by('host__ip', 'port')
    serializer_class = serializers.PublicTorBridgeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['host', 'status']

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        tor_bridge = self.get_object()

        if(tor_bridge.host.is_test_host):
            res = {
                'status': 'error',
                'detail': 'This bridge is in a test host and therefore cannot be extended. Try creating a completely new one from scratch.'
            }
        else:
            # create a new PO
            po = PurchaseOrder.objects.create()
            po_item = PurchaseOrderItemDetail(price=tor_bridge.host.tor_bridge_price_extension,
                                            product=tor_bridge,
                                            quantity=1)
            po.item_details.add(po_item, bulk=False)
            po_item.save()
            add_change_log_entry(po_item, "set created")
            po.save()
            add_change_log_entry(po, "added item_details")

            res = {
                'status': 'ok',
                'po_id': po.id,
                'po': reverse('v1:purchaseorder-detail', args=(po.id,), request=request)
            }

        return Response(res)

    @action(detail=True, methods=['post'], url_path='extend_bandwidth/(?P<bandwidth_extension_option_pk>[^/.]+)')
    def extend_bandwidth(self, request, pk=None, bandwidth_extension_option_pk=None):

        try:
            uuid_bandwidth_extension_option_pk = uuid.UUID(bandwidth_extension_option_pk)
            tor_bridge = self.get_object()
            beo = BandwidthExtensionOption.objects.get(pk=uuid_bandwidth_extension_option_pk)
        except ValueError:
            return Response({'status': 'error', 'detail': 'Invalid UUID format for the extension option ID'}, status=status.HTTP_400_BAD_REQUEST)
        except BandwidthExtensionOption.DoesNotExist:
            return Response({'status': 'error', 'detail': 'Extension option does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        
        # Need to check that this option ID is available in the Host in which the TorBridge is hosted 
        # Otherwise the user could add other ids from different Hosts
        if tor_bridge.host not in list(beo.hosts.all()):
            return Response({'status': 'error', 'detail': 'This bandwidth extension is not offered by the host selected'}, status=status.HTTP_400_BAD_REQUEST)

        if(tor_bridge.host.is_test_host):
            return Response({'status': 'error', 'detail': 'This bridge is in a test host and therefore cannot be extended. Try creating a completely new one from scratch.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            # create a new PO
            
            # Create a new BandwidthExtension object attached to the TorBridge
            bandwidth_extension = BandwidthExtension.objects.create(
                tor_bridge=tor_bridge,
                total=beo.bandwidth,
                remaining=0, # will be updated when the invoice is paid
                created_at=timezone.now(),
                updated_at=timezone.now(),
                expires_at=timezone.now() + timedelta(seconds=beo.duration) 
            )
            
            po = PurchaseOrder.objects.create()
            po_item = PurchaseOrderItemDetail(price=beo.price,
                                            product=bandwidth_extension,
                                            quantity=1)
            po.item_details.add(po_item, bulk=False)
            po_item.save()
            add_change_log_entry(po_item, "set created")
            po.save()
            add_change_log_entry(po, "added item_details")

            res = {
                'status': 'ok',
                'po_id': po.id,
                'po': reverse('v1:purchaseorder-detail', args=(po.id,), request=request)
            }

        return Response(res)

class PublicNostrAliasViewSet(mixins.RetrieveModelMixin,
                             GenericViewSet):
    """
    API endpoint that allows **anybody** to `retrieve` nostr aliases.
    Additional action `extend` allows **anybody** to extend an existing nostr alias.
    `Create`, `edit`, `list` and `delete` is **not possible**.
    """
    queryset = NostrAlias.objects.all().order_by('host__ip', 'alias')
    serializer_class = serializers.PublicNostrAliasSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['host', 'status']

    @action(detail=True, methods=['post'])
    def extend(self, request, pk=None):
        nostr_alias = self.get_object()

        if(nostr_alias.host.is_test_host):
            res = {
                'status': 'error',
                'detail': 'This bridge is in a test host and therefore cannot be extended. Try creating a completely new one from scratch.'
            }
        else:
            # create a new PO
            po = PurchaseOrder.objects.create()
            po_item = PurchaseOrderItemDetail(price=nostr_alias.host.nostr_alias_price_extension,
                                            product=nostr_alias,
                                            quantity=1)
            po.item_details.add(po_item, bulk=False)
            po_item.save()
            add_change_log_entry(po_item, "set created")
            po.save()
            add_change_log_entry(po, "added item_details")

            res = {
                'status': 'ok',
                'po_id': po.id,
                'po': reverse('v1:purchaseorder-detail', args=(po.id,), request=request)
            }

        return Response(res)
