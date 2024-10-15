from datetime import timedelta
from pyexpat.errors import messages
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min, Max
from django.utils import timezone
from .models import Teacher, Attendance, Salary
from .forms import BulkAttendanceForm, TeacherForm


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

class AttendanceCreateView(LoginRequiredMixin, View):
    def get(self, request):
        teachers = Teacher.objects.filter(is_active=True)
        form = BulkAttendanceForm(teachers=teachers)
        current_date = timezone.now().date()
        month_start = current_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        monthly_records = Attendance.objects.filter(date__range=[month_start, month_end]).order_by('teacher', 'date')
        
        teacher_records = {}
        for record in monthly_records:
            if record.teacher not in teacher_records:
                teacher_records[record.teacher] = {'records': [], 'total_hours': 0}
            
            if record.start_time and record.end_time:
                start_datetime = timezone.make_aware(timezone.datetime.combine(record.date, record.start_time))
                end_datetime = timezone.make_aware(timezone.datetime.combine(record.date, record.end_time))
                work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                record.work_hours = round(work_hours, 2)
                teacher_records[record.teacher]['total_hours'] += record.work_hours
            else:
                record.work_hours = None
            
            teacher_records[record.teacher]['records'].append(record)
        
        context = {
            'form': form,
            'teacher_records': teacher_records,
            'current_month': current_date.strftime('%Y년 %m월')
        }
        return render(request, 'teachers/attendance_form.html', context)

    def post(self, request):
        teachers = Teacher.objects.filter(is_active=True)
        form = BulkAttendanceForm(request.POST, teachers=teachers)
        if form.is_valid():
            date = form.cleaned_data['date']
            for teacher in teachers:
                is_present = form.cleaned_data.get(f'is_present_{teacher.id}', False)
                start_time = form.cleaned_data.get(f'start_time_{teacher.id}')
                end_time = form.cleaned_data.get(f'end_time_{teacher.id}')
                
                if is_present:
                    Attendance.objects.update_or_create(
                        teacher=teacher,
                        date=date,
                        defaults={
                            'is_present': True,
                            'start_time': start_time,
                            'end_time': end_time
                        }
                    )
                else:
                    Attendance.objects.filter(teacher=teacher, date=date).delete()
            
            request.session['message'] = '출근 기록이 성공적으로 저장되었습니다.'
            return redirect('teachers:attendance_create')
        
        # 폼이 유효하지 않은 경우, 에러와 함께 폼을 다시 렌더링
        current_date = timezone.now().date()
        context = {
            'form': form,
            'teacher_records': {},
            'current_month': current_date.strftime('%Y년 %m월')
        }
        return render(request, 'teachers/attendance_form.html', context)


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
            year = timezone.now().year
        
        teachers = Teacher.objects.filter(is_active=True)
        months = range(1, 13)

        salary_table = []
        for teacher in teachers:
            teacher_data = {'teacher': teacher}
            total = 0
            for month in months:
                start_date = timezone.datetime(year, month, 1)
                end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)
                
                attendances = Attendance.objects.filter(
                    teacher=teacher,
                    date__range=[start_date, end_date]
                )
                
                work_hours = sum(
                    (a.end_time.hour * 60 + a.end_time.minute) - (a.start_time.hour * 60 + a.start_time.minute)
                    for a in attendances if a.start_time and a.end_time
                ) / 60  # Convert minutes to hours
                
                salary = work_hours * (teacher.base_salary or 15000)  # Use 15000 as default if base_salary is not set
                teacher_data[month] = round(salary, 2)
                total += salary
            
            teacher_data['total'] = round(total, 2)
            salary_table.append(teacher_data)

        # 연도 범위 계산
        min_year = Attendance.objects.aggregate(Min('date'))['date__min']
        max_year = Attendance.objects.aggregate(Max('date'))['date__max']
        if min_year and max_year:
            year_range = range(min_year.year, max_year.year + 1)
        else:
            current_year = timezone.now().year
            year_range = range(current_year - 5, current_year + 1)

        context = {
            'year': year,
            'months': months,
            'salary_table': salary_table,
            'year_range': year_range,
        }
        return render(request, 'teachers/salary_table.html', context)