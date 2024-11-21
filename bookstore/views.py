from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils import timezone
from bookstore.forms import StockCreateForm, StockUpdateForm
from .models import BookStock, BookReturn, BookIssue, Book
from .forms import BookIssueForm
from django.db.models import Sum, Q
from django.shortcuts import render


def stock_list(request):
    # 각 책별 총 재고 수량을 계산
    books_with_quantity = Book.objects.annotate(
        total_quantity=Sum('bookstock__quantity')
    )
    
    # 재고가 있는 도서들의 재고 정보를 가져옵니다
    stocks_in_stock = BookStock.objects.filter(quantity__gt=0)
    
    # 총 재고가 0인 도서들을 찾습니다
    zero_quantity_books = books_with_quantity.filter(
        Q(total_quantity=0) | Q(total_quantity__isnull=True)
    ).values_list('id', flat=True)
    
    # 총 재고가 0인 도서들의 가장 최근 재고 정보를 가져옵니다
    stocks_zero_quantity = []
    for book_id in zero_quantity_books:
        latest_stock = BookStock.objects.filter(
            book_id=book_id
        ).order_by('-received_date').first()
        if latest_stock:
            stocks_zero_quantity.append(latest_stock)
    
    # 같은 책이지만 다른 가격을 가진 도서들을 찾습니다
    books_with_price_variations = set()
    for book in Book.objects.all():
        prices = BookStock.objects.filter(book=book).values_list('selling_price', flat=True).distinct()
        if len(prices) > 1:
            books_with_price_variations.add(book.id)
    
    # 디버깅을 위한 출력
    # print("Books with zero total quantity:", len(zero_quantity_books))
    # print("Stocks with zero quantity:", len(stocks_zero_quantity))
    
    context = {
        'stocks_in_stock': stocks_in_stock,
        'stocks_zero_quantity': stocks_zero_quantity,
        'books_with_different_prices': books_with_price_variations
    }
    return render(request, 'bookstore/stock_list.html', context)


def stock_list_with_new_stock(request, new_stock):
    new_stock_obj = BookStock.objects.get(pk=new_stock)
    context = {
        'stock_list': BookStock.objects.all(),
        'new_stock': new_stock_obj,
    }
    return render(request, 'bookstore/stock_list.html', context)
  

class StockCreateView(LoginRequiredMixin, CreateView):
    model = BookStock
    template_name = 'bookstore/stock_form.html'
    form_class = StockCreateForm

    def get_success_url(self):
        return reverse('bookstore:stock_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, '새로운 재고가 성공적으로 등록되었습니다.')
        return response


class StockUpdateView(LoginRequiredMixin, UpdateView):
    model = BookStock
    template_name = 'bookstore/stock_form.html'
    fields = [
        'received_date',
        'book', 
        'quantity',  
        'list_price', 
        'unit_price', 
        'selling_price', 
        'memo',
    ]

    def get_success_url(self):
        return reverse('bookstore:stock_detail', kwargs={'pk': self.object.pk})


class StockDeleteView(LoginRequiredMixin, DeleteView):
    model = BookStock
    template_name = 'bookstore/stock_confirm_delete.html'

    def get_success_url(self):
        return reverse('bookstore:stock_list')


def stock_detail(request, pk):
    # 현재 선택된 재고 항목
    stock = get_object_or_404(BookStock, pk=pk)
    
    # 같은 책의 모든 재고 항목을 입고일자 순으로 조회
    stock_list = BookStock.objects.filter(
        book=stock.book
    ).order_by('-received_date')
    
    # 전체 재고 수량 계산
    total_quantity = stock_list.aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    context = {
        'book': stock.book,
        'total_quantity': total_quantity,
        'stock_list': stock_list,
        'selected_stock': stock,  # 현재 선택된 재고 항목 추가
    }
    
    return render(request, 'bookstore/stock_detail.html', context)


def stock_create(request):
    if request.method == 'POST':
        form = StockCreateForm(request.POST)
        if form.is_valid():
            new_stock = form.save()
            messages.success(request, '재고가 성공적으로 등록되었습니다.')
            return redirect('bookstore:stock_list')  # 단순히 등록 페이지로 리다이렉트
    else:
        form = StockCreateForm()
    return render(request, 'bookstore/stock_form.html', {'form': form})


def stock_update(request, pk):
    stock = get_object_or_404(BookStock, pk=pk)
    if request.method == 'POST':
        form = StockUpdateForm(request.POST, instance=stock)
        if form.is_valid():
            form.save()
            messages.success(request, '도서 재고가 성공적으로 수정되었습니다.')
            return redirect('bookstore:stock_detail', pk=pk)
    else:
        form = StockUpdateForm(instance=stock)
    return render(request, 'bookstore/stock_form.html', {'form': form})


def stock_delete(request, pk):
    stock = get_object_or_404(BookStock, pk=pk)
    if request.method == 'POST':
        stock.delete()
        messages.success(request, '도서 재고가 성공적으로 삭제되었습니다.')
        return redirect('bookstore:stock_list')
    return render(request, 'bookstore/stock_confirm_delete.html', {'stock': stock})


def book_issue_list(request):
    issues = BookIssue.objects.all()
    return render(request, 'bookstore/book_issue_list.html', {'issues': issues})


def book_issue_create(request):
    if request.method == 'POST':
        form = BookIssueForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bookstore:book_issue_list')
    else:
        form = BookIssueForm()
    return render(request, 'bookstore/book_issue_form.html', {'form': form})


def stock_return(request, stock_id):
    stock = get_object_or_404(BookStock, id=stock_id)
    
    # 수량이 0인 재고는 반품할 수 없음
    if stock.quantity == 0:
        messages.error(request, '수량이 0인 재고는 반품할 수 없습니다.')
        return redirect('bookstore:stock_detail', pk=stock.id)
    
    # 동일한 도서의 모든 재고 가져오기
    stock_list = BookStock.objects.filter(book=stock.book).order_by('received_date')
    
    # 합산된 전체 수량 계산
    total_quantity = stock_list.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    
    if request.method == 'POST':
        return_quantity = int(request.POST.get('return_quantity', 0))
        return_date = request.POST.get('return_date', timezone.now().date())
        
        # 반품 수량 유효성 검사 추가
        if return_quantity <= 0:
            messages.error(request, '반품 수량은 0보다 커야 합니다.')
            return render(request, 'bookstore/stock_return_form.html', 
                        {'stock': stock, 'today': timezone.now().date(), 'total_quantity': total_quantity})
            
        if return_quantity > stock.quantity:
            messages.error(request, f'반품 수량이 현재 재고 수량({stock.quantity}권)보다 많을 수 없습니다.')
            return render(request, 'bookstore/stock_return_form.html', 
                        {'stock': stock, 'today': timezone.now().date(), 'total_quantity': total_quantity})
        
        # 반품 처리
        stock.quantity -= return_quantity
        stock.save()
        
        BookReturn.objects.create(
            book_stock=stock,
            quantity=return_quantity,
            return_date=return_date
        )
        
        messages.success(request, f'{return_quantity}권이 성공적으로 반품 처리되었습니다.')
        return redirect('bookstore:stock_detail', pk=stock.id)
        
    return render(request, 'bookstore/stock_return_form.html', 
                 {'stock': stock, 'today': timezone.now().date(), 'total_quantity': stock.quantity})


def stock_return_list(request):
    # 반품 목록을 날짜 역순으로 가져옵니다
    return_list = BookReturn.objects.select_related(
        'book_stock', 
        'book_stock__book'
    ).order_by('-return_date')
    
    # 디버깅을 위한 출력
    # print("Returns found:", return_list.count())
    # for ret in return_list:
    #     print(f"Date: {ret.return_date}, Book: {ret.book_stock.book.name}, Quantity: {ret.quantity}")
    
    context = {
        'return_list': return_list,
        'total_returned': sum(ret.quantity for ret in return_list)
    }
    return render(request, 'bookstore/stock_return_list.html', context)
