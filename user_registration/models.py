from django.contrib.auth.models import User
from django.db import models
import uuid
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from datetime import date, timedelta
from django.conf import settings
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from django.utils import timezone

class Role(models.Model):
    """
    Represents roles in the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Corresponds to role_id
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(null=True, blank=True)  # Allows NULL values

    def __str__(self):
        return self.name


class UserRole(models.Model):
    """
    Maps users to roles.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Corresponds to user_role_id
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_roles")
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name="user_roles")

    def __str__(self):
        return f"{self.user.username} - {self.role.name}"


class SuperAdmin(models.Model):
    """
    Represents super admins.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Corresponds to superadmin_id
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="super_admin")
    user_role = models.ForeignKey('UserRole', on_delete=models.CASCADE, related_name='super_admins', null=True)
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.surname}"


class School(models.Model):
    """
    Represents schools in the system.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Corresponds to school_id
    school_name = models.CharField(max_length=100)
    # registration_number = models.CharField(max_length=50, unique=True)  # Optional unique identifier
    school_address = models.CharField(max_length=255, default="Default Address")
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    short_name = models.CharField(max_length=15)
    logo = models.ImageField(upload_to="school_logos/", null=True, blank=True)  # Optional field for school logo
    school_type = models.CharField(max_length=100)
    education_level = models.CharField(max_length=100)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="registered_schools")  # Track user who registered the school
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['school_name', 'school_address'],
                name='unique_school_name_address',
                violation_error_message="A school with this name and address already exists."
            )
        ]
        
    def __str__(self):
        return self.school_name


class Subscription(models.Model):
    """
    Represents school subscriptions to the platform.
    """
    subscription_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="school_subscriptions")
    number_students = models.IntegerField(default=0)  # Still stored, but not relied on
    amount_per_student = models.FloatField()
    expected_fee = models.FloatField(default=0.0)     # Still stored, but not relied on
    amount_paid = models.FloatField()
    expired_date = models.DateField()
    active_date = models.DateField()
    is_active = models.BooleanField(default=False)    # Still stored, but not relied on

    def save(self, *args, **kwargs):
        # Keep old behavior for POST/PUT, but dynamic logic will be used on GET
        if self.school and self.school.school_students.exists():
            self.number_students = self.school.school_students.count()
        else:
            self.number_students = 0
        self.expected_fee = self.number_students * self.amount_per_student
        today = date.today()
        self.is_active = (self.amount_paid >= self.expected_fee) and (today <= self.expired_date)
        super().save(*args, **kwargs)

    @property
    def live_number_students(self):
        return self.school.school_students.count() if self.school else 0

    @property
    def live_expected_fee(self):
        return self.live_number_students * self.amount_per_student

    @property
    def live_is_active(self):
        today = date.today()
        return (self.amount_paid >= self.live_expected_fee) and (today <= self.expired_date)

    def __str__(self):
        return f"Subscription for {self.school.school_name}"
    class Meta:
        ordering = ['-active_date']
    

class ComplianceVerification(models.Model):
    """
    Represents compliance documents for school registration.
    """
    school = models.OneToOneField('School', on_delete=models.CASCADE, related_name="compliance_verification")
    accreditation_certificates = models.ImageField(upload_to="compliance/accreditation/")
    proof_of_registration = models.ImageField(upload_to="compliance/registration/")
    tax_identification_number = models.CharField(max_length=40)
    compliance = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Compliance for {self.school.school_name}"


class Message(models.Model):
    """
    Represents messages sent between users.
    """
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.sender.username} to {self.recipient.username}"


class SchoolAdmin(models.Model):
    """
    Represents school administrators.
    """
    schooladmin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="school_admin")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="school_admins")
    surname = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    designation = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.surname} - {self.school.school_name}"



class Year(models.Model):
    """
    Represents academic years for a school.
    """
    year_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="years")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        # If this year is being set to active
        if self.status:
            # Deactivate other years for the same school
            Year.objects.filter(school=self.school, status=True).exclude(pk=self.pk).update(status=False)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.school.school_name})"

    

class Term(models.Model):
    """
    Represents terms within an academic year.
    """
    term_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="terms")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="terms")
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def save(self, *args, **kwargs):
        # If this year is being set to active
        if self.status:
            # Deactivate other years for the same school
            Term.objects.filter(school=self.school, status=True).exclude(pk=self.pk).update(status=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} - {self.year.name} ({self.school.school_name})"

    

class ClassYear(models.Model):
    """
    Represents class years within an academic year for a school.
    """
    class_year_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="class_years")
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name="class_years")
    class_name = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.class_name} - {self.year.name} ({self.school.school_name})"


class Class(models.Model):
    """
    Represents individual classes (e.g., Grade 1A) in a school.
    """
    class_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    arm_name = models.CharField(max_length=50)
    class_year = models.ForeignKey(ClassYear, on_delete=models.CASCADE, related_name="classes")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="classes")

    def __str__(self):
        return f"{self.arm_name} ({self.class_year.class_name}) - {self.school.school_name}"


class Classroom(models.Model):
    """
    Represents physical classrooms in a school.
    """
    classroom_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    block_name = models.CharField(max_length=50)
    room_number = models.CharField(max_length=50)
    capacity = models.IntegerField()
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="classrooms")

    def __str__(self):
        return f"{self.block_name} {self.room_number} ({self.school.school_name})"


class Student(models.Model):
    """
    Represents students enrolled in schools.
    """
    student_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="student")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="school_students")
    admission_number = models.IntegerField( verbose_name="Admission Number",
                                           help_text="Unique number assigned to the student upon admission")
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name = models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    region = models.CharField(max_length=255,null=True, blank=True)
    country = models.CharField(max_length=255)
    admission_date = models.DateField()
    status = models.CharField(max_length=20, default="Active")
    profile_picture_path = models.ImageField(upload_to="student_profiles/", null=True, blank=True)

    parent_first_name = models.CharField(max_length=50, default='Unknown')
    parent_middle_name = models.CharField(max_length=50, null=True, blank=True)
    parent_last_name = models.CharField(max_length=50, default='Unknown')
    parent_occupation = models.CharField(max_length=100, default='Unknown')
    parent_contact_info = models.CharField(max_length=100, default='Unknown') 
    parent_emergency_contact = models.CharField(max_length=100, default='Unknown')
    parent_relationship = models.CharField(max_length=50, default='Unknown')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.school.school_name})"


class StudentRegistrationPin(models.Model):
    """
    Model to store one-time pins (OTPs) for student self-registration.
    """
    pin_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name='registration_pins')
    otp = models.CharField(max_length=16)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('school', 'otp')

    def __str__(self):
        return f"{self.school.school_name} - {self.otp}"


class Teacher(models.Model):
    """
    Represents teachers employed by schools.
    """
    teacher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="teachers")
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, null=True, blank=True)
    last_name= models.CharField(max_length=50)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    date_hire = models.DateField()
    status = models.CharField(max_length=20, default="Active")
    qualification = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)
    profile_picture_path = models.ImageField(upload_to="teacher_profiles/", null=True, blank=True)
    cv = models.FileField(upload_to="teacher_cvs/", null=True, blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.school.school_name})"


class Department(models.Model):
    """
    Represents academic departments in a school.
    """
    department_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="departments")

    def __str__(self):
        return f"{self.name} ({self.school.school_name})"


class Subject(models.Model):
    """
    Represents subjects offered by schools.
    """
    subject_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="subjects")

    def __str__(self):
        return f"{self.name} ({self.school.school_name})"


class ClassTeacher(models.Model):
    """Maps teachers to their assigned classes."""
    
    class_teacher_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="class_teacher")
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE, related_name="assigned_classes")
    school = models.ForeignKey('School', on_delete=models.CASCADE, null=True, related_name="class_teachers")

    def __str__(self):
        return f"{self.teacher.first_name} {self.teacher.last_name} - {self.class_assigned.arm_name}"


class SubjectClass(models.Model):
    subject_class_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="subject_class")
    # class_year= models.ForeignKey('ClassYear', on_delete=models.CASCADE, related_name="subject_class")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="subject_class")
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name="subject_class")  # Fix here
    
    def __str__(self):
        return f"{self.subject.name} ({self.department.name})"

class ClassDepartment(models.Model):
    subject_class_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="class_department")
    classes = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="class_department")
    department = models.ForeignKey('Department', on_delete=models.SET_NULL, null=True, blank=True, related_name="class_department")  # Fix here
    
    def __str__(self):
        return f"{self.classes.arm_name} ({self.department.name})"

class TeacherAssignment(models.Model):
    """
    Tracks teacher assignments to subjects and classes.
    """
    teacher_subject_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True, blank=True, related_name="subject_assignments")
    subject_class = models.ForeignKey('SubjectClass', on_delete=models.CASCADE, related_name="teacher_assignments")
    class_department_assigned = models.ForeignKey('ClassDepartment', on_delete=models.CASCADE, related_name="teacher_assignments")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="teacher_assignments")
    
    # availability = models.JSONField(null=True, blank=True)

    def __str__(self):
        teacher_name = self.teacher.first_name if self.teacher else "NoTeacher"
        class_arm = self.class_department_assigned.classes.arm_name if self.class_department_assigned and self.class_department_assigned.classes else "NoClass"
        subject_name = self.subject_class.subject.name if self.subject_class and self.subject_class.subject else "NoSubject"
        dept_name = self.subject_class.department.name if self.subject_class and self.subject_class.department else "NoDept"
    
        return f"{teacher_name} {class_arm} - {subject_name} {dept_name}"


class StudentClass(models.Model):
    student_class_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="subject_class")
    class_year = models.ForeignKey('ClassYear', on_delete=models.CASCADE, related_name="subject_class")
    class_arm = models.ForeignKey('ClassDepartment', on_delete=models.CASCADE, related_name="subject_class")

    class Meta:
        unique_together = ('student', 'class_year','class_arm')  # Optional: Prevent same student being assigned multiple times to same year
        
    def __str__(self):
        return f" {self.class_arm.classes.arm_name} {self.student.last_name}"


class SubjectRegistrationControl(models.Model):
    """
    Controls whether students can register subjects for a given school.
    """
    school = models.OneToOneField('School', on_delete=models.CASCADE, related_name="registration_control")
    is_open = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Subject Registration - {self.school.school_name}"


# models.py (snippet for StudentSubjectRegistration)
class StudentSubjectRegistration(models.Model):
    registration_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student_class = models.ForeignKey('StudentClass', on_delete=models.CASCADE, related_name="subject_registrations")
    subject_class = models.ForeignKey('SubjectClass', on_delete=models.CASCADE, related_name="subject_registrations")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="subject_registrations")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="subject_registrations", null=True, blank=True)

    # Class history snapshot at the time of registration
    class_year_name = models.CharField(max_length=100,null=True, blank=True)
    class_arm_name = models.CharField(max_length=100,null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected')
        ],
        default='Pending'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student_class', 'subject_class', 'term')
        verbose_name = "Student Subject Registration"
        verbose_name_plural = "Student Subject Registrations"

    def save(self, *args, **kwargs):
        if self.student_class:
            self.class_year_name = self.student_class.class_year.class_name
            self.class_arm_name = self.student_class.class_arm.classes.arm_name
        if self.student_class and not self.school:
            self.school = self.student_class.student.school

        if not self.term and self.school:
            active_term = Term.objects.filter(school=self.school, status=True).first()
            if not active_term:
                raise ValidationError("No active term found for this school.")
            self.term = active_term

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student_class.student.last_name} - {self.subject_class.subject.name} ({self.term.name})"
    


# class StudentSubjectAssignment(models.Model):
    # """
    # Tracks subject assignments for students.
    # """
    # assignment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="subject_assignments")
    # subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="student_assignments")
    # class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="student_subject_assignments")
    # term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="student_subject_assignments")
    # year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="student_subject_assignments")
    # school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="student_subject_assignments")
    # assigned_by = models.ForeignKey('ClassTeacher', on_delete=models.SET_NULL, null=True, related_name="assigned_students")
    # assignment_date = models.DateTimeField(auto_now_add=True)
    # status = models.CharField(max_length=20, choices=[
    #     ('Pending', 'Pending'),
    #     ('Approved', 'Approved'),
    #     ('Rejected', 'Rejected')
    # ], default='Pending')
    # status_updated_at = models.DateTimeField(null=True, blank=True)
    # rejection_reason = models.TextField(null=True, blank=True)

    # def __str__(self):
    #     return f"{self.student.first_name} - {self.subject.name} ({self.status})"
    # pass

################ RESULT MODULE ##################
class ResultVisibilityControl(models.Model):
    school = models.OneToOneField('School', on_delete=models.CASCADE, related_name='result_visibility_control')
    term_result_open = models.BooleanField(default=False)
    annual_result_open = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VisibilityControl - {self.school.school_name} | Term: {self.term_result_open}, Annual: {self.annual_result_open}"

class AssessmentCategory(models.Model):
    assessment_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="assessment_categories")
    assessment_name = models.CharField(max_length=50)
    number_of_times = models.IntegerField()
    max_score_per_one = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.assessment_name} ({self.school.school_name})"


class ResultConfiguration(models.Model):
    school = models.OneToOneField('School', on_delete=models.CASCADE, related_name='result_configuration')
    total_ca_score = models.FloatField(default=30)
    total_exam_score = models.FloatField(default=70)
    pass_mark = models.FloatField(default=50)  # <== this should be defined

    def __str__(self):
        return f"ResultConfig for {self.school.school_name}"


class AnnualResultWeightConfig(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="annual_weights")
    class_year = models.ForeignKey('ClassYear', on_delete=models.CASCADE)
    department = models.ForeignKey('Department', on_delete=models.CASCADE)

    first_term_weight = models.FloatField(default=1/3)
    second_term_weight = models.FloatField(default=1/3)
    third_term_weight = models.FloatField(default=1/3)

    class Meta:
        unique_together = ('school', 'class_year', 'department')

    def __str__(self):
        return f"Annual Weights - {self.class_year.name}/{self.department.name} - {self.school.school_name}"

class GradingSystem(models.Model):
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="grading_systems")
    min_score = models.FloatField()
    max_score = models.FloatField()
    grade = models.CharField(max_length=5)
    remarks = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        ordering = ['-max_score']

    def __str__(self):
        return f"{self.grade} ({self.min_score}-{self.max_score})"


class ScorePerAssessmentInstance(models.Model):
    scoreperassessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey('StudentSubjectRegistration', on_delete=models.CASCADE, related_name="assessment_scores",null=True)
    category = models.ForeignKey('AssessmentCategory', on_delete=models.CASCADE, related_name="instance_scores")
    instance_number = models.IntegerField()
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.registration.student_class.student.last_name} - {self.category.assessment_name} (Instance {self.instance_number})"


class ScoreObtainedPerAssessment(models.Model):
    scoreperassessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey('StudentSubjectRegistration', on_delete=models.CASCADE, related_name="total_assessment_scores",null=True)
    category = models.ForeignKey('AssessmentCategory', on_delete=models.CASCADE, related_name="total_scores")
    total_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.registration.student_class.student.last_name} - {self.category.assessment_name}"


class ExamScore(models.Model):
    examscore_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey('StudentSubjectRegistration', on_delete=models.CASCADE, related_name="exam_scores",null=True)
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.registration.student_class.student.last_name} ({self.registration.subject_class.subject.name}) - {self.score}"


class ContinuousAssessment(models.Model):
    continuous_assessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey('StudentSubjectRegistration', on_delete=models.CASCADE, related_name="continuous_assessments",null=True)
    ca_total = models.FloatField(help_text="Total score from all continuous assessments.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.registration.student_class.student.last_name} ({self.registration.subject_class.subject.name}) - {self.ca_total}"



class Result(models.Model):
    result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey('StudentSubjectRegistration', on_delete=models.CASCADE, related_name="results", null=True)
    ca_total = models.FloatField()
    exam_score = models.FloatField()
    total_score = models.FloatField()
    grade = models.CharField(max_length=5)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.registration.student_class.student.last_name} - {self.total_score} ({self.registration.subject_class.subject.name})"


class AnnualResult(models.Model):
    annual_result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    registration = models.ForeignKey('StudentSubjectRegistration', on_delete=models.CASCADE, related_name="annual_results", null=True)
    first_term_score = models.FloatField(null=True, blank=True)
    second_term_score = models.FloatField(null=True, blank=True)
    third_term_score = models.FloatField(null=True, blank=True)
    annual_average = models.FloatField(null=True, blank=True)
    grade = models.CharField(max_length=10, null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def calculate_annual_average(self):
        config = AnnualResultWeightConfig.objects.filter(
            school=self.registration.school,
            class_year=self.registration.student_class.class_year,
            department=self.registration.subject_class.department
        ).first()

        if config:
            weighted = (
                (self.first_term_score or 0) * config.first_term_weight +
                (self.second_term_score or 0) * config.second_term_weight +
                (self.third_term_score or 0) * config.third_term_weight
            )
        else:
            valid_scores = [score for score in [self.first_term_score, self.second_term_score, self.third_term_score] if score is not None]
            weighted = sum(valid_scores) / len(valid_scores) if valid_scores else 0

        self.annual_average = weighted
        self.save()
        return self.annual_average

    def __str__(self):
        return f"{self.registration.student_class.student.last_name} ({self.registration.subject_class.subject.name}) - {self.annual_average}"


# models.py

class ClassTeacherComment(models.Model):
    """
    Represents comments made by class teachers for specific students.
    """
    classteacher_comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="class_teacher_comments")
    classteacher = models.ForeignKey('ClassTeacher', on_delete=models.CASCADE, related_name="comments")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="teacher_comments")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="teacher_comments")
    comment = models.TextField(max_length=1000)

    class Meta:
        unique_together = ('student', 'term', 'school')

    def __str__(self):
        return f"Comment by {self.classteacher} for {self.student.first_name} {self.student.last_name}"

############# END OF RESULT MODULE #################

############# COMMENT MODULE #################


############# END OF COMMENT MODULE #################

class AttendancePolicy(models.Model):
    """
    Represents attendance requirements for a school.
    """
    policy_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="attendance_policies")
    minimum_attendance_percentage = models.FloatField()
    total_time_school_open = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance Policy ({self.minimum_attendance_percentage}%)"


class FeeCategory(models.Model):
    """
    Represents fee categories for specific classes.
    """
    fee_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_level = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="fee_categories")
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    amount = models.FloatField()
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="fee_categories")

    def __str__(self):
        return self.name


class Fee(models.Model):
    """
    Represents individual student fee records.
    """
    fee_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="fees")
    fee_category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name="fees")
    amount = models.FloatField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Fee for {self.student.first_name} {self.student.last_name}"


class Notification(models.Model):
    """
    Represents notifications sent to users or groups in a school.
    """
    notification_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=100)
    content = models.TextField()
    recipient_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="notifications")
    recipient_group = models.CharField(max_length=50, choices=[
        ('Teacher', 'Teacher'),
        ('Student', 'Student'),
        ('Everyone', 'Everyone')
    ])
    notification_type = models.CharField(max_length=50)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


############TIME TABLE #################
class Day(models.Model):
    """
    Represents days of the week or academic schedule.
    """
    day_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="days")

    def __str__(self):
        return self.name
    pass


class Period(models.Model):
    """
    Represents time periods in a school's timetable.
    """
    period_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="periods")
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.start_time} - {self.end_time}"
    pass


class SubjectPeriodLimit(models.Model):
    """
    Represents subject-specific period constraints.
    """
    subjectperiodlimit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="subject_period_limits")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="period_limits")
    periods_per_week = models.IntegerField()
    double_periods = models.IntegerField()

    def __str__(self):
        return f"{self.subject.name} ({self.periods_per_week} periods/week)"
    pass

class Constraint(models.Model):
    """
    Represents time constraints for a school (e.g., breaks, fellowship).
    """
    school = models.OneToOneField('School', on_delete=models.CASCADE, related_name="constraints")
    fellowship_time = models.JSONField()
    break_times = models.JSONField()

    def __str__(self):
        return f"Constraints for {self.school.school_name}"
    pass

class Timetable(models.Model):
    """
    Represents a generated timetable for a school.
    """
    timetable_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('user_registration.School', on_delete=models.CASCADE, related_name="timetables")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class ClassTimetable(models.Model):
    """
    Represents a timetable for a specific class arm.
    """
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name="class_timetables")
    class_arm = models.ForeignKey('user_registration.Class', on_delete=models.CASCADE, related_name="timetables")
    schedule = models.JSONField()  # Store the timetable as JSON


class TeacherTimetable(models.Model):
    """
    Represents a timetable for a specific teacher.
    """
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name="teacher_timetables")
    teacher = models.ForeignKey('user_registration.Teacher', on_delete=models.CASCADE, related_name="timetables")
    schedule = models.JSONField()  # Store the timetable as JSON


"""
Attendance models live in this app to centralize core domain models used by other apps.
"""

class AttendanceSession(models.Model):
    ROLE_CHOICES = [
        ("school_admin", "School Admin"),
        ("teacher", "Teacher"),
    ]
    class_obj = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="attendance_sessions")
    date = models.DateField()
    taken_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="attendance_sessions")
    taken_by_role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["class_obj", "date"], name="uniq_attendance_session_class_date")
        ]
        ordering = ["-date", "class_obj__arm_name"]

    def __str__(self):
        return f"{self.class_obj} - {self.date}"


class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ("present", "Present"),
        ("absent", "Absent"),
    ]
    session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name="records")
    student = models.ForeignKey('Student', on_delete=models.SET_NULL, null=True, blank=True, related_name="attendance_records")
    student_name = models.CharField(max_length=255)
    admission_number = models.CharField(max_length=50)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="present")
    marked_at = models.DateTimeField(default=timezone.now)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["session", "student"], name="uniq_attendance_session_student")
        ]
        ordering = ["student_name"]

    def __str__(self):
        return f"{self.student_name} ({self.admission_number}) - {self.status}"

