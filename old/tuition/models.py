from django.db import models
from students.models import Student
from classes.models import Class

class Tuition(models.Model):
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='수업')
    month = models.DateField(verbose_name='수강료 기준 월')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='수강료')

    class Meta:
        verbose_name = '수강료'
        verbose_name_plural = '수강료'
        unique_together = ('class_instance', 'month')

    def __str__(self):
        return f"{self.class_instance} - {self.month.strftime('%Y년 %m월')}"

class TuitionPayment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='학생')
    tuition = models.ForeignKey(Tuition, on_delete=models.CASCADE, verbose_name='수강료')
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='납부 금액')
    payment_date = models.DateField(verbose_name='납부일')

    class Meta:
        verbose_name = '수강료 납부'
        verbose_name_plural = '수강료 납부'

    def __str__(self):
        return f"{self.student} - {self.tuition} 납부"