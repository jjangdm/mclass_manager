from datetime import timedelta, datetime, time
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
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus.frames import Frame
from reportlab.platypus.doctemplate import PageTemplate
import urllib.parse


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

        start_date = datetime(year, month, 1)
        end_date = (start_date + timedelta(days=32)).replace(day=1) - timedelta(days=1)

        teachers = Teacher.objects.filter(is_active=True)
        salary_data = []

        for teacher in teachers:
            attendances = Attendance.objects.filter(
                teacher=teacher,
                date__range=[start_date, end_date]
            )

            total_work_hours = 0
            for attendance in attendances:
                if attendance.start_time and attendance.end_time:
                    start_datetime = datetime.combine(attendance.date, attendance.start_time)
                    end_datetime = datetime.combine(attendance.date, attendance.end_time)
                    if end_datetime < start_datetime:  # 자정을 넘긴 경우
                        end_datetime += timedelta(days=1)
                    work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                    total_work_hours += work_hours

            total_work_hours = round(total_work_hours, 2)
            base_amount = int(teacher.base_salary * total_work_hours) if teacher.base_salary else 0
            additional_amount = int(teacher.additional_salary) if teacher.additional_salary else 0
            total_amount = base_amount + additional_amount

            salary_data.append({
                'teacher': teacher,
                'work_days': attendances.count(),
                'work_hours': total_work_hours,
                'total_amount': total_amount,
                'bank_name': teacher.bank.name if teacher.bank else '',
                'account_number': teacher.account_number,
            })

        total_salary = sum(data['total_amount'] for data in salary_data)

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
        
        def footer(canvas, doc):
            canvas.saveState()
            footer_text = "엠클래스수학과학전문학원"
            canvas.setFont('NanumGothic', 10)
            canvas.drawCentredString(A4[0]/2, 20*mm, footer_text)
            canvas.restoreState()
        
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=20*mm, leftMargin=20*mm, topMargin=20*mm, bottomMargin=30*mm)
        
        frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height - 10*mm, id='normal')
        template = PageTemplate(id='test', frames=frame, onPage=footer)
        doc.addPageTemplates([template])

        elements = []

        styles = getSampleStyleSheet()
        styles.add(ParagraphStyle(name='Korean', fontName='NanumGothic', fontSize=10, leading=14, encoding='utf-8'))
        styles.add(ParagraphStyle(name='KoreanTitle', fontName='NanumGothic', fontSize=16, leading=20, alignment=1, encoding='utf-8'))
        styles.add(ParagraphStyle(name='KoreanSubtitle', fontName='NanumGothic', fontSize=12, leading=16, encoding='utf-8'))

        # 제목
        elements.append(Paragraph(f"{teacher.name} 선생님 근무 내역", styles['KoreanTitle']))
        elements.append(Spacer(1, 10*mm))

        # 기본 정보
        data = [
            ["이름:", teacher.name],
            ["전화번호:", teacher.phone_number],
            ["이메일:", teacher.email],
            ["입사일:", teacher.hire_date.strftime("%Y-%m-%d")],
            ["퇴사일:", teacher.resignation_date.strftime("%Y-%m-%d") if teacher.resignation_date else "재직 중"]
        ]
        t = Table(data, colWidths=[50*mm, 120*mm])
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
        elements.append(Spacer(1, 10*mm))

        # 출근 기록
        elements.append(Paragraph("근무 기록", styles['KoreanSubtitle']))
        elements.append(Spacer(1, 5*mm))

        attendances = Attendance.objects.filter(teacher=teacher).order_by('date')
        
        if attendances:
            monthly_data = {}
            for attendance in attendances:
                year_month = attendance.date.strftime("%Y-%m")
                if year_month not in monthly_data:
                    monthly_data[year_month] = {'hours': 0, 'amount': 0}
                
                if attendance.start_time and attendance.end_time:
                    start_datetime = datetime.combine(attendance.date, attendance.start_time)
                    end_datetime = datetime.combine(attendance.date, attendance.end_time)
                    if end_datetime < start_datetime:  # 자정을 넘긴 경우
                        end_datetime += timedelta(days=1)
                    work_hours = (end_datetime - start_datetime).total_seconds() / 3600
                    monthly_data[year_month]['hours'] += work_hours
                    monthly_data[year_month]['amount'] += work_hours * teacher.base_salary

            attendance_data = [["년월", "근무 시간", "급여"]]
            total_hours = 0
            total_amount = 0
            for year_month, data in monthly_data.items():
                year, month = year_month.split('-')
                hours = round(data['hours'], 2)
                amount = round(data['amount'])
                attendance_data.append([f"{year}년 {month}월", f"{hours}시간", f"{amount:,}원"])
                total_hours += hours
                total_amount += amount
            
            attendance_data.append(["총계", f"{total_hours:.2f}시간", f"{total_amount:,}원"])

            t = Table(attendance_data, colWidths=[60*mm, 50*mm, 60*mm])
            t.setStyle(TableStyle([
                ('FONT', (0,0), (-1,-1), 'NanumGothic'),
                ('FONTSIZE', (0,0), (-1,-1), 10),
                ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
                ('TEXTCOLOR', (0,0), (-1,0), colors.black),
                ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black),
                ('BACKGROUND', (0,-1), (-1,-1), colors.lightgrey),
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("근무 기록이 없습니다.", styles['Korean']))

        doc.build(elements)

        pdf = buffer.getvalue()
        buffer.close()
        
        # PDF 파일 이름 설정
        filename = f"{teacher.name} 선생님 근무 내역.pdf"
        encoded_filename = urllib.parse.quote(filename.encode('utf-8'))
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{encoded_filename}"'
        response.write(pdf)
        
        return response

# class TeacherPDFViewerView(LoginRequiredMixin, View):
#     def get(self, request, teacher_id):
#         teacher = get_object_or_404(Teacher, id=teacher_id)
#         pdf_filename = f'teacher_{teacher.id}_report.pdf'
#         pdf_path = os.path.join(settings.MEDIA_ROOT, 'temp_pdfs', pdf_filename)
        
#         if not os.path.exists(pdf_path):
#             # PDF가 없으면 생성
#             pdf_report_view = TeacherPDFReportView()
#             return pdf_report_view.get(request, teacher_id)
        
#         pdf_url = settings.MEDIA_URL + f'temp_pdfs/{pdf_filename}'
#         return render(request, 'teachers/pdf_viewer.html', {'teacher': teacher, 'pdf_url': pdf_url})