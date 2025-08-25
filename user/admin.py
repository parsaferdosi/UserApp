from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Account

class AccountAdmin(UserAdmin):
    # Customizing the admin interface for the Account model
    list_display = ('email', 'username', 'is_active', 'is_staff',)
    list_filter = ('is_active', 'is_staff',)
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone_number', 'birth_date', 'bio', 'profile_picture')}),
        ('Permissions', {'fields': ('groups', 'user_permissions','is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('created_at', 'last_updated')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
        ),
    )
    filter_horizontal = ()
    readonly_fields = ('created_at', 'last_updated')

admin.site.register(Account, AccountAdmin)