from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from accounts.models import User

class Patient(models.Model):
    """
    Patient demographic and identification information
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
        ('UNKNOWN', 'Unknown'),
    ]
    
    MARITAL_STATUS_CHOICES = [
        ('single', 'Single'),
        ('married', 'Married'),
        ('divorced', 'Divorced'),
        ('widowed', 'Widowed'),
    ]
    
    # Personal Information
    mrn = models.CharField(max_length=20, unique=True, verbose_name="Medical Record Number")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=10, choices=BLOOD_GROUP_CHOICES, default='UNKNOWN')
    
    # Contact Information
    phone_number = models.CharField(max_length=15, validators=[RegexValidator(r'^\+?254\d{9}$')])
    alternative_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    
    # Address
    county = models.CharField(max_length=100, default='Baringo')
    sub_county = models.CharField(max_length=100)
    village = models.CharField(max_length=200)
    landmark = models.CharField(max_length=200, blank=True)
    
    # Next of Kin
    next_of_kin_name = models.CharField(max_length=200)
    next_of_kin_relationship = models.CharField(max_length=50)
    next_of_kin_phone = models.CharField(max_length=15)
    
    # Medical Information
    allergies = models.TextField(blank=True, help_text="List any known allergies")
    chronic_conditions = models.TextField(blank=True)
    disabilities = models.TextField(blank=True)
    
    # Identification
    national_id = models.CharField(max_length=10, unique=True, null=True, blank=True)
    nhif_number = models.CharField(max_length=20, blank=True, verbose_name="NHIF Number")
    
    # System Fields
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_patients')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['mrn']),
            models.Index(fields=['last_name', 'first_name']),
        ]
    
    def __str__(self):
        return f"{self.mrn} - {self.full_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        today = timezone.now().date()
        born = self.date_of_birth
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
    
    def get_age_group(self):
        age = self.age
        if age < 1:
            return 'Infant'
        elif age < 5:
            return 'Toddler'
        elif age < 13:
            return 'Child'
        elif age < 18:
            return 'Adolescent'
        elif age < 60:
            return 'Adult'
        else:
            return 'Elderly'


class EmergencyContact(models.Model):
    """
    Additional emergency contacts
    """
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='emergency_contacts')
    name = models.CharField(max_length=200)
    relationship = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=15)
    is_primary = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'emergency_contacts'
    
    def __str__(self):
        return f"{self.name} - {self.relationship}"


class PatientDocument(models.Model):
    """
    Store scanned documents, IDs, consent forms
    """
    DOCUMENT_TYPES = [
        ('id', 'National ID'),
        ('nhif', 'NHIF Card'),
        ('birth', 'Birth Certificate'),
        ('consent', 'Consent Form'),
        ('lab', 'Lab Report'),
        ('other', 'Other'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to='patient_docs/%Y/%m/')
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True)
    
    class Meta:
        db_table = 'patient_documents'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.patient.mrn} - {self.title}"