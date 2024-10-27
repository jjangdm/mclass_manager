from django.utils import timezone
from django import forms
from .models import Teacher

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['name', 'phone_number', 'email', 'hire_date', 'resignation_date', 
                 'base_salary', 'additional_salary', 'bank', 'account_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '이름을 입력하세요'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '전화번호를 입력하세요'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': '이메일을 입력하세요'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'resignation_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'base_salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '시급을 입력하세요'
            }),
            'additional_salary': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '추가 급여를 입력하세요'
            }),
            'bank': forms.Select(attrs={
                'class': 'form-input'
            }),
            'account_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '계좌번호를 입력하세요'
            })
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 필수가 아닌 필드들 설정
        self.fields['resignation_date'].required = False
        self.fields['additional_salary'].required = False
        self.fields['email'].required = False
        self.fields['bank'].required = False
        self.fields['account_number'].required = False

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
