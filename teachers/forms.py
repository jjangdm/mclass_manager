from django.utils import timezone
from django import forms
from .models import Teacher, Attendance

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'email', 'phone_number', 'base_salary', 'additional_salary', 'is_active', 'resignation_date']

    def clean(self):
        cleaned_data = super().clean()
        resignation_date = cleaned_data.get('resignation_date')
        is_active = cleaned_data.get('is_active')

        if resignation_date and resignation_date <= timezone.now().date():
            cleaned_data['is_active'] = False
        
        return cleaned_data

class AttendanceRecordForm(forms.Form):
    is_present = forms.BooleanField(required=False, initial=True, label='출근')
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=timezone.now().replace(hour=18, minute=0, second=0).time(),
        required=False,
        label='시작 시간'
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=timezone.now().replace(hour=20, minute=0, second=0).time(),
        required=False,
        label='종료 시간'
    )

class BulkAttendanceForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), initial=timezone.now)

    def __init__(self, *args, **kwargs):
        teachers = kwargs.pop('teachers', None)
        super().__init__(*args, **kwargs)
        
        if teachers:
            for teacher in teachers:
                self.fields[f'is_present_{teacher.id}'] = forms.BooleanField(required=False, initial=True, label=f'{teacher.name} 출근')
                self.fields[f'start_time_{teacher.id}'] = forms.TimeField(
                    widget=forms.TimeInput(attrs={'type': 'time'}),
                    initial=timezone.now().replace(hour=18, minute=0, second=0).time(),
                    required=False,
                    label=f'{teacher.name} 시작 시간'
                )
                self.fields[f'end_time_{teacher.id}'] = forms.TimeField(
                    widget=forms.TimeInput(attrs={'type': 'time'}),
                    initial=timezone.now().replace(hour=20, minute=0, second=0).time(),
                    required=False,
                    label=f'{teacher.name} 종료 시간'
                )
