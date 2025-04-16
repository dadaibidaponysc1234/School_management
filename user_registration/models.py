from django.contrib.auth.models import User
from django.db import models
import uuid
# from django.db.models.signals import post_save
# from django.dispatch import receiver
from datetime import date, timedelta
from django.conf import settings
from django.utils.timezone import now


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
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    short_name = models.CharField(max_length=15)
    logo = models.ImageField(upload_to="school_logos/", null=True, blank=True)  # Optional field for school logo
    school_type = models.CharField(max_length=100)
    education_level = models.CharField(max_length=100)
    registered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="registered_schools")  # Track user who registered the school

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
    subject = models.ForeignKey('SubjectClass', on_delete=models.CASCADE, related_name="teacher_assignments")
    class_assigned = models.ForeignKey('ClassDepartment', on_delete=models.CASCADE, related_name="teacher_assignments")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="teacher_assignments")
    
    # availability = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.teacher.first_name} {self.class_assigned.classes.arm_name} - {self.subject.subject.name} {self.subject.department.name}"


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


class StudentClassAndSubjectAssignment(models.Model):
    """
    Tracks student class and subject assignments.
    """
    assignment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="class_and_subject_assignments")
    class_arm = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="class_arm_assignments")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="student_assignments")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="student_assignments")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="student_assignments")
    subjects = models.ManyToManyField('Subject', related_name="student_subject_assignments")
    assignment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Rejected', 'Rejected')],
        default='Pending'
    )

    def __str__(self):
        return f"Assignment for {self.student.first_name} {self.student.last_name}"


class AssessmentCategory(models.Model):
    """
    Represents types of assessments (e.g., tests, assignments).
    """
    assessment_category_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="assessment_categories")
    assessment_name = models.CharField(max_length=50)
    number_of_times = models.IntegerField()
    max_score_per_one = models.IntegerField()
    max_score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.assessment_name


class ExamCategory(models.Model):
    """
    Represents exam categories.
    """
    assessment_category = models.OneToOneField(AssessmentCategory, on_delete=models.CASCADE, related_name="exam_category")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="exam_categories")
    exam_name = models.CharField(max_length=50, default="Exam")
    max_score = models.IntegerField()

    def __str__(self):
        return self.exam_name


class ScorePerAssessmentInstance(models.Model):
    """
    Represents scores for individual assessment instances.
    """
    scoreperassessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="assessment_scores")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="assessment_scores")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="assessment_scores")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="assessment_scores")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="assessment_scores")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="assessment_scores")
    category = models.ForeignKey(AssessmentCategory, on_delete=models.CASCADE, related_name="scores")
    instance_number = models.IntegerField()
    score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Score for {self.student.first_name} - {self.category.assessment_name}"
    
class ExamScore(models.Model):
    """
    Represents exam scores for students in a specific subject, term, and year.
    """
    examscore_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="exam_scores")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="exam_scores")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="exam_scores")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="exam_scores")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="exam_scores")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="exam_scores")
    score = models.FloatField(help_text="Exam score achieved by the student.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"ExamScore: {self.student.first_name} ({self.subject.name}) - {self.score}"

class ScoreObtainedPerAssessment(models.Model):
    scoreperassessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey(
        'School',
        on_delete=models.CASCADE,
        related_name="obtained_assessment_scores"  # Unique related_name
    )
    class_assigned = models.ForeignKey(
        'Class',
        on_delete=models.CASCADE,
        related_name="obtained_assessment_scores"  # Unique related_name
    )
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        related_name="obtained_assessment_scores"  # Unique related_name
    )
    subject = models.ForeignKey(
        'Subject',
        on_delete=models.CASCADE,
        related_name="obtained_assessment_scores"  # Unique related_name
    )
    term = models.ForeignKey(
        'Term',
        on_delete=models.CASCADE,
        related_name="obtained_assessment_scores"  # Unique related_name
    )
    year = models.ForeignKey(
        'Year',
        on_delete=models.CASCADE,
        related_name="obtained_assessment_scores"  # Unique related_name
    )
    category = models.ForeignKey(
        'AssessmentCategory',
        on_delete=models.CASCADE,
        related_name="total_scores"
    )
    total_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Assessment Score: {self.student.first_name} ({self.subject.name})"

class ContinuousAssessment(models.Model):
    """
    Represents continuous assessment scores for a student.
    """
    continuous_assessment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="continuous_assessments")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="continuous_assessments")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="continuous_assessments")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="continuous_assessments")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="continuous_assessments")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="continuous_assessments")
    ca_total = models.FloatField(help_text="Total score from all continuous assessments.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CA: {self.student.first_name} ({self.subject.name}) - {self.ca_total}"


class Result(models.Model):
    """
    Represents final term results for a student in a subject.
    """
    result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="results")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="results")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="results")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="results")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="results")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="results")
    ca_total = models.FloatField()
    exam_score = models.FloatField()
    total_score = models.FloatField()
    grade = models.CharField(max_length=5)
    remarks = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Result for {self.student.first_name} ({self.subject.name})"
    

class AnnualResult(models.Model):
    """
    Represents annual results for a student in a specific subject and class.
    """
    annual_result_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="annual_results")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="annual_results")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="annual_results")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="annual_results")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="annual_results")
    first_term_score = models.FloatField(null=True, blank=True)
    second_term_score = models.FloatField(null=True, blank=True)
    third_term_score = models.FloatField(null=True, blank=True)
    annual_average = models.FloatField(null=True, blank=True, help_text="Automatically calculated as the average of term scores.")
    grade = models.CharField(max_length=10, null=True, blank=True, help_text="Grade assigned, e.g., A, B, C.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Annual Result: {self.student.first_name} ({self.subject.name}) - {self.year.year_id}"

    def calculate_annual_average(self):
        """
        Calculate and return the annual average based on term scores.
        """
        scores = [self.first_term_score, self.second_term_score, self.third_term_score]
        valid_scores = [score for score in scores if score is not None]
        if valid_scores:
            self.annual_average = sum(valid_scores) / len(valid_scores)
            self.save()
        return self.annual_average




class Day(models.Model):
    """
    Represents days of the week or academic schedule.
    """
    day_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="days")

    def __str__(self):
        return self.name


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


class Constraint(models.Model):
    """
    Represents time constraints for a school (e.g., breaks, fellowship).
    """
    school = models.OneToOneField('School', on_delete=models.CASCADE, related_name="constraints")
    fellowship_time = models.JSONField()
    break_times = models.JSONField()

    def __str__(self):
        return f"Constraints for {self.school.school_name}"

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


class ClassTeacherComment(models.Model):
    """
    Represents comments made by class teachers for specific students.
    """
    classteacher_comment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="class_teacher_comments")
    classteacher = models.ForeignKey('ClassTeacher', on_delete=models.CASCADE, related_name="comments")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="teacher_comments")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="teacher_comments")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="teacher_comments")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="teacher_comments")
    comment = models.TextField(max_length=1000)

    def __str__(self):
        return f"Comment by {self.classteacher.teacher.first_name} for {self.student.first_name}"


class Attendance(models.Model):
    """
    Represents attendance records for students.
    """
    attendance_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="attendance_records")
    date = models.DateField()
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="attendance_records")
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="attendance_records")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="attendance_records")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="attendance_records")
    is_present = models.BooleanField(default=False)
    designation = models.ForeignKey('ClassTeacher', on_delete=models.CASCADE, related_name="attendance_records")

    def __str__(self):
        return f"Attendance for {self.student.first_name} on {self.date}"


class AttendanceFlag(models.Model):
    """
    Represents flagged attendance records for students.
    """
    flag_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="attendance_flags")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="attendance_flags")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="attendance_flags")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="attendance_flags")
    number_of_times_attended = models.FloatField()
    number_of_times_open = models.FloatField()
    attendance_percentage = models.FloatField()
    flag_reason = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Flag for {self.student.first_name} ({self.attendance_percentage}%)"


class StudentSubjectAssignment(models.Model):
    """
    Tracks subject assignments for students.
    """
    assignment_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey('Student', on_delete=models.CASCADE, related_name="subject_assignments")
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE, related_name="student_assignments")
    class_assigned = models.ForeignKey('Class', on_delete=models.CASCADE, related_name="student_subject_assignments")
    term = models.ForeignKey('Term', on_delete=models.CASCADE, related_name="student_subject_assignments")
    year = models.ForeignKey('Year', on_delete=models.CASCADE, related_name="student_subject_assignments")
    school = models.ForeignKey('School', on_delete=models.CASCADE, related_name="student_subject_assignments")
    assigned_by = models.ForeignKey('ClassTeacher', on_delete=models.SET_NULL, null=True, related_name="assigned_students")
    assignment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ], default='Pending')
    status_updated_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.first_name} - {self.subject.name} ({self.status})"


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

