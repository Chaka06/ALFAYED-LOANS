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
    
    # Gestion des prêts
    path('loan-request/', views.loan_request, name='loan_request'),
    path('loan/<int:loan_id>/', views.loan_detail, name='loan_detail'),
    path('download-certificate/<int:loan_id>/', views.download_certificate, name='download_certificate'),
]