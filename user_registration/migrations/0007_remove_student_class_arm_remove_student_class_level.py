# Generated by Django 5.1.4 on 2025-01-13 07:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0006_student_class_arm_alter_student_admission_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='student',
            name='class_arm',
        ),
        migrations.RemoveField(
            model_name='student',
            name='class_level',
        ),
    ]
