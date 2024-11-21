# Generated by Django 4.2.16 on 2024-11-21 16:08

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('bookstore', '0003_bookissue'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookissue',
            name='issued_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='출고일'),
        ),
    ]