from django.contrib import admin

from . models import *


# Pre-Populate Slug Fields
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug':('category_name',)}
    list_display = ('category_name','slug')     # Display Lists

admin.site.register(Category,CategoryAdmin)