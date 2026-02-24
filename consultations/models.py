from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from patients.models import Patient
from accounts.models import User

class Consultation(models.Model):
    """
    Patient consultation/visit records
    """
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('waiting', 'Waiting'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    VISIT_TYPE_CHOICES = [
        ('new', 'New Patient'),
        ('follow_up', 'Follow-up'),
        ('emergency', 'Emergency'),
        ('review', 'Review'),
        ('referral', 'Referral'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'doctor'})
    visit_date = models.DateField(auto_now_add=True)
    visit_time = models.TimeField(auto_now_add=True)
    visit_type = models.CharField(max_length=20, choices=VISIT_TYPE_CHOICES, default='new')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Chief Complaint
    chief_complaint = models.TextField()
    history_presenting_illness = models.TextField(blank=True)
    
    # Vital Signs
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True, help_text="°C")
    heart_rate = models.IntegerField(null=True, blank=True, help_text="bpm", validators=[MinValueValidator(30), MaxValueValidator(200)])
    respiratory_rate = models.IntegerField(null=True, blank=True, help_text="breaths/min")
    blood_pressure_systolic = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(70), MaxValueValidator(250)])
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(40), MaxValueValidator(150)])
    oxygen_saturation = models.IntegerField(null=True, blank=True, help_text="%", validators=[MinValueValidator(50), MaxValueValidator(100)])
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="kg")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text="cm")
    bmi = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    
    # Clinical Findings
    physical_examination = models.TextField(blank=True)
    diagnosis = models.TextField()
    differential_diagnosis = models.TextField(blank=True)
    
    # Treatment Plan
    treatment_plan = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    
    # Follow-up
    follow_up_date = models.DateField(null=True, blank=True)
    follow_up_notes = models.TextField(blank=True)
    
    # System Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_consultations')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'consultations'
        ordering = ['-visit_date', '-visit_time']
        indexes = [
            models.Index(fields=['patient', 'visit_date']),
            models.Index(fields=['doctor', 'visit_date']),
        ]
    
    def __str__(self):
        return f"{self.patient.mrn} - {self.visit_date} - {self.doctor}"
    
    def save(self, *args, **kwargs):
        # Calculate BMI if weight and height are provided
        if self.weight and self.height:
            height_m = self.height / 100
            self.bmi = self.weight / (height_m * height_m)
        super().save(*args, **kwargs)


class Diagnosis(models.Model):
    """
    Structured diagnoses (can be ICD-10 coded)
    """
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='diagnoses')
    code = models.CharField(max_length=20, blank=True, help_text="ICD-10 Code")
    description = models.CharField(max_length=500)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'diagnoses'
    
    def __str__(self):
        return f"{self.code} - {self.description}"


class LabOrder(models.Model):
    """
    Laboratory test orders
    """
    PRIORITY_CHOICES = [
        ('routine', 'Routine'),
        ('urgent', 'Urgent'),
        ('stat', 'STAT'),
    ]
    
    STATUS_CHOICES = [
        ('ordered', 'Ordered'),
        ('collected', 'Sample Collected'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='lab_orders')
    test_name = models.CharField(max_length=200)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='routine')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ordered')
    ordered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='ordered_tests')
    ordered_date = models.DateTimeField(auto_now_add=True)
    clinical_notes = models.TextField(blank=True)
    
    # Results
    results = models.TextField(blank=True)
    result_date = models.DateTimeField(null=True, blank=True)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='performed_tests')
    
    class Meta:
        db_table = 'lab_orders'
    
    def __str__(self):
        return f"{self.test_name} - {self.consultation.patient.mrn}"