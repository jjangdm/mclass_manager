from datetime import timedelta
from io import BytesIO
from pyexpat.errors import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Min, Max
from django.utils import timezone
from .models import Teacher, Attendance, Salary
from .forms import BulkAttendanceForm, TeacherForm
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


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

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_active_status()
        return response

class TeacherUpdateView(LoginRequiredMixin, UpdateView):
    model = Teacher
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    success_url = reverse_lazy('teachers:teacher_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.update_active_status()
        return response

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
            form.save()
            messages.success(request, '출근 기록이 성공적으로 저장되었습니다.')
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

        teachers = Teacher.objects.filter(is_active=True)
        salary_data = []

        for teacher in teachers:
            start_date = timezone.datetime(year, month, 1)
            end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            if teacher.resignation_date and start_date <= teacher.resignation_date <= end_date:
                work_days = Attendance.objects.filter(
                    teacher=teacher, 
                    date__year=year, 
                    date__month=month,
                    date__lte=teacher.resignation_date
                ).count()
            else:
                work_days = Attendance.objects.filter(
                    teacher=teacher, 
                    date__year=year, 
                    date__month=month
                ).count()

            base_amount = teacher.base_salary * work_days * 2 if teacher.base_salary else 0
            additional_amount = teacher.additional_salary if teacher.additional_salary else 0
            total_amount = base_amount + additional_amount

            salary_data.append({
                'teacher': teacher,
                'work_days': work_days,
                'total_amount': total_amount,
                'bank_name': teacher.bank.name if teacher.bank else '',  # 은행명 추가
                'account_number': teacher.account_number,  # 계좌번호 추가
                'work_hours': work_days * 8  # 근무시간 추가 (1일 8시간 근무 가정)
            })

        total_salary = sum(data['total_amount'] for data in salary_data)  # 급여 합계 계산

        years = range(current_year - 5, current_year + 1)
        months = range(1, 13)

        context = {
            'year': year,
            'month': month,
            'salary_data': salary_data,
            'years': years,
            'months': months,
            'current_year': current_year,
            'current_month': current_month,
            'total_salary': total_salary,
        }
        return render(request, 'teachers/salary_calculation.html', context)
    

class SalaryTableView(LoginRequiredMixin, View):
    def get(self, request, year=None):
        if year is None:
            year = timezone.now().year
        
        teachers = Teacher.objects.filter(is_active=True)
        months = range(1, 13)

        salary_table = []
        grand_total = 0
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
            grand_total += total
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
            'grand_total': round(grand_total, 2)
        }
        return render(request, 'teachers/salary_table.html', context)



class TeacherPDFReportView(LoginRequiredMixin, View):
    def get(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Create a file-like buffer to receive PDF data
        buffer = BytesIO()

        # Create the PDF object, using the buffer as its "file."
        p = canvas.Canvas(buffer, pagesize=letter)

        # Draw things on the PDF. Here's where the PDF generation happens.
        self.draw_pdf(p, teacher)

        # Close the PDF object cleanly, and we're done.
        p.showPage()
        p.save()

        # FileResponse sets the Content-Disposition header so that browsers
        # present the option to save the file.
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

    def draw_pdf(self, p, teacher):
        # Draw the teacher's information
        p.setFont("Helvetica-Bold", 16)
        p.drawString(1*inch, 10*inch, f"{teacher.name} 교사 보고서")
        
        p.setFont("Helvetica", 12)
        p.drawString(1*inch, 9.5*inch, f"전화번호: {teacher.phone_number}")
        p.drawString(1*inch, 9.25*inch, f"이메일: {teacher.email}")
        p.drawString(1*inch, 9*inch, f"입사일: {teacher.hire_date}")

        # Draw attendance information
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1*inch, 8*inch, "출근 기록 (최근 30일)")
        
        current_date = timezone.now().date()
        start_date = current_date - timedelta(days=30)
        attendances = Attendance.objects.filter(teacher=teacher, date__range=[start_date, current_date]).order_by('-date')
        
        y = 7.5*inch
        for attendance in attendances:
            p.setFont("Helvetica", 12)
            p.drawString(1*inch, y, f"{attendance.date}: {attendance.start_time} - {attendance.end_time}")
            y -= 0.25*inch

        # Draw salary information
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1*inch, 3*inch, "급여 정보 (최근 3개월)")
        
        current_month = timezone.now().month
        current_year = timezone.now().year
        salaries = Salary.objects.filter(teacher=teacher, year=current_year, month__in=[current_month-2, current_month-1, current_month]).order_by('-month')
        
        y = 2.5*inch
        for salary in salaries:
            p.setFont("Helvetica", 12)
            p.drawString(1*inch, y, f"{salary.year}년 {salary.month}월: {salary.total_amount:,}원")
            y -= 0.25*inch
