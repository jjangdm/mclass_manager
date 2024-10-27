from django.contrib import admin
from .models import Textbook, TextbookInventory, TextbookQuestion
from django.urls import path
from django.shortcuts import render, redirect
from django import forms

class TextbookInventoryInline(admin.TabularInline):
    model = TextbookInventory
    extra = 1

class TextbookQuestionInline(admin.TabularInline):
    model = TextbookQuestion
    extra = 1

class CsvImportForm(forms.Form):
    csv_file = forms.FileField()

@admin.register(Textbook)
class TextbookAdmin(admin.ModelAdmin):
    list_display = ('name', 'subject', 'isbn', 'publisher', 'difficulty', 'selling_price')
    search_fields = ('name', 'isbn')
    list_filter = ('subject', 'publisher', 'difficulty')
    inlines = [TextbookInventoryInline, TextbookQuestionInline]

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('import-csv/', self.import_csv)]
        return new_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            csv_file = request.FILES["csv_file"]
            # CSV 파일 처리 로직 구현
            self.message_user(request, "CSV 파일이 성공적으로 가져와졌습니다.")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(request, "admin/csv_form.html", payload)

@admin.register(TextbookInventory)
class TextbookInventoryAdmin(admin.ModelAdmin):
    list_display = ('textbook', 'quantity', 'date', 'is_incoming')
    list_filter = ('is_incoming', 'date')
    search_fields = ('textbook__name',)

@admin.register(TextbookQuestion)
class TextbookQuestionAdmin(admin.ModelAdmin):
    list_display = ('textbook', 'question_number', 'category_large', 'category_medium', 'category_small', 'question_type', 'difficulty')
    list_filter = ('textbook', 'category_large', 'difficulty')
    search_fields = ('textbook__name', 'question_number')