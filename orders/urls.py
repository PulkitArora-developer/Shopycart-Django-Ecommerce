from django.urls import path
from . import views


urlpatterns = [
    path('place_order/',views.place_order,name='place_order'),
    path('payments/',views.payments,name='payments'),
    path('success/<int:order_number>/',views.success,name='success'),


]
