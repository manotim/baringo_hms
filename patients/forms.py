from django import forms
from .models import Patient, EmergencyContact, PatientDocument

class PatientRegistrationForm(forms.ModelForm):
    """
    Form for registering new patients
    """
    class Meta:
        model = Patient
        fields = '__all__'
        exclude = ['mrn', 'created_by', 'created_at', 'updated_at', 'is_active']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'chronic_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        # Make some fields optional
        self.fields['email'].required = False
        self.fields['middle_name'].required = False
        self.fields['alternative_phone'].required = False
        self.fields['national_id'].required = False
        self.fields['nhif_number'].required = False


class PatientSearchForm(forms.Form):
    """
    Form for searching patients
    """
    search_term = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by MRN, Name, or ID...'
        })
    )
    search_by = forms.ChoiceField(
        choices=[
            ('all', 'All Fields'),
            ('mrn', 'MRN'),
            ('name', 'Name'),
            ('id', 'National ID'),
            ('phone', 'Phone'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class EmergencyContactForm(forms.ModelForm):
    """
    Form for emergency contacts
    """
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'phone_number', 'is_primary']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})