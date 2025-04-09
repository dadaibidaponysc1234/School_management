# Generated by Django 5.1.4 on 2025-03-19 19:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0015_remove_subjectclass_class_year'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacherassignment',
            name='department',
        ),
        migrations.AlterField(
            model_name='teacherassignment',
            name='subject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='user_registration.subjectclass'),
        ),
        migrations.AlterField(
            model_name='teacherassignment',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='subject_assignments', to='user_registration.teacher'),
        ),
    ]
