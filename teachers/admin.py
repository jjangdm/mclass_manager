from django.contrib import admin
from .models import Teacher, TeacherSalary

class TeacherSalaryInline(admin.TabularInline):
    model = TeacherSalary
    extra = 1

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'hire_date', 'get_employment_status')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('gender', 'hire_date')
    inlines = [TeacherSalaryInline]

    def get_employment_status(self, obj):
        return '재직 중' if obj.resignation_date is None else '퇴사'
    get_employment_status.short_description = '근무 상태'

@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'month', 'amount', 'paid_date')
    list_filter = ('month', 'paid_date')
    search_fields = ('teacher__name',)