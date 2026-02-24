from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from patients.models import Patient
from .models import Consultation, LabOrder
from .forms import ConsultationForm, LabOrderForm
from security.models import AuditLog

@login_required
def consultation_list(request):
    """
    List all consultations
    """
    consultations = Consultation.objects.all().select_related('patient', 'doctor')
    
    # Filter by date if provided
    date_filter = request.GET.get('date')
    if date_filter:
        consultations = consultations.filter(visit_date=date_filter)
    
    # Filter by doctor if provided
    doctor_filter = request.GET.get('doctor')
    if doctor_filter and doctor_filter != 'all':
        consultations = consultations.filter(doctor_id=doctor_filter)
    
    context = {
        'consultations': consultations.order_by('-visit_date', '-visit_time')[:50],
        'today': timezone.now().date(),
    }
    return render(request, 'consultations/consultation_list.html', context)


@login_required
def consultation_detail(request, pk):
    """
    View consultation details
    """
    consultation = get_object_or_404(Consultation, pk=pk)
    
    context = {
        'consultation': consultation,
        'lab_orders': consultation.lab_orders.all(),
    }
    return render(request, 'consultations/consultation_detail.html', context)


@login_required
def new_consultation(request, mrn):
    """
    Create a new consultation for a patient
    """
    patient = get_object_or_404(Patient, mrn=mrn)
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST)
        if form.is_valid():
            consultation = form.save(commit=False)
            consultation.patient = patient
            consultation.doctor = request.user if request.user.role == 'doctor' else None
            consultation.created_by = request.user
            consultation.save()
            
            messages.success(request, 'Consultation recorded successfully')
            
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Consultation',
                object_id=consultation.id,
                details=f"New consultation for patient: {patient.full_name}"
            )
            
            return redirect('consultation_detail', pk=consultation.id)
    else:
        # Pre-populate with patient's last vitals if available
        last_consultation = patient.consultation_set.order_by('-visit_date').first()
        initial = {}
        if last_consultation:
            initial = {
                'temperature': last_consultation.temperature,
                'heart_rate': last_consultation.heart_rate,
                'blood_pressure_systolic': last_consultation.blood_pressure_systolic,
                'blood_pressure_diastolic': last_consultation.blood_pressure_diastolic,
                'weight': last_consultation.weight,
                'height': last_consultation.height,
            }
        form = ConsultationForm(initial=initial)
    
    return render(request, 'consultations/consultation_form.html', {
        'form': form,
        'patient': patient,
    })


@login_required
def order_lab_test(request, consultation_id):
    """
    Order lab tests for a consultation
    """
    consultation = get_object_or_404(Consultation, pk=consultation_id)
    
    if request.method == 'POST':
        form = LabOrderForm(request.POST)
        if form.is_valid():
            lab_order = form.save(commit=False)
            lab_order.consultation = consultation
            lab_order.ordered_by = request.user
            lab_order.save()
            
            messages.success(request, 'Lab test ordered successfully')
            return redirect('consultation_detail', pk=consultation_id)
    else:
        form = LabOrderForm()
    
    return render(request, 'consultations/lab_order_form.html', {
        'form': form,
        'consultation': consultation,
    })