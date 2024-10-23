from django import forms
from .models import Maintenance
import datetime

class MaintenanceForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'month', 'class': 'form-control'},
            format='%Y-%m'
        ),
        input_formats=['%Y-%m'],
    )

    class Meta:
        model = Maintenance
        fields = ['room', 'date', 'charge', 'date_paid', 'memo']
        widgets = {
            'room': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control'
            }),
            'charge': forms.NumberInput(attrs={
                'min': '0',
                'class': 'form-control'
            }),
            'date_paid': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'memo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }

    def clean_date(self):
        date = self.cleaned_data['date']
        if isinstance(date, str):
            try:
                year, month = map(int, date.split('-'))
                date = datetime.date(year, month, 1)
            except ValueError:
                raise forms.ValidationError('올바른 년월 형식이 아닙니다.')
        return date.replace(day=1)