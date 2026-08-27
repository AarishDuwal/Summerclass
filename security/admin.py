from django.contrib import admin

from .models import LoginAttempt


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'ip_address', 'path', 'success', 'attempted_at')
    list_filter = ('success', 'attempted_at')
    search_fields = ('username', 'ip_address', 'user_agent', 'path')
    date_hierarchy = 'attempted_at'
    ordering = ('-attempted_at',)

    # This is an audit log — nobody should be able to create or edit
    # entries by hand, only view and (if needed) clear old ones.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
