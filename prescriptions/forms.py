from django import forms
from .models import Prescription, PrescriptionItem, Medication

class PrescriptionForm(forms.ModelForm):
    """
    Main prescription form
    """
    class Meta:
        model = Prescription
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }


class PrescriptionItemForm(forms.ModelForm):
    """
    Form for individual prescription items
    """
    class Meta:
        model = PrescriptionItem
        fields = ['medication', 'dosage', 'frequency', 'route', 'duration', 
                 'duration_unit', 'quantity', 'refills', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Limit medication choices to active ones
        self.fields['medication'].queryset = Medication.objects.filter(is_active=True)


class MedicationSearchForm(forms.Form):
    """
    Search medications
    """
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search medications...'
        })
    )