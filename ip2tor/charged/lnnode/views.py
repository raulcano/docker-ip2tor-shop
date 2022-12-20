from charged.lnnode.tasks import node_alive_check
from charged.utils import dynamic_import_class
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse



def check_if_node_is_alive(request, pk):
    
    module_name = 'charged.lnnode.models'
    found = False

    for lndnode_class in getattr(settings, 'CHARGED_LNDNODE_IMPLEMENTING_CLASSES'):
        TempNode = dynamic_import_class(module_name, lndnode_class)
        if TempNode.objects.filter(pk=pk).exists():
            found = True
            node = TempNode.objects.filter(pk=pk).first()

    if found:
        status, info = node.check_alive_status()
    else:
        status = False
        info = "The node does not exist in our database"
    
    
    # node_alive_check.apply_async(priority=0, args=(pk,), countdown=1)
    
    return render(request, 'alive.html', {'pk': pk, 'status': status, 'info': info})
