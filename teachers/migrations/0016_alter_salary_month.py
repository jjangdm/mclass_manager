# Generated by Django 4.2.16 on 2024-11-13 01:50

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teachers', '0015_alter_attendance_options_alter_teacher_hire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salary',
            name='month',
            field=models.PositiveIntegerField(default=11, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)], verbose_name='월'),
        ),
    ]