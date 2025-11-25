from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Pages principales
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentification
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='loan_system/login.html'), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    
    # Profil
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    # Gestion des prêts
    path('loan-request/', views.loan_request, name='loan_request'),
    path('loan/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('download-certificate/<int:loan_id>/', views.download_certificate, name='download_certificate'),
    
    # Messagerie
    path('messages/', views.messages_list, name='messages_list'),
    path('messages/<int:message_id>/', views.message_detail, name='message_detail'),
    path('messages/send/', views.send_message, name='send_message'),
    path('messages/<int:message_id>/reply/', views.reply_message, name='reply_message'),
    path('messages/<int:message_id>/mark-read/', views.mark_message_read, name='mark_message_read'),
    path('admin-reply/<int:message_id>/', views.admin_reply_message, name='admin_reply_message'),
    path('api/unread-count/', views.get_unread_count, name='get_unread_count'),
    
    # Notifications
    path('notifications/', views.notifications_list, name='notifications_list'),
    path('notifications/<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('admin/send-notification/', views.send_notification, name='send_notification'),
    path('api/notification-count/', views.get_notification_count, name='get_notification_count'),
]