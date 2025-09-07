from rest_framework import serializers

from user_registration.models import ( Year,Term,ClassYear,Class,Classroom,
                     Department,Subject,ClassTeacher,
                     TeacherAssignment,StudentClass,
                     SubjectRegistrationControl,SubjectClass,ClassDepartment,
                     StudentSubjectRegistration, SubjectClass, StudentClass,
                     Day,Period,SubjectPeriodLimit,Constraint)


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
    class_assigned_arm = serializers.CharField(source='class_assigned.arm_name', read_only=True)
    teacher_name = serializers.CharField(source='teacher.first_name', read_only=True)
    teacher_lastname = serializers.CharField(source='teacher.last_name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    class_assigned_name = serializers.CharField(source='class_assigned.class_year.class_name', read_only=True)

    class Meta:
        model = ClassTeacher
        fields = [
            'class_teacher_id', 'class_assigned', 'teacher', 'school',
            'class_assigned_name', 'class_assigned_arm', 'teacher_name', 'teacher_lastname', 'school_name'
        ]
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


class BulkSubjectClassAssignmentSerializer(serializers.Serializer):
    """
    Accepts a list of subject IDs and one department ID for bulk assignment.
    """
    subject_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True
    )
    department_id = serializers.UUIDField()

    def validate(self, data):
        request = self.context['request']
        school = request.user.school_admin.school
        subjects = Subject.objects.filter(subject_id__in=data['subject_ids'], school=school)
        department = Department.objects.filter(department_id=data['department_id'], school=school).first()

        if len(subjects) != len(data['subject_ids']):
            raise serializers.ValidationError("Some subjects are invalid or do not belong to your school.")
        if not department:
            raise serializers.ValidationError("Department not found or does not belong to your school.")

        data['subjects'] = subjects
        data['department'] = department
        return data


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
    subject_name = serializers.CharField(source='subject_class.subject.name', read_only=True)
    class_name = serializers.CharField(source='class_department_assigned.classes.arm_name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    department_name = serializers.CharField(source='subject_class.department.name', read_only=True)

    class Meta:
        model = TeacherAssignment
        fields = [
            'teacher_subject_id', 'teacher', 'subject_class', 'class_department_assigned', 'school',
            'teacher_name', 'teacher_lastname', 'subject_name', 'class_name', 'school_name', 'department_name'
        ]
        extra_kwargs = {
            'teacher': {'write_only': True},
            'subject_class': {'write_only': True},
            'class_department_assigned': {'write_only': True},
        }
        read_only_fields = ['teacher_subject_id', 'school']
        
#############################################################################################################

class StudentClassSerializer(serializers.ModelSerializer):
    student_firstname = serializers.CharField(source='student.first_name', read_only=True)
    student_surname = serializers.CharField(source='student.last_name', read_only=True)
    student_name = serializers.SerializerMethodField()
    class_year = serializers.CharField(source='class_year.class_years.class_name', read_only=True)
    class_name = serializers.CharField(source='class_arm.classes.arm_name', read_only=True)

    class Meta:
        model = StudentClass
        fields = [
            'student_class_id', 'student', 'class_year', 'class_arm',
            'student_firstname', 'student_surname', 'student_name', 'class_year'
            ,'class_name'
        ]

    def get_student_name(self, obj):
        return f"{obj.student.last_name} {obj.student.first_name}"


#############################################################################################################
# from rest_framework import serializers
# from user_registration.models import 


class StudentSubjectRegistrationSerializer(serializers.ModelSerializer):
    # Related fields for better readability
    student_id = serializers.UUIDField(source='student_class.student.student_id', read_only=True)
    student_firstname = serializers.CharField(source='student_class.student.first_name', read_only=True)
    student_surname = serializers.CharField(source='student_class.student.last_name', read_only=True)
    student_admission_number = serializers.CharField(source='student_class.student.admission_number', read_only=True)
    class_year = serializers.CharField(source='student_class.class_year.name', read_only=True)
    class_arm = serializers.CharField(source='student_class.class_arm.classes.arm_name', read_only=True)
    department = serializers.CharField(source='subject_class.department.name', read_only=True)
    subject_name = serializers.CharField(source='subject_class.subject.name', read_only=True)
    subject_id = serializers.UUIDField(source='subject_class.subject.subject_id', read_only=True)
    term_name = serializers.CharField(source='term.name', read_only=True)
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentSubjectRegistration
        fields = [
            'registration_id', 'student_class', 'subject_class', 'term', 'school',
            'status', 'created_at', 'updated_at',
            'student_id', 'student_firstname', 'student_surname', 'student_admission_number',
            'student_name', 'class_year', 'class_arm', 'department',
            'subject_id', 'subject_name', 'term_name', 'school_name'
        ]
        read_only_fields = [
            'term', 'school', 'created_at', 'updated_at',
            # 'student_admission_number', 'student_name', 'class_year',
            # 'class_arm', 'department', 'subject_name', 'term_name', 'school_name'
        ]

    def get_student_name(self, obj):
        return f"{obj.student_class.student.first_name} {obj.student_class.student.last_name}"

    def validate(self, attrs):
        """
        Ensure that the registration control is open and term is active for the student's school.
        Automatically sets the school and term if not provided.
        """
        student_class = attrs.get('student_class')
        subject_class = attrs.get('subject_class')

        if not student_class:
            raise serializers.ValidationError("Student class is required.")

        school = student_class.student.school
        attrs['school'] = school

        # Check if registration is open for the school
        control = getattr(school, 'registration_control', None)
        if not control or not control.is_open:
            raise serializers.ValidationError("Subject registration is currently closed for this school.")

        # Fetch active term
        active_term = school.terms.filter(status=True).first()
        if not active_term:
            raise serializers.ValidationError("No active term found for this school.")

        attrs['term'] = active_term

        return attrs


class SubjectRegistrationControlSerializer(serializers.ModelSerializer):
    """
    Serializer for reading subject registration control data.
    """
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = SubjectRegistrationControl
        fields = ['school', 'school_name', 'is_open', 'start_date', 'end_date']


class SubjectRegistrationControlUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating registration control settings.
    """
    class Meta:
        model = SubjectRegistrationControl
        fields = ['is_open', 'start_date', 'end_date']

class StudentSubjectStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Allows only School Admins or Class Teachers to update the `status` field of a registration.
    """
    class Meta:
        model = StudentSubjectRegistration
        fields = ['status']
        read_only_fields = []

    def validate_status(self, value):
        if value not in ['Pending', 'Approved', 'Rejected']:
            raise serializers.ValidationError("Status must be Pending, Approved, or Rejected.")
        return value



#################################################################################################
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
