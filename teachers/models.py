from django.db import models
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime


def validate_phone_number(value):
    if not value.isdigit() or len(value) != 11:
        raise ValidationError(
            _('%(value)s 는 유효한 전화번호가 아닙니다.'),
            params={'value': value},
        )

class Teacher(models.Model):
    GENDER_CHOICES = [
        ('M', '남'),
        ('F', '여'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='이름')
    phone_number = models.CharField(
        max_length=11, 
        validators=[validate_phone_number],
        blank=True,
        null=True,
        verbose_name='전화번호'
    )
    email = models.EmailField(blank=True, null=True, verbose_name='이메일')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True, verbose_name='성별')
    hire_date = models.DateField(blank=True, null=True, verbose_name='입사일')
    resignation_date = models.DateField(blank=True, null=True, verbose_name='퇴사일')
    bank = models.ForeignKey('common.Bank', on_delete=models.SET_NULL, blank=True, null=True, verbose_name='거래은행')
    account_number = models.CharField(max_length=20, blank=True, null=True, verbose_name='급여계좌')
    base_salary = models.IntegerField(blank=True, null=True, verbose_name='급여기준', default=15000)
    additional_salary = models.IntegerField(blank=True, null=True, verbose_name='추가급여', default=0)
    other_info = models.TextField(blank=True, null=True, verbose_name='기타')
    is_active = models.BooleanField(default=True, verbose_name='재직중')
    extra_field1 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비1')
    extra_field2 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비2')
    extra_field3 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비3')
    extra_field4 = models.CharField(max_length=100, blank=True, null=True, verbose_name='예비4')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '교사'
        verbose_name_plural = '교사'

class Attendance(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    date = models.DateField(default=timezone.now, verbose_name='날짜')
    is_present = models.BooleanField(default=True, verbose_name='출근')
    start_time = models.TimeField(null=True, blank=True, verbose_name='근무 시작 시간')
    end_time = models.TimeField(null=True, blank=True, verbose_name='근무 종료 시간')

    class Meta:
        unique_together = ['teacher', 'date']
        verbose_name = '출근기록'
        verbose_name_plural = '출근기록들'

    def __str__(self):
        return f"{self.teacher.name} - {self.date}"

class Salary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    year = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(2100)],
        default=timezone.now().year,
        verbose_name='년도'
    )
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        default=timezone.now().month,
        verbose_name='월'
    )
    work_days = models.PositiveIntegerField(verbose_name='근무일수')
    base_amount = models.PositiveIntegerField(verbose_name='기본급', default=15000)
    additional_amount = models.PositiveIntegerField(verbose_name='추가급', default=0)
    total_amount = models.PositiveIntegerField(verbose_name='총액')

    class Meta:
        verbose_name = '급여'
        verbose_name_plural = '급여'
        unique_together = ['teacher', 'year', 'month']

    def __str__(self):
        return f"{self.teacher.name} - {self.year}년 {self.month}월"

    def clean(self):
        super().clean()
        if self.month < 1 or self.month > 12:
            raise ValidationError({'month': _('월은 1부터 12 사이의 값이어야 합니다.')})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)