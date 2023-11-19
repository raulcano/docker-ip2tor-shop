from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.encoding import smart_str
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from shop.models import TorBridge, Host, NostrAlias, BandwidthExtension
from . import serializers
from .serializers import HostCheckInSerializer


class PlainTextRenderer(renderers.BaseRenderer):
    media_type = 'text/plain'
    format = 'txt'

    def render(self, data, media_type=None, renderer_context=None):
        return smart_str(data, encoding=self.charset)


class NostrAliasViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows **admins** and **authenticated users** to `create`, `retrieve`,
    `update`, `delete` and `list` nostr aliases.
    """
    queryset = NostrAlias.objects.all().order_by('host__ip', 'alias')
    serializer_class = serializers.NostrAliasSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['host', 'status']

    def get_queryset(self):
        """
        This view returns a list of all the nostr aliases for the currently authenticated user.
        """
        user = self.request.user
        if user.is_superuser:
            return NostrAlias.objects.all()

        return NostrAlias.objects.filter(host__token_user=user)
    
    # @action(detail=False, methods=['get'], renderer_classes=[PlainTextRenderer])
    # def get_telegraf_config(self, request, **kwargs):

class TorBridgeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows **admins** and **authenticated users** to `create`, `retrieve`,
    `update`, `delete` and `list` tor bridges. Also, there is an additional action 'consume_bandwidth', to 
    substract a certain amount of bytes from the bridge remaining bandwidth.
    """
    queryset = TorBridge.objects.all().order_by('host__ip', 'port')
    serializer_class = serializers.TorBridgeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['host', 'status']
  
    def get_queryset(self):
        """
        This view returns a list of all the tor bridges for the currently authenticated user.
        """
        user = self.request.user
        if user.is_superuser:
            return TorBridge.objects.all()

        return TorBridge.objects.filter(host__token_user=user)

    # Allows to post an amount in bytes to substract from the Tor Bridge
    # { amount: <amount_in_bytes> }
    # This method:
    # - Substracts bandwidth from TorBridge (it also updates date of last check of bandwidth of TorBridge)
    @action(detail=True, methods=['patch'])
    def consume_bandwidth(self, request, pk=None):
        tor_bridge = self.get_object()

        amount = request.data.get('amount')

        # Make sure the 'amount' is a valid value
        if amount is None:
            return Response({'status': 'error', 'detail': 'Invalid payload. "amount" field is required.'}, status=status.HTTP_400_BAD_REQUEST)

        # Convert the 'amount' to integer if needed
        try:
            amount = int(amount)
        except ValueError:
            return Response({'status': 'error', 'detail': 'Invalid value for "amount" field. Must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

        previous_bw = tor_bridge.total_remaining_valid_bandwidth
        tor_bridge.substract_consumed_bandwidth(amount)
        current_bw = tor_bridge.total_remaining_valid_bandwidth
        res = {
                'status': 'ok',
                'detail': 'The remaining bandwidth of the tor bridge was updated. Previous remaining bandwidth: {} MB ({} GB). Current remaining bandwidth: {} MB ({} GB)'.format(str(round(previous_bw/1024)), str(round(previous_bw/1024/1024)), str(round(current_bw/1024)),str(round(current_bw/1024/1024)))
            }
        return Response(res)

    @action(detail=False, methods=['get'], renderer_classes=[PlainTextRenderer])
    def get_telegraf_config(self, request, **kwargs):
        tor_port = request.GET.get('port', '9065')

        user = self.request.user
        if user.is_superuser:
            # admin can see all monitored bridges
            qs = self.queryset.filter()\
                .filter(is_monitored=True)\
                .order_by('host')

        elif user.username == 'telegraf':
            # monitoring user 'telegraf' may see all active bridges
            qs = self.queryset.filter(status=TorBridge.ACTIVE)\
                .filter(is_monitored=True)\
                .order_by('host')

        else:
            # others will see their own active bridges
            qs = self.queryset.filter(host__token_user=user)\
                .filter(is_monitored=True)\
                .filter(status=TorBridge.ACTIVE)\
                .order_by('host')

        data = ""
        for item in qs:
            data += ('''
# Port:{0.port} via-ip2tor on {0.host}
[[inputs.http_response]]
  urls = ["https://{0.host.ip}:{0.port}"]

  response_timeout = "15s"
  insecure_skip_verify = true

  [inputs.http_response.tags]
    bridge_host = "{0.host.name}"
    bridge_port = "{0.port}"
    checks = "via-ip2tor"

# Port:{0.port} via-tor on {0.host}
[[inputs.http_response]]
  urls = ["https://{0.target}"]
  http_proxy = "http://localhost:{1}"

  response_timeout = "15s"
  insecure_skip_verify = true

  [inputs.http_response.tags]
    bridge_host = "{0.host.name}"
    bridge_port = "{0.port}"
    checks = "via-tor"
'''.format(item, tor_port))

        # now return data
        return Response(data)


class HostViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows **admins** to `view` and `edit` hosts.
    """
    queryset = Host.objects.all().order_by('ip')
    serializer_class = serializers.HostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        This view returns a list of all the tor bridges for the currently authenticated user.
        """
        user = self.request.user
        if user.is_superuser:
            return Host.objects.all()
        return Host.objects.filter(token_user=user)

    @action(detail=True, methods=['get', 'post'], serializer_class=HostCheckInSerializer)
    def check_in(self, request, pk=None):
        serializer = self.get_serializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        status = serializer.data.get('ci_status')
        message = serializer.data.get('ci_message')

        host = self.get_object()
        host.check_in(status=status, message=message)

        return Response({
            'check_in': 'ok',
            'date': host.ci_date,
            'status': host.ci_status,
            'message': host.ci_message
        })


class SiteViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows **admins** to `view` and `edit` sites.
    """
    queryset = Site.objects.all().order_by('domain', 'name')
    serializer_class = serializers.SiteSerializer
    permission_classes = [permissions.IsAdminUser]


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows **admins** to `view` and `edit` users.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAdminUser]

class BandwidthExtensionViewSet(viewsets.ModelViewSet):
    queryset = BandwidthExtension.objects.all().order_by('created_at')
    serializer_class = serializers.BandwidthExtensionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        This view returns a list of all the extensions for the currently authenticated user.
        """
        user = self.request.user
        if user.is_superuser:
            return BandwidthExtension.objects.all()
        return BandwidthExtension.objects.filter(tor_bridge__host__token_user=user)
