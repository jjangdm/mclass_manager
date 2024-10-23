from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
import datetime


class MonthYearField(models.DateField):
    """Custom field for Month/Year without day"""
    def __init__(self, *args, **kwargs):
        kwargs['help_text'] = '년월을 선택해주세요 (예: 2024년 10월)'
        super().__init__(*args, **kwargs)

    def to_python(self, value):
        if isinstance(value, datetime.date):
            return datetime.date(value.year, value.month, 1)
        if not value:
            return None
        try:
            if isinstance(value, str):
                # Handle string input in format "YYYY년 MM월"
                if '년' in value and '월' in value:
                    year = int(value.split('년')[0].strip())
                    month = int(value.split('년')[1].split('월')[0].strip())
                    return datetime.date(year, month, 1)
                # Handle string input in format "YYYY-MM"
                year, month = map(int, value.split('-'))
                return datetime.date(year, month, 1)
        except (ValueError, TypeError):
            raise ValidationError('올바른 년월 형식이 아닙니다. (예: 2024년 10월 또는 2024-10)')
        return None

class Maintenance(models.Model):
    room = models.IntegerField(
        validators=[MinValueValidator(1, message='호실 번호는 양수여야 합니다.')],
        verbose_name='호실'
    )
    date = models.DateField(
        verbose_name='부과년월'
    )
    charge = models.IntegerField(
        validators=[MinValueValidator(0, message='금액은 0 이상이어야 합니다.')],
        verbose_name='부과금액'
    )
    date_paid = models.DateField(
        null=True,
        blank=True,
        verbose_name='납부일자'
    )
    memo = models.TextField(
        blank=True,
        verbose_name='메모'
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = '관리비'
        verbose_name_plural = '관리비'
        ordering = ['-date', 'room']
        indexes = [
            models.Index(fields=['room']),
            models.Index(fields=['date']),
            models.Index(fields=['date_paid']),
        ]

    def __str__(self):
        return f"{self.room}호 - {self.date.strftime('%Y년 %m월')} ({self.charge:,}원)"

    def save(self, *args, **kwargs):
        # 항상 날짜를 해당 월의 1일로 저장
        if self.date:
            self.date = self.date.replace(day=1)
        super().save(*args, **kwargs)