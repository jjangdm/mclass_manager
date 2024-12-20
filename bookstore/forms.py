from django import forms
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import BookStock, BookIssue
from students.models import Student
from bookstore.models import BookDistribution


class StockCreateForm(forms.ModelForm):
    class Meta:
        model = BookStock
        fields = ['received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo']

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = BookStock
        fields = ['received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo']

class BookIssueForm(forms.ModelForm):
    class Meta:
        model = BookDistribution  # BookIssue 대신 BookDistribution 사용
        fields = ['book_stock', 'student', 'quantity', 'sold_date', 'notes']
        widgets = {
            'sold_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 활성 학생만 필터링
        self.fields['student'].queryset = Student.objects.filter(is_active=True)
        # 재고가 있는 도서만 필터링
        self.fields['book_stock'].queryset = BookStock.objects.filter(quantity__gt=0)
        # 기본값 설정
        self.fields['quantity'].initial = 1
        self.fields['sold_date'].initial = timezone.now().date()
        
        # 필드 레이블 수정
        self.fields['sold_date'].label = '판매일'
        self.fields['notes'].label = '비고'
        
        # 필수 필드 표시
        self.fields['book_stock'].required = True
        self.fields['student'].required = True
        self.fields['quantity'].required = True
        self.fields['sold_date'].required = True

    def clean(self):
        cleaned_data = super().clean()
        book_stock = cleaned_data.get('book_stock')
        quantity = cleaned_data.get('quantity')

        if book_stock and quantity:
            if book_stock.quantity < quantity:
                raise ValidationError({
                    'quantity': f'재고가 부족합니다. 현재 재고: {book_stock.quantity}권'
                })

        return cleaned_data
