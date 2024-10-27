from django.db import models
from students.models import Student
from textbooks.models import Textbook, TextbookQuestion

class GradeAnalysis(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, verbose_name='학생')
    textbook = models.ForeignKey(Textbook, on_delete=models.CASCADE, verbose_name='교재')
    analysis_date = models.DateField(verbose_name='분석일')
    total_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='총점')

    class Meta:
        verbose_name = '성적 분석'
        verbose_name_plural = '성적 분석'

    def __str__(self):
        return f"{self.student.name} - {self.textbook.name} ({self.analysis_date})"

class QuestionResult(models.Model):
    grade_analysis = models.ForeignKey(GradeAnalysis, on_delete=models.CASCADE, verbose_name='성적 분석')
    question = models.ForeignKey(TextbookQuestion, on_delete=models.CASCADE, verbose_name='문제')
    is_correct = models.BooleanField(verbose_name='정답 여부')

    class Meta:
        verbose_name = '문제 결과'
        verbose_name_plural = '문제 결과'

    def __str__(self):
        return f"{self.grade_analysis} - {self.question.question_number}"