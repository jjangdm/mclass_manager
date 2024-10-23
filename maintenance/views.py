# views.py
from django.views.generic import CreateView, ListView
from django.views.generic.base import TemplateView
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Maintenance
from .forms import MaintenanceForm
from datetime import datetime

class MaintenanceCreateView(CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:monthly_report')

class MonthlyReportView(ListView):
    model = Maintenance
    template_name = 'maintenance/monthly_report.html'
    context_object_name = 'maintenance_list'

    def get_queryset(self):
        year = self.request.GET.get('year', timezone.now().year)
        month = self.request.GET.get('month', timezone.now().month)
        return Maintenance.objects.filter(
            date__year=year,
            date__month=month
        ).order_by('room')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()
        context['year'] = self.request.GET.get('year', timezone.now().year)
        context['month'] = self.request.GET.get('month', timezone.now().month)
        context['total_charge'] = queryset.aggregate(Sum('charge'))['charge__sum'] or 0
        return context

class YearlyReportView(TemplateView):
    template_name = 'maintenance/yearly_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year = self.request.GET.get('year', timezone.now().year)
        
        # Get all unique rooms
        rooms = Maintenance.objects.filter(
            date__year=year
        ).values_list('room', flat=True).distinct().order_by('room')

        yearly_data = []
        total_charge = 0

        for room in rooms:
            monthly_charges = []
            room_total = 0
            
            for month in range(1, 13):
                charge = Maintenance.objects.filter(
                    room=room,
                    date__year=year,
                    date__month=month
                ).aggregate(Sum('charge'))['charge__sum'] or 0
                
                monthly_charges.append(charge)
                room_total += charge
            
            yearly_data.append({
                'room': room,
                'monthly_charges': monthly_charges,
                'total': room_total
            })
            total_charge += room_total

        context.update({
            'year': year,
            'months': range(1, 13),
            'yearly_data': yearly_data,
            'total_charge': total_charge
        })
        return context