from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, reverse
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
        'quick_actions',
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

    def quick_actions(self, obj):
        return format_html(
            '<a class="button" href="{}">Approve</a>&nbsp;'
            '<a class="button" style="background:#ba2121;color:#fff;" href="{}">Reject</a>',
            reverse('admin:product_quick_approve', args=[obj.pk]),
            reverse('admin:product_quick_reject', args=[obj.pk]),
        )
    quick_actions.short_description = 'Quick actions'

    def get_urls(self):
        custom = [
            path(
                '<int:pk>/quick-approve/',
                self.admin_site.admin_view(self.quick_approve),
                name='product_quick_approve',
            ),
            path(
                '<int:pk>/quick-reject/',
                self.admin_site.admin_view(self.quick_reject),
                name='product_quick_reject',
            ),
        ]
        return custom + super().get_urls()

    def quick_approve(self, request, pk):
        product.objects.filter(pk=pk).update(approval_status=product.APPROVAL_APPROVED)
        self.message_user(request, 'Product approved.')
        return redirect('admin:products_product_changelist')

    def quick_reject(self, request, pk):
        product.objects.filter(pk=pk).update(approval_status=product.APPROVAL_REJECTED)
        self.message_user(request, 'Product rejected.')
        return redirect('admin:products_product_changelist')


admin.site.register(product, ProductAdmin)
admin.site.register(category, CategoryAdmin)