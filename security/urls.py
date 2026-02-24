# security/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Audit logs
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    
    # Database backup
    path('backup/', views.create_backup, name='create_backup'),
    path('backup/create/', views.create_backup, name='create_backup_post'),  # For POST requests
    
    # You might also want to add:
    # path('backup/list/', views.backup_list, name='backup_list'),
    # path('backup/download/<int:backup_id>/', views.download_backup, name='download_backup'),
    # path('login-attempts/', views.login_attempts, name='login_attempts'),
]