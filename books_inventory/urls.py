from django.urls import path
from . import views

app_name = 'books_inventory'

urlpatterns = [
    # 재고 관리
    path('', views.StockListView.as_view(), name='stock_list'),
    path('create/', views.StockCreateView.as_view(), name='stock_create'),
    path('<int:pk>/edit/', views.StockUpdateView.as_view(), name='stock_edit'),
    path('<int:pk>/', views.StockDetailView.as_view(), name='stock_detail'),
    
    # 교재 지급
    path('distribute/', views.BookDistributionCreateView.as_view(), name='distribute'),
    path('distribute/<int:pk>/delete/', views.BookDistributionDeleteView.as_view(), name='distribution_delete'),
    
    # API
    path('api/books-by-subject/', views.get_books_by_subject, name='get_books_by_subject'),
]