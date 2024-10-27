from django.contrib import admin
from .models import Class, Enrollment
from django.http import HttpResponse
import csv

class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 1

@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'teacher', 'day', 'time', 'tuition_fee')
    list_filter = ('subject', 'teacher', 'day')
    search_fields = ('name', 'teacher__name')
    inlines = [EnrollmentInline]


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'class_instance', 'enrollment_date')
    list_filter = ('class_instance', 'enrollment_date')
    search_fields = ('student__name', 'class_instance__name')
    actions = ['export_as_csv']

    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response
    export_as_csv.short_description = "선택된 수강신청을 CSV로 내보내기"