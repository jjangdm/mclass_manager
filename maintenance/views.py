from django.views.generic import CreateView, ListView
from django.views.generic.base import TemplateView
from django.db.models import Sum
from django.urls import reverse_lazy
from django.contrib.messages import add_message, SUCCESS
from maintenance.forms import MaintenanceForm
from .models import Maintenance, Room
from django.utils import timezone


class MaintenanceCreateView(CreateView):
    model = Maintenance
    form_class = MaintenanceForm
    template_name = 'maintenance/maintenance_form.html'
    success_url = reverse_lazy('maintenance:create')

    def form_valid(self, form):
        self.object = form.save()  # 폼 저장
        add_message(              # 메시지 한 번만 추가
            self.request,
            SUCCESS,
            '성공적으로 등록되었습니다.'
        )
        return super(CreateView, self).form_valid(form)  # CreateView의 form_valid 직접 호출
    

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
        current_year = timezone.now().year
        
        year_range = range(current_year - 5, current_year + 6)
        selected_year = int(self.request.GET.get('year', current_year))
        selected_month = int(self.request.GET.get('month', timezone.now().month))
        
        months = [(i, f"{i}월") for i in range(1, 13)]
        
        queryset = self.get_queryset()
        
        context.update({
            'year_range': year_range,
            'months': months,
            'selected_year': selected_year,
            'selected_month': selected_month,
            'total_charge': queryset.aggregate(Sum('charge'))['charge__sum'] or 0
        })
        return context
    

class YearlyReportView(TemplateView):
    template_name = 'maintenance/yearly_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        available_years = [d.year for d in Maintenance.objects
                         .dates('date', 'year', order='DESC')
                         .distinct()]
        
        current_year = available_years[0] if available_years else timezone.now().year
        selected_year = int(self.request.GET.get('year', current_year))
        
        active_rooms = Room.objects.filter(
            maintenance__date__year=selected_year
        ).distinct().order_by('number')

        yearly_data = []
        total_charge = 0
        monthly_totals = [0] * 12  # 월별 합계를 저장할 리스트

        for room in active_rooms:
            monthly_charges = []
            room_total = 0
            
            for month in range(1, 13):
                charge = Maintenance.objects.filter(
                    room=room,
                    date__year=selected_year,
                    date__month=month
                ).aggregate(Sum('charge'))['charge__sum'] or 0
                
                monthly_charges.append(charge)
                room_total += charge
                monthly_totals[month-1] += charge  # 월별 합계 누적
            
            yearly_data.append({
                'room': room.number,
                'monthly_charges': monthly_charges,
                'total': room_total
            })
            total_charge += room_total

        context.update({
            'year': selected_year,
            'available_years': available_years,
            'months': range(1, 13),
            'yearly_data': yearly_data,
            'monthly_totals': monthly_totals,  # 월별 합계 추가
            'total_charge': total_charge,
            'grand_total': total_charge  # 총계
        })
        return context