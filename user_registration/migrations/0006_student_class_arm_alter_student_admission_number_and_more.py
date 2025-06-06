# Generated by Django 5.1.4 on 2025-01-11 15:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0005_alter_studentregistrationpin_otp_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='class_arm',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='user_registration.class'),
        ),
        migrations.AlterField(
            model_name='student',
            name='admission_number',
            field=models.IntegerField(help_text='Unique number assigned to the student upon admission', verbose_name='Admission Number'),
        ),
        migrations.AlterField(
            model_name='student',
            name='class_level',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='user_registration.classyear'),
        ),
    ]
