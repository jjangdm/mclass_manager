# Generated by Django 5.1.4 on 2024-12-20 00:37

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('bookstore', '0002_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='금액')),
                ('payment_date', models.DateField(default=django.utils.timezone.now, verbose_name='결제일')),
                ('payment_method', models.CharField(choices=[('CASH', '현금'), ('CARD', '카드'), ('TRANSFER', '계좌이체'), ('OTHER', '기타')], default='CASH', max_length=50, verbose_name='결제 방법')),
                ('notes', models.TextField(blank=True, null=True, verbose_name='비고')),
                ('book_distribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.bookdistribution', verbose_name='도서 지급 내역')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student', verbose_name='학생')),
            ],
            options={
                'verbose_name': '결제',
                'verbose_name_plural': '결제 내역',
                'ordering': ['-payment_date', 'student__name'],
            },
        ),
    ]
