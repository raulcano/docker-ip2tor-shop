"""django_ip2tor URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from shop.views import index

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/v1/', include('shop.api.v1.urls', namespace='v1')),

    path('charged/lninvoice/', include('charged.lninvoice.urls')),
    path('charged/lnpurchase/', include('charged.lnpurchase.urls')),
    path('charged/lnnode/', include('charged.lnnode.urls')),

    path('shop/', include('shop.urls')),

    # path('', RedirectView.as_view(pattern_name='shop:host-list', permanent=False), name='index')
    path('', index, name="index")

]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = 'IP2Tor administration'    # default: "Django Administration"
admin.site.index_title = 'Main dashboard'           # default: "Site administration"
admin.site.site_title = 'IP2Tor site admin'         # default: "Django site admin"
