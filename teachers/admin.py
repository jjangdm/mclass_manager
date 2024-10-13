from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django.utils.formats import number_format
from .models import Teacher, Attendance, Salary

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'gender', 'hire_date', 'resignation_date')
    search_fields = ('name', 'phone_number', 'email')
    list_filter = ('gender', 'hire_date', 'resignation_date')


class AttendanceAdminForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = '__all__'
        widgets = {
            'check_in': forms.TimeInput(attrs={'type': 'time', 'value': '18:00'}),
            'check_out': forms.TimeInput(attrs={'type': 'time', 'value': '20:00'}),
        }

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    form = AttendanceAdminForm
    list_display = ('teacher', 'date', 'check_in', 'check_out')
    list_filter = ('date',)
    date_hierarchy = 'date'
    

class SalaryAdminForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = '__all__'
        widgets = {
            'year': forms.NumberInput(attrs={'min': 2000, 'max': 2100}),
            'month': forms.Select(choices=[(i, i) for i in range(1, 13)])
        }

@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    form = SalaryAdminForm
    list_display = ('teacher', 'year', 'month', 'work_days', 'formatted_base_amount', 'formatted_additional_amount', 'formatted_total_amount')
    list_filter = ('year', 'month')
    search_fields = ('teacher__name',)

    def formatted_base_amount(self, obj):
        return format_html('{}원', number_format(obj.base_amount, force_grouping=True))
    formatted_base_amount.short_description = '기본급'

    def formatted_additional_amount(self, obj):
        return format_html('{}원', number_format(obj.additional_amount, force_grouping=True))
    formatted_additional_amount.short_description = '추가급'

    def formatted_total_amount(self, obj):
        return format_html('{}원', number_format(obj.total_amount, force_grouping=True))
    formatted_total_amount.short_description = '총액'