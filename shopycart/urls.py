from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', include('admin_honeypot.urls',namespace='admin_honeypot')),
    path('secure/shopycart/pulkit-arora/superuser/', admin.site.urls),
    path('',include('mysite.urls')),
    path('store/',include('shop.urls')),
    path('cart/',include('cart.urls')),
    path('accounts/',include('accounts.urls')),
    path('orders/',include('orders.urls')),

] + static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)