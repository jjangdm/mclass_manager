from django.contrib import admin
from .models import GradeAnalysis, QuestionResult

class QuestionResultInline(admin.TabularInline):
    model = QuestionResult
    extra = 1

@admin.register(GradeAnalysis)
class GradeAnalysisAdmin(admin.ModelAdmin):
    list_display = ('student', 'textbook', 'analysis_date', 'total_score')
    list_filter = ('analysis_date', 'textbook')
    search_fields = ('student__name', 'textbook__name')
    inlines = [QuestionResultInline]

@admin.register(QuestionResult)
class QuestionResultAdmin(admin.ModelAdmin):
    list_display = ('grade_analysis', 'question', 'is_correct')
    list_filter = ('is_correct', 'question__textbook')
    search_fields = ('grade_analysis__student__name', 'question__question_number')