from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import Subject, Publisher, PurchaseLocation


class Book(models.Model):
    name = models.CharField(
        max_length=200, 
        verbose_name='교재 이름'
    )
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='과목'
    )
    isbn = models.CharField(
        max_length=13, 
        null=True, 
        blank=True, 
        verbose_name='ISBN'
    )
    publisher = models.ForeignKey(
        Publisher, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='출판사'
    )
    entry_date = models.DateField(
        null=True, 
        blank=True, 
        verbose_name='입고일'
    )
    original_price = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='원가'
    )
    purchase_price = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='입고 가격'
    )
    selling_price = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name='판매 가격'
    )
    purchase_location = models.ForeignKey(
        PurchaseLocation, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name='구입처'
    )
    difficulty_level = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(10)
        ],
        null=True, 
        blank=True, 
        verbose_name='교재 난이도'
    )
    memo = models.TextField(
        null=True, 
        blank=True, 
        verbose_name='메모'
    )
    spare1 = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='예비1'
    )
    spare2 = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='예비2'
    )
    spare3 = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name='예비3'
    )

    class Meta:
        verbose_name = '교재'
        verbose_name_plural = '교재 목록'

    def __str__(self):
        return self.name
