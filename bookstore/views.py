from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from bookstore.forms import StockCreateForm, StockUpdateForm
from .models import BookStock
from books.models import Book
from students.models import Student


class StockListView(ListView):
    model = BookStock
    template_name = 'bookstore/stock_list.html'
    context_object_name = 'stock_list'

def stock_list_with_new_stock(request, new_stock):
    new_stock_obj = BookStock.objects.get(pk=new_stock)
    context = {
        'stock_list': BookStock.objects.all(),
        'new_stock': new_stock_obj,
    }
    return render(request, 'bookstore/stock_list.html', context)


class StockDetailView(LoginRequiredMixin, DetailView):
    model = BookStock
    template_name = 'bookstore/stock_detail.html'


class StockCreateView(LoginRequiredMixin, CreateView):
    model = BookStock
    template_name = 'bookstore/stock_form.html'
    fields = [
        'received_date',
        'book', 
        'quantity',  
        'list_price', 
        'unit_price', 
        'selling_price', 
        'memo',]
    
    def get_success_url(self):
        return reverse('bookstore:stock_list')


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


def stock_list(request):
    stock_list = BookStock.objects.order_by('-received_date')
    return render(request, 'bookstore/stock_list.html', {'stock_list': stock_list})  # template 경로 수정


def stock_detail(request, pk):
    stock = get_object_or_404(BookStock, pk=pk)
    return render(request, 'bookstore/stock_detail.html', {'stock': stock})


def stock_create(request):
    if request.method == 'POST':
        form = StockCreateForm(request.POST)
        if form.is_valid():
            new_stock = form.save()
            messages.success(request, '도서 재고가 성공적으로 등록되었습니다.')
            return redirect('bookstore:stock_list')  # 단순히 목록 페이지로 리다이렉트
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
