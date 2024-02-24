from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account
# Register your models here.


class AccountAdmin(UserAdmin):
    list_display        = ('email','username','last_login','joined_on','is_active')
    list_display_links  = ('email',)
    readonly_fields     = ('last_login','joined_on')
    ordering            = ('-joined_on',)

    filter_horizontal   = ()
    list_filter         = ()
    fieldsets           = ()



    
admin.site.register(Account,AccountAdmin)