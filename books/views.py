from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DetailView, DeleteView
from django.contrib import messages

from common.models import Publisher, PurchaseLocation, Subject
from .models import Book
from .forms import BookForm

from django.db.models import Q

import pandas as pd
from django.http import HttpResponse
from django.contrib import messages
from django.views.generic import FormView
from django.shortcuts import redirect


class BookListView(LoginRequiredMixin, ListView):
    model = Book
    template_name = 'books/books_list.html'
    context_object_name = 'books'
    ordering = ['-entry_date', 'name']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # 과목 필터
        subject = self.request.GET.get('subject')
        if subject:
            queryset = queryset.filter(subject_id=subject)
        
        # 출판사 필터
        publisher = self.request.GET.get('publisher')
        if publisher:
            queryset = queryset.filter(publisher_id=publisher)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # 필터링을 위한 선택 옵션들 추가
        context['subjects'] = Subject.objects.all()
        context['publishers'] = Publisher.objects.all()
        # 현재 적용된 필터값들 유지
        context['current_filters'] = {
            'subject': self.request.GET.get('subject', ''),
            'publisher': self.request.GET.get('publisher', ''),
        }
        return context


class BookCreateView(LoginRequiredMixin, CreateView):
    model = Book
    form_class = BookForm
    template_name = 'books/books_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '교재 등록'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '교재가 성공적으로 등록되었습니다.')
        return super().form_valid(form)


class BookUpdateView(LoginRequiredMixin, UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/books_form.html'
    success_url = reverse_lazy('books:book_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '교재 수정'
        return context
    
    def form_valid(self, form):
        messages.success(self.request, '교재가 성공적으로 수정되었습니다.')
        return super().form_valid(form)
    

# class BookDetailView(LoginRequiredMixin, DetailView):
#     model = Book
#     template_name = 'books/book_detail.html'
#     context_object_name = 'book'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         book = self.get_object()
        
#         # QR 코드와 바코드 URL이 있는지 확인
#         context['has_qr_code'] = bool(book.qr_code)
#         context['has_barcode'] = bool(book.barcode)
        
#         return context

class BookDetailView(LoginRequiredMixin, DetailView):
    model = Book
    template_name = 'books/book_detail.html'
    context_object_name = 'book'


class BookDeleteView(LoginRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books:book_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "교재가 성공적으로 삭제되었습니다.")
        return super().delete(request, *args, **kwargs)



class BookExportView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # 교재 데이터를 DataFrame으로 변환
        books = Book.objects.all().values(
            'name', 'subject__name', 'isbn', 'publisher__name',
            'entry_date', 'original_price', 'purchase_price',
            'selling_price', 'purchase_location__name',
            'difficulty_level', 'memo'
        )
        
        df = pd.DataFrame(books)
        # 컬럼명 한글로 변경
        df.columns = [
            '교재명', '과목', 'ISBN', '출판사', '입고일',
            '원가', '입고가', '판매가', '구입처',
            '난이도', '메모'
        ]
        
        # 엑셀 파일 생성
        response = HttpResponse(content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = 'attachment; filename="books_export.xlsx"'
        
        df.to_excel(response, index=False, engine='openpyxl')
        return response

class BookImportForm(forms.Form):
    file = forms.FileField(
        label='엑셀 파일',
        help_text='*.xlsx 또는 *.csv 파일을 선택해주세요.'
    )

class BookImportView(LoginRequiredMixin, FormView):
    template_name = 'books/book_import.html'
    form_class = BookImportForm
    success_url = reverse_lazy('books:book_list')
    
    def form_valid(self, form):
        file = form.cleaned_data['file']
        
        try:
            # 파일 확장자 확인
            if file.name.endswith('.xlsx'):
                df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                raise ValueError('지원하지 않는 파일 형식입니다.')
            
            # 필수 컬럼 확인
            required_columns = ['교재명']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise ValueError(f'필수 컬럼이 없습니다: {", ".join(missing_columns)}')
            
            # 데이터 저장
            for _, row in df.iterrows():
                # 관련 객체 조회 또는 생성
                subject = Subject.objects.filter(name=row.get('과목')).first()
                publisher = Publisher.objects.filter(name=row.get('출판사')).first()
                purchase_location = PurchaseLocation.objects.filter(name=row.get('구입처')).first()
                
                # 교재 생성 또는 업데이트
                book, created = Book.objects.update_or_create(
                    name=row['교재명'],
                    defaults={
                        'subject': subject,
                        'isbn': row.get('ISBN'),
                        'publisher': publisher,
                        'entry_date': pd.to_datetime(row.get('입고일')).date() if pd.notna(row.get('입고일')) else None,
                        'original_price': row.get('원가'),
                        'purchase_price': row.get('입고가'),
                        'selling_price': row.get('판매가'),
                        'purchase_location': purchase_location,
                        'difficulty_level': row.get('난이도'),
                        'memo': row.get('메모')
                    }
                )
            
            messages.success(self.request, '교재 데이터를 성공적으로 가져왔습니다.')
            return super().form_valid(form)
            
        except Exception as e:
            messages.error(self.request, f'데이터 가져오기 실패: {str(e)}')
            return redirect('books:book_list')