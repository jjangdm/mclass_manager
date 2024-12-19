from django.shortcuts import render
from django.db.models import Sum, F
from .models import Payment
from students.models import Student
from bookstore.models import BookDistribution

def dashboard(request):
    search_query = request.GET.get('search', '')
    
    # 학생 정보 조회
    students = Student.objects.all()
    if search_query:
        students = students.filter(name__icontains=search_query)

    # 각 학생별 미납 금액 계산
    for student in students:
        # 총 교재 금액 계산
        total_books = BookDistribution.objects.filter(student=student).aggregate(
            total=Sum(F('book_stock__selling_price') * F('quantity'))
        )['total'] or 0
        
        # 납부 금액 계산
        paid_amount = Payment.objects.filter(student=student).aggregate(
            total=Sum('paid_amount')
        )['total'] or 0
        
        student.unpaid_amount = total_books - paid_amount

    context = {
        'students': students,
        'total_students': students.count(),
        'search_query': search_query,
        'total_unpaid': sum(student.unpaid_amount for student in students)
    }
    
    return render(request, 'payment/dashboard.html', context)
