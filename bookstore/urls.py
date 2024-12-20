from django.urls import path
from . import views

app_name = 'bookstore'

# urlpatterns = [
#     path('', views.stock_list, name='stock_list'),
#     path('stock/<int:pk>/', views.stock_detail, name='stock_detail'),  # 함수 기반 뷰로 변경
#     path('create/', views.stock_create, name='stock_create'),
#     path('<int:pk>/update/', views.stock_update, name='stock_update'),
#     path('<int:pk>/delete/', views.stock_delete, name='stock_delete'),
#     path('list/<int:new_stock>/', views.stock_list_with_new_stock, name='stock_list_with_new_stock'),
#     path('issues/', views.book_issue_list, name='book_issue_list'),
#     path('issues/create/', views.book_issue_create, name='book_issue_create'),
#     path('stock/<int:stock_id>/return/', views.stock_return, name='stock_return'),
#     path('returns/', views.stock_return_list, name='stock_return_list'),
#     path('distribute/', views.distribute_book, name='distribute_book'),
#     path('distributions/', views.distribution_list, name='distribution_list'),
# ]


urlpatterns = [
    path('', views.stock_list, name='stock_list'),
    path('stock/create/', views.stock_create, name='stock_create'),
    path('stock/<int:pk>/', views.stock_detail, name='stock_detail'),
    path('stock/<int:pk>/update/', views.stock_update, name='stock_update'),
    path('stock/<int:pk>/delete/', views.stock_delete, name='stock_delete'),
    path('stock/<int:stock_id>/return/', views.stock_return, name='stock_return'),
    path('returns/', views.stock_return_list, name='stock_return_list'),
    
    # BookDistribution 관련 URL
    path('distributions/', views.distribution_list, name='distribution_list'),
    path('distribute/', views.distribute_book, name='distribute_book'),
    
    # 이전 URL 패턴들은 당분간 유지하되 새로운 뷰로 리다이렉트
    path('issues/', views.distribution_list, name='book_issue_list'),
    path('issues/create/', views.distribute_book, name='book_issue_create'),
]