from django import forms
from .models import Teacher, Attendance

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'phone_number', 'email', 'gender', 'hire_date', 'resignation_date',
                  'bank', 'account_number', 'base_salary', 'additional_salary', 'other_info']
        widgets = {
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'resignation_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['teacher', 'date', 'check_in', 'check_out']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'check_in': forms.TimeInput(attrs={'type': 'time'}),
            'check_out': forms.TimeInput(attrs={'type': 'time'}),
        }