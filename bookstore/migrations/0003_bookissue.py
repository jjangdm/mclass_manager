# Generated by Django 4.2.16 on 2024-11-21 15:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0007_student_is_active'),
        ('bookstore', '0002_alter_bookdistribution_quantity_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='BookIssue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveIntegerField(verbose_name='수량')),
                ('issued_date', models.DateField(auto_now_add=True, verbose_name='출고일')),
                ('memo', models.TextField(blank=True, null=True, verbose_name='비고')),
                ('book_stock', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.bookstock', verbose_name='재고')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student', verbose_name='학생')),
            ],
            options={
                'verbose_name': '도서 출고',
                'verbose_name_plural': '도서 출고 목록',
            },
        ),
    ]
