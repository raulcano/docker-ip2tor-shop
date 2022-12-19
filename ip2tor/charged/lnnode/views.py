from charged.lnnode.models import LndGRpcNode
from charged.lnnode.tasks import node_alive_check
from django.shortcuts import render
from django.http import HttpResponse



def check_if_node_is_alive(request, pk):
    node_alive_check.apply_async(priority=0, args=(pk,), countdown=1)
    return render(request, 'alive.html', {'pk': pk})
