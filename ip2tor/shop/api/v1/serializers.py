from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from rest_framework import serializers

from shop.models import TorBridge, Host, NostrAlias, BandwidthExtension, BandwidthExtensionOption


class SiteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Site
        fields = ('domain', 'name')

class BandwidthExtensionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BandwidthExtensionOption
        fields = ('id', 'duration', 'bandwidth', 'price')

class HostSerializer(serializers.HyperlinkedModelSerializer):
    site = SiteSerializer()
    bandwidth_extension_options = BandwidthExtensionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Host
        fields = ('url', 'ip', 'name', 'site', 'is_testnet', 'ci_date', 'ci_status', 'ci_message', 'bridge_bandwidth_initial', 'bandwidth_extension_options')


class HostCheckInSerializer(serializers.HyperlinkedModelSerializer):
    ci_status = serializers.IntegerField(required=False, read_only=False, min_value=0, max_value=2)
    ci_message = serializers.CharField(required=False, read_only=False)

    class Meta:
        model = Host
        fields = ('ci_date', 'ci_status', 'ci_message')


class BandwidthExtensionSerializer(serializers.HyperlinkedModelSerializer):
    tor_bridge = serializers.StringRelatedField()
    class Meta:
        model = BandwidthExtension
        fields = ('id', 'total', 'remaining', 'created_at', 'updated_at', 'expires_at', 'tor_bridge')

class TorBridgeSerializer(serializers.HyperlinkedModelSerializer):
    host = HostSerializer()
    bandwidth_extensions = BandwidthExtensionSerializer(many=True, read_only=True)

    class Meta:
        model = TorBridge
        fields = ('url', 'id', 'comment', 'status', 'host', 'port', 'target', 'suspend_after', 'bandwidth_remaining', 'bandwidth_last_checked', 'bandwidth_extensions')


class NostrAliasSerializer(serializers.HyperlinkedModelSerializer):
    host = HostSerializer()

    class Meta:
        model = NostrAlias
        fields = ('url', 'id', 'comment', 'status', 'host', 'port', 'alias', 'public_key', 'suspend_after')


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'groups')


