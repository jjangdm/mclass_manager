# Register your models here.
from django.contrib import admin
from .models import Enrollment, Payment

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'start_date', 'end_date', 'fee')
    list_filter = ('subject', 'start_date')
    search_fields = ('student__name', 'subject__name')
    inlines = [PaymentInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'amount', 'payment_date', 'payment_method', 'is_refunded')
    list_filter = ('payment_date', 'payment_method', 'is_refunded')
    search_fields = ('enrollment__student__name',)

    def enrollment(self, obj):
        return f"{obj.enrollment.student.name} - {obj.enrollment.subject.name}"
    enrollment.short_description = '등록 정보'