from django.contrib import admin
from .models import *

class OrderProductInline(admin.TabularInline):
    model = OrderProduct
    extra = 0
    readonly_fields = ('user','product','quantity','variations','product_price','ordered')

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number','full_name','phone','email','is_ordered','zip_code','tax','order_total','status','ip_address','created_at']
    list_filter = ['status','is_ordered','created_at']
    search_fields = ['order_number','phone','email','zip_code','first_name','last_name']
    list_per_page = 20
    inlines = [OrderProductInline]

admin.site.register(Order,OrderAdmin)
admin.site.register(OrderProduct)
