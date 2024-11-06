# Generated by Django 5.1 on 2024-10-30 01:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('books_inventory', '0002_bookstock_bookdistribution_delete_bookinventory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='bookdistribution',
            options={'verbose_name': '교재 지급', 'verbose_name_plural': '교재 지급 관리'},
        ),
        migrations.AlterModelOptions(
            name='bookstock',
            options={'verbose_name': '교재 입고', 'verbose_name_plural': '교재 입고 관리'},
        ),
        migrations.RemoveField(
            model_name='bookdistribution',
            name='distribution_target',
        ),
        migrations.RemoveField(
            model_name='bookstock',
            name='return_date',
        ),
        migrations.RemoveField(
            model_name='bookstock',
            name='return_quantity',
        ),
        migrations.AlterField(
            model_name='bookdistribution',
            name='book_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books_inventory.bookstock', verbose_name='교재'),
        ),
    ]