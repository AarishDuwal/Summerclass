from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('dashboard/', views.dashboard, name='dashboard'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-sales/', views.my_sales, name='my_sales'),

    path('my-requests-sent/', views.requests_sent, name='requests_sent'),
    path('my-requests-received/', views.requests_received, name='requests_received'),
    path('requests/<int:request_id>/<str:action>/', views.request_respond, name='request_respond'),
    path('requests/product/<int:product_id>/send/', views.send_product_request, name='send_product_request'),

    path('messages/inbox/', views.messages_inbox, name='messages_inbox'),
    path('messages/sent/', views.messages_sent, name='messages_sent'),
    path('messages/<int:message_id>/read/', views.message_mark_read, name='message_mark_read'),
    path('messages/compose/<int:recipient_id>/', views.send_message, name='send_message'),

    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('change-password/', views.change_password, name='change_password'),
]
