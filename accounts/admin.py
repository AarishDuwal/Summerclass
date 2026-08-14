from django.contrib import admin

from .models import Message, Profile, ProductRequest

admin.site.register(Profile)


@admin.register(ProductRequest)
class ProductRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'product', 'status', 'created_at')
    list_filter = ('status',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'recipient', 'subject', 'is_read', 'created_at')
    list_filter = ('is_read',)
