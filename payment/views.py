from django.shortcuts import render
from django.db.models import Sum, F, Value
from payment.models import Payment
from students.models import Student
from django.core.paginator import Paginator
from django.db.models.functions import Coalesce
from bookstore.models import BookDistribution

def dashboard(request):
    search_query = request.GET.get('search', '')
    page = request.GET.get('page', '1')
    
    # 기본 쿼리셋 구성
    students = Student.objects.all()
    if search_query:
        students = students.filter(name__icontains=search_query)

    # 학생별 교재 지급 금액과 납부 금액을 계산
    for student in students:
        # 교재 지급 총액 계산
        distributed_amount = BookDistribution.objects.filter(
            student=student
        ).aggregate(
            total=Sum(F('book_stock__selling_price') * F('quantity'))
        )['total'] or 0
        
        # 납부 금액 계산
        paid_amount = Payment.objects.filter(
            student=student
        ).aggregate(
            total=Sum('paid_amount')
        )['total'] or 0
        
        # 각 학생 객체에 미납 금액 할당
        student.unpaid_amount = distributed_amount - paid_amount

    # 페이지네이션 설정
    paginator = Paginator(students, 10)  # 페이지당 10명씩 표시
    page_obj = paginator.get_page(page)
    
    # 페이지 범위 계산
    page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=2, on_ends=1)

    # 전체 미납 금액 계산
    total_unpaid = sum(student.unpaid_amount for student in students)

    context = {
        'students': page_obj,
        'total_students': students.count(),
        'search_query': search_query,
        'total_unpaid': total_unpaid,
        'page_range': page_range,
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
    }
    
    return render(request, 'payment/dashboard.html', context)