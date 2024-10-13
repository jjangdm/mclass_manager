from django.shortcuts import render
from django.contrib.humanize.templatetags.humanize import intcomma

# Create your views here.
from django.views.generic import TemplateView
from django.db.models import Sum, DecimalField, CharField, Value
from django.db.models.functions import Cast, Substr, Concat
from django.db.models.fields import DateField
from .models import Teacher, MonthlySalary
from datetime import datetime

class TeacherSalaryView(TemplateView):
    template_name = 'teachers/teacher_salary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        teachers = Teacher.objects.all()
        salary_data = []
        for teacher in teachers:
            monthly_salaries = MonthlySalary.objects.filter(teacher=teacher).order_by('year_month')
            total_salary = monthly_salaries.aggregate(total=Sum('base_salary') + Sum('overtime_pay') + Sum('bonus') - Sum('deductions'))['total']
            salary_data.append({
                'teacher': teacher,
                'monthly_salaries': monthly_salaries,
                'total_salary': total_salary
            })
        context['salary_data'] = salary_data
        return context

class SalaryTotalView(TemplateView):
    template_name = 'teachers/salary_total.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        teachers = Teacher.objects.all()
        
        # year_month를 날짜로 변환
        date_cast = Cast(
            Concat(
                Substr('year_month', 1, 4),  # 년도
                Value('-'),
                Substr('year_month', 5, 2),  # 월
                Value('-01')  # 일 (항상 1일로 설정)
            ),
            DateField()
        )

        # 연도와 월 추출
        years = MonthlySalary.objects.annotate(
            date=date_cast
        ).dates('date', 'year', order='DESC').distinct()
        months = range(1, 13)

        salary_data = {}
        for year in years:
            salary_data[year.year] = {}
            for month in months:
                salary_data[year.year][month] = {teacher.name: 0 for teacher in teachers}
                salary_data[year.year][month]['total'] = 0

        salaries = MonthlySalary.objects.annotate(date=date_cast)
        for salary in salaries:
            if salary.date:
                year = salary.date.year
                month = salary.date.month
                total = salary.base_salary + salary.overtime_pay + salary.bonus - salary.deductions
                salary_data[year][month][salary.teacher.name] = total
                salary_data[year][month]['total'] += total
            else:
                print(f"Warning: Invalid date for salary id {salary.id}")

        context['salary_data'] = salary_data
        context['teachers'] = teachers
        context['years'] = years
        context['months'] = months
        # context['intcomma'] = intcomma  # 이 줄을 제거하거나 주석 처리
        return context
