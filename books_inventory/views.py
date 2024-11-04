# mclass_manager/books_inventory/views.py

from django.views.generic import (
    ListView, DetailView, CreateView, DeleteView, UpdateView,
)
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.db.models import Q, F, Sum, Count, Case, When, Value
from django.db.models.functions import Coalesce
from django.contrib import messages
from .models import BookStock, BookDistribution, BookStockHistory
from common.models import Subject, PurchaseLocation
from books.models import Book


class StockListView(LoginRequiredMixin, ListView):
    model = BookStock
    template_name = 'books_inventory/stock_list.html'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BookStock.objects.select_related(
            'subject', 'book', 'purchase_location',
        ).annotate(
            distributed_total=Coalesce(Sum('bookdistribution__quantity'), 0),
            current_stock=F('quantity_received') - F('distributed_total')
        )
        
        # 과목 필터
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
            
        # 공급업체 필터
        purchase_location = self.request.GET.get('purchase_location')
        if purchase_location:
            queryset = queryset.filter(purchase_location_id=purchase_location)
            
        # 재고 상태 필터
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(order_status=status)
            
        # 검색어 필터
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(book__name__icontains=search) |
                Q(subject__name__icontains=search) |
                Q(purchase_location__name__icontains=search)
            )
            
        # 정렬
        sort_by = self.request.GET.get('sort', '-received_date')
        if sort_by in ['book__name', '-book__name', 'current_stock',
                      '-current_stock', 'received_date', '-received_date']:
            queryset = queryset.order_by(sort_by)
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'subjects': Subject.objects.all(),
            'purchase_location': PurchaseLocation.objects.all(),
            'status_choices': BookStock._meta.get_field('order_status').choices,
            'current_filters': {
                'subject': self.request.GET.get('subject', ''),
                'purchase_location': self.request.GET.get('purchase_location', ''),
                'status': self.request.GET.get('status', ''),
                'search': self.request.GET.get('search', ''),
                'sort': self.request.GET.get('sort', '-received_date'),
            }
        })
        return context


class StockDetailView(LoginRequiredMixin, DetailView):
    model = BookStock
    template_name = 'books_inventory/stock_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock = self.object
        
        # 배포 내역
        distributions = stock.bookdistribution_set.all().select_related('student')
        
        # 재고 변동 이력
        history = stock.bookstockhistory_set.all().select_related('processed_by')
        
        # 월별 배포 통계
        monthly_stats = distributions.values('distribution_date__month').annotate(
            total_distributed=Sum('quantity')
        ).order_by('distribution_date__month')
        
        context.update({
            'distributions': distributions,
            'history': history,
            'monthly_stats': monthly_stats,
        })
        return context


class StockCreateView(LoginRequiredMixin, CreateView):
    model = BookStock
    template_name = 'books_inventory/stock_form.html'
    fields = ['subject', 'book', 'purchase_location', 'quantity_received',
              'received_date', 'list_price', 'unit_price', 'selling_price',
              'reorder_point', 'notes']
    success_url = reverse_lazy('books_inventory:stock_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'subjects': Subject.objects.all(),
            'books': Book.objects.all(),
            'purchase_location': PurchaseLocation.objects.all(),
            'today': timezone.now().date()
        })
        return context
        
    def form_valid(self, form):
        form.instance.user = self.request.user  # user 정보 직접 전달
        return super().form_valid(form)


class StockUpdateView(LoginRequiredMixin, UpdateView):
    model = BookStock
    template_name = 'books_inventory/stock_form.html'
    fields = ['subject', 'book', 'purchase_location', 'quantity_received',
              'received_date', 'list_price', 'unit_price', 'selling_price',
              'reorder_point', 'notes']
    success_url = reverse_lazy('books_inventory:stock_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'subjects': Subject.objects.all(),
            'books': Book.objects.all(),
            'purchase_location': PurchaseLocation.objects.all(),
            'today': timezone.now().date(),
            'is_update': True
        })
        return context
        
    def form_valid(self, form):
        if form.has_changed():
            # 수량이 변경된 경우 이력 기록
            if 'quantity_received' in form.changed_data:
                old_quantity = self.get_object().quantity_received
                new_quantity = form.cleaned_data['quantity_received']
                quantity_diff = new_quantity - old_quantity
                
                if quantity_diff != 0:
                    self.object.log_transaction(
                        'ADJUST',
                        quantity_diff,
                        self.request.user,
                        f'재고 수정: {old_quantity} → {new_quantity}'
                    )
            
            messages.success(self.request, '재고 정보가 업데이트되었습니다.')
        return super().form_valid(form)


class BookDistributionCreateView(LoginRequiredMixin, CreateView):
    model = BookDistribution
    template_name = 'books_inventory/distribute.html'
    fields = ['book_stock', 'student', 'distribution_date', 'quantity', 'notes']
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        
        # 재고가 있는 교재만 표시
        stocks = BookStock.objects.annotate(
            available_stock=F('quantity_received') - Coalesce(
                Sum('bookdistribution__quantity'), 0
            )
        ).filter(available_stock__gt=0)
        
        form.fields['book_stock'].queryset = stocks
        form.fields['book_stock'].label_from_instance = lambda obj: (
            f"{obj.subject.name} - {obj.book.name} "
            f"(재고: {obj.current_stock}권)"
        )
        
        # 기본값 설정
        form.fields['distribution_date'].initial = timezone.now().date()
        form.fields['quantity'].initial = 1
        
        return form
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # 배포 기록 생성
        book_stock = form.cleaned_data['book_stock']
        book_stock.log_transaction(
            'OUT',
            form.cleaned_data['quantity'],
            self.request.user,
            f"배포: {form.cleaned_data['student']}에게 지급"
        )
        
        # 재고 상태 업데이트
        book_stock.update_order_status()
        
        messages.success(
            self.request,
            f"{book_stock.book.name} {form.cleaned_data['quantity']}권이 "
            f"{form.cleaned_data['student']}에게 지급되었습니다."
        )
        return response

    def get_success_url(self):
        return reverse('books_inventory:stock_detail',
                      kwargs={'pk': self.object.book_stock.pk})


class BookDistributionDeleteView(LoginRequiredMixin, DeleteView):
    model = BookDistribution
    
    def delete(self, request, *args, **kwargs):
        distribution = self.get_object()
        book_stock = distribution.book_stock
        
        # 재고 반환 기록
        book_stock.log_transaction(
            'RETURN',
            distribution.quantity,
            request.user,
            f"배포 취소: {distribution.student}의 지급 기록 삭제"
        )
        
        # 재고 상태 업데이트
        response = super().delete(request, *args, **kwargs)
        book_stock.update_order_status()
        
        messages.success(request, '지급 기록이 삭제되었습니다.')
        return response
    
    def get_success_url(self):
        return reverse('books_inventory:stock_detail',
                      kwargs={'pk': self.object.book_stock.pk})


class StockHistoryListView(LoginRequiredMixin, ListView):
    model = BookStockHistory
    template_name = 'books_inventory/stock_history.html'
    paginate_by = 20
    context_object_name = 'history_entries'
    
    def get_queryset(self):
        queryset = BookStockHistory.objects.select_related(
            'book_stock', 'book_stock__book', 'processed_by'
        )
        
        # 필터링
        book_stock_id = self.request.GET.get('book_stock')
        if book_stock_id:
            queryset = queryset.filter(book_stock_id=book_stock_id)
            
        transaction_type = self.request.GET.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
            
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(transaction_date__date__gte=date_from)
            
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(transaction_date__date__lte=date_to)
            
        return queryset.order_by('-transaction_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'book_stocks': BookStock.objects.all(),
            'transaction_types': BookStockHistory.TRANSACTION_TYPES,
            'current_filters': {
                'book_stock': self.request.GET.get('book_stock', ''),
                'type': self.request.GET.get('type', ''),
                'date_from': self.request.GET.get('date_from', ''),
                'date_to': self.request.GET.get('date_to', ''),
            }
        })
        return context


# API Views
def get_books_by_subject(request):
    """과목별 교재 목록을 반환하는 API"""
    subject_id = request.GET.get('subject_id')
    if not subject_id:
        return JsonResponse({'error': '과목을 선택해주세요.'}, status=400)
    
    try:
        books = Book.objects.filter(subject_id=subject_id).values('id', 'name')
        books_with_stock = []
        
        for book in books:
            stock = BookStock.objects.filter(book_id=book['id']).first()
            if stock:
                books_with_stock.append({
                    'id': stock.id,
                    'name': book['name'],
                    'current_stock': stock.current_stock,
                    'has_stock': stock.current_stock > 0
                })
            else:
                books_with_stock.append({
                    'id': None,
                    'name': f"{book['name']} (입고 필요)",
                    'current_stock': 0,
                    'has_stock': False
                })
            
        return JsonResponse(books_with_stock, safe=False)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_stock_status(request):
    """재고 현황 요약 정보를 반환하는 API"""
    try:
        summary = BookStock.objects.aggregate(
            total_books=Count('id'),
            low_stock=Count(
                Case(When(order_status='LOW_STOCK', then=Value(1)))
            ),
            out_of_stock=Count(
                Case(When(order_status='OUT_OF_STOCK', then=Value(1)))
            ),
            total_quantity=Sum('quantity_received'),
            total_distributed=Sum('bookdistribution__quantity')
        )
        
        return JsonResponse({
            'total_books': summary['total_books'],
            'low_stock': summary['low_stock'],
            'out_of_stock': summary['out_of_stock'],
            'total_quantity': summary['total_quantity'] or 0,
            'total_distributed': summary['total_distributed'] or 0,
            'current_stock': (summary['total_quantity'] or 0) -
                           (summary['total_distributed'] or 0)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




# from django.views.generic import ListView, DetailView, CreateView, DeleteView, UpdateView
# from django.contrib.auth.mixins import LoginRequiredMixin
# from django.http import JsonResponse
# from django.urls import reverse_lazy, reverse
# from django.utils import timezone
# from django.db.models import Q, F, Sum
# from .models import BookStock, BookDistribution
# from common.models import Subject
# from students.models import Student
# from books.models import Book
# from django.contrib import messages
# from django.db.models.functions import Coalesce


# class StockListView(LoginRequiredMixin, ListView):
#     model = BookStock
#     template_name = 'books_inventory/stock_list.html'
#     paginate_by = 10
    
#     def get_queryset(self):
#         queryset = BookStock.objects.select_related('subject', 'book').all()
        
#         # 과목 필터
#         subject = self.request.GET.get('subject')
#         if subject:
#             queryset = queryset.filter(subject_id=subject)
            
#         # 검색어 필터
#         search = self.request.GET.get('search')
#         if search:
#             queryset = queryset.filter(
#                 Q(book__name__icontains=search) |
#                 Q(subject__name__icontains=search)
#             )
            
#         return queryset


# class StockCreateView(LoginRequiredMixin, CreateView):
#     model = BookStock
#     template_name = 'books_inventory/stock_form.html'
#     fields = ['subject', 'book', 'quantity_received', 'received_date',
#               'list_price', 'unit_price', 'selling_price', 'notes']
#     success_url = reverse_lazy('books_inventory:stock_list')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['subjects'] = Subject.objects.all()
#         context['books'] = Book.objects.all()
#         context['today'] = timezone.now().date()
#         return context


# class StockUpdateView(LoginRequiredMixin, UpdateView):
#     model = BookStock
#     template_name = 'books_inventory/stock_form.html'
#     fields = ['subject', 'book', 'quantity_received', 'received_date',
#               'list_price', 'unit_price', 'selling_price', 'notes']
#     success_url = reverse_lazy('books_inventory:stock_list')

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['subjects'] = Subject.objects.all()
#         context['books'] = Book.objects.all()
#         context['today'] = timezone.now().date()
#         return context


# class StockDetailView(LoginRequiredMixin, DetailView):
#     model = BookStock
#     template_name = 'books_inventory/stock_detail.html'
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['distributions'] = self.object.bookdistribution_set.all().select_related('student')
#         return context


# class BookDistributionCreateView(LoginRequiredMixin, CreateView):
#     model = BookDistribution
#     template_name = 'books_inventory/distribute.html'
#     fields = ['book_stock', 'student', 'distribution_date', 'notes']
#     success_url = reverse_lazy('books_inventory:stock_list')
    
#     def get_form(self, form_class=None):
#         form = super().get_form(form_class)
#         # 모든 교재 stock 정보 가져오기
#         stocks = BookStock.objects.annotate(
#             distributed_total=Coalesce(Sum('bookdistribution__quantity'), 0)
#         ).select_related('subject', 'book')
        
#         form.fields['book_stock'].queryset = stocks
#         form.fields['book_stock'].label_from_instance = lambda obj: (
#             f"{obj.subject.name} - {obj.book.name} "
#             f"(재고: {obj.quantity_received - obj.distributed_total}권)"
#         )
#         return form


# class BookDistributionDeleteView(LoginRequiredMixin, DeleteView):
#     model = BookDistribution
    
#     def get_success_url(self):
#         messages.success(self.request, '지급 기록이 삭제되었습니다.')
#         return reverse('books_inventory:stock_detail',
#                       kwargs={'pk': self.object.book_stock.pk})
    
#     def get(self, request, *args, **kwargs):
#         return self.post(request, *args, **kwargs)


# # API Views (독립적인 함수)
# def get_books_by_subject(request):
#     """과목별 교재 목록을 반환하는 API"""
#     subject_id = request.GET.get('subject_id')
#     if not subject_id:
#         return JsonResponse({'error': '과목을 선택해주세요.'}, status=400)
    
#     try:
#         # 해당 과목의 교재 목록 조회
#         books = Book.objects.filter(
#             subject_id=subject_id
#         ).values('id', 'name')
        
#         # 각 교재의 재고 정보 추가
#         books_with_stock = []
#         for book in books:
#             stock = BookStock.objects.filter(book_id=book['id']).first()
#             if stock:
#                 books_with_stock.append({
#                     'id': stock.id,  # BookStock의 id를 반환
#                     'name': book['name'],
#                     'current_stock': stock.current_stock,
#                     'has_stock': stock.current_stock > 0
#                 })
#             else:
#                 # 재고 정보가 없는 경우
#                 books_with_stock.append({
#                     'id': None,
#                     'name': f"{book['name']} (입고 필요)",
#                     'current_stock': 0,
#                     'has_stock': False
#                 })
            
#         return JsonResponse(books_with_stock, safe=False)
        
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)