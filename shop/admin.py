from django.contrib import admin
import admin_thumbnails
from .models import Product,Variation,ReviewRating,ProductGallery


@admin_thumbnails.thumbnail('image') # Preview of product image in admin panel
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1
admin.site.register(ProductGallery)


class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name','category','price','stock','created_on','modified_on','is_available')
    prepopulated_fields = {'slug':('product_name',)}
    inlines = [ProductGalleryInline]
admin.site.register(Product,ProductAdmin)

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product','variation_category','variation_value','is_active')
    list_editable = ('is_active',)
    list_filter = ('product','variation_category','variation_value','is_active')
admin.site.register(Variation,VariationAdmin)


class ReviewRatingAdmin(admin.ModelAdmin):
    list_display = ('product','rating','status_flag','ip')
    list_editable = ('status_flag',)
    list_filter = ('rating','status_flag')
admin.site.register(ReviewRating,ReviewRatingAdmin)

