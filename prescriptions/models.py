from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient
from consultations.models import Consultation
from accounts.models import User

class Medication(models.Model):
    """
    Medication catalog
    """
    UNIT_CHOICES = [
        ('tablet', 'Tablet'),
        ('capsule', 'Capsule'),
        ('ml', 'Milliliter'),
        ('mg', 'Milligram'),
        ('g', 'Gram'),
        ('drop', 'Drop'),
        ('inhalation', 'Inhalation'),
        ('suppository', 'Suppository'),
    ]
    
    ROUTE_CHOICES = [
        ('oral', 'Oral'),
        ('iv', 'Intravenous'),
        ('im', 'Intramuscular'),
        ('sc', 'Subcutaneous'),
        ('topical', 'Topical'),
        ('inhaled', 'Inhaled'),
        ('rectal', 'Rectal'),
    ]
    
    name = models.CharField(max_length=200)
    generic_name = models.CharField(max_length=200, blank=True)
    brand_name = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=100, blank=True)
    strength = models.CharField(max_length=50, help_text="e.g., 500mg")
    unit = models.CharField(max_length=20, choices=UNIT_CHOICES, default='tablet')
    route = models.CharField(max_length=20, choices=ROUTE_CHOICES, default='oral')
    side_effects = models.TextField(blank=True)
    contraindications = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'medications'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} {self.strength}"


class Prescription(models.Model):
    """
    Patient prescriptions
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('dispensed', 'Dispensed'),
        ('partial', 'Partially Dispensed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    prescribed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='prescribed_meds')
    prescribed_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'prescriptions'
        ordering = ['-prescribed_date']
    
    def __str__(self):
        return f"Prescription for {self.patient.full_name} on {self.prescribed_date.date()}"


class PrescriptionItem(models.Model):
    """
    Individual medication items in a prescription
    """
    FREQUENCY_CHOICES = [
        ('od', 'Once daily'),
        ('bd', 'Twice daily'),
        ('tds', 'Three times daily'),
        ('qds', 'Four times daily'),
        ('prn', 'As needed'),
        ('stat', 'Immediately'),
        ('nocte', 'At night'),
    ]
    
    DURATION_UNIT_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
    ]
    
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medication = models.ForeignKey(Medication, on_delete=models.PROTECT)
    dosage = models.CharField(max_length=100, help_text="e.g., 1 tablet")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    duration = models.IntegerField(validators=[MinValueValidator(1)])
    duration_unit = models.CharField(max_length=20, choices=DURATION_UNIT_CHOICES, default='days')
    route = models.CharField(max_length=20, choices=Medication.ROUTE_CHOICES, default='oral')
    instructions = models.TextField(blank=True)
    quantity = models.IntegerField(validators=[MinValueValidator(1)], help_text="Total quantity dispensed")
    refills = models.IntegerField(default=0)
    is_dispensed = models.BooleanField(default=False)
    dispensed_date = models.DateTimeField(null=True, blank=True)
    dispensed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='dispensed_items')
    
    class Meta:
        db_table = 'prescription_items'
    
    def __str__(self):
        return f"{self.medication.name} - {self.dosage} {self.frequency}"