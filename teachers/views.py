from django.shortcuts import render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min, Max
from django.utils import timezone
from .models import Teacher, Attendance, Salary
from .forms import TeacherForm, AttendanceForm


class TeacherListView(LoginRequiredMixin, ListView):
    model = Teacher
    template_name = 'teachers/teacher_list.html'
    context_object_name = 'teachers'

class TeacherDetailView(LoginRequiredMixin, DetailView):
    model = Teacher
    template_name = 'teachers/teacher_detail.html'

class TeacherCreateView(LoginRequiredMixin, CreateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')

class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')

class AttendanceCreateView(LoginRequiredMixin, CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'teachers/attendance_form.html'
    success_url = reverse_lazy('teachers:teacher_list')

class SalaryCalculationView(LoginRequiredMixin, View):
    def get(self, request):
        current_year = timezone.now().year
        current_month = timezone.now().month

        year = int(request.GET.get('year', current_year))
        month = int(request.GET.get('month', current_month))

        teachers = Teacher.objects.all()
        salary_data = []

        for teacher in teachers:
            work_days = Attendance.objects.filter(teacher=teacher, date__year=year, date__month=month).count()
            base_amount = teacher.base_salary * work_days if teacher.base_salary else 0
            additional_amount = teacher.additional_salary if teacher.additional_salary else 0
            total_amount = base_amount + additional_amount

            Salary.objects.update_or_create(
                teacher=teacher,
                year=year,
                month=month,
                defaults={
                    'work_days': work_days,
                    'base_amount': base_amount,
                    'additional_amount': additional_amount,
                    'total_amount': total_amount
                }
            )

            salary_data.append({
                'teacher': teacher,
                'work_days': work_days,
                'total_amount': total_amount
            })

        # 년도와 월 선택을 위한 옵션 생성
        years = range(current_year - 5, current_year + 1)  # 현재 년도부터 5년 전까지
        months = range(1, 13)

        context = {
            'year': year,
            'month': month,
            'salary_data': salary_data,
            'years': years,
            'months': months,
            'current_year': current_year,
            'current_month': current_month
        }
        return render(request, 'teachers/salary_calculation.html', context)
    

class SalaryTableView(LoginRequiredMixin, View):
    def get(self, request, year=None):
        if year is None:
            year = request.GET.get('year')
        
        if year is None:
            year = timezone.now().year
        else:
            year = int(year)
        
        teachers = Teacher.objects.all()
        months = range(1, 13)

        salary_table = []
        for teacher in teachers:
            teacher_data = {'teacher': teacher}
            total = 0
            for month in months:
                salary = Salary.objects.filter(teacher=teacher, year=year, month=month).first()
                amount = salary.total_amount if salary else 0
                teacher_data[month] = amount
                total += amount
            teacher_data['total'] = total
            salary_table.append(teacher_data)

        min_year = Salary.objects.aggregate(Min('year'))['year__min'] or timezone.now().year
        max_year = Salary.objects.aggregate(Max('year'))['year__max'] or timezone.now().year
        year_range = range(min_year, max_year + 1)

        context = {
            'year': year,
            'months': months,
            'salary_table': salary_table,
            'year_range': year_range,
        }
        return render(request, 'teachers/salary_table.html', context)