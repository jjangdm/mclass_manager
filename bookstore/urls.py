from django.urls import path
from . import views

app_name = 'bookstore'

urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('create/', views.stock_create, name='stock_create'),
    path('<int:pk>/', views.stock_detail, name='stock_detail'),
    path('<int:pk>/update/', views.stock_update, name='stock_update'),
    path('<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('list/<int:new_stock>/', views.stock_list_with_new_stock, name='stock_list_with_new_stock'),  # 수정된 부분
]