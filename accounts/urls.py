from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='NewDesign/password_reset_form.html',
        email_template_name='NewDesign/password_reset_email.txt',
        subject_template_name='NewDesign/password_reset_subject.txt',
        success_url='/accounts/password-reset/done/',
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='NewDesign/password_reset_done.html',
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='NewDesign/password_reset_confirm.html',
        success_url='/accounts/reset/done/',
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='NewDesign/password_reset_complete.html',
    ), name='password_reset_complete'),

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
