import datetime
from django import forms
from django.contrib import admin
from .models import Maintenance
from django.db.models import Sum

class MaintenanceAdminForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(
            attrs={'type': 'month'},
            format='%Y-%m'
        ),
        input_formats=['%Y-%m'],
    )

    class Meta:
        model = Maintenance
        fields = '__all__'
        widgets = {
            'room': forms.NumberInput(attrs={
                'min': '1',
                'step': '1',
            }),
            'charge': forms.NumberInput(attrs={
                'min': '0',
                'step': '1',
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

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    form = MaintenanceAdminForm
    list_display = ['room', 'formatted_date', 'formatted_charge', 'date_paid', 'payment_status']
    list_filter = ['room', 'date', 'date_paid']
    search_fields = ['room', 'memo']
    ordering = ['-date', 'room']
    date_hierarchy = 'date'

    def formatted_date(self, obj):
        return obj.date.strftime('%Y년 %m월')
    formatted_date.short_description = '부과년월'

    def formatted_charge(self, obj):
        return f"{obj.charge:,}원"
    formatted_charge.short_description = '부과금액'

    def payment_status(self, obj):
        return '납부완료' if obj.date_paid else '미납'
    payment_status.short_description = '납부상태'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        try:
            queryset = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response
        
        metrics = {
            'total_charge': queryset.aggregate(Sum('charge'))['charge__sum'] or 0,
            'total_count': queryset.count(),
        }
        response.context_data.update(metrics)
        return response