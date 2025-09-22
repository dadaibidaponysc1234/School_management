from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
                     Class, Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     ClassYear,Student,Teacher,StudentRegistrationPin,
                     ClassDepartment, StudentClass
                     )

from django.db import transaction


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the Role model.
    """
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']
# ==================================================================================

class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserRole model.
    """
    role = RoleSerializer()  # Include role details

    class Meta:
        model = UserRole
        fields = ['id', 'role']
# ==================================================================================

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django User model.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Create user with hashed password
        return User.objects.create_user(**validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Ensure self.user is valid and active
        if not self.user or not self.user.is_active:
            raise serializers.ValidationError({"detail": "No active account found with the given credentials"})

        # Add basic user details
        user = self.user
        data['id'] = user.id
        data['username'] = user.username
        data['email'] = user.email

        # Add roles and user roles
        user_roles = UserRole.objects.filter(user=user).select_related('role')
        data['user_roles'] = [
            {
                'id': user_role.id,
                'role': {
                    'id': user_role.role.id,
                    'name': user_role.role.name,
                    'description': user_role.role.description,
                },
            }
            for user_role in user_roles
        ]

        # Add details for SuperAdmin if applicable
        try:
            super_admin = SuperAdmin.objects.get(user=user)
            data['super_admin'] = {
                'id': super_admin.id,
                'surname': super_admin.surname,
                'first_name': super_admin.first_name,
                'phone_number': super_admin.phone_number,
                'address': super_admin.address,
                'created_at': super_admin.created_at,
                'updated_at': super_admin.updated_at,
            }
        except SuperAdmin.DoesNotExist:
            data['super_admin'] = None

        # Add details for SchoolAdmin if applicable
        try:
            school_admin = SchoolAdmin.objects.get(user=user)
            data['school_admin'] = {
                'schooladmin_id': school_admin.schooladmin_id,
                'school_id': school_admin.school.id,
                'school_name': school_admin.school.school_name,
                'school_logo': school_admin.school.logo.url if school_admin.school.logo else None,
                'surname': school_admin.surname,
                'first_name': school_admin.first_name,
                'email': school_admin.email,
                'phone_number': school_admin.phone_number,
                'designation': school_admin.designation,
                'address': school_admin.address,
                'city': school_admin.city,
                'state': school_admin.state,
                'region': school_admin.region,
                'country': school_admin.country,
                'created_at': school_admin.created_at,
                'updated_at': school_admin.updated_at,
            }
        except SchoolAdmin.DoesNotExist:
            data['school_admin'] = None

        # Add details for Student if applicable
        try:
            student = Student.objects.get(user=user)
            data['student'] = {
                'student_id': student.student_id,
                'school_id': student.school.id,
                'school_name': student.school.school_name,
                'school_logo': student.school.logo.url if student.school.logo else None,
                'first_name': student.first_name,
                'last_name': student.last_name,
                'admission_number': student.admission_number,
                # 'class_level': student.class_level.name,
                # 'class_arm': student.class_arm.arm_name,
                'profile_picture_path': student.profile_picture_path.url if student.profile_picture_path else None,
            }
        except Student.DoesNotExist:
            data['student'] = None

        # Add details for Teacher if applicable
        try:
            teacher = Teacher.objects.get(user=user)
            data['teacher'] = {
                'teacher_id': teacher.teacher_id,
                'school_id': teacher.school.id,
                'school_name': teacher.school.school_name,
                'school_logo': teacher.school.logo.url if teacher.school.logo else None,
                'first_name': teacher.first_name,
                'last_name': teacher.last_name,
                'qualification': teacher.qualification,
                'specialization': teacher.specialization,
                'profile_picture_path': teacher.profile_picture_path.url if teacher.profile_picture_path else None,
                'cv': teacher.cv.url if teacher.cv else None,
            }
        except Teacher.DoesNotExist:
            data['teacher'] = None

        return data


# ==================================================================================
class SuperAdminCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to create a SuperAdmin along with a User and UserRole.
    """
    user = UserSerializer()
    role = RoleSerializer(source='user_role.role', read_only=True)  # Nested Role details
    user_role = serializers.UUIDField(write_only=True)  # Accept UUID for user_role

    class Meta:
        model = SuperAdmin
        fields = ['id', 'user', 'role', 'user_role', 'surname', 'first_name', 'middle_name','phone_number', 'address', 'created_at', 'updated_at']
        read_only_fields = ['id', 'role', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Extract user data and user_role UUID
        user_data = validated_data.pop('user')
        user_role_uuid = validated_data.pop('user_role')

        # Create the User
        user = UserSerializer().create(user_data)

        # Resolve the UUID to a Role instance or raise an error
        try:
            role = Role.objects.get(id=user_role_uuid)
        except Role.DoesNotExist:
            raise serializers.ValidationError({"user_role": "Invalid role UUID provided."})

        # Create UserRole
        user_role = UserRole.objects.create(user=user, role=role)

        # Create SuperAdmin with the created user and user_role
        super_admin = SuperAdmin.objects.create(user=user, user_role=user_role, **validated_data)
        return super_admin

# ==================================================================================

class SuperAdminSerializer(serializers.ModelSerializer):
    """
    Serializer for viewing, updating, and deleting a SuperAdmin profile.
    """
    email = serializers.EmailField(source='user.email', read_only=True)
    class Meta:
        model = SuperAdmin
        fields = [
            'id',
            'user',
            'email',
            'surname',
            'first_name',
            'middle_name',
            'phone_number',
            'address',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


# ==================================================================================

class SchoolCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a School.
    Automatically associates the school with the user who registers it.
    """
    class Meta:
        model = School
        fields = [
            'id',
            'school_name',
            'school_address',
            'city',
            'state',
            'region',
            'country',
            'email',
            'phone_number',
            'short_name',
            'logo',
            'school_type',
            'education_level',
        ]
        read_only_fields = ['id']

    def create(self, validated_data):
        # Add the `registered_by` user dynamically in the view
        user = self.context['request'].user
        validated_data['registered_by'] = user
        return super().create(validated_data)


class SchoolListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing schools.
    """
    registered_by = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = School
        fields = [
            'id',
            'school_name',
            'school_address',
            'city',
            'state',
            'region',
            'country',
            'email',
            'phone_number',
            'short_name',
            'logo',
            'school_type',
            'education_level',
            'registered_by',
            'created_at',
            'status',
        ]

    def get_registered_by(self, obj):
        if obj.registered_by:
            super_admin = getattr(obj.registered_by, 'super_admin', None)
            if super_admin:
                return {
                    "id": str(obj.registered_by.id),
                    "surname": super_admin.surname,
                    "first_name": super_admin.first_name,
                }
            return {
                "id": str(obj.registered_by.id),
                "surname": obj.registered_by.last_name,
                "first_name": obj.registered_by.first_name,
            }
        return None

    def get_status(self, obj):
        try:
            subscription = obj.school_subscriptions.latest('active_date')
            return subscription.live_is_active
        except Subscription.DoesNotExist:
            return None
# # =================================================================================================

class SubscriptionSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    live_number_students = serializers.SerializerMethodField()
    live_expected_fee = serializers.SerializerMethodField()
    live_is_active = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            'subscription_id', 'school', 'school_name',
            'amount_per_student', 'amount_paid',
            'expired_date', 'active_date',
            'live_number_students', 'live_expected_fee', 'live_is_active',
        ]
        read_only_fields = ['school', 'school_name', 'live_number_students', 'live_expected_fee', 'live_is_active']

    def get_live_number_students(self, obj):
        return obj.school.school_students.count()

    def get_live_expected_fee(self, obj):
        return self.get_live_number_students(obj) * obj.amount_per_student

    def get_live_is_active(self, obj):
        from datetime import date
        today = date.today()
        return (obj.amount_paid >= self.get_live_expected_fee(obj)) and (today <= obj.expired_date)



# =================================================================================================

class ComplianceVerificationSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)  # Add this line
    accreditation_certificates = serializers.FileField(use_url=True)  # Use_url=True to get the file URL in the response
    proof_of_registration = serializers.FileField(use_url=True)

    class Meta:
        model = ComplianceVerification
        fields = ['school','school_name','accreditation_certificates',
                  'proof_of_registration','tax_identification_number',
                  'compliance','approved', 'last_updated_on', 'uploaded_on']  # Or specify the fields explicitly

# =================================================================================================
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'  # Or specify fields explicitly
# =================================================================================================
# Serializers

class RegistrationPinSerializer(serializers.ModelSerializer):
    """
    Serializer for handling registration pins.
    """

    school_name = serializers.CharField(source="school.school_name", read_only=True)  # Fetch school name

    class Meta:
        model = StudentRegistrationPin
        fields = ['pin_id', 'school', 'school_name', 'otp', 'is_used', 'created_at']
        read_only_fields = ['pin_id', 'school', 'school_name', 'is_used', 'created_at']


# class StudentCreateSerializer(serializers.ModelSerializer):
#     """
#     Serializer for creating students.
#     Automatically assigns the 'Student' role.
#     """
#     user = UserSerializer()
#     role = serializers.CharField(source='user_role.role.name', read_only=True)
#     school = serializers.PrimaryKeyRelatedField(read_only=True)  # Auto-assigned school

#     class Meta:
#         model = Student
#         fields = [
#             'student_id', 'user', 'role', 'school', 'admission_number', 'first_name',
#             'middle_name', 'last_name', 'date_of_birth', 'gender', 'address', 'city', 'state',
#             'region', 'country', 'admission_date', 'status', 'profile_picture_path',
#             'parent_first_name', 'parent_middle_name', 'parent_last_name', 'parent_occupation',
#             'parent_contact_info', 'parent_emergency_contact', 'parent_relationship'
#         ]
#         read_only_fields = ['student_id', 'role', 'school']

#     def create(self, validated_data):
#         user_data = validated_data.pop('user')

#         try:
#             with transaction.atomic():
#                 # Create the user
#                 user = UserSerializer().create(user_data)

#                 # Retrieve the 'Student' role automatically
#                 student_role = Role.objects.get(name='Student')

#                 # Assign the Student role automatically
#                 user_role = UserRole.objects.create(user=user, role=student_role)

#                 # Create the student record
#                 student = Student.objects.create(user=user, **validated_data)

#                 return student

#         except Exception as e:
#             raise serializers.ValidationError({"error": f"Student creation failed: {str(e)}"})

class StudentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating students.
    Automatically assigns the 'Student' role and assigns them to a class.
    """
    user = UserSerializer()
    role = serializers.CharField(source='user_role.role.name', read_only=True)
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    class_year = serializers.UUIDField(write_only=True)
    class_arm = serializers.UUIDField(write_only=True)

    class Meta:
        model = Student
        fields = [
            'student_id', 'user', 'role', 'school', 'admission_number', 'first_name',
            'middle_name', 'last_name', 'date_of_birth', 'gender', 'address', 'city', 'state',
            'region', 'country', 'admission_date', 'status', 'profile_picture_path',
            'parent_first_name', 'parent_middle_name', 'parent_last_name', 'parent_occupation',
            'parent_contact_info', 'parent_emergency_contact', 'parent_relationship',
            'class_year', 'class_arm'
        ]
        read_only_fields = ['student_id', 'role', 'school']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        class_year = validated_data.pop('class_year')
        class_arm = validated_data.pop('class_arm')

        try:
            with transaction.atomic():
                user = UserSerializer().create(user_data)
                student_role = Role.objects.get(name='Student')
                user_role = UserRole.objects.create(user=user, role=student_role)
                student = Student.objects.create(user=user, **validated_data)

                # Assign class to student
                # Get the class (klass) using year + arm
                klass = get_object_or_404(
                    Class,
                    class_year=class_year,
                    arm_name=class_arm
                )

                # Create StudentClass
                StudentClass.objects.create(
                    student=student,
                    klass=klass
                )

                return student

        except Exception as e:
            raise serializers.ValidationError({"error": f"Student creation failed: {str(e)}"})


class StudentUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role = serializers.CharField(source='user_role.role.name', read_only=True)
    school = serializers.PrimaryKeyRelatedField(read_only=True)
    class_year = serializers.UUIDField(write_only=True)
    class_arm = serializers.UUIDField(write_only=True)

    class Meta:
        model = Student
        fields = [
            'student_id', 'user', 'role', 'school', 'admission_number', 'first_name',
            'middle_name', 'last_name', 'date_of_birth', 'gender', 'address', 'city', 'state',
            'region', 'country', 'admission_date', 'status', 'profile_picture_path',
            'parent_first_name', 'parent_middle_name', 'parent_last_name', 'parent_occupation',
            'parent_contact_info', 'parent_emergency_contact', 'parent_relationship',
            'class_year', 'class_arm'
        ]
        read_only_fields = ['student_id', 'role', 'school']

    def update(self, validated_data):
        user_data = validated_data.pop('user')
        class_year = validated_data.pop('class_year')
        class_arm = validated_data.pop('class_arm')

        try:
            with transaction.atomic():
                user = UserSerializer().create(user_data)
                student_role = Role.objects.get(name='Student')
                user_role = UserRole.objects.create(user=user, role=student_role)
                student = Student.objects.create(user=user, **validated_data)

                # Assign class to student
                # Get the class (klass) using year + arm
                klass = get_object_or_404(
                    Class,
                    class_year=class_year,
                    arm_name=class_arm
                )

                # Create StudentClass
                StudentClass.objects.create(
                    student=student,
                    klass=klass
                )

                return student

        except Exception as e:
            raise serializers.ValidationError({"error": f"Student creation failed: {str(e)}"})



class StudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = [
            'student_id', 'admission_number', 'first_name', 'last_name',
             'status', 'parent_contact_info'
        ]


class StudentDetailSerializer(serializers.ModelSerializer):
    class_year = serializers.SerializerMethodField()
    class_arm = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            'student_id', 'user', 'school', 'admission_number', 'first_name', 
            'middle_name', 'last_name', 'date_of_birth', 'gender', 'address', 
            'city', 'state', 'region', 'country', 'admission_date', 'status', 
            'profile_picture_path', 'parent_first_name', 
            'parent_middle_name', 'parent_last_name', 'parent_occupation', 
            'parent_contact_info', 'parent_emergency_contact', 'parent_relationship',
            'class_year', 'class_arm'
        ]

    def get_class_year(self, obj):
        try:
            student_class = obj.subject_class.first()
            return student_class.class_year.name if student_class else None
        except:
            return None

    def get_class_arm(self, obj):
        try:
            student_class = obj.subject_class.first()
            return student_class.class_arm.classes.arm_name if student_class else None
        except:
            return None



# =================================================================================================
class TeacherCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to create a Teacher along with a User.
    Automatically assigns the 'Teacher' role.
    """
    user = UserSerializer()
    role = serializers.CharField(source='user_role.role.name', read_only=True)  # Role is always 'Teacher'
    school = serializers.PrimaryKeyRelatedField(read_only=True)  # Auto-assigned school

    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'user', 'role', 'school', 'first_name', 'middle_name',
            'last_name', 'date_of_birth', 'gender', 'address', 'city', 'state', 'region',
            'country', 'date_hire', 'status', 'qualification', 'specialization',
            'profile_picture_path', 'cv'
        ]
        read_only_fields = ['teacher_id', 'role', 'school']

    def create(self, validated_data):
        """
        Handles user creation, role assignment, and teacher creation.
        Ensures all operations are atomic (transactional).
        """
        user_data = validated_data.pop('user')
        try:

            with transaction.atomic():
                # Create User
                user = UserSerializer().create(user_data)

                # Get the 'Teacher' role
                role = Role.objects.get(name="Teacher")

                # Assign role
                UserRole.objects.create(user=user, role=role)

                # Create Teacher
                teacher = Teacher.objects.create(user=user, **validated_data)

                return teacher
        except Exception as e:
            raise serializers.ValidationError({"error": f"Teacher creation failed: {str(e)}"})


class TeacherUpdateSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role = serializers.CharField(source='user_role.role.name', read_only=True)  # Role is always 'Teacher'
    school = serializers.PrimaryKeyRelatedField(read_only=True)  # Auto-assigned school

    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'user', 'role', 'school', 'first_name', 'middle_name',
            'last_name', 'date_of_birth', 'gender', 'address', 'city', 'state', 'region',
            'country', 'date_hire', 'status', 'qualification', 'specialization',
            'profile_picture_path', 'cv'
        ]
        read_only_fields = ['teacher_id', 'role', 'school']

    def update(self, validated_data):
        """
        Handles user creation, role assignment, and teacher creation.
        Ensures all operations are atomic (transactional).
        """
        user_data = validated_data.pop('user')
        try:

            with transaction.atomic():
                # Create User
                user = UserSerializer().create(user_data)

                # Get the 'Teacher' role
                role = Role.objects.get(name="Teacher")

                # Assign role
                UserRole.objects.create(user=user, role=role)

                # Create Teacher
                teacher = Teacher.objects.create(user=user, **validated_data)

                return teacher
        except Exception as e:
            raise serializers.ValidationError({"error": f"Teacher creation failed: {str(e)}"})



class TeacherListSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'first_name', 'last_name', 'qualification', 
            'specialization', 'status', 'school_name'
        ]

class TeacherDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = [
            'teacher_id', 'user', 'school', 'first_name', 'middle_name', 
            'last_name', 'date_of_birth', 'gender', 'address', 'city', 
            'state', 'region', 'country', 'date_hire', 'status', 
            'qualification', 'specialization', 'profile_picture_path', 'cv'
        ]

# =================================================================================================
class SchoolAdminCreateSerializer(serializers.ModelSerializer):
    """
    Serializer to create a SchoolAdmin along with a User and UserRole.
    """
    user = UserSerializer()  # Serialize and create the User object
    role = serializers.CharField(source='user_role.role.name', read_only=True)
    user_role = serializers.UUIDField(write_only=True)  # Write-only role UUID

    class Meta:
        model = SchoolAdmin
        fields = [
            'schooladmin_id', 'user', 'role', 'user_role', 'school', 'surname',
            'first_name','middle_name', 'email', 'phone_number', 'address', 'city', 'state',
            'region', 'country', 'designation', 'created_at', 'updated_at'
        ]
        read_only_fields = ['schooladmin_id', 'role', 'created_at', 'updated_at']

    def create(self, validated_data):
        # Extract user data and user_role UUID
        user_data = validated_data.pop('user')
        user_role_uuid = validated_data.pop('user_role')

        # Create the User
        user = UserSerializer().create(user_data)

        # Retrieve the Role object and ensure it is 'School Admin'
        try:
            role = Role.objects.get(id=user_role_uuid)
            if role.name != 'School Admin':
                raise serializers.ValidationError({"user_role": "The provided role must be 'School Admin'."})
        except Role.DoesNotExist:
            raise serializers.ValidationError({"user_role": "Invalid role UUID provided."})

        # Create the UserRole
        UserRole.objects.create(user=user, role=role)

        # Create the SchoolAdmin with the created user
        school_admin = SchoolAdmin.objects.create(user=user, **validated_data)
        return school_admin


class SchoolAdminUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a SchoolAdmin.
    """
    user = UserSerializer()  # Serialize and create the User object
    role = serializers.CharField(source='user_role.role.name', read_only=True)
    user_role = serializers.UUIDField(write_only=True)  # Write-only role UUID

    class Meta:
        model = SchoolAdmin
        fields = [
            'schooladmin_id', 'user', 'role', 'user_role', 'school', 'surname',
            'first_name', 'email', 'phone_number', 'address', 'city', 'state',
            'region', 'country', 'designation', 'created_at', 'updated_at'
        ]
        read_only_fields = ['schooladmin_id', 'role', 'created_at', 'updated_at']

    def update(self, validated_data):
        # Extract user data and user_role UUID
        user_data = validated_data.pop('user')
        user_role_uuid = validated_data.pop('user_role')

        # Create the User
        user = UserSerializer().create(user_data)

        # Retrieve the Role object and ensure it is 'School Admin'
        try:
            role = Role.objects.get(id=user_role_uuid)
            if role.name != 'School Admin':
                raise serializers.ValidationError({"user_role": "The provided role must be 'School Admin'."})
        except Role.DoesNotExist:
            raise serializers.ValidationError({"user_role": "Invalid role UUID provided."})

        # Create the UserRole
        UserRole.objects.create(user=user, role=role)

        # Create the SchoolAdmin with the created user
        school_admin = SchoolAdmin.objects.create(user=user, **validated_data)
        return school_admin


class SchoolAdminListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing SchoolAdmins.
    """
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = SchoolAdmin
        fields = [
            'schooladmin_id', 'first_name', 'surname', 'email',
            'phone_number', 'designation', 'school_name'
        ]

class SchoolAdminDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for retrieving details of a SchoolAdmin.
    """
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = SchoolAdmin
        fields = [
            'schooladmin_id', 'user', 'school', 'school_name', 'surname',
            'first_name', 'email', 'phone_number', 'address', 'city', 'state',
            'region', 'country', 'designation', 'created_at', 'updated_at'
        ]
