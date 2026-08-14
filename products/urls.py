from django.urls import path
from . import views

urlpatterns = [
    path('', views.products, name='products'),
    path('my-products/', views.my_products, name='my_products'),
    path('add-product/', views.add_product, name='add_product'),
    path('<int:id>/edit/', views.edit_product, name='edit_product'),
    path('<int:id>/toggle-status/', views.toggle_product_status, name='toggle_product_status'),
    path('<int:id>/', views.product_detail, name='product_detail'),
]