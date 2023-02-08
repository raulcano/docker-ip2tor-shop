from django.shortcuts import redirect
from django.views import generic
from django.views.generic import TemplateView

from .forms import PurchaseTorBridgeOnHostForm
from .models import Host, ShopPurchaseOrder
from django.shortcuts import render
from shop.models import Host
from django.db.models import Value

class HostListView(generic.ListView):
    model = Host

    def get_queryset(self):
        return Host.active.all()


class PurchaseTorBridgeOnHostView(generic.UpdateView):
    model = Host
    form_class = PurchaseTorBridgeOnHostForm

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)

        # print(context)
        return context

    def get_queryset(self):
        return Host.active.all()

    def get_success_url(self):
        pass

    def form_valid(self, form):
        clean_target = form.cleaned_data.get('target')
        clean_comment = form.cleaned_data.get('comment')

        # tor_bridge = TorBridge.objects.create(comment=clean_comment,
        #                                       host=form.instance,
        #                                       target=clean_target)
        #
        # po = PurchaseOrder.objects.create()
        # po_item = PurchaseOrderItemDetail(price=form.instance.tor_bridge_price_initial,
        #                                   product=tor_bridge,
        #                                   quantity=1)
        # po.item_details.add(po_item, bulk=False)
        # po_item.save()
        # po.save()
        
        host=form.instance
        if not host.tor_bridge_ports_available(consider_safety_margin=True):
            raise Exception('The current host does not have any Tor bridge ports available.')
        po = ShopPurchaseOrder.tor_bridges.create(host=host, target=clean_target, comment=clean_comment)

        return redirect('lnpurchase:po-detail', pk=po.pk)
        # return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form):
        print("form invalid")  # ToDo(frennkie) use messages
        return super().form_invalid(form)


class DemoView(TemplateView):
    template_name = 'shop/demo.html'


def index(request):

    fields_nostr_alias = [
        { 'name': 'alias',
        'placeholder': 'Enter your alias here...',
        'help_text': 'This is the recognizable alias you would like to appear after the slash in the URL "/".'
         },
         { 'name': 'public_key',
        'placeholder': 'Enter your Nostr public key...',
        'help_text': 'This is a long alphanumeric string that uniquely identifies you in the Nostr network.'
         },
    ]

    fields_tor_bridge = [
        { 'name': 'target',
        'placeholder': 'Enter your onion address and port...',
        'help_text': 'Target address and port. E.g. "myonionhiddenservice:8333"'
         },
    ]

    

    return  render(request, 'shop/landing.html', { 
            'hosts_tor_bridges': sorted(Host.active.filter(offers_tor_bridges=True), key=lambda t: t.sats_per_day_tor_bridge, reverse=True), 
            'hosts_nostr_aliases': sorted(Host.active.filter(offers_nostr_aliases=True), key=lambda t: t.sats_per_day_nostr_alias, reverse=True),
            'fields_nostr_alias': fields_nostr_alias,
            'fields_tor_bridge': fields_tor_bridge,
        })