from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from common.models import Subject, Publisher, PurchaseLocation
from django.utils.translation import gettext_lazy as _

import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image, ImageDraw
import barcode
from barcode.writer import ImageWriter


class Book(models.Model):
    # 기존 필드들은 그대로 유지
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

    # 새로 추가되는 필드들
    barcode = models.ImageField(
        upload_to='books/barcodes/', 
        blank=True, 
        null=True,
        verbose_name='바코드'
    )
    qr_code = models.ImageField(
        upload_to='books/qrcodes/', 
        blank=True, 
        null=True,
        verbose_name='QR코드'
    )
    unique_code = models.CharField(
        max_length=50, 
        unique=True, 
        null=True, 
        blank=True,
        verbose_name='고유코드'
    )

    class Meta:
        verbose_name = '교재'
        verbose_name_plural = '교재 목록'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        # 고유 코드가 없는 경우 생성
        if not self.unique_code:
            self.unique_code = f"BK{self.isbn if self.isbn else str(self.id).zfill(8)}"

        # QR 코드 생성
        if not self.qr_code:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(self.unique_code)
            qr.make(fit=True)
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # BytesIO를 사용하여 이미지를 임시로 저장
            temp_handle = BytesIO()
            qr_image.save(temp_handle, 'PNG')
            temp_handle.seek(0)
            
            # 파일 이름 생성
            self.qr_code.save(
                f'qr_{self.unique_code}.png',
                File(temp_handle),
                save=False
            )

        # 바코드 생성
        if not self.barcode and self.isbn:
            EAN = barcode.get_barcode_class('ean13')
            ean = EAN(self.isbn, writer=ImageWriter())
            buffer = BytesIO()
            ean.write(buffer)
            self.barcode.save(
                f'barcode_{self.isbn}.png',
                File(buffer),
                save=False
            )

        super().save(*args, **kwargs)



# class Book(models.Model):
#     name = models.CharField(
#         max_length=200, 
#         verbose_name='교재 이름'
#     )
#     subject = models.ForeignKey(
#         Subject, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         verbose_name='과목'
#     )
#     isbn = models.CharField(
#         max_length=13, 
#         null=True, 
#         blank=True, 
#         verbose_name='ISBN'
#     )
#     publisher = models.ForeignKey(
#         Publisher, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         verbose_name='출판사'
#     )
#     entry_date = models.DateField(
#         null=True, 
#         blank=True, 
#         verbose_name='입고일'
#     )
#     original_price = models.PositiveIntegerField(
#         null=True, 
#         blank=True, 
#         verbose_name='원가'
#     )
#     purchase_price = models.PositiveIntegerField(
#         null=True, 
#         blank=True, 
#         verbose_name='입고 가격'
#     )
#     selling_price = models.PositiveIntegerField(
#         null=True, 
#         blank=True, 
#         verbose_name='판매 가격'
#     )
#     purchase_location = models.ForeignKey(
#         PurchaseLocation, 
#         on_delete=models.SET_NULL, 
#         null=True, 
#         blank=True, 
#         verbose_name='구입처'
#     )
#     difficulty_level = models.PositiveIntegerField(
#         validators=[
#             MinValueValidator(1),
#             MaxValueValidator(10)
#         ],
#         null=True, 
#         blank=True, 
#         verbose_name='교재 난이도'
#     )
#     memo = models.TextField(
#         null=True, 
#         blank=True, 
#         verbose_name='메모'
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

#     class Meta:
#         verbose_name = '교재'
#         verbose_name_plural = '교재 목록'

#     def __str__(self):
#         return self.name
