# Generated by Django 5.1 on 2024-10-24 02:57

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0003_remove_maintenance_maintenance_room_id_681cd3_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenance',
            name='room',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maintenance.room', verbose_name='호실'),
        ),
    ]