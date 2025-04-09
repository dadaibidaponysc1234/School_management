from rest_framework import serializers

from user_registration.models import (Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     Year,Term,ClassYear,Class,Classroom,
                     Student,Teacher,Department,Subject,ClassTeacher,
                     TeacherAssignment,Day,Period,
                     SubjectPeriodLimit,Constraint,AttendancePolicy,FeeCategory,
                     Fee,AssessmentCategory,ExamCategory,ScorePerAssessmentInstance,ExamScore, 
                     ScoreObtainedPerAssessment, ContinuousAssessment,Result,AnnualResult,Notification, 
                     ClassTeacherComment, Attendance, AttendanceFlag, StudentSubjectAssignment,StudentClass,
                     StudentClassAndSubjectAssignment,SubjectRegistrationControl,SubjectClass,ClassDepartment)


class YearSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating an academic year.
    The school field is read-only because it's automatically assigned.
    """
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name

    class Meta:
        model = Year
        fields = ['year_id', 'name', 'start_date', 'end_date', 'school', 'school_name', 'status']
        read_only_fields = ['school', 'school_name']  # School & school name are auto-assigned

    def create(self, validated_data):
        """Ensures the school is correctly assigned when creating a year."""
        request = self.context['request']
        school = request.user.school_admin.school  # Get the School Admin’s School

        # Ensure `school` is not in `validated_data` to prevent duplicate keyword error
        validated_data.pop('school', None)  

        return Year.objects.create(school=school, **validated_data)

class TermSerializer(serializers.ModelSerializer):
    # school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    class Meta:
        model = Term
        fields = ['term_id', 'name', 'start_date', 'end_date', 'year', 'school','school_name', 'status']
        read_only_fields = ['term_id', 'school','school_name','created_at']

class ClassYearSerializer(serializers.ModelSerializer):
    """
    Serializer for Class Year including School Name and Year Name.
    """
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    year_name = serializers.CharField(source="year.name", read_only=True)  # Fetch year name

    class Meta:
        model = ClassYear
        fields = ['class_year_id', 'school', 'school_name', 'year', 'year_name', 'class_name']
        read_only_fields = ['class_year_id', 'school', 'school_name', 'year_name']

class ClassSerializer(serializers.ModelSerializer):
    """
    Serializer for Class including School Name, Year Name, and Class Year Name.
    """
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    year_name = serializers.CharField(source="class_year.year.name", read_only=True)  # Fetch year name
    class_year_name = serializers.CharField(source="class_year.class_name", read_only=True)  # Fetch class year name

    class Meta:
        model = Class
        fields = ['class_id', 'arm_name', 'class_year', 'class_year_name', 'year_name', 'school', 'school_name']
        read_only_fields = ['class_id', 'school', 'school_name', 'year_name', 'class_year_name']

class ClassroomSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    class Meta:
        model = Classroom
        fields = ['classroom_id', 'block_name', 'room_number', 'capacity', 'school','school_name']
        read_only_fields = ['classroom_id', 'school','school_name']


class DepartmentSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    class Meta:
        model = Department
        fields = ['department_id', 'name', 'school', 'school_name']
        read_only_fields = ['department_id', 'school', 'school_name']

class SubjectSerializer(serializers.ModelSerializer): 
    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name
    # department_name = serializers.CharField(source="department.name", read_only=True)  # Fetch department name

    class Meta:
        model = Subject
        fields = ['subject_id', 'name', 'school', 'school_name']
        read_only_fields = ['subject_id', 'school', 'school_name']

####################################################################################################################
class ClassTeacherSerializer(serializers.ModelSerializer):
    """
    Serializer for ClassTeacher model.
    Returns teacher name, class name, and school name.
    """
    class_assigned_name = serializers.CharField(source='class_assigned.arm_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)
    teacher_lastname = serializers.CharField(source='teacher.last_name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = ClassTeacher
        fields = [
            'class_teacher_id', 'class_assigned', 'teacher', 'school',
            'class_assigned_name', 'teacher_name', 'teacher_lastname', 'school_name'
        ]
        extra_kwargs = {
            'class_assigned': {'write_only': True},
            'teacher': {'write_only': True},
        }
        read_only_fields = ['school']

#############################################################################################################
class SubjectClassSerializer(serializers.ModelSerializer):
    """
    Serializer for SubjectClass model.
    Returns related subject, school, and department names.
    """
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = SubjectClass
        fields = [
            'subject_class_id', 'subject', 'school', 'department', 
            'subject_name', 'school_name', 'department_name'
        ]
        read_only_fields = ['school']

#############################################################################################################
class ClassDepartmentSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(source='classes.arm_name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    
    class Meta:
        model = ClassDepartment
        fields = ['subject_class_id', 'school', 'classes', 'department', 'class_name', 'school_name', 'department_name']
        read_only_fields = ['school']

#############################################################################################################
class TeacherAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for teacher assignments to subjects and classes.
    """
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)
    teacher_lastname = serializers.CharField(source='teacher.last_name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject.name', read_only=True)
    class_name = serializers.CharField(source='class_assigned.classes.arm_name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    department_name = serializers.CharField(source='subject.department.name', read_only=True)

    class Meta:
        model = TeacherAssignment
        fields = [
            'teacher_subject_id', 'teacher', 'subject', 'class_assigned', 'school',
            'teacher_name', 'teacher_lastname', 'subject_name', 'class_name', 'school_name', 'department_name'
        ]
        extra_kwargs = {
            'teacher': {'write_only': True},
            'subject': {'write_only': True},
            'class_assigned': {'write_only': True},
        }
        read_only_fields = ['teacher_subject_id', 'school']
        
#############################################################################################################

class StudentClassSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    class_name = serializers.CharField(source='class_arm.classes.arm_name', read_only=True)

    class Meta:
        model = StudentClass
        fields = [
            'student_class_id', 'student', 'class_year', 'class_arm',
            'student_name', 'class_name'
        ]


#############################################################################################################
class StudentClassAndSubjectAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for student class and subject assignment.
    """
    class Meta:
        model = StudentClassAndSubjectAssignment
        fields = [
            'assignment_id',
            'student',
            'class_arm',
            'term',
            'year',
            'school',
            'subjects',
            'assignment_date',
            'status',
        ]
        read_only_fields = ['assignment_id', 'assignment_date', 'status']


class SubjectRegistrationControlSerializer(serializers.ModelSerializer):
    """
    Serializer to control subject registration settings.
    """
    class Meta:
        model = SubjectRegistrationControl
        fields = ['school', 'is_open', 'start_date', 'end_date']
        read_only_fields = ['school']


class DaySerializer(serializers.ModelSerializer):
    """
    Serializer for the Day model.
    """
    class Meta:
        model = Day
        fields = ['day_id', 'name', 'school']
        read_only_fields = ['day_id']


class PeriodSerializer(serializers.ModelSerializer):
    """
    Serializer for the Period model.
    """
    class Meta:
        model = Period
        fields = ['period_id', 'school', 'start_time', 'end_time']
        read_only_fields = ['period_id']


class SubjectPeriodLimitSerializer(serializers.ModelSerializer):
    """
    Serializer for the SubjectPeriodLimit model.
    """
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = SubjectPeriodLimit
        fields = ['subjectperiodlimit_id', 'school', 'subject', 'subject_name', 'periods_per_week', 'double_periods']
        read_only_fields = ['subjectperiodlimit_id']


class ConstraintSerializer(serializers.ModelSerializer):
    """
    Serializer for the Constraint model.
    """
    class Meta:
        model = Constraint
        fields = ['school', 'fellowship_time', 'break_times']
