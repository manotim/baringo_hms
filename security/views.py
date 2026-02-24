from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from .models import AuditLog, LoginAttempt, DataBackup
from django.http import HttpResponse
import os
import subprocess
from django.conf import settings
from datetime import datetime

@login_required
@staff_member_required
def audit_logs(request):
    """
    View system audit logs
    """
    logs = AuditLog.objects.all().select_related('user')
    
    # Filter by user
    user_id = request.GET.get('user')
    if user_id:
        logs = logs.filter(user_id=user_id)
    
    # Filter by action
    action = request.GET.get('action')
    if action:
        logs = logs.filter(action=action)
    
    # Filter by date
    date = request.GET.get('date')
    if date:
        logs = logs.filter(timestamp__date=date)
    
    paginator = Paginator(logs, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logs': page_obj,
        'actions': AuditLog.ACTION_CHOICES,
    }
    return render(request, 'security/audit_logs.html', context)


@login_required
@staff_member_required
def create_backup(request):
    """
    Create database backup
    """
    if request.method == 'POST':
        # Create backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.sql"
        backup_path = os.path.join(settings.BASE_DIR, 'backups', filename)
        
        # Ensure backup directory exists
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # Run backup command (for SQLite)
        import sqlite3
        from django.core import serializers
        
        # Backup all data as JSON
        from django.apps import apps
        data = {}
        for model in apps.get_models():
            data[model.__name__] = list(model.objects.values())
        
        import json
        with open(backup_path.replace('.sql', '.json'), 'w') as f:
            json.dump(data, f, default=str)
        
        # Log backup creation
        DataBackup.objects.create(
            filename=filename,
            file_size=os.path.getsize(backup_path.replace('.sql', '.json')),
            created_by=request.user
        )
        
        return HttpResponse(f"Backup created: {filename}")
    
    return render(request, 'security/backup.html')