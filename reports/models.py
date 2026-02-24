from django.db import models
from accounts.models import User

class SavedReport(models.Model):
    """
    Store generated reports
    """
    REPORT_TYPES = [
        ('daily', 'Daily Summary'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report'),
    ]
    
    name = models.CharField(max_length=200)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    parameters = models.JSONField()  # Store report parameters
    file = models.FileField(upload_to='reports/%Y/%m/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'saved_reports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.date()}"