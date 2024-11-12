from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from common.models import School

class Student(models.Model):
    GRADE_CHOICES = [
        ('K5', 'K5'), ('K6', 'K6'), ('K7', 'K7'), ('K8', 'K8'),
        ('K9', 'K9'), ('K10', 'K10'), ('K11', 'K11'), ('K12', 'K12'),
    ]
    GENDER_CHOICES = [
        ('M', '남'),
        ('F', '여'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='이름')
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='학교')
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, null=True, blank=True, verbose_name='학년')
    phone_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='학생 전화번호',
                                    validators=[RegexValidator(regex=r'^\d{3}-\d{3,4}-\d{4}$',
                                                message="형식: 000-0000-0000")])
    email = models.EmailField(null=True, blank=True, verbose_name='이메일 주소')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True, verbose_name='성별')
    parent_phone = models.CharField(max_length=15, null=True, blank=True, verbose_name='부모님 전화번호',
                                    validators=[RegexValidator(regex=r'^\d{3}-\d{3,4}-\d{4}$',
                                                message="형식: 000-0000-0000")])
    receipt_number = models.CharField(max_length=15, null=True, blank=True, verbose_name='현금영수증용 번호')
    interview_date = models.DateField(null=True, blank=True, verbose_name='인터뷰 날짜')
    interview_score = models.IntegerField(null=True, blank=True, verbose_name='인터뷰 기본 성적',
                                          validators=[MinValueValidator(1), MaxValueValidator(10)])
    interview_info = models.TextField(null=True, blank=True, verbose_name='인터뷰 정보')
    first_class_date = models.DateField(null=True, blank=True, verbose_name='첫수업 날짜')
    quit_date = models.DateField(null=True, blank=True, verbose_name='그만 둔 날짜')
    student_id = models.CharField(max_length=8, unique=True, verbose_name='고유번호')
    personal_file = models.FileField(upload_to='student_files/', null=True, blank=True, verbose_name='개인 파일')
    etc = models.TextField(null=True, blank=True, verbose_name='기타')
    extra1 = models.CharField(max_length=100, null=True, blank=True, verbose_name='예비1')
    extra2 = models.CharField(max_length=100, null=True, blank=True, verbose_name='예비2')
    extra3 = models.CharField(max_length=100, null=True, blank=True, verbose_name='예비3')
    extra4 = models.CharField(max_length=100, null=True, blank=True, verbose_name='예비4')
    extra5 = models.CharField(max_length=100, null=True, blank=True, verbose_name='예비5')

    def save(self, *args, **kwargs):
        if not self.receipt_number and self.parent_phone:
            self.receipt_number = self.parent_phone
        if not self.student_id:
            self.student_id = self.generate_student_id()
        super().save(*args, **kwargs)

    def generate_student_id(self):
        import random
        return ''.join([str(random.randint(0, 9)) for _ in range(8)])

    class Meta:
        verbose_name = '학생'
        verbose_name_plural = '학생'

    def __str__(self):
        return f"{self.name} ({self.student_id})"