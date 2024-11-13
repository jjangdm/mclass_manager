# forms.py
from django import forms
from .models import Student


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name', 'school', 'grade', 'phone_number', 'email',
            'gender', 'parent_phone', 'receipt_number', 'interview_date',
            'interview_score', 'interview_info', 'first_class_date',
            'quit_date', 'etc', 'personal_file'
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '이름을 입력하세요'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '학생 전화번호를 입력하세요'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': '이메일을 입력하세요'
            }),
            'parent_phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '부모님 전화번호를 입력하세요'
            }),
            'receipt_number': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '현금영수증용 번호를 입력하세요'
            }),
            'interview_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'interview_score': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '인터뷰 평가를 입력하세요',
                'min': 1,
                'max' : 10
            }),
            'interview_info': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': '인터뷰 정보를 입력하세요',
                'style': 'height: 100px;'
            }),
            'first_class_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'quit_date': forms.DateInput(attrs={
                'class': 'form-input',
                'type': 'date'
            }),
            'etc': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': '기타 정보를 입력하세요'
            }),
            'personal_file': forms.FileInput(attrs={
                'class': 'form-input'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 필수가 아닌 필드들 설정
        self.fields['school'].required = False
        self.fields['grade'].required = False
        self.fields['email'].required = False
        self.fields['gender'].required = False
        self.fields['parent_phone'].required = False
        self.fields['receipt_number'].required = False
        self.fields['interview_date'].required = False
        self.fields['interview_info'].required = False
        self.fields['first_class_date'].required = False
        self.fields['quit_date'].required = False
        self.fields['etc'].required = False
        self.fields['personal_file'].required = False


class StudentImportForm(forms.Form):
    file = forms.FileField(
        label='파일 업로드',
        help_text='허용된 확장자: .xlsx, .xls, .csv',
    )

    def clean_file(self):
        file = self.cleaned_data['file']
        ext = file.name.split('.')[-1].lower()
        
        if ext not in ['xlsx', 'xls', 'csv']:
            raise forms.ValidationError('엑셀 파일(.xlsx, .xls) 또는 CSV 파일(.csv)만 업로드 가능합니다.')
        
        return file