from datetime import timedelta
from io import BytesIO
from pyexpat.errors import messages
from django.http import HttpResponse
from django.http import FileResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Teacher, Attendance, Salary
from .forms import BulkAttendanceForm, TeacherForm
from django.contrib import messages
from reportlab.lib.pagesizes import letter
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import os
import base64
from django.views import View
from django.db.models import Min, Max
from django.conf import settings



# 폰트 등록
font_path = settings.FONT_PATH
if os.path.exists(font_path):
    pdfmetrics.registerFont(TTFont('NanumGothic', font_path))
    print(f"Font registered successfully: {font_path}")
else:
    print(f"Error: Font file not found at {font_path}")
    # 폰트 파일이 없을 경우 대체 폰트 사용 (예: Helvetica)
    pdfmetrics.registerFont(TTFont('NanumGothic', 'Helvetica'))



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
                            'start_time': start_time,
                            'end_time': end_time
                        }
                    )
                else:
                    Attendance.objects.filter(teacher=teacher, date=date).delete()
            
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
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

        elements = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Korean', fontName='NanumGothic', fontSize=10, leading=14, encoding='utf-8'))

        # 제목
        elements.append(Paragraph(f"{teacher.name} 교사 보고서", styles['Korean']))
        elements.append(Spacer(1, 12))

        # 교사 정보
        data = [
            ["이름:", teacher.name],
            ["전화번호:", teacher.phone_number],
            ["이메일:", teacher.email],
            ["입사일:", teacher.hire_date.strftime("%Y-%m-%d")],
        ]
        t = Table(data, colWidths=[100, 300])
        t.setStyle(TableStyle([
            ('FONT', (0,0), (-1,-1), 'NanumGothic'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('TEXTCOLOR', (0,0), (0,-1), colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 12))

        # 출근 기록
        elements.append(Paragraph("출근 기록 (최근 30일)", styles['Korean']))
        elements.append(Spacer(1, 6))

        current_date = timezone.now().date()
        start_date = current_date - timedelta(days=30)
        attendances = Attendance.objects.filter(teacher=teacher, date__range=[start_date, current_date]).order_by('-date')
        
        if attendances:
            attendance_data = [["날짜", "출근 시간", "퇴근 시간"]]
            for attendance in attendances:
                attendance_data.append([
                    attendance.date.strftime("%Y-%m-%d"),
                    attendance.start_time.strftime("%H:%M") if attendance.start_time else "-",
                    attendance.end_time.strftime("%H:%M") if attendance.end_time else "-"
                ])
            t = Table(attendance_data, colWidths=[100, 100, 100])
            t.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), 'NanumGothic'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("출근 기록이 없습니다.", styles['Korean']))

        elements.append(Spacer(1, 12))

        # 급여 정보
        elements.append(Paragraph("급여 정보 (최근 3개월)", styles['Korean']))
        elements.append(Spacer(1, 6))

        current_month = timezone.now().month
        current_year = timezone.now().year
        salaries = Salary.objects.filter(teacher=teacher, year=current_year, month__in=[current_month-2, current_month-1, current_month]).order_by('-month')
        
        if salaries:
            salary_data = [["년월", "급여"]]
            for salary in salaries:
                salary_data.append([f"{salary.year}년 {salary.month}월", f"{salary.total_amount:,}원"])
            t = Table(salary_data, colWidths=[100, 200])
            t.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), 'NanumGothic'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BACKGROUND', (0,0), (-1,0), colors.grey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("급여 정보가 없습니다.", styles['Korean']))

        # PDF 생성
        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        
        if request.GET.get('download') == 'true':
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{teacher.name}_report.pdf"'
            response.write(pdf)
            return response
        else:
            # PDF를 임시 파일로 저장
            pdf_dir = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs')
            os.makedirs(pdf_dir, exist_ok=True)
            pdf_filename = f'teacher_{teacher.id}_report.pdf'
            pdf_path = os.path.join(pdf_dir, pdf_filename)
            
            with open(pdf_path, 'wb') as f:
                f.write(pdf)
            
            response = FileResponse(open(pdf_path, 'rb'), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{pdf_filename}"'
            return response


class TeacherPDFViewerView(LoginRequiredMixin, View):
    def get(self, request, teacher_id):
        teacher = get_object_or_404(Teacher, id=teacher_id)
        pdf_filename = f'teacher_{teacher.id}_report.pdf'
        pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', pdf_filename)
        
        if not os.path.exists(pdf_path):
            # PDF가 없으면 생성
            pdf_report_view = TeacherPDFReportView()
            return pdf_report_view.get(request, teacher_id)
        
        pdf_url = settings.MEDIA_URL + f'temp_pdfs/{pdf_filename}'
        return render(request, 'teachers/pdf_viewer.html', {'teacher': teacher, 'pdf_url': pdf_url})