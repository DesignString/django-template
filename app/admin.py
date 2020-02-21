from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from . import models

# Register your models here.
class UserAdmin(DjangoUserAdmin):
    list_display = ('email', 'first_name', 'last_name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'profile_pic')}),
        (_('Permissions'), {'fields': ('groups', 'user_permissions',)}),
        (_('More'), {'fields': ('is_active', 'is_superuser', 'is_staff', 'last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)
    search_fields = ('first_name', 'last_name', 'email')
    
admin.site.register(models.User, UserAdmin)
