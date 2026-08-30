from django.contrib import admin
from django.utils.html import format_html

from .models import LoginAttempt, ActivityEvent


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'path', 'success', 'honeypot_badge', 'attempted_at')
    list_filter = ('success', 'is_honeypot', 'attempted_at')
    search_fields = ('username', 'ip_address', 'user_agent', 'path')
    date_hierarchy = 'attempted_at'
    ordering = ('-attempted_at',)

    def honeypot_badge(self, obj):
        if obj.is_honeypot:
            return format_html('<span style="color:#fff;background:#ba2121;padding:2px 8px;border-radius:4px;">HONEYPOT</span>')
        return ''
    honeypot_badge.short_description = 'Flag'

    # This is an audit log — nobody should be able to create or edit
    # entries by hand, only view and (if needed) clear old ones.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(ActivityEvent)
class ActivityEventAdmin(admin.ModelAdmin):
    list_display = ('event_type', 'who', 'detail', 'ip_address', 'created_at')
    list_filter = ('event_type', 'created_at')
    search_fields = ('detail', 'ip_address', 'user__username', 'guest_id')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def who(self, obj):
        if obj.user:
            return obj.user.username
        if obj.guest_id:
            return f'Guest-{obj.guest_id[:6]}'
        return 'unknown'
    who.short_description = 'User'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
