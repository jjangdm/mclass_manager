from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView
from .models import Student, School  # Import School model
from .forms import StudentForm, StudentImportForm
import pandas as pd
from django.http import HttpResponse
from datetime import datetime  # Import datetime module


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 50

    def get_queryset(self):
        return Student.objects.select_related('school').all()


class StudentCreateView(LoginRequiredMixin, CreateView):
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        student = form.save(commit=False)
        student.student_id = self.generate_student_id()
        student.save()

        # Add a success message to inform the user about registration
        messages.success(self.request, f"학생 '{student.name}' 등록되었습니다.")

        return redirect('students:student_list')  # Redirect to the list view

    def generate_student_id(self):
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])


def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    context = {'student': student}
    return render(request, 'students/student_detail.html', context)


def student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, '학생 정보가 성공적으로 수정되었습니다.')
            return redirect('students:student_list')
    else:
        form = StudentForm(instance=student)
    return render(request, 'students/student_form.html', {'form': form})


def student_import(request):
    if request.method == 'POST':
        form = StudentImportForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                file = form.cleaned_data['file']
                file_ext = file.name.split('.')[-1].lower()

                # 파일 형식에 따라 적절한 방법으로 읽기
                if file_ext == 'csv':
                    df = pd.read_csv(file)
                else:
                    df = pd.read_excel(file)

                # 중복 체크를 위한 카운터 초기화
                new_count = 0
                duplicate_count = 0

                for index, row in df.iterrows():
                    school_name = row['school']
                    school = School.objects.get(name=school_name)

                    # 중복 체크
                    existing_student = Student.objects.filter(
                        name=row['name'],
                        school=school,
                        phone_number=row['phone_number']
                    ).exists()

                    if existing_student:
                        duplicate_count += 1
                        continue  # 중복된 학생은 건너뛰기

                    # 날짜 처리 함수
                    def process_date(date_value):
                        if pd.isna(date_value):
                            return None

                        if isinstance(date_value, str):
                            try:
                                return datetime.strptime(date_value.split()[0], '%Y-%m-%d').date()
                            except ValueError:
                                return None
                        elif isinstance(date_value, (datetime, pd.Timestamp)):
                            return date_value.date()
                        return None

                    # 각 날짜 필드 처리
                    interview_date = process_date(row['interview_date'])
                    first_class_date = process_date(row['first_class_date'])
                    quit_date = process_date(row['quit_date'])

                    student = Student(
                        name=row['name'],
                        school=school,
                        grade=row['grade'],
                        phone_number=row['phone_number'],
                        email=row['email'],
                        gender=row['gender'],
                        parent_phone=row['parent_phone'],
                        receipt_number=row['receipt_number'],
                        interview_date=interview_date,
                        interview_score=row['interview_score'],
                        interview_info=row['interview_info'],
                        first_class_date=first_class_date,
                        quit_date=quit_date,
                        etc=row['etc'],
                    )
                    student.save()
                    new_count += 1

                # 결과 메시지 생성
                message_parts = []
                if new_count > 0:
                    message_parts.append(f'{new_count}명의 학생이 새로 등록되었습니다.')
                if duplicate_count > 0:
                    message_parts.append(f'{duplicate_count}명의 학생은 이미 등록되어 있어 건너뛰었습니다.')

                if message_parts:
                    messages.success(request, ' '.join(message_parts))
                else:
                    messages.warning(request, '등록된 학생이 없습니다.')

                return redirect('students:student_list')

            except Exception as e:
                messages.error(request, f'파일 처리 중 오류가 발생했습니다: {str(e)}')
    else:
        form = StudentImportForm()

    return render(request, 'students/student_import.html', {'form': form})


def student_export(request):
    students = Student.objects.all()

    df = pd.DataFrame({
        'name': [student.name for student in students],
        'school': [student.school.name if student.school else '' for student in students],
        'grade': [student.grade for student in students],
        'phone_number': [student.phone_number for student in students],
        'email': [student.email for student in students],
        'gender': [student.get_gender_display() for student in students],
        'parent_phone': [student.parent_phone for student in students],
        'receipt_number': [student.receipt_number for student in students],
        'interview_date': [student.interview_date.strftime('%Y-%m-%d') if student.interview_date else '' for student in students],
        'interview_score': [student.interview_score for student in students],
        'interview_info': [student.interview_info for student in students],
        'first_class_date': [student.first_class_date.strftime('%Y-%m-%d') if student.first_class_date else '' for student in students],
        'quit_date': [student.quit_date.strftime('%Y-%m-%d') if student.quit_date else '' for student in students],
        'etc': [student.etc for student in students]
    })

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
    df.to_excel(response, sheet_name='학생 목록', index=False, engine='xlsxwriter')

    return response
