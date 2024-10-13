import random
from django.db import models
from django.utils import timezone
from common.models import School
from classes.models import Class

class Student(models.Model):
    GRADE_CHOICES = [
        ('K5', 'K5'), ('K6', 'K6'), ('K7', 'K7'), ('K8', 'K8'),
        ('K9', 'K9'), ('K10', 'K10'), ('K11', 'K11'), ('K12', 'K12'),
    ]
    GENDER_CHOICES = [('M', '남'), ('F', '여')]

    name = models.CharField(max_length=100, verbose_name='이름')
    student_id = models.CharField(max_length=8, unique=True, editable=False, verbose_name='학생 고유번호')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, verbose_name='학교', blank=True)
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, verbose_name='학년', blank=True)
    phone = models.CharField(max_length=15, verbose_name='전화번호', blank=True)
    email = models.EmailField(verbose_name='이메일', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='성별', blank=True)
    parent_phone = models.CharField(max_length=15, verbose_name='부모님 전화번호', blank=True)
    cash_receipt_number = models.CharField(max_length=20, verbose_name='현금영수증용 번호', blank=True)
    interview_date = models.DateField(verbose_name='인터뷰 날짜', null=True, blank=True)
    first_class_date = models.DateField(verbose_name='첫수업 날짜', null=True, blank=True)
    last_class_date = models.DateField(verbose_name='그만 둔 날짜',null=True, blank=True)
    interview_score = models.IntegerField(choices=[(i, i) for i in range(1, 11)], verbose_name='상담시 성적', null=True, blank=True)
    base_class = models.ForeignKey(Class, on_delete=models.SET_NULL, related_name='base_students', verbose_name='기본 학급', null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = self.generate_student_id()
        if not self.cash_receipt_number:
            self.cash_receipt_number = self.parent_phone
        super().save(*args, **kwargs)

    def generate_student_id(self):
        year = str(timezone.now().year)[-2:]
        while True:
            random_numbers = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            student_id = f"{year}{random_numbers}"
            if not Student.objects.filter(student_id=student_id).exists():
                return student_id

    class Meta:
        verbose_name = '학생'
        verbose_name_plural = '학생'

    def __str__(self):
        return f"{self.name} ({self.student_id})"