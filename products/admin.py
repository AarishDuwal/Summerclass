from django.contrib import admin
from django.utils.html import format_html
from .models import category, product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProductAdmin(admin.ModelAdmin):
    exclude = ('created_at',)

    list_display = (
        'id',
        'name',
        'price',
        'stock',
        'category',
        'status',
        'image_preview',
    )

    search_fields = ('name',)
    list_filter = ('category',)
    readonly_fields = ('image_preview',)

    def image_preview(self, obj):
        if obj.product_image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit: cover;" />',
                obj.product_image.url
            )
        return "No Image"

    image_preview.short_description = "Image"


admin.site.register(product, ProductAdmin)
admin.site.register(category, CategoryAdmin)