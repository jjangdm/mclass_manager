from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 
        'subject', 
        'publisher', 
        'entry_date', 
        'original_price',
        'purchase_price', 
        'selling_price',
        'difficulty_level',
        'isbn', 
        'unique_code',
    ]
    list_filter = ['subject', 'publisher', 'purchase_location', 'difficulty_level']
    readonly_fields = ['barcode', 'qr_code', 'unique_code']
    search_fields = ['name', 'isbn', 'memo']
    fieldsets = [
        ('기본 정보', {
            'fields': ['name', 'subject', 'isbn', 'publisher']
        }),
        ('가격 정보', {
            'fields': ['original_price', 'purchase_price', 'selling_price']
        }),
        ('구매 정보', {
            'fields': ['entry_date', 'purchase_location']
        }),
        ('추가 정보', {
            'fields': ['difficulty_level', 'memo']
        }),
        ('예비 필드', {
            'fields': ['spare1', 'spare2', 'spare3'],
            'classes': ['collapse']
        })
    ]