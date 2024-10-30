# mclass_manager/books_inventory/models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.forms import ValidationError
from books.models import Book
from students.models import Student
from common.models import Subject, PurchaseLocation
from django.contrib.auth import get_user_model
from django.db.models import Sum


class BookStockHistory(models.Model):
    """교재 재고 변동 이력"""
    TRANSACTION_TYPES = [
        ('IN', '입고'),
        ('OUT', '출고'),
        ('RETURN', '반품'),
        ('LOSS', '분실/파손'),
        ('ADJUST', '재고조정'),
    ]

    book_stock = models.ForeignKey(
        'BookStock',
        on_delete=models.CASCADE,
        verbose_name='교재'
    )
    transaction_type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        verbose_name='거래 유형'
    )
    quantity = models.IntegerField(verbose_name='수량')
    transaction_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='처리일시'
    )
    processed_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='처리자'
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='비고'
    )

    class Meta:
        verbose_name = '재고 변동 이력'
        verbose_name_plural = '재고 변동 이력 관리'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.book_stock} ({self.quantity}권)"


class BookStock(models.Model):
    """교재 입고 및 재고 관리"""
    subject = models.ForeignKey(
        Subject,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='과목'
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='도서명'
    )
    purchase_location = models.ForeignKey(
        PurchaseLocation,  # Common app의 PurchaseLocation 모델 참조
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='구매처'
    )
    quantity_received = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='수량'
    )
    received_date = models.DateField(
        verbose_name='입고 날짜'
    )
    list_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='정가'
    )
    unit_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='단가'
    )
    selling_price = models.PositiveIntegerField(
        validators=[MinValueValidator(0)],
        verbose_name='판매가'
    )
    reorder_point = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        verbose_name='재주문 기준수량'
    )
    order_status = models.CharField(
        max_length=20,
        choices=[
            ('IN_STOCK', '재고충분'),
            ('LOW_STOCK', '재고부족'),
            ('OUT_OF_STOCK', '재고없음'),
            ('ON_ORDER', '주문중')
        ],
        default='IN_STOCK',
        verbose_name='재고상태'
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='참고'
    )

    @property
    def distributed_quantity(self):
        """총 배포 수량"""
        distributed = self.bookdistribution_set.aggregate(
            total=Sum('quantity')
        )['total']
        return distributed or 0

    @property
    def current_stock(self):
        """현재 재고"""
        try:
            return self.quantity_received - self.distributed_quantity
        except (TypeError, AttributeError):
            return 0

    def update_order_status(self):
        """재고 상태 자동 업데이트"""
        current = self.current_stock
        if current <= 0:
            new_status = 'OUT_OF_STOCK'
        elif current <= self.reorder_point:
            new_status = 'LOW_STOCK'
        else:
            new_status = 'IN_STOCK'
            
        if self.order_status != new_status:
            self.order_status = new_status
            models.Model.save(self, update_fields=['order_status'])

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            # 새로운 입고 기록일 경우 히스토리 생성
            self.log_transaction('IN', self.quantity_received, 
                               kwargs.pop('user', None), 
                               '최초 입고')
        
        # update_order_status는 save() 호출 후에만 실행
        if not kwargs.get('update_fields'):  # update_fields가 지정되지 않은 경우에만
            self.update_order_status()

    def log_transaction(self, transaction_type, quantity, user, notes=None):
        """재고 변동 이력 기록"""
        BookStockHistory.objects.create(
            book_stock=self,
            transaction_type=transaction_type,
            quantity=quantity,
            processed_by=user,
            notes=notes
        )

    def clean(self):
        if self.book and self.subject and self.book.subject != self.subject:
            raise ValidationError('선택한 도서가 해당 과목에 속하지 않습니다.')
        
    # def save(self, *args, **kwargs):
    #     is_new = self.pk is None
    #     super().save(*args, **kwargs)
        
    #     if is_new:
    #         # 새로운 입고 기록일 경우 히스토리 생성
    #         self.log_transaction('IN', self.quantity_received, 
    #                            kwargs.get('user', None), 
    #                            '최초 입고')
        
    #     # 재고 상태 업데이트
    #     self.update_order_status()

    class Meta:
        verbose_name = '교재 입고'
        verbose_name_plural = '교재 입고 관리'
        ordering = ['-received_date']

    def __str__(self):
        book_name = self.book.name if self.book else '미지정'
        return f"{book_name} (재고: {self.current_stock}/{self.quantity_received})"


class BookDistribution(models.Model):
    """교재 배포 관리"""
    book_stock = models.ForeignKey(
        BookStock,
        on_delete=models.CASCADE,
        verbose_name='교재'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='지급 학생'
    )
    distribution_date = models.DateField(
        verbose_name='지급 날짜'
    )
    quantity = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name='지급 수량'
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name='비고'
    )

    def clean(self):
        if not self.book_stock:
            return
        
        # 현재 지급 가능한 재고 확인
        available_stock = self.book_stock.current_stock
        if self.pk:  # 수정 시 자신의 수량은 제외
            available_stock += BookDistribution.objects.get(pk=self.pk).quantity
            
        if self.quantity > available_stock:
            raise ValidationError(
                f'지급 가능한 재고가 {available_stock}권 남아있습니다.'
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # 저장 후 book_stock의 상태만 업데이트
        if self.book_stock:
            self.book_stock.update_order_status()

    class Meta:
        verbose_name = '교재 지급'
        verbose_name_plural = '교재 지급 관리'
        ordering = ['-distribution_date']

    def __str__(self):
        student_name = self.student.name if self.student else '미지정'
        book_name = self.book_stock.book.name if self.book_stock and self.book_stock.book else '미지정'
        return f"{book_name} -> {student_name}"
    


# from django.db import models
# from django.core.validators import MinValueValidator
# from django.forms import ValidationError
# from books.models import Book
# from common.models import Subject
# from students.models import Student
# from django.core.exceptions import ValidationError
# from django.db.models import Sum
# from books.models import Book
# from common.models import Subject
# from students.models import Student


# class BookStock(models.Model):
#     """교재 입고 및 재고 관리"""
#     subject = models.ForeignKey(
#         Subject,
#         on_delete=models.SET_NULL,
#         null=True,
#         verbose_name='과목'
#     )
#     book = models.ForeignKey(
#         Book,
#         on_delete=models.SET_NULL,
#         null=True,
#         verbose_name='도서명'
#     )
#     quantity_received = models.PositiveIntegerField(
#         validators=[MinValueValidator(1)],
#         verbose_name='입고 수량'
#     )
#     received_date = models.DateField(
#         verbose_name='입고 날짜'
#     )
#     list_price = models.PositiveIntegerField(
#         validators=[MinValueValidator(0)],
#         verbose_name='정가'
#     )
#     unit_price = models.PositiveIntegerField(
#         validators=[MinValueValidator(0)],
#         verbose_name='단가'
#     )
#     selling_price = models.PositiveIntegerField(
#         validators=[MinValueValidator(0)],
#         verbose_name='판매가'
#     )
#     notes = models.TextField(
#         null=True,
#         blank=True,
#         verbose_name='참고'
#     )
#     spare1 = models.CharField(
#         max_length=200,
#         null=True,
#         blank=True,
#         verbose_name='예비1'
#     )
#     spare2 = models.CharField(
#         max_length=200,
#         null=True,
#         blank=True,
#         verbose_name='예비2'
#     )
#     spare3 = models.CharField(
#         max_length=200,
#         null=True,
#         blank=True,
#         verbose_name='예비3'
#     )

#     @property
#     def distributed_quantity(self):
#         """총 배포 수량"""
#         distributed = self.bookdistribution_set.aggregate(
#             total=Sum('quantity')
#         )['total']
#         return distributed or 0

#     @property
#     def current_stock(self):
#         """현재 재고"""
#         try:
#             return self.quantity_received - self.distributed_quantity
#         except (TypeError, AttributeError):
#             return 0

#     def clean(self):
#         if self.book and self.subject and self.book.subject != self.subject:
#             raise ValidationError('선택한 도서가 해당 과목에 속하지 않습니다.')

#     class Meta:
#         verbose_name = '교재 입고'
#         verbose_name_plural = '교재 입고 관리'

#     def __str__(self):
#         book_name = self.book.name if self.book else '미지정'
#         return f"{book_name} (재고: {self.current_stock}/{self.quantity_received})"


# class BookDistribution(models.Model):
#     """교재 배포 관리"""
#     book_stock = models.ForeignKey(
#         BookStock,
#         on_delete=models.CASCADE,
#         verbose_name='교재'
#     )
#     student = models.ForeignKey(
#         Student,
#         on_delete=models.SET_NULL,
#         null=True,
#         verbose_name='지급 학생'
#     )
#     distribution_date = models.DateField(
#         verbose_name='지급 날짜'
#     )
#     quantity = models.PositiveIntegerField(
#         default=1,
#         validators=[MinValueValidator(1)],
#         verbose_name='지급 수량'
#     )
#     notes = models.TextField(
#         null=True,
#         blank=True,
#         verbose_name='비고'
#     )

#     def clean(self):
#         if not self.book_stock:
#             return
        
#         # 현재 지급 가능한 재고 확인
#         available_stock = self.book_stock.current_stock
#         if self.pk:  # 수정 시 자신의 수량은 제외
#             available_stock += BookDistribution.objects.get(pk=self.pk).quantity
            
#         if self.quantity > available_stock:
#             raise ValidationError(
#                 f'지급 가능한 재고가 {available_stock}권 남아있습니다.'
#             )

#     class Meta:
#         verbose_name = '교재 지급'
#         verbose_name_plural = '교재 지급 관리'

#     def __str__(self):
#         student_name = self.student.name if self.student else '미지정'
#         book_name = self.book_stock.book.name if self.book_stock and self.book_stock.book else '미지정'
#         return f"{book_name} -> {student_name}"