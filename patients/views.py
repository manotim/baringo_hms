from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Patient, PatientDocument
from .forms import PatientRegistrationForm, PatientSearchForm, EmergencyContactForm
from security.models import AuditLog

@login_required
def patient_list(request):
    """
    List all patients with search functionality
    """
    form = PatientSearchForm(request.GET or None)
    patients = Patient.objects.filter(is_active=True)
    
    if form.is_valid():
        search_term = form.cleaned_data.get('search_term')
        search_by = form.cleaned_data.get('search_by')
        
        if search_term:
            if search_by == 'mrn':
                patients = patients.filter(mrn__icontains=search_term)
            elif search_by == 'name':
                patients = patients.filter(
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(middle_name__icontains=search_term)
                )
            elif search_by == 'id':
                patients = patients.filter(national_id__icontains=search_term)
            elif search_by == 'phone':
                patients = patients.filter(phone_number__icontains=search_term)
            else:
                # Search all fields
                patients = patients.filter(
                    Q(mrn__icontains=search_term) |
                    Q(first_name__icontains=search_term) |
                    Q(last_name__icontains=search_term) |
                    Q(national_id__icontains=search_term) |
                    Q(phone_number__icontains=search_term)
                )
    
    # Pagination
    paginator = Paginator(patients, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'page_obj': page_obj,
        'patients': page_obj,
    }
    return render(request, 'patients/patient_list.html', context)


@login_required
def patient_detail(request, mrn):
    """
    View patient details
    """
    patient = get_object_or_404(Patient, mrn=mrn, is_active=True)
    
    # Log access for audit
    AuditLog.objects.create(
        user=request.user,
        action='VIEW',
        model_name='Patient',
        object_id=patient.id,
        details=f"Viewed patient: {patient.full_name}"
    )
    
    context = {
        'patient': patient,
        'recent_consultations': patient.consultation_set.all()[:5],
        'documents': patient.documents.all(),
    }
    return render(request, 'patients/patient_detail.html', context)


@login_required
def patient_register(request):
    """
    Register a new patient
    """
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            
            # Generate MRN (format: BCH-YYYY-XXXXX)
            year = timezone.now().year
            last_patient = Patient.objects.filter(
                mrn__startswith=f'BCH-{year}'
            ).order_by('-mrn').first()
            
            if last_patient:
                last_number = int(last_patient.mrn.split('-')[-1])
                new_number = last_number + 1
            else:
                new_number = 1
            
            patient.mrn = f'BCH-{year}-{new_number:05d}'
            patient.created_by = request.user
            patient.save()
            
            messages.success(request, f'Patient registered successfully! MRN: {patient.mrn}')
            
            # Log the action
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Patient',
                object_id=patient.id,
                details=f"Registered new patient: {patient.full_name}"
            )
            
            return redirect('patient_detail', mrn=patient.mrn)
    else:
        form = PatientRegistrationForm()
    
    return render(request, 'patients/patient_register.html', {'form': form})


@login_required
def patient_edit(request, mrn):
    """
    Edit patient information
    """
    patient = get_object_or_404(Patient, mrn=mrn, is_active=True)
    
    # Check permissions
    if not request.user.has_perm_patient_edit():
        messages.error(request, 'You do not have permission to edit patient records')
        return redirect('patient_detail', mrn=mrn)
    
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient information updated successfully')
            
            AuditLog.objects.create(
                user=request.user,
                action='UPDATE',
                model_name='Patient',
                object_id=patient.id,
                details=f"Updated patient: {patient.full_name}"
            )
            
            return redirect('patient_detail', mrn=mrn)
    else:
        form = PatientRegistrationForm(instance=patient)
    
    return render(request, 'patients/patient_edit.html', {'form': form, 'patient': patient})


@login_required
def patient_search_api(request):
    """
    AJAX endpoint for patient search
    """
    from django.http import JsonResponse
    
    term = request.GET.get('term', '')
    if len(term) < 2:
        return JsonResponse([], safe=False)
    
    patients = Patient.objects.filter(
        Q(mrn__icontains=term) |
        Q(first_name__icontains=term) |
        Q(last_name__icontains=term) |
        Q(national_id__icontains=term)
    )[:10]
    
    results = []
    for patient in patients:
        results.append({
            'id': patient.id,
            'mrn': patient.mrn,
            'name': patient.full_name,
            'age': patient.age,
            'gender': patient.get_gender_display(),
        })
    
    return JsonResponse(results, safe=False)