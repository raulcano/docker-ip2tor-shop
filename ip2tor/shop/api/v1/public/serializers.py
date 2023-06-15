from collections import OrderedDict

from rest_framework import serializers
from rest_framework.reverse import reverse

from charged.lnpurchase.serializers import PurchaseOrderItemDetailSerializer, PurchaseOrderSerializer
from shop.api.v1.serializers import TorBridgeSerializer, NostrAliasSerializer, BandwidthExtensionOptionSerializer, BandwidthExtensionSerializer
from shop.models import Host, TorBridge, ShopPurchaseOrder, RSshTunnel, NostrAlias, BandwidthExtension
from shop.validators import validate_target_is_onion, validate_target_has_port


class PublicHostSerializer(serializers.ModelSerializer):
    site = serializers.StringRelatedField(read_only=True)
    
    are_there_tor_bridge_ports_available = serializers.SerializerMethodField('are_there_tor_bridge_ports_available')
    are_there_rssh_tunnels_ports_available = serializers.SerializerMethodField('are_there_rssh_tunnels_ports_available')
    bandwidth_extension_options = BandwidthExtensionOptionSerializer(many=True, read_only=True)
    
    def are_there_tor_bridge_ports_available(self):
        return self.tor_bridge_ports_available(consider_safety_margin=True)
    
    def are_there_rssh_tunnels_ports_available(self):
        return self.rssh_tunnels_ports_available(consider_safety_margin=True)

    class Meta:
        model = Host
        fields = (
            'id',
            'site',
            'created_at',
            'modified_at',
            'ip',
            'is_enabled',
            'is_alive',
            'is_test_host',
            'name',
            'description',
            'is_testnet',
            'offers_tor_bridges',
            'tor_bridge_duration',
            'tor_bridge_price_initial',
            'tor_bridge_price_extension',
            'offers_nostr_aliases',
            'nostr_alias_port',
            'nostr_alias_duration',
            'nostr_alias_price_initial',
            'nostr_alias_price_extension',
            'offers_rssh_tunnels',
            'rssh_tunnel_price',
            'terms_of_service',
            'terms_of_service_url',
            'ci_date',
            'ci_message',
            'ci_status',
            'owner',
            'are_there_tor_bridge_ports_available',
            'are_there_rssh_tunnels_ports_available',
            'bandwidth_extension_options'
        )
        # exclude = ('token_user',)


class PublicOrderSerializer(serializers.Serializer):
    host = None

    def update(self, instance, validated_data):
        raise NotImplementedError()

    def create(self, validated_data):
        product = validated_data.get('product')
        if product == TorBridge.PRODUCT:
            if not self.host.tor_bridge_ports_available(consider_safety_margin=True):
                raise Exception('The current host does not have any Tor bridge ports available.')

            po = ShopPurchaseOrder.tor_bridges.create(
                host=self.host,
                target=validated_data.get('target'),
                comment=validated_data.get('comment')
            )
            return po
        elif product == NostrAlias.PRODUCT:
            po = ShopPurchaseOrder.nostr_aliases.create(
                host=self.host,
                alias=validated_data.get('alias'),
                public_key=validated_data.get('public_key'),
                comment=validated_data.get('comment')
            )
            return po

        elif product == RSshTunnel.PRODUCT:
            raise NotImplementedError("only tor_bridges")

        else:
            raise NotImplementedError("only tor_bridges")

    product = serializers.ChoiceField(choices=[TorBridge.PRODUCT, NostrAlias.PRODUCT, RSshTunnel.PRODUCT])

    host_id = serializers.UUIDField()
    tos_accepted = serializers.BooleanField(required=True)

    comment = serializers.CharField(required=False, max_length=42)

    target = serializers.CharField(
        required=False,
        validators=[validate_target_is_onion,
                    validate_target_has_port]
    )

    alias = serializers.CharField(required=False, max_length=100)

    public_key = serializers.CharField(required=False, max_length=5000)

    class Meta:
        fields = ('product', 'host_id', 'tos_accepted', 'comment', 'target', 'alias', 'public_key')

    def to_representation(self, instance):
        req = self.context.get('request')
        return OrderedDict({
            'id': instance.id,
            'url': req.build_absolute_uri(reverse('v1:purchaseorder-detail', args=(instance.id,)))
        })

    def validate(self, attrs):
        """
        check required fields based on product
        """

        if attrs['product'] == TorBridge.PRODUCT:
            if not self.host.offers_tor_bridges:
                raise serializers.ValidationError(f"Sorry, this host does not offer the product '{TorBridge.PRODUCT}' at the moment.")
            if not attrs.get('target'):
                raise serializers.ValidationError(f"Product '{TorBridge.PRODUCT}' requires 'target'")

        if attrs['product'] == NostrAlias.PRODUCT:
            if not self.host.offers_nostr_aliases:
                raise serializers.ValidationError(f"Sorry, this host does not offer the product '{NostrAlias.PRODUCT}' at the moment.")
            if not attrs.get('alias') or not attrs.get('public_key'):
                raise serializers.ValidationError(f"Product '{NostrAlias.PRODUCT}' requires 'alias' and 'public_key'")
            
            for nostr_alias in NostrAlias.objects.filter(alias__iexact=attrs.get('alias')):
                if nostr_alias.host.ip == self.host.ip:
                    raise serializers.ValidationError(f"Sorry, the alias '{attrs.get('alias')}' is taken. Try another one.")

        if attrs['product'] == RSshTunnel.PRODUCT:
            if not self.host.offers_rssh_tunnels:
                raise serializers.ValidationError(f"Sorry, this host does not offer the product '{RSshTunnel.PRODUCT}' at the moment.")
            if not attrs.get('public_key'):
                raise serializers.ValidationError(f"Product '{RSshTunnel.PRODUCT}' requires 'public_key'")

        if not attrs.get('tos_accepted'):
            if self.host.terms_of_service_url:
                raise serializers.ValidationError(f"Must accept "
                                                  f"Terms of Service (ToS): {self.host.terms_of_service} "
                                                  f"({self.host.terms_of_service_url})")
            else:
                raise serializers.ValidationError(f"Must accept "
                                                  f"Terms of Service (ToS): {self.host.terms_of_service}")

        # Check there are ports available
        if attrs['product'] == TorBridge.PRODUCT and not self.host.tor_bridge_ports_available(consider_safety_margin=True):
            raise serializers.ValidationError(f"The current host does not have any Tor bridge ports available.")
            
        if attrs['product'] == RSshTunnel.PRODUCT and not self.host.rssh_tunnels_ports_available(consider_safety_margin=True):
            raise serializers.ValidationError(f"The current host does not have any RSSH Tunnel ports available.")    

        return attrs

    def validate_host_id(self, value):
        try:
            self.host = Host.objects.get(id=str(value))
        except Host.DoesNotExist:
            raise serializers.ValidationError(f"No host exists with ID: {value}.")

        return value


class ProductRelatedField(serializers.RelatedField):
    """
    A custom field to use for the `tagged_object` generic relationship.
    """

    def to_representation(self, value):
        """
        Serialize product instances with the their own  serializer.
        """
        if isinstance(value, TorBridge):
            serializer = TorBridgeSerializer(value, context={'request': self.context.get('request')})
            # ToDo(frennkie) public should link to public..
            # serializer = PublicTorBridgeSerializer(value, context={'request': self.context.get('request')})

        elif isinstance(value, NostrAlias):
            serializer = NostrAliasSerializer(value, context={'request': self.context.get('request')})

        elif isinstance(value, BandwidthExtension):
            serializer = BandwidthExtensionSerializer(value, context={'request': self.context.get('request')})
        
        # elif isinstance(value, RSshTunnel):
        #     # ToDo(frennkie) replace with RSshTunnel
        #     serializer = TorBridgeSerializer(value, context={'request': self.context.get('request')})

        else:
            raise Exception('Unexpected type of product')

        return serializer.data


class PublicShopPurchaseOrderItemDetailSerializer(PurchaseOrderItemDetailSerializer):
    product = ProductRelatedField(read_only=True)

    class Meta(PurchaseOrderItemDetailSerializer.Meta):
        pass


class PublicShopPurchaseOrderSerializer(PurchaseOrderSerializer):
    item_details = PublicShopPurchaseOrderItemDetailSerializer(read_only=True, many=True)

    class Meta(PurchaseOrderSerializer.Meta):
        pass


class PublicTorBridgeSerializer(serializers.HyperlinkedModelSerializer):

    available_bandwidth_extension_options = serializers.SerializerMethodField()
    bandwidth_extensions = BandwidthExtensionSerializer(many=True, read_only=True)
    
    def get_available_bandwidth_extension_options(self, instance):
        host = instance.host
        beos = host.bandwidth_extension_options.all()
        return BandwidthExtensionOptionSerializer(beos, many=True).data

    class Meta:
        model = TorBridge
        fields = ('id', 'status', 'host_id', 'port', 'suspend_after',
                  'comment', 'target', 'bandwidth_extensions', 'total_remaining_valid_bandwidth','bandwidth_last_checked', 'available_bandwidth_extension_options')
        read_only_fields = ['id', 'status', 'port', 'suspend_after']

class PublicNostrAliasSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = NostrAlias
        fields = ('id', 'status', 'host_id', 'port', 'suspend_after',
                  'comment', 'alias', 'public_key')
        read_only_fields = ['id', 'status', 'port', 'suspend_after']
