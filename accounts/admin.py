from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import Account,UserProfile


class accountAdmin(UserAdmin):
    # Display columns in admin panel
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')

    list_display_links = ('email','first_name','last_name') # To Make clicable so that we want to see details to click on these columns

    readonly_fields = ('last_login','date_joined')  # Readonly Not Changeble

    ordering = ('-date_joined',)   # Descending Order

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()  # It make essential columns read only


admin.site.register(Account,accountAdmin)


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src="{}" width="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description = 'Profile Picture'
    list_display = ('thumbnail','user','country','city','state')

admin.site.register(UserProfile,UserProfileAdmin)