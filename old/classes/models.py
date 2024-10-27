from django.db import models
from teachers.models import Teacher
from textbooks.models import Textbook
from common.models import Subject

class Class(models.Model):
    DAY_CHOICES = [
        (0, '일'), (1, '월'), (2, '화'), (3, '수'), (4, '목'), (5, '금'), (6, '토')
    ]
    TIME_CHOICES = [(i, f'{i:02d}:00') for i in range(10, 23)]

    name = models.CharField(max_length=100, verbose_name='수업명')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='과목')
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, verbose_name='담당교사')
    textbook = models.ForeignKey(Textbook, on_delete=models.SET_NULL, null=True, verbose_name='교재')
    day = models.IntegerField(choices=DAY_CHOICES, verbose_name='수업 요일')
    time = models.IntegerField(choices=TIME_CHOICES, verbose_name='수업 시간')
    tuition_fee = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='수강료')

    class Meta:
        verbose_name = '수업'
        verbose_name_plural = '수업'

    def __str__(self):
        return f"{self.name} ({self.get_day_display()} {self.get_time_display()})"

class Enrollment(models.Model):
    student = models.ForeignKey('students.Student', on_delete=models.CASCADE, verbose_name='학생')
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='수업')
    enrollment_date = models.DateField(verbose_name='등록일')

    class Meta:
        verbose_name = '수강신청'
        verbose_name_plural = '수강신청'
        unique_together = ('student', 'class_instance')

    def __str__(self):
        return f"{self.student.name} - {self.class_instance.name}"