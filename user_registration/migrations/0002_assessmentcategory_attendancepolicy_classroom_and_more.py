# Generated by Django 5.1.4 on 2024-12-28 08:01

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_registration', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AssessmentCategory',
            fields=[
                ('assessment_category_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('assessment_name', models.CharField(max_length=50)),
                ('number_of_times', models.IntegerField()),
                ('max_score_per_one', models.IntegerField()),
                ('max_score', models.IntegerField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_categories', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='AttendancePolicy',
            fields=[
                ('policy_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('minimum_attendance_percentage', models.FloatField()),
                ('total_time_school_open', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_policies', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('classroom_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('block_name', models.CharField(max_length=50)),
                ('room_number', models.CharField(max_length=50)),
                ('capacity', models.IntegerField()),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classrooms', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='ClassYear',
            fields=[
                ('class_year_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('class_name', models.CharField(max_length=50)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_years', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Class',
            fields=[
                ('class_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('arm_name', models.CharField(max_length=50)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='user_registration.school')),
                ('class_year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='classes', to='user_registration.classyear')),
            ],
        ),
        migrations.CreateModel(
            name='ComplianceVerification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accreditation_certificates', models.ImageField(upload_to='compliance/accreditation/')),
                ('proof_of_registration', models.ImageField(upload_to='compliance/registration/')),
                ('tax_identification_number', models.CharField(max_length=40)),
                ('compliance', models.BooleanField(default=True)),
                ('approved', models.BooleanField(default=False)),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='compliance_verification', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Constraint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fellowship_time', models.JSONField()),
                ('break_times', models.JSONField()),
                ('school', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='constraints', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Day',
            fields=[
                ('day_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='days', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Department',
            fields=[
                ('department_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='departments', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='ExamCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exam_name', models.CharField(default='Exam', max_length=50)),
                ('max_score', models.IntegerField()),
                ('assessment_category', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='exam_category', to='user_registration.assessmentcategory')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_categories', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='FeeCategory',
            fields=[
                ('fee_category_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
                ('amount', models.FloatField()),
                ('class_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fee_categories', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fee_categories', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('message_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='received_messages', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sent_messages', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('content', models.TextField()),
                ('recipient_group', models.CharField(choices=[('Teacher', 'Teacher'), ('Student', 'Student'), ('Everyone', 'Everyone')], max_length=50)),
                ('notification_type', models.CharField(max_length=50)),
                ('is_read', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipient_user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='notifications', to=settings.AUTH_USER_MODEL)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notifications', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('parent_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('occupation', models.CharField(max_length=100)),
                ('contact_info', models.CharField(max_length=100)),
                ('emergency_contact', models.CharField(max_length=100)),
                ('relationship', models.CharField(max_length=50)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='parents', to='user_registration.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Period',
            fields=[
                ('period_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='periods', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolAdmin',
            fields=[
                ('schooladmin_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('surname', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone_number', models.CharField(max_length=15)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('designation', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='school_admins', to='user_registration.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='school_admin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('student_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('admission_number', models.IntegerField()),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('admission_date', models.DateField()),
                ('status', models.CharField(default='Active', max_length=20)),
                ('profile_picture_path', models.ImageField(blank=True, null=True, upload_to='student_profiles/')),
                ('class_level', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='user_registration.class')),
                ('parent', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='students', to='user_registration.parent')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='students', to='user_registration.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('fee_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('amount', models.FloatField()),
                ('is_paid', models.BooleanField(default=False)),
                ('fee_category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='user_registration.feecategory')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='user_registration.student')),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('subject_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('department', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='user_registration.department')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subjects', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='SubjectPeriodLimit',
            fields=[
                ('subjectperiodlimit_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('periods_per_week', models.IntegerField()),
                ('double_periods', models.IntegerField()),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_period_limits', to='user_registration.school')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='period_limits', to='user_registration.subject')),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('subscription_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number_students', models.IntegerField()),
                ('amount_per_student', models.FloatField()),
                ('expected_fee', models.FloatField()),
                ('amount_paid', models.FloatField()),
                ('expired_date', models.DateField()),
                ('active_date', models.DateField()),
                ('is_active', models.BooleanField(default=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('teacher_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(max_length=50)),
                ('date_of_birth', models.DateField()),
                ('gender', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=255)),
                ('city', models.CharField(max_length=255)),
                ('state', models.CharField(max_length=255)),
                ('region', models.CharField(max_length=255)),
                ('country', models.CharField(max_length=255)),
                ('date_hire', models.DateField()),
                ('status', models.CharField(default='Active', max_length=20)),
                ('qualification', models.CharField(max_length=100)),
                ('specialization', models.CharField(max_length=100)),
                ('profile_picture_path', models.ImageField(blank=True, null=True, upload_to='teacher_profiles/')),
                ('cv', models.FileField(blank=True, null=True, upload_to='teacher_cvs/')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teachers', to='user_registration.school')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='teacher', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ClassTeacher',
            fields=[
                ('class_teacher_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_teacher', to='user_registration.class')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assigned_classes', to='user_registration.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='TeacherAssignment',
            fields=[
                ('teacher_subject_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('availability', models.JSONField(blank=True, null=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='user_registration.school')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_assignments', to='user_registration.subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_assignments', to='user_registration.teacher')),
            ],
        ),
        migrations.CreateModel(
            name='Year',
            fields=[
                ('year_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.BooleanField(default=False)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='years', to='user_registration.school')),
            ],
        ),
        migrations.CreateModel(
            name='Term',
            fields=[
                ('term_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=100)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('status', models.BooleanField(default=False)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terms', to='user_registration.school')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='terms', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='StudentSubjectAssignment',
            fields=[
                ('assignment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('assignment_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('status_updated_at', models.DateTimeField(blank=True, null=True)),
                ('rejection_reason', models.TextField(blank=True, null=True)),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_students', to='user_registration.classteacher')),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_subject_assignments', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_subject_assignments', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subject_assignments', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='user_registration.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_subject_assignments', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_subject_assignments', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='StudentClassAssignment',
            fields=[
                ('assignment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('assignment_date', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')], default='Pending', max_length=20)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_assignments', to='user_registration.student')),
                ('assigned_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignments_made', to='user_registration.teacher')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='student_assignments', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='ScorePerAssessmentInstance',
            fields=[
                ('scoreperassessment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('instance_number', models.IntegerField()),
                ('score', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='scores', to='user_registration.assessmentcategory')),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='user_registration.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_scores', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='ScoreObtainedPerAssessment',
            fields=[
                ('scoreperassessment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('total_score', models.FloatField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='total_scores', to='user_registration.assessmentcategory')),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obtained_assessment_scores', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obtained_assessment_scores', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obtained_assessment_scores', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obtained_assessment_scores', to='user_registration.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obtained_assessment_scores', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='obtained_assessment_scores', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('result_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ca_total', models.FloatField()),
                ('exam_score', models.FloatField()),
                ('total_score', models.FloatField()),
                ('grade', models.CharField(max_length=5)),
                ('remarks', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_registration.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='ExamScore',
            fields=[
                ('examscore_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('score', models.FloatField(help_text='Exam score achieved by the student.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_scores', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_scores', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_scores', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_scores', to='user_registration.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_scores', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='exam_scores', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='ContinuousAssessment',
            fields=[
                ('continuous_assessment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ca_total', models.FloatField(help_text='Total score from all continuous assessments.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='user_registration.class')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='user_registration.subject')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='continuous_assessments', to='user_registration.year')),
            ],
        ),
        migrations.AddField(
            model_name='classyear',
            name='year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_years', to='user_registration.year'),
        ),
        migrations.CreateModel(
            name='ClassTeacherComment',
            fields=[
                ('classteacher_comment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('comment', models.TextField(max_length=1000)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_comments', to='user_registration.class')),
                ('classteacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='user_registration.classteacher')),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='class_teacher_comments', to='user_registration.school')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_comments', to='user_registration.student')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_comments', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='teacher_comments', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='AttendanceFlag',
            fields=[
                ('flag_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('number_of_times_attended', models.FloatField()),
                ('number_of_times_open', models.FloatField()),
                ('attendance_percentage', models.FloatField()),
                ('flag_reason', models.CharField(blank=True, max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_flags', to='user_registration.class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_flags', to='user_registration.student')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_flags', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_flags', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('attendance_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('is_present', models.BooleanField(default=False)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='user_registration.school')),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='user_registration.class')),
                ('designation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='user_registration.classteacher')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='user_registration.student')),
                ('term', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='user_registration.term')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='user_registration.year')),
            ],
        ),
        migrations.CreateModel(
            name='AnnualResult',
            fields=[
                ('annual_result_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('first_term_score', models.FloatField(blank=True, null=True)),
                ('second_term_score', models.FloatField(blank=True, null=True)),
                ('third_term_score', models.FloatField(blank=True, null=True)),
                ('annual_average', models.FloatField(blank=True, help_text='Automatically calculated as the average of term scores.', null=True)),
                ('grade', models.CharField(blank=True, help_text='Grade assigned, e.g., A, B, C.', max_length=10, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('school', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_results', to='user_registration.school')),
                ('class_assigned', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_results', to='user_registration.class')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_results', to='user_registration.student')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_results', to='user_registration.subject')),
                ('year', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annual_results', to='user_registration.year')),
            ],
        ),
    ]
