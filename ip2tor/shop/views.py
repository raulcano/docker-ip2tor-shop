from django.shortcuts import redirect
from django.views import generic
from django.views.generic import TemplateView

from .forms import PurchaseTorBridgeOnHostForm, PurchaseNostrAliasOnHostForm
from .models import Host, ShopPurchaseOrder, TorBridge, NostrAlias
from django.shortcuts import render
from shop.models import Host
from charged.lnpurchase.models import PurchaseOrder, PurchaseOrderItemDetail
from django.db.models import Value
from django.core.exceptions import ValidationError

class HostListView(generic.ListView):
    model = Host

    def get_queryset(self):
        return Host.active.all()

# To be deleted
class PurchaseProductHostView(generic.UpdateView):
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
        clean_product_type = form.cleaned_data.get('product_type')
        if (clean_product_type == 'tor_bridge'):
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
        elif (clean_product_type == 'nostr_alias'):
            pass

    def form_invalid(self, form):
        print("form invalid")  # ToDo(frennkie) use messages
        return super().form_invalid(form)

# To be deleted
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
    host_id = '' # empty if there are no errors
    productID = ''
    submitted_product_type = ''
    errors = []
    form_tb = PurchaseTorBridgeOnHostForm()
    form_na = PurchaseNostrAliasOnHostForm()
    
    if request.method == 'POST':
        if request.POST.get('action_type') == 'purchase':
            # create a form instance and populate it with data from the request:
            submitted_product_type = request.POST.get('product_type')
            
            if(submitted_product_type == 'tor_bridge'):
                form_tb = PurchaseTorBridgeOnHostForm(request.POST)
                form = form_tb
            elif(submitted_product_type == 'nostr_alias'):
                form_na = PurchaseNostrAliasOnHostForm(request.POST)
                form = form_na
            else:
                raise Exception('Invalid product submitted in the form')
            
            if form.is_valid():
                host = Host.objects.get(pk=request.POST.get(submitted_product_type + 'Host_id'))
                if(submitted_product_type == 'tor_bridge'):
                    if not host.offers_tor_bridges:
                        raise Exception('This host does not offer the product "' + submitted_product_type + '". Please stop messing around.')
                    clean_target = form.cleaned_data.get('target')
                    if not host.tor_bridge_ports_available(consider_safety_margin=True):
                        host_id = request.POST.get(submitted_product_type + 'Host_id')
                        errors.append('Sorry, the current host does not have any Tor bridge ports available. Try another one.')
                    else:
                        po = ShopPurchaseOrder.tor_bridges.create(host=host, target=clean_target, comment='')
                        return redirect('lnpurchase:po-detail', pk=po.pk)
                elif(submitted_product_type == 'nostr_alias'):
                    if not host.offers_nostr_aliases:
                        raise Exception('This host does not offer the product "' + submitted_product_type + '". Please stop messing around.')
                    clean_alias = form.cleaned_data.get('alias')
                    clean_public_key = form.cleaned_data.get('public_key')
                    po = ShopPurchaseOrder.nostr_aliases.create(host=host, alias=clean_alias, public_key=clean_public_key, comment='')
                    return redirect('lnpurchase:po-detail', pk=po.pk)
            else:
                host_id = request.POST.get(submitted_product_type + 'Host_id')
        
        elif request.POST.get('action_type') == 'extend':
            submitted_product_type = 'extension'
            # check the ID exists
            try:
                productID = request.POST.get('productID')
            
                if TorBridge.objects.filter(pk=productID).exists():
                    product_object = TorBridge.objects.get(pk=productID)
                    price_extension = product_object.host.tor_bridge_price_extension
                elif NostrAlias.objects.filter(pk=productID).exists():
                    product_object = NostrAlias.objects.get(pk=productID)
                    price_extension = product_object.host.nostr_alias_price_extension
                else:
                    errors.append('The ID does not exist')
            except ValidationError:
                errors.append('The ID is not valid')
            
            # create a new PO for the extension with the updated data and price
            if len(errors) == 0:
                if(product_object.host.is_test_host):
                    errors.append('This bridge is in a test host and therefore cannot be extended. Try creating a completely new one from scratch.')
                else:
                    # create a new PO
                    po = PurchaseOrder.objects.create()
                    po_item = PurchaseOrderItemDetail(price=price_extension,
                                                    product=product_object,
                                                    quantity=1)
                    po.item_details.add(po_item, bulk=False)
                    po_item.save()
                    po.save()

                    # redirect to the poextend-detail form for payment
                    return redirect('lnpurchase:poextend-detail', pk=po.pk)

        else:
            raise Exception('Invalid action type. Use "buy" or "extend".')

    return  render(request, 'shop/landing.html', { 
            'hosts_tor_bridges': sorted(Host.active.filter(offers_tor_bridges=True), key=lambda t: t.sats_per_day_tor_bridge, reverse=True), 
            'hosts_nostr_aliases': sorted(Host.active.filter(offers_nostr_aliases=True), key=lambda t: t.sats_per_day_nostr_alias, reverse=True),
            'form_tb': form_tb,
            'form_na': form_na,
            'host_id': host_id,
            'submitted_product_type': submitted_product_type,
            'errors': errors,
            'productID': productID,
        })