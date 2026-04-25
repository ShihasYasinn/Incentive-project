from django import forms
from django.contrib.auth import get_user_model
from employees.models import MonthlyTarget, IncentiveSlab, LoadGrowthSlab

User = get_user_model()



class AnalystCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'}))
    
    class Meta:
        model = User
        fields = ['email', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'analyst@example.com'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = 'analyst'
        if commit:
            user.save()
        return user


class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx, .xls'}),
        help_text="Select an Excel file (.xlsx or .xls)"
    )
    report_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        help_text="Select the date for this report"
    )


class MonthlyTargetForm(forms.ModelForm):
    class Meta:
        model = MonthlyTarget
        fields = ['month', 'target_amount']
        widgets = {
            'month': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'target_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
        }


class IncentiveSlabForm(forms.ModelForm):
    class Meta:
        model = IncentiveSlab
        fields = ['load_slab', 'min_achievement_percent', 'max_achievement_percent', 'incentive_percent']
        widgets = {
            'load_slab': forms.Select(attrs={'class': 'form-control'}),
            'min_achievement_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 80'}),
            'max_achievement_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 89 (Optional)'}),
            'incentive_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 2.5'}),
        }


class LoadGrowthSlabForm(forms.ModelForm):
    class Meta:
        model = LoadGrowthSlab
        fields = ['load_slab', 'min_growth_percent', 'max_growth_percent', 'incentive_amount', 'deduction_percent']
        widgets = {
            'load_slab': forms.Select(attrs={'class': 'form-control'}),
            'min_growth_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 5.00'}),
            'max_growth_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 10.00 (Optional)'}),
            'incentive_amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Fixed amount (e.g. 3000)'}),
            'deduction_percent': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Percentage (e.g. 15 for degrowth)'}),
        }
