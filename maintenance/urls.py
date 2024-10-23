# maintenance/urls.py
from django.urls import path
from . import views

app_name = 'maintenance'

urlpatterns = [
    path('create/', views.MaintenanceCreateView.as_view(), name='create'),
    path('monthly/', views.MonthlyReportView.as_view(), name='monthly_report'),
    path('yearly/', views.YearlyReportView.as_view(), name='yearly_report'),
]