from django import forms
from .models import Consultation, Diagnosis, LabOrder

class ConsultationForm(forms.ModelForm):
    """
    Form for creating/editing consultations
    """
    class Meta:
        model = Consultation
        exclude = ['created_by', 'created_at', 'updated_at', 'bmi']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'visit_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'follow_up_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'chief_complaint': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'history_presenting_illness': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'physical_examination': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'treatment_plan': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if not isinstance(self.fields[field].widget, (forms.CheckboxInput, forms.RadioSelect)):
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Make some fields optional
        self.fields['temperature'].required = False
        self.fields['heart_rate'].required = False
        self.fields['blood_pressure_systolic'].required = False
        self.fields['blood_pressure_diastolic'].required = False


class LabOrderForm(forms.ModelForm):
    """
    Form for ordering lab tests
    """
    class Meta:
        model = LabOrder
        fields = ['test_name', 'priority', 'clinical_notes']
        widgets = {
            'clinical_notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})