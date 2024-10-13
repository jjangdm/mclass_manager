from django.db import models
from common.models import Bank

class Teacher(models.Model):
    GENDER_CHOICES = [('M', '남'), ('F', '여')]

    name = models.CharField(max_length=100, verbose_name='이름')
    phone = models.CharField(max_length=15, verbose_name='전화번호', null=True, blank=True)
    email = models.EmailField(verbose_name='이메일', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name='성별', null=True, blank=True)
    hire_date = models.DateField(verbose_name='입사일', null=True, blank=True)
    resignation_date = models.DateField(verbose_name='퇴사일', null=True, blank=True)
    id_number = models.CharField(max_length=14, verbose_name='주민번호', null=True, blank=True)
    bank = models.ForeignKey(Bank, on_delete=models.SET_NULL, verbose_name='거래은행', null=True, blank=True)
    account_number = models.CharField(max_length=20, verbose_name='급여 계좌', null=True, blank=True)

    class Meta:
        verbose_name = '교사'
        verbose_name_plural = '교사'

    def __str__(self):
        return self.name

class TeacherSalary(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, verbose_name='교사')
    month = models.DateField(verbose_name='급여 월', null=True, blank=True)        
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='급여 금액', null=True, blank=True)
    paid_date = models.DateField(verbose_name='지급일', null=True, blank=True)

    class Meta:
        verbose_name = '교사 급여'
        verbose_name_plural = '교사 급여'
        unique_together = ('teacher', 'month')

    def __str__(self):
        return f"{self.teacher.name} - {self.month.strftime('%Y년 %m월')} 급여"