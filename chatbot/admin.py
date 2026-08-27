from django.contrib import admin

from .models import ChatQuery


@admin.register(ChatQuery)
class ChatQueryAdmin(admin.ModelAdmin):
    list_display = ('message', 'user', 'session_key', 'matched_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('message', 'user__email', 'session_key')
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
