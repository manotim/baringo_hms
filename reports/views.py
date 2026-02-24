from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Avg
from django.utils import timezone
from datetime import timedelta, datetime
from patients.models import Patient
from consultations.models import Consultation
from prescriptions.models import Prescription
from django.http import HttpResponse
import csv
import json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

@login_required
def report_dashboard(request):
    """
    Main reporting dashboard
    """
    context = {
        'today': timezone.now().date(),
        'total_patients': Patient.objects.filter(is_active=True).count(),
        'total_consultations': Consultation.objects.count(),
        'total_prescriptions': Prescription.objects.count(),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
def daily_report(request):
    """
    Generate daily statistics
    """
    date_str = request.GET.get('date')
    if date_str:
        report_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    else:
        report_date = timezone.now().date()
    
    # Daily statistics
    consultations = Consultation.objects.filter(visit_date=report_date)
    
    stats = {
        'date': report_date,
        'total_visits': consultations.count(),
        'new_patients': consultations.filter(visit_type='new').count(),
        'emergencies': consultations.filter(visit_type='emergency').count(),
        'follow_ups': consultations.filter(visit_type='follow_up').count(),
        'by_department': consultations.values('doctor__department').annotate(count=Count('id')),
        'top_diagnoses': consultations.values('diagnosis').annotate(count=Count('id')).order_by('-count')[:5],
    }
    
    if request.GET.get('format') == 'csv':
        return generate_csv_report(stats)
    elif request.GET.get('format') == 'pdf':
        return generate_pdf_report(stats)
    
    return render(request, 'reports/daily_report.html', {'stats': stats})


@login_required
def monthly_report(request):
    """
    Generate monthly statistics
    """
    year = int(request.GET.get('year', timezone.now().year))
    month = int(request.GET.get('month', timezone.now().month))
    
    start_date = datetime(year, month, 1).date()
    if month == 12:
        end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    # Monthly statistics
    consultations = Consultation.objects.filter(visit_date__range=[start_date, end_date])
    
    stats = {
        'year': year,
        'month': start_date.strftime('%B'),
        'total_visits': consultations.count(),
        'unique_patients': consultations.values('patient').distinct().count(),
        'avg_daily_visits': consultations.count() / 30 if consultations.count() > 0 else 0,
        'gender_distribution': consultations.values('patient__gender').annotate(count=Count('id')),
        'age_groups': get_age_distribution(consultations),
        'daily_trend': consultations.values('visit_date').annotate(count=Count('id')).order_by('visit_date'),
    }
    
    return render(request, 'reports/monthly_report.html', {'stats': stats})


def generate_csv_report(stats):
    """
    Generate CSV report
    """
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="report_{stats["date"]}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    writer.writerow(['Date', stats['date']])
    writer.writerow(['Total Visits', stats['total_visits']])
    writer.writerow(['New Patients', stats['new_patients']])
    writer.writerow(['Emergencies', stats['emergencies']])
    
    return response


def generate_pdf_report(stats):
    """
    Generate PDF report
    """
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="report_{stats["date"]}.pdf"'
    
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Add content
    styles = getSampleStyleSheet()
    title = Paragraph(f"Daily Report - {stats['date']}", styles['Title'])
    elements.append(title)
    
    # Create table
    data = [
        ['Metric', 'Value'],
        ['Total Visits', str(stats['total_visits'])],
        ['New Patients', str(stats['new_patients'])],
        ['Emergencies', str(stats['emergencies'])],
    ]
    
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    elements.append(table)
    doc.build(elements)
    
    return response


def get_age_distribution(consultations):
    """
    Helper function to calculate age distribution
    """
    age_groups = {'0-18': 0, '19-35': 0, '36-50': 0, '51+': 0}
    
    for consultation in consultations:
        age = consultation.patient.age
        if age <= 18:
            age_groups['0-18'] += 1
        elif age <= 35:
            age_groups['19-35'] += 1
        elif age <= 50:
            age_groups['36-50'] += 1
        else:
            age_groups['51+'] += 1
    
    return age_groups