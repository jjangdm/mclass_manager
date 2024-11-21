from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView
from django.utils import timezone
from bookstore.forms import StockCreateForm, StockUpdateForm
from .models import BookStock, BookReturn
from .models import BookIssue
from .forms import BookIssueForm
from django.db.models import Sum


def stock_list(request):
    stocks_in_stock = BookStock.objects.filter(quantity__gt=0)
    stocks_zero_quantity = BookStock.objects.filter(quantity=0)
    context = {
        'stocks_in_stock': stocks_in_stock,
        'stocks_zero_quantity': stocks_zero_quantity,
    }
    return render(request, 'bookstore/stock_list.html', context)


def stock_list_with_new_stock(request, new_stock):
    new_stock_obj = BookStock.objects.get(pk=new_stock)
    context = {
        'stock_list': BookStock.objects.all(),
        'new_stock': new_stock_obj,
    }
    return render(request, 'bookstore/stock_list.html', context)


# class StockDetailView(DetailView):
#     model = BookStock
#     template_name = 'bookstore/stock_detail.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         book = self.object.book
        
#         # 동일 도서의 모든 재고 정보 조회
#         stocks = BookStock.objects.filter(book=book).order_by('received_date')
        
#         # 총 수량 계산
#         total_quantity = stocks.aggregate(Sum('quantity'))['quantity__sum'] or 0

#         # 입고일자별, 판매가별 그룹화
#         grouped_stocks = defaultdict(lambda: defaultdict(list))
#         for stock in stocks:
#             grouped_stocks[stock.received_date][stock.selling_price].append(stock)

#         context.update({
#             'book': book,
#             'total_quantity': total_quantity,
#             'grouped_stocks': dict(grouped_stocks),
#         })
        
#         return context
    

class StockCreateView(LoginRequiredMixin, CreateView):
    model = BookStock
    template_name = 'bookstore/stock_form.html'
    form_class = StockCreateForm

    def form_valid(self, form):
        stock = form.save(commit=False)
        existing_stock = BookStock.objects.filter(
            book=stock.book,
            unit_price=stock.unit_price,
            selling_price=stock.selling_price
        ).first()

        if existing_stock:
            existing_stock.quantity += stock.quantity
            existing_stock.save()
            return redirect('bookstore:stock_detail', pk=existing_stock.pk)
            
        return super().form_valid(form)


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
    ).order_by('received_date')
    
    # 전체 재고 수량 계산
    total_quantity = stock_list.aggregate(
        total=Sum('quantity')
    )['total'] or 0
    
    context = {
        'book': stock.book,
        'total_quantity': total_quantity,
        'stock_list': stock_list,  # 입고일자 순으로 정렬된 재고 목록
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
    
    # 동일한 도서의 모든 재고 가져오기
    stock_list = BookStock.objects.filter(book=stock.book).order_by('received_date')
    
    # 합산된 전체 수량 계산
    total_quantity = stock_list.aggregate(total_quantity=Sum('quantity'))['total_quantity']
    
    if request.method == 'POST':
        return_quantity = int(request.POST.get('return_quantity', 0))
        return_date = request.POST.get('return_date', timezone.now().date())
        
        if return_quantity > 0 and return_quantity <= total_quantity:
            remaining_quantity = return_quantity
            for s in stock_list:
                if s.quantity >= remaining_quantity:
                    s.quantity -= remaining_quantity
                    s.save()
                    break
                else:
                    remaining_quantity -= s.quantity
                    s.quantity = 0
                    s.save()
            
            BookReturn.objects.create(
                book_stock=stock,
                quantity=return_quantity,
                return_date=return_date
            )
            
            return redirect(reverse('bookstore:stock_detail', kwargs={'pk': stock.id}))
    else:
        return render(request, 'bookstore/stock_return_form.html', {'stock': stock, 'today': timezone.now().date(), 'total_quantity': total_quantity})


def stock_return_list(request):
    return_list = BookReturn.objects.all()
    return render(request, 'bookstore/stock_return_list.html', {'return_list': return_list})
