from django.db import models
class SiteSetting(models.Model):
    site_title = models.CharField(max_length=100, default="Marketplace")
    meta_description = models.TextField(blank=True, null=True)
    meta_keywords = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='photos/logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='photos/favicons/', blank=True, null=True)


def __str__(self):
    return "Site Setting"




class Meta:
    verbose_name = "Site Setting"
    verbose_name_plural = "Site Settings"
# Create your models here.
