import os
import django
import random
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'baringo_hms.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import User
from patients.models import Patient
from consultations.models import Consultation
from prescriptions.models import Medication, Prescription, PrescriptionItem
from django.utils import timezone

def create_users():
    """Create initial users"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@baringohospital.go.ke',
            'password': 'Admin@2026',
            'first_name': 'John',
            'last_name': 'Admin',
            'role': 'admin',
            'employee_id': 'AD001',
            'department': 'Administration',
            'phone_number': '+254700000001',
        },
        {
            'username': 'doctor1',
            'email': 'doctor1@baringohospital.go.ke',
            'password': 'Doctor@2026',
            'first_name': 'Sarah',
            'last_name': 'Kimani',
            'role': 'doctor',
            'employee_id': 'DOC001',
            'department': 'Internal Medicine',
            'phone_number': '+254700000002',
        },
        {
            'username': 'doctor2',
            'email': 'doctor2@baringohospital.go.ke',
            'password': 'Doctor@2026',
            'first_name': 'James',
            'last_name': 'Omondi',
            'role': 'doctor',
            'employee_id': 'DOC002',
            'department': 'Pediatrics',
            'phone_number': '+254700000003',
        },
        {
            'username': 'nurse1',
            'email': 'nurse1@baringohospital.go.ke',
            'password': 'Nurse@2026',
            'first_name': 'Mary',
            'last_name': 'Wanjiku',
            'role': 'nurse',
            'employee_id': 'NUR001',
            'department': 'Emergency',
            'phone_number': '+254700000004',
        },
        {
            'username': 'records',
            'email': 'records@baringohospital.go.ke',
            'password': 'Records@2026',
            'first_name': 'Peter',
            'last_name': 'Kipchoge',
            'role': 'records_officer',
            'employee_id': 'REC001',
            'department': 'Records',
            'phone_number': '+254700000005',
        },
        {
            'username': 'pharmacist',
            'email': 'pharmacy@baringohospital.go.ke',
            'password': 'Pharm@2026',
            'first_name': 'Lucy',
            'last_name': 'Akinyi',
            'role': 'pharmacist',
            'employee_id': 'PHA001',
            'department': 'Pharmacy',
            'phone_number': '+254700000006',
        },
    ]
    
    for user_data in users_data:
        password = user_data.pop('password')
        user, created = User.objects.get_or_create(
            username=user_data['username'],
            defaults=user_data
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created user: {user.username}")
        else:
            print(f"User already exists: {user.username}")

def create_medications():
    """Create medication catalog"""
    medications = [
        {
            'name': 'Paracetamol',
            'generic_name': 'Acetaminophen',
            'strength': '500mg',
            'unit': 'tablet',
            'route': 'oral',
            'category': 'Analgesic',
        },
        {
            'name': 'Amoxicillin',
            'generic_name': 'Amoxicillin',
            'strength': '500mg',
            'unit': 'capsule',
            'route': 'oral',
            'category': 'Antibiotic',
        },
        {
            'name': 'Ibuprofen',
            'generic_name': 'Ibuprofen',
            'strength': '400mg',
            'unit': 'tablet',
            'route': 'oral',
            'category': 'NSAID',
        },
        {
            'name': 'Metformin',
            'generic_name': 'Metformin Hydrochloride',
            'strength': '500mg',
            'unit': 'tablet',
            'route': 'oral',
            'category': 'Antidiabetic',
        },
        {
            'name': 'Lisinopril',
            'generic_name': 'Lisinopril',
            'strength': '10mg',
            'unit': 'tablet',
            'route': 'oral',
            'category': 'Antihypertensive',
        },
        {
            'name': 'Salbutamol Inhaler',
            'generic_name': 'Albuterol',
            'strength': '100mcg',
            'unit': 'inhalation',
            'route': 'inhaled',
            'category': 'Bronchodilator',
        },
        {
            'name': 'ORS',
            'generic_name': 'Oral Rehydration Salts',
            'strength': '20.5g',
            'unit': 'sachet',
            'route': 'oral',
            'category': 'Electrolyte',
        },
        {
            'name': 'Artemether/Lumefantrine',
            'generic_name': 'Coartem',
            'strength': '20/120mg',
            'unit': 'tablet',
            'route': 'oral',
            'category': 'Antimalarial',
        },
        {
            'name': 'Ceftriaxone Injection',
            'generic_name': 'Ceftriaxone',
            'strength': '1g',
            'unit': 'ml',
            'route': 'iv',
            'category': 'Antibiotic',
        },
        {
            'name': 'Omeprazole',
            'generic_name': 'Omeprazole',
            'strength': '20mg',
            'unit': 'capsule',
            'route': 'oral',
            'category': 'PPI',
        },
    ]
    
    for med_data in medications:
        med, created = Medication.objects.get_or_create(
            name=med_data['name'],
            defaults=med_data
        )
        if created:
            print(f"Created medication: {med.name}")

def create_sample_patients():
    """Create sample patients"""
    first_names = ['John', 'Jane', 'Peter', 'Mary', 'David', 'Sarah', 'Michael', 'Grace', 'Paul', 'Esther']
    last_names = ['Kamau', 'Odhiambo', 'Kiprop', 'Wambui', 'Otieno', 'Akinyi', 'Mwangi', 'Chebet', 'Omondi', 'Jerono']
    
    doctors = User.objects.filter(role='doctor')
    
    patients = []
    for i in range(20):
        # Generate random date of birth (between 1 and 80 years ago)
        years_ago = random.randint(1, 80)
        dob = date.today() - timedelta(days=years_ago*365 + random.randint(0, 365))
        
        patient = Patient(
            mrn=f"BCH-2026-{i+1:05d}",
            first_name=random.choice(first_names),
            last_name=random.choice(last_names),
            date_of_birth=dob,
            gender=random.choice(['M', 'F']),
            phone_number=f"+2547{random.randint(10000000, 99999999)}",
            county='Baringo',
            sub_county=random.choice(['Kabarnet', 'Eldama Ravine', 'Mogotio', 'Marigat']),
            village=f"Village {i+1}",
            next_of_kin_name=f"Next of Kin {i+1}",
            next_of_kin_relationship=random.choice(['Spouse', 'Parent', 'Child', 'Sibling']),
            next_of_kin_phone=f"+2547{random.randint(10000000, 99999999)}",
            blood_group=random.choice(['A+', 'A-', 'B+', 'B-', 'O+', 'O-']),
            allergies=random.choice(['', 'Penicillin', 'NSAIDs', 'None']) if i % 3 == 0 else '',
        )
        patients.append(patient)
    
    Patient.objects.bulk_create(patients)
    print(f"Created {len(patients)} patients")
    
    # Create some consultations
    for patient in Patient.objects.all()[:10]:
        for j in range(random.randint(1, 3)):
            Consultation.objects.create(
                patient=patient,
                doctor=random.choice(doctors),
                visit_type=random.choice(['new', 'follow_up', 'emergency']),
                chief_complaint=random.choice([
                    'Fever and headache',
                    'Cough and cold',
                    'Abdominal pain',
                    'Malaria symptoms',
                    'Hypertension check',
                ]),
                diagnosis=random.choice([
                    'Malaria',
                    'Upper respiratory infection',
                    'Hypertension',
                    'Gastroenteritis',
                    'Diabetes',
                ]),
                temperature=random.uniform(36.0, 39.0),
                heart_rate=random.randint(60, 100),
                blood_pressure_systolic=random.randint(100, 160),
                blood_pressure_diastolic=random.randint(60, 100),
                created_by=random.choice(doctors),
            )
    print("Created sample consultations")

def run():
    """Main seed function"""
    print("Starting database seeding...")
    create_users()
    create_medications()
    create_sample_patients()
    print("Seeding completed!")

if __name__ == '__main__':
    run()