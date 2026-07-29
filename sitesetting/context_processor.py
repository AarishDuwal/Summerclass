from . models import SiteSetting


def site_setting(request):
    site_setting = SiteSetting.objects.first()
    return {'site_setting': site_setting}