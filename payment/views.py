from django.shortcuts import render
from django.db.models import Sum, F, Q
from students.models import Student
from bookstore.models import BookDistribution
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

def dashboard(request):
    search_query = request.GET.get('search', '').strip()
    page = request.GET.get('page', '1')
    
    # 기본 쿼리셋 생성
    students = Student.objects.annotate(
        unpaid_amount=Sum(
            F('bookdistribution__book_stock__selling_price') * F('bookdistribution__quantity'),
            filter=Q(bookdistribution__bookpayment__payment__isnull=True)
        )
    )
    
    # 검색 적용
    if search_query:
        students = students.filter(name__icontains=search_query)
    else:
        # 검색어가 없을 때만 미납금액이 있는 학생만 필터
        students = students.filter(unpaid_amount__gt=0)
    
    students = students.order_by('name')
    
    # 전체 통계 계산 (페이지네이션 적용 전)
    total_students = students.count()
    total_unpaid = sum(student.unpaid_amount or 0 for student in students)
    
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
    
    # 표시할 페이지 범위 (현재 페이지 앞뒤로 2페이지씩)
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