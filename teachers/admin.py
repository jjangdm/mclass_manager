from django.contrib import admin
from django.utils.html import mark_safe
from django.urls import reverse
from django.utils import timezone
from django.db.models import Sum as DjangoSum
from .models import Teacher, MonthlySalary

class MonthlySalaryInline(admin.TabularInline):
    model = MonthlySalary
    extra = 0
    fields = ('year_month', 'base_salary', 'overtime_pay', 'bonus', 'deductions', 'total_salary_display', 'paid_date')
    readonly_fields = ('total_salary_display',)
    ordering = ('-year_month',)
    
    def total_salary_display(self, obj):
        return mark_safe(f'<strong>{obj.total_salary():,.0f}원</strong>')
    total_salary_display.short_description = '총 급여'

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'email', 'gender', 'hire_date', 'resignation_date', 'bank', 'account_number', 'total_salary_year_to_date')
    list_filter = ('gender', 'hire_date', 'resignation_date', 'bank')
    search_fields = ('name', 'phone_number', 'email')
    readonly_fields = ('id_number', 'salary_history_link')
    inlines = [MonthlySalaryInline]

    fieldsets = (
        ('기본 정보', {
            'fields': ('name', 'phone_number', 'email', 'gender')
        }),
        ('고용 정보', {
            'fields': ('hire_date', 'resignation_date')
        }),
        ('급여 정보', {
            'fields': ('bank', 'account_number', 'salary_history_link')
        }),
        ('보안 정보', {
            'fields': ('id_number',),
            'classes': ('collapse',)
        })
    )

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 이미 생성된 객체인 경우
            return self.readonly_fields + ('id_number',)
        return self.readonly_fields

    def total_salary_year_to_date(self, obj):
        year = timezone.now().year
        total = MonthlySalary.objects.filter(
            teacher=obj,
            year_month__year=year
        ).aggregate(
            total=DjangoSum('base_salary') + DjangoSum('overtime_pay') + DjangoSum('bonus') - DjangoSum('deductions')
        )['total'] or 0
        return mark_safe(f'<strong>{total:,.0f}원</strong>')
    total_salary_year_to_date.short_description = '올해 총 급여'

    def salary_history_link(self, obj):
        url = reverse('admin:teachers_monthlysalary_changelist') + f'?teacher__id__exact={obj.id}'
        return mark_safe(f'<a href="{url}">급여 내역 보기</a>')
    salary_history_link.short_description = '급여 내역'

@admin.register(MonthlySalary)
class MonthlySalaryAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'year_month', 'base_salary', 'overtime_pay', 'bonus', 'deductions', 'total_salary_display', 'paid_date')
    list_filter = ('year_month', 'paid_date', 'teacher')
    search_fields = ('teacher__name',)
    readonly_fields = ('total_salary_display',)

    fieldsets = (
        ('기본 정보', {
            'fields': ('teacher', 'year_month', 'paid_date')
        }),
        ('급여 정보', {
            'fields': ('base_salary', 'overtime_pay', 'bonus', 'deductions', 'total_salary_display')
        }),
    )

    def total_salary_display(self, obj):
        return mark_safe(f'<strong style="color: green;">{obj.total_salary():,.0f}원</strong>')
    total_salary_display.short_description = '총 급여'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('teacher')
        return queryset

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '월별 급여 목록'
        return super().changelist_view(request, extra_context=extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '월별 급여 추가'
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = '월별 급여 수정'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)