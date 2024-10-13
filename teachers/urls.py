from django.urls import path
from django.contrib import admin
from .admin import MonthlySalaryAdmin, TeacherAdmin

app_name = 'teachers'

urlpatterns = [
    path('monthlysalary/', MonthlySalaryAdmin.changelist_view, name='monthlysalary_changelist'),
    path('monthlysalary/add/', MonthlySalaryAdmin.add_view, name='monthlysalary_add'),
    path('monthlysalary/<path:object_id>/change/', MonthlySalaryAdmin.change_view, name='monthlysalary_change'),
    path('teacher/', TeacherAdmin.changelist_view, name='teacher_changelist'),
    path('teacher/add/', TeacherAdmin.add_view, name='teacher_add'),
    path('teacher/<path:object_id>/change/', TeacherAdmin.change_view, name='teacher_change'),
]