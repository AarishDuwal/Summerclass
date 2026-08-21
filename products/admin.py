from django.contrib import admin
from django.utils.html import format_html
from .models import category, product


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_count')
    search_fields = ('name',)

    def product_count(self, obj):
        return obj.product_set.count()
    product_count.short_description = 'Products'


class ProductAdmin(admin.ModelAdmin):
    exclude = ('created_at',)

    list_display = (
        'id',
        'name',
        'price',
        'stock',
        'category',
        'owner',
        'approval_status',
        'status',
        'image_preview',
    )

    search_fields = ('name',)
    list_filter = ('category', 'approval_status', 'status')
    readonly_fields = ('image_preview',)
    actions = ['approve_products', 'reject_products']

    def approve_products(self, request, queryset):
        updated = queryset.update(approval_status=product.APPROVAL_APPROVED)
        self.message_user(request, f'{updated} product(s) approved.')
    approve_products.short_description = 'Approve selected products'

    def reject_products(self, request, queryset):
        updated = queryset.update(approval_status=product.APPROVAL_REJECTED)
        self.message_user(request, f'{updated} product(s) rejected.')
    reject_products.short_description = 'Reject selected products'

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