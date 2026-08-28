from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('order/<int:order_id>/', views.choose_payment, name='choose'),

    path('esewa/start/<int:order_id>/', views.esewa_start, name='esewa_start'),
    path('esewa/success/', views.esewa_success, name='esewa_success'),
    path('esewa/failure/', views.esewa_failure, name='esewa_failure'),

    path('khalti/start/<int:order_id>/', views.khalti_start, name='khalti_start'),
    path('khalti/callback/', views.khalti_callback, name='khalti_callback'),
]
