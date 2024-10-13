from django.db import models
from django.core.validators import RegexValidator
from django.db.models import Sum
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.utils.crypto import get_random_string
from common.models import Bank  # Bank 모델이 실제로 존재하는지 확인하세요
from django.urls import reverse

class Teacher(models.Model):
    GENDER_CHOICES = [('M', '남'), ('F', '여')]
    
    name = models.CharField(max_length=100, verbose_name='이름')
    phone_number = models.CharField(
        max_length=15, 
        verbose_name='전화번호', 
        null=True, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\d{3}-\d{3,4}-\d{4}$',
                message="전화번호는 '000-0000-0000' 형식이어야 합니다."
            )
        ]
    )
    email = models.EmailField(verbose_name='이메일', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='성별', null=True, blank=True)
    hire_date = models.DateField(verbose_name='입사일', null=True, blank=True)
    resignation_date = models.DateField(verbose_name='퇴사일', null=True, blank=True)
    id_number = models.CharField(max_length=256, verbose_name='주민번호(암호화됨)', null=True, blank=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, verbose_name='거래은행', null=True, blank=True)
    account_number = models.CharField(max_length=20, verbose_name='급여 계좌', null=True, blank=True)

    class Meta:
        verbose_name = '교사'
        verbose_name_plural = '교사'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.id_number:
            self.id_number = self.encrypt_id_number(self.id_number)
        super().save(*args, **kwargs)

    @staticmethod
    def encrypt_id_number(id_number):
        # 실제 운영 환경에서는 더 강력한 암호화 방식을 사용해야 합니다
        return get_random_string(length=256)

    def yearly_salary(self, year=None):
        if year is None:
            year = timezone.now().year
        start_date = timezone.datetime(year, 1, 1)
        end_date = timezone.datetime(year, 12, 31)
        salaries = MonthlySalary.objects.filter(
            teacher=self,
            year_month__range=(start_date, end_date)
        )
        return sum(salary.total_salary() for salary in salaries)

class MonthlySalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    year_month = models.DateField(verbose_name='급여 년월')
    base_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='기본급', default=0)
    overtime_pay = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='초과 근무 수당', default=0)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='보너스', default=0)
    deductions = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='공제액', default=0)
    paid_date = models.DateField(verbose_name='지급일', null=True, blank=True)

    class Meta:
        verbose_name = '월별 급여'
        verbose_name_plural = '월별 급여'
        unique_together = ('teacher', 'year_month')

    def save(self, *args, **kwargs):
        if self.year_month:
            self.year_month = self.year_month.replace(day=1)
        super().save(*args, **kwargs)

    def total_salary(self):
        return (self.base_salary or 0) + (self.overtime_pay or 0) + (self.bonus or 0) - (self.deductions or 0)

    def __str__(self):
        if self.year_month:
            return f"{self.teacher.name} - {self.year_month.strftime('%Y년 %m월')} 급여"
        return f"{self.teacher.name} - 날짜 미지정 급여"
    
    def get_absolute_url(self):
        return reverse('teachers:monthlysalary_change', args=[str(self.id)])

    @classmethod
    def get_next_month(cls, date):
        return date + relativedelta(months=1)

    @classmethod
    def get_previous_month(cls, date):
        return date - relativedelta(months=1)