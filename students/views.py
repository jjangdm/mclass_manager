# from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from .models import Student
from django.contrib.auth.mixins import LoginRequiredMixin


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20  # 페이지당 20명의 학생을 표시합니다.

    def get_queryset(self):
        return Student.objects.select_related('school').all()