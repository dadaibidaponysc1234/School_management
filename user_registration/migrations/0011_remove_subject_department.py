# Generated by Django 5.1.4 on 2025-03-04 13:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0010_school_registered_by'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='subject',
            name='department',
        ),
    ]
