from django.urls import path

from . import views

app_name = 'security'

urlpatterns = [
    path('', views.fake_admin_login, name='fake_admin_root'),
    path('login/', views.fake_admin_login, name='fake_admin_login'),
    # Catches anything else someone probes for under /admin/, e.g.
    # /admin/auth/user/, /admin/wp-login.php-style scans, etc. — all of it
    # just bounces to the same fake login, exactly like the real admin
    # would redirect an unauthenticated visitor.
    path('<path:sub_path>/', views.fake_admin_login, name='fake_admin_catchall'),
]
