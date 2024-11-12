from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView
from .models import Student
from django.contrib.auth.mixins import LoginRequiredMixin


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'
    paginate_by = 20  # 페이지당 20명의 학생을 표시합니다.

    def get_queryset(self):
        return Student.objects.select_related('school').all()


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    fields = ['name', 'school', 'grade', 'phone_number', 'email', 
              'gender', 'parent_phone', 'receipt_number', 'first_class_date', 
              'quit_date', 'etc', 'personal_file']  # Adjust fields as needed
    template_name = 'students/student_form.html'  # Use the new student_form.html
    success_url = reverse_lazy('students:student_list')

    def form_valid(self, form):
        # Save the new student
        student = form.save()

        # Set the student ID on the context for use in the template
        self.object = student 
        return super().form_valid(form)