from django.contrib import admin
from . models import category, product

# Register your models here.


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


class ProductAdmin(admin.ModelAdmin):
    exclude = ('created_at',)
    list_display = ('id', 'name', 'price', 'stock', 'category', 'status')

admin.site.register(product, ProductAdmin)
admin.site.register(category, CategoryAdmin)