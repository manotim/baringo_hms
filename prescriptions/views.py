from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from consultations.models import Consultation
from .models import Prescription, PrescriptionItem, Medication
from .forms import PrescriptionForm, PrescriptionItemForm, MedicationSearchForm
from security.models import AuditLog

@login_required
def prescription_list(request):
    """
    List all prescriptions
    """
    prescriptions = Prescription.objects.all().select_related('patient', 'prescribed_by')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        prescriptions = prescriptions.filter(status=status)
    
    context = {
        'prescriptions': prescriptions.order_by('-prescribed_date')[:50],
    }
    return render(request, 'prescriptions/prescription_list.html', context)


@login_required
def prescription_detail(request, pk):
    """
    View prescription details
    """
    prescription = get_object_or_404(Prescription, pk=pk)
    
    context = {
        'prescription': prescription,
        'items': prescription.items.all(),
    }
    return render(request, 'prescriptions/prescription_detail.html', context)


@login_required
def new_prescription(request, consultation_id):
    """
    Create a new prescription from consultation
    """
    consultation = get_object_or_404(Consultation, pk=consultation_id)
    
    # Check if prescription already exists for this consultation
    if Prescription.objects.filter(consultation=consultation).exists():
        messages.warning(request, 'A prescription already exists for this consultation')
        return redirect('prescription_detail', pk=consultation.prescription.first().id)
    
    if request.method == 'POST':
        prescription_form = PrescriptionForm(request.POST)
        if prescription_form.is_valid():
            prescription = prescription_form.save(commit=False)
            prescription.consultation = consultation
            prescription.patient = consultation.patient
            prescription.prescribed_by = request.user
            prescription.save()
            
            messages.success(request, 'Prescription created successfully')
            
            AuditLog.objects.create(
                user=request.user,
                action='CREATE',
                model_name='Prescription',
                object_id=prescription.id,
                details=f"New prescription for patient: {consultation.patient.full_name}"
            )
            
            return redirect('add_prescription_item', prescription_id=prescription.id)
    else:
        prescription_form = PrescriptionForm()
    
    return render(request, 'prescriptions/prescription_form.html', {
        'form': prescription_form,
        'consultation': consultation,
    })


@login_required
def add_prescription_item(request, prescription_id):
    """
    Add items to a prescription
    """
    prescription = get_object_or_404(Prescription, pk=prescription_id)
    
    if request.method == 'POST':
        form = PrescriptionItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.prescription = prescription
            item.save()
            
            messages.success(request, 'Medication added to prescription')
            return redirect('add_prescription_item', prescription_id=prescription_id)
    else:
        form = PrescriptionItemForm()
    
    # Get existing items
    items = prescription.items.all()
    
    context = {
        'form': form,
        'prescription': prescription,
        'items': items,
    }
    return render(request, 'prescriptions/add_item.html', context)


@login_required
def dispense_medication(request, item_id):
    """
    Mark a prescription item as dispensed
    """
    if request.method == 'POST':
        item = get_object_or_404(PrescriptionItem, pk=item_id)
        
        if not item.is_dispensed:
            from django.utils import timezone
            item.is_dispensed = True
            item.dispensed_date = timezone.now()
            item.dispensed_by = request.user
            item.save()
            
            # Update prescription status
            prescription = item.prescription
            if all(i.is_dispensed for i in prescription.items.all()):
                prescription.status = 'dispensed'
            else:
                prescription.status = 'partial'
            prescription.save()
            
            messages.success(request, 'Medication dispensed successfully')
        else:
            messages.warning(request, 'Medication already dispensed')
    
    return redirect('prescription_detail', pk=item.prescription.id)


@login_required
def search_medications_api(request):
    """
    AJAX endpoint for medication search
    """
    term = request.GET.get('term', '')
    if len(term) < 2:
        return JsonResponse([], safe=False)
    
    medications = Medication.objects.filter(
        models.Q(name__icontains=term) |
        models.Q(generic_name__icontains=term) |
        models.Q(brand_name__icontains=term),
        is_active=True
    )[:15]
    
    results = []
    for med in medications:
        results.append({
            'id': med.id,
            'name': f"{med.name} {med.strength}",
            'strength': med.strength,
            'unit': med.unit,
            'route': med.route,
        })
    
    return JsonResponse(results, safe=False)