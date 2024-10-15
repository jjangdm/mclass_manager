# Generated by Django 5.1 on 2024-10-16 02:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0013_alter_attendance_options_attendance_end_time_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='teacher',
            name='hire_date',
            field=models.DateField(blank=True, null=True, verbose_name='입사��'),
        ),
        migrations.AlterField(
            model_name='teacher',
            name='is_active',
            field=models.BooleanField(default=True, verbose_name='재직 중'),
        ),
    ]
