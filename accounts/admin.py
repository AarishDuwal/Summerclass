from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from .models import Message, Profile, ProductRequest


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0


class UserAdmin(BaseUserAdmin):
    inlines = [ProfileInline]

    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_active', 'is_staff', 'is_superuser', 'date_joined', 'quick_actions',
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

    def quick_actions(self, obj):
        if obj.is_active:
            return format_html(
                '<a class="button" style="background:#ba2121;color:#fff;" href="{}">Deactivate</a>',
                reverse('admin:user_quick_deactivate', args=[obj.pk]),
            )
        return format_html(
            '<a class="button" href="{}">Activate</a>',
            reverse('admin:user_quick_activate', args=[obj.pk]),
        )
    quick_actions.short_description = 'Quick actions'

    def get_urls(self):
        custom = [
            path(
                '<int:pk>/quick-activate/',
                self.admin_site.admin_view(self.quick_activate),
                name='user_quick_activate',
            ),
            path(
                '<int:pk>/quick-deactivate/',
                self.admin_site.admin_view(self.quick_deactivate),
                name='user_quick_deactivate',
            ),
        ]
        return custom + super().get_urls()

    def quick_activate(self, request, pk):
        User.objects.filter(pk=pk).update(is_active=True)
        self.message_user(request, 'User activated.')
        return redirect('admin:auth_user_changelist')

    def quick_deactivate(self, request, pk):
        User.objects.filter(pk=pk).exclude(pk=request.user.id).update(is_active=False)
        self.message_user(request, 'User deactivated.')
        return redirect('admin:auth_user_changelist')


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
