from django import forms

from shop.models import TorBridge, NostrAlias, RSshTunnel


class TorBridgeAdminForm(forms.ModelForm):
    class Meta:
        model = TorBridge
        fields = '__all__'

class NostrAliasAdminForm(forms.ModelForm):
    class Meta:
        model = NostrAlias
        fields = '__all__'
    
    def clean(self):
        cleaned_data = super().clean()
        clean_alias = cleaned_data['alias']
        clean_public_key = cleaned_data['public_key']

        # ensure the host_id belogs to a host in the system that is enabled and offers nostr aliases
        # raise forms.ValidationError("The host id does not correspond to a host in our system that is enabled and offers Nostr aliases. Wtf are you trying?")

        # ensure the alias and the pub key are alphanumeric
        # raise forms.ValidationError("The alias and the public_key need to be alphanumeric characters only")

        # If the alias exists, raise error
        # raise forms.ValidationError("The alias '{}' is taken, sorry".format(clean_alias))
        return cleaned_data


class PurchaseTorBridgeOnHostForm(forms.ModelForm):
    class Meta:
        model = TorBridge
        fields = ['target']

    def clean(self):
        cleaned_data = super().clean()
        clean_target = cleaned_data['target']
        
        # ensure the host_id belogs to a host in the system that is enabled and offers tor bridges
        # raise forms.ValidationError("The host id does not correspond to a host in our system that is enabled and offers tor bridges. Wtf are you trying?

        # raise forms.ValidationError("I don't like this: {}".format(clean_target))
    
        return cleaned_data


    # def clean(self):
    #     cleaned_data = super().clean()
    #     clean_choice = cleaned_data['choice']
    #
    #     # make sure this Choice exists for this Question
    #     try:
    #         self.instance.choice_set.get(pk=clean_choice)
    #     except Choice.DoesNotExist as err:
    #         raise forms.ValidationError("Not found: {} - {}".format(clean_choice, err))
    #
    #     return cleaned_data

class PurchaseNostrAliasOnHostForm(forms.ModelForm):
    class Meta:
        model = NostrAlias
        fields = ['alias', 'public_key']

class RSshTunnelAdminForm(forms.ModelForm):
    class Meta:
        model = RSshTunnel
        fields = '__all__'
