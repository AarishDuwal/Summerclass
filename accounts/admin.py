from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import Message, Profile, ProductRequest


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'is_superuser', 'date_joined',
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined')
    actions = ['activate_users', 'deactivate_users']

    def activate_users(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} user(s) activated.')
    activate_users.short_description = 'Activate selected users'

    def deactivate_users(self, request, queryset):
        updated = queryset.exclude(id=request.user.id).update(is_active=False)
        self.message_user(request, f'{updated} user(s) deactivated.')
    deactivate_users.short_description = 'Deactivate selected users'


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'product', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('sender__username', 'sender__email', 'receiver__username', 'receiver__email', 'product__name')
    date_hierarchy = 'created_at'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('sender__username', 'recipient__username', 'subject', 'body')
    date_hierarchy = 'created_at'
