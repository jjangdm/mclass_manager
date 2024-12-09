# Generated by Django 5.1.4 on 2024-12-08 23:03

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('books', '0007_remove_book_entry_date_remove_book_purchase_location'),
        ('bookstore', '0001_initial'),
        ('students', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bookdistribution',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student', verbose_name='학생'),
        ),
        migrations.AddField(
            model_name='bookissue',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='students.student', verbose_name='학생'),
        ),
        migrations.AddField(
            model_name='bookstock',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='books.book', verbose_name='도서명'),
        ),
        migrations.AddField(
            model_name='bookreturn',
            name='book_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.bookstock', verbose_name='재고'),
        ),
        migrations.AddField(
            model_name='bookissue',
            name='book_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.bookstock', verbose_name='재고'),
        ),
        migrations.AddField(
            model_name='bookdistribution',
            name='book_stock',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bookstore.bookstock', verbose_name='도서'),
        ),
    ]