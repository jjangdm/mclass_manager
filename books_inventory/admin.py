from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.db.models import F, Value, IntegerField, Sum
from django.db.models.functions import Coalesce
from books.models import Book
from .models import BookStock, BookDistribution, BookStockHistory


@admin.register(BookStock)
class BookStockAdmin(admin.ModelAdmin):
    list_display = ('book', 'subject', 'quantity_received', 
                   'current_stock', 'status_display', 'purchase_location', 
                   'received_date')
    list_filter = ('subject', 'purchase_location', 'order_status', 'received_date')
    search_fields = ('book__name', 'purchase_location__name')
    readonly_fields = ('current_stock', 'distributed_quantity', 'order_status')
    autocomplete_fields = ['book', 'purchase_location']
    
    fieldsets = (
        ('기본 정보', {
            'fields': ('subject', 'book', 'purchase_location', 
                      'quantity_received', 'received_date')
        }),
        ('가격 정보', {
            'fields': ('list_price', 'unit_price', 'selling_price')
        }),
        ('재고 현황', {
            'fields': ('current_stock', 'distributed_quantity', 
                      'reorder_point', 'order_status')
        }),
        ('추가 정보', {
            'fields': ('notes',),
            'classes': ('collapse',)
        })
    )

    def status_display(self, obj):
        status_colors = {
            'IN_STOCK': 'green',
            'LOW_STOCK': 'orange',
            'OUT_OF_STOCK': 'red',
            'ON_ORDER': 'blue'
        }
        color = status_colors.get(obj.order_status, 'gray')
        return format_html(
            '<span style="color: {};">{}</span>',
            color,
            obj.get_order_status_display()
        )
    status_display.short_description = '재고 상태'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "book":
            if request.method == "GET" and "subject" in request.GET:
                kwargs["queryset"] = Book.objects.filter(
                    subject_id=request.GET["subject"]
                )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        creating = not obj.pk
        if creating:
            # 신규 입고의 경우
            obj.save()
            obj.log_transaction(
                'IN', 
                obj.quantity_received,
                request.user,
                '최초 입고'
            )
        else:
            # 수정의 경우
            if 'quantity_received' in form.changed_data:
                old_obj = self.model.objects.get(pk=obj.pk)
                quantity_diff = obj.quantity_received - old_obj.quantity_received
                if quantity_diff != 0:
                    obj.log_transaction(
                        'ADJUST',
                        quantity_diff,
                        request.user,
                        f'수량 조정: {old_obj.quantity_received} → {obj.quantity_received}'
                    )
            obj.save()
        
        obj.update_order_status()

    class Media:
        js = ('admin/js/vendor/jquery/jquery.min.js',
              'books_inventory/js/book_stock_admin.js')


@admin.register(BookDistribution)
class BookDistributionAdmin(admin.ModelAdmin):
    list_display = ('student', 'book_display', 'quantity', 
                   'distribution_date', 'purchase_location_display')
    list_filter = ('distribution_date', 'book_stock__subject', 
                  'book_stock__purchase_location')
    search_fields = ('student__name', 'book_stock__book__name', 
                    'book_stock__purchase_location__name')
    autocomplete_fields = ['student', 'book_stock']
    
    def book_display(self, obj):
        if obj.book_stock and obj.book_stock.book:
            return format_html(
                '{} <br><small style="color: {};">재고: {}/{}</small>',
                obj.book_stock.book.name,
                'red' if obj.book_stock.current_stock < 5 else 'green',
                obj.book_stock.current_stock,
                obj.book_stock.quantity_received
            )
        return "-"
    book_display.short_description = '교재 (현재 재고)'

    def purchase_location_display(self, obj):
        if obj.book_stock and obj.book_stock.purchase_location:
            return obj.book_stock.purchase_location.name
        return "-"
    purchase_location_display.short_description = '구매처'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['book_stock'].queryset = BookStock.objects.annotate(
            distributed_sum=Coalesce(
                Sum('bookdistribution__quantity'),
                Value(0),
                output_field=IntegerField()
            )
        ).filter(
            quantity_received__gt=F('distributed_sum')
        )
        if 'book_stock' in form.base_fields:
            form.base_fields['book_stock'].label = '교재 (재고)'
        return form

    def save_model(self, request, obj, form, change):
        if not obj.distribution_date:
            obj.distribution_date = timezone.now().date()
        
        creating = not obj.pk
        super().save_model(request, obj, form, change)
        
        # 재고 이력 기록
        if creating:
            obj.book_stock.log_transaction(
                'OUT',
                obj.quantity,
                request.user,
                f'배포: {obj.student}에게 지급'
            )
        elif 'quantity' in form.changed_data:
            old_obj = self.model.objects.get(pk=obj.pk)
            quantity_diff = obj.quantity - old_obj.quantity
            if quantity_diff != 0:
                obj.book_stock.log_transaction(
                    'ADJUST',
                    -quantity_diff,
                    request.user,
                    f'배포 수량 수정: {old_obj.quantity} → {obj.quantity}'
                )
        
        obj.book_stock.update_order_status()

    class Media:
        js = ('admin/js/vendor/jquery/jquery.min.js',)


@admin.register(BookStockHistory)
class BookStockHistoryAdmin(admin.ModelAdmin):
    list_display = ('book_stock', 'transaction_type', 'quantity', 
                   'transaction_date', 'processed_by')
    list_filter = ('transaction_type', 'transaction_date', 
                  'book_stock__subject', 'book_stock__purchase_location')
    search_fields = ('book_stock__book__name', 'notes', 
                    'processed_by__username')
    readonly_fields = ('book_stock', 'transaction_type', 'quantity', 
                      'transaction_date', 'processed_by', 'notes')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False