# Generated by Django 5.1.4 on 2025-03-16 10:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0012_teacherassignment_department'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacherassignment',
            name='availability',
        ),
    ]
