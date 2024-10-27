from django.contrib import admin
from .models import Tuition, TuitionPayment

@admin.register(Tuition)
class TuitionAdmin(admin.ModelAdmin):
    list_display = ('class_instance', 'month', 'amount')
    list_filter = ('class_instance', 'month')

@admin.register(TuitionPayment)
class TuitionPaymentAdmin(admin.ModelAdmin):
    list_display = ('student', 'tuition', 'paid_amount', 'payment_date')
    list_filter = ('payment_date', 'tuition__class_instance')
    search_fields = ('student__name', 'student__student_id')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['student'].widget.can_add_related = False
        form.base_fields['tuition'].widget.can_add_related = False
        return form