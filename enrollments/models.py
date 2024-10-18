from django.db import models

# Create your models here.
from django.db import models
from students.models import Student
from common.models import Subject

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.student.name} - {self.subject.name}"

class Payment(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=50)  # e.g., "현금", "카드", "계좌이체" 등
    is_refunded = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.enrollment.student.name} - {self.amount} - {self.payment_date}"