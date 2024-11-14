from django import forms
from .models import BookStock

class StockCreateForm(forms.ModelForm):
    class Meta:
        model = BookStock
        fields = ['received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo']

class StockUpdateForm(forms.ModelForm):
    class Meta:
        model = BookStock
        fields = ['received_date', 'book', 'quantity', 'list_price', 'unit_price', 'selling_price', 'memo']
