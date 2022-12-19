from django.urls import path

from . import views

app_name = 'lnnode'

urlpatterns = [
    path('<uuid:pk>/alive', views.check_if_node_is_alive),
]
 