from .models import category


def nav_categories(request):
    """Makes the category list available to the 'All category' nav dropdown
    on every page that uses the NewDesign base template."""
    return {'nav_categories': category.objects.all()}
