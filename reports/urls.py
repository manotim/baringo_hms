# reports/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main dashboard
    path('', views.report_dashboard, name='report_dashboard'),
    
    # Daily reports
    path('daily/', views.daily_report, name='daily_report'),
    
    # Monthly reports
    path('monthly/', views.monthly_report, name='monthly_report'),
    
    # You can add more report types as needed
    # path('weekly/', views.weekly_report, name='weekly_report'),
    # path('custom/', views.custom_report, name='custom_report'),
]