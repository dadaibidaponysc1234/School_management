# Generated by Django 5.1.4 on 2025-06-28 17:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0026_school_created_at_superadmin_middle_name_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'ordering': ['-active_date']},
        ),
        migrations.AlterUniqueTogether(
            name='classteachercomment',
            unique_together={('student', 'term', 'school')},
        ),
        migrations.DeleteModel(
            name='StudentSubjectAssignment',
        ),
        migrations.RemoveField(
            model_name='classteachercomment',
            name='class_assigned',
        ),
        migrations.RemoveField(
            model_name='classteachercomment',
            name='year',
        ),
    ]
