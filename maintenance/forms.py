from django import forms
from .models import Maintenance, Room
import datetime


class MonthYearWidget(forms.widgets.Widget):
    template_name = 'maintenance/month_year_widget.html'
    
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if value:
            if isinstance(value, datetime.date):
                value = value.strftime('%Y-%m')
            context['widget']['value'] = value
        return context



# class MaintenanceForm(forms.ModelForm):
#     class Meta:
#         model = Maintenance
#         fields = ['room', 'date', 'charge', 'date_paid', 'memo']
#         widgets = {
#             'room': forms.NumberInput(attrs={
#                 'min': '1',
#                 'class': 'form-control'
#             }),
#             'date': forms.DateInput(attrs={
#                 'type': 'month',
#                 'class': 'form-control'
#             }),
#             'charge': forms.NumberInput(attrs={
#                 'min': '0',
#                 'class': 'form-control'
#             }),
#             'date_paid': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control'
#             }),
#             'memo': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3
#             }),
#         }

#     def clean_date(self):
#         date = self.cleaned_data['date']
#         if isinstance(date, str):
#             try:
#                 year, month = map(int, date.split('-'))
#                 date = datetime.date(year, month, 1)
#             except ValueError:
#                 raise forms.ValidationError('올바른 년월 형식이 아닙니다.')
#         return date.replace(day=1)




class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['number', 'contract_start_date', 'contract_end_date', 'is_active']
        widgets = {
            'number': forms.NumberInput(attrs={
                'min': '1',
                'class': 'form-control'
            }),
            'contract_start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'contract_end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
        }


class MaintenanceForm(forms.ModelForm):
    room = forms.ModelChoiceField(
        queryset=None,  # __init__에서 설정
        label='호실',
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )

    date = forms.DateField(
        label='부과년월',
        widget=forms.DateInput(
            attrs={
                'type': 'month',
                'class': 'form-control'
            }
        ),
        input_formats=['%Y-%m'],
    )

    class Meta:
        model = Maintenance
        fields = ['room', 'date', 'charge', 'date_paid', 'memo']
        widgets = {
            'charge': forms.NumberInput(attrs={
                'min': '0',
                'step': '1',
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 활성화된 호실만 가져오기
        active_rooms = Room.objects.filter(is_active=True).order_by('number')
        self.fields['room'].queryset = active_rooms
        self.fields['room'].empty_label = None  # "-------" 제거

    def clean_date(self):
        date = self.cleaned_data['date']
        if isinstance(date, str):
            try:
                year, month = map(int, date.split('-'))
                date = datetime.date(year, month, 1)
            except ValueError:
                raise forms.ValidationError('올바른 년월 형식이 아닙니다.')
        return date.replace(day=1)

    def clean_charge(self):
        charge = self.cleaned_data['charge']
        if charge < 0:
            raise forms.ValidationError('금액은 0 이상이어야 합니다.')
        return charge