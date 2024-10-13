from django.contrib import admin
from .models import Student

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    readonly_fields = ('student_id',)
    fields = ('student_id', 'name', 'school', 'grade', 'phone', 'email', 'gender', 'parent_phone', 
              'cash_receipt_number', 'interview_date', 'first_class_date', 'last_class_date', 
              'interview_score', 'base_class')
    list_display = ('student_id', 'name', 'school', 'grade', 'first_class_date')
    search_fields = ('name', 'student_id', 'school__name')
    list_filter = ('grade', 'school')

    def get_readonly_fields(self, request, obj=None):
        if obj:  # 이미 생성된 객체인 경우
            return self.readonly_fields + ('student_id',)
        return self.readonly_fields

    def save_model(self, request, obj, form, change):
        if not obj.pk:  # 새로운 객체를 생성하는 경우
            obj.student_id = obj.generate_student_id()
        super().save_model(request, obj, form, change)