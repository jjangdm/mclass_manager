from django.db import models
from common.models import Subject, Publisher, PurchaseLocation

class Textbook(models.Model):
    DIFFICULTY_CHOICES = [(i, i) for i in range(1, 6)]

    name = models.CharField(max_length=200, verbose_name='교재명')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='과목')
    isbn = models.CharField(max_length=13, unique=True, verbose_name='ISBN')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, verbose_name='출판사')
    purchase_location = models.ForeignKey(PurchaseLocation, on_delete=models.SET_NULL, null=True, verbose_name='구입처')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, verbose_name='교재 난이도')
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='원가')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='입고가격')
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='판매가격')

    class Meta:
        verbose_name = '교재'
        verbose_name_plural = '교재'

    def __str__(self):
        return self.name

class TextbookInventory(models.Model):
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, verbose_name='교재')
    quantity = models.IntegerField(verbose_name='수량')
    date = models.DateField(verbose_name='입고/출고일')
    is_incoming = models.BooleanField(verbose_name='입고 여부')

    class Meta:
        verbose_name = '교재 재고'
        verbose_name_plural = '교재 재고'

    def __str__(self):
        return f"{self.textbook.name} - {'입고' if self.is_incoming else '출고'} ({self.quantity}권)"

class TextbookQuestion(models.Model):
    DIFFICULTY_CHOICES = [(i, i) for i in range(1, 11)]

    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, verbose_name='교재')
    question_number = models.CharField(max_length=20, verbose_name='문제 고유번호')
    category_large = models.CharField(max_length=100, verbose_name='대분류')
    category_medium = models.CharField(max_length=100, verbose_name='중분류')
    category_small = models.CharField(max_length=100, verbose_name='소분류')
    question_type = models.CharField(max_length=50, verbose_name='유형번호')
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, verbose_name='문제 난이도')

    class Meta:
        verbose_name = '교재 문항'
        verbose_name_plural = '교재 문항'
        unique_together = ('textbook', 'question_number')

    def __str__(self):
        return f"{self.textbook.name} - {self.question_number}"