# Generated by Django 5.1 on 2024-10-13 20:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classes', '0002_initial'),
        ('students', '0002_alter_student_cash_receipt_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='base_class',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='base_students', to='classes.class', verbose_name='기본 학급'),
        ),
        migrations.AlterField(
            model_name='student',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True, verbose_name='이메일'),
        ),
        migrations.AlterField(
            model_name='student',
            name='first_class_date',
            field=models.DateField(blank=True, null=True, verbose_name='첫수업 날짜'),
        ),
        migrations.AlterField(
            model_name='student',
            name='interview_date',
            field=models.DateField(blank=True, null=True, verbose_name='인터뷰 날짜'),
        ),
        migrations.AlterField(
            model_name='student',
            name='interview_score',
            field=models.IntegerField(blank=True, choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7), (8, 8), (9, 9), (10, 10)], null=True, verbose_name='상담시 성적'),
        ),
    ]
