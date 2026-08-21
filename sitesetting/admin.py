from django.contrib import admin

from .models import SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_title',)

    def has_add_permission(self, request):
        # Singleton: only one row should ever exist (the site loads it via
        # SiteSetting.objects.first() in the context processor).
        return not SiteSetting.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
