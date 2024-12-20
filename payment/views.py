from django.shortcuts import get_object_or_404, render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Sum, F, Q, Value, OuterRef, Subquery, Count
from django.db.models.functions import Coalesce
from students.models import Student
from bookstore.models import BookDistribution, BookStock
from payment.models import BookPayment, Payment, PaymentHistory

def dashboard(request):
    search_query = request.GET.get('search', '').strip()
    
    # 각 학생별 미납 금액 계산을 위한 서브쿼리
    unpaid_amounts = BookDistribution.objects.filter(
        student=OuterRef('pk'),
        bookpayment__isnull=True  # 결제되지 않은 배부만 계산
    ).values('student').annotate(
        unpaid_total=Sum(F('book_stock__selling_price') * F('quantity'))
    ).values('unpaid_total')

    # 학생 쿼리셋 생성
    students = Student.objects.annotate(
        unpaid_amount=Coalesce(Subquery(unpaid_amounts), 0),
        unpaid_books_count=Count(
            'bookdistribution',
            filter=Q(bookdistribution__bookpayment__isnull=True)
        )
    )
    
    # 검색 적용
    if search_query:
        students = students.filter(name__icontains=search_query)
    else:
        students = students.filter(unpaid_amount__gt=0)
    
    students = students.order_by('name')
    
    # 전체 통계 계산
    total_students = students.count()
    total_unpaid = students.aggregate(total=Sum('unpaid_amount'))['total'] or 0
    
    # 페이지네이션 적용
    paginator = Paginator(students, 20)  # 한 페이지당 20명
    page = request.GET.get('page')
    
    try:
        students_page = paginator.page(page)
    except PageNotAnInteger:
        students_page = paginator.page(1)
    except EmptyPage:
        students_page = paginator.page(paginator.num_pages)
    
    # 현재 페이지 범위 계산
    current_page = students_page.number
    total_pages = paginator.num_pages
    page_range = range(max(1, current_page - 2), 
                      min(total_pages + 1, current_page + 3))
    
    context = {
        'students': students_page,
        'search_query': search_query,
        'total_students': total_students,
        'total_unpaid': total_unpaid,
        'page_range': page_range,
        'total_pages': total_pages,
        'current_page': current_page
    }
    
    return render(request, 'payment/dashboard.html', context)


def student_detail(request, student_id):
    student = get_object_or_404(Student.objects.annotate(
        unpaid_amount=Sum(
            F('bookdistribution__book_stock__selling_price') * F('bookdistribution__quantity'),
            filter=Q(bookdistribution__bookpayment__payment__isnull=True)
        )
    ), pk=student_id)
    
    unpaid_books = student.get_unpaid_books()
    
    return render(request, 'payment/student_detail.html', {
        'student': student,
        'unpaid_books': unpaid_books,
    })