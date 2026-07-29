from django.contrib import admin
from .models import Blog


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'title',
        'author',
        'published_date',
    )

    search_fields = (
        'title',
        'author',
    )

    list_filter = (
        'published_date',
    )