from rest_framework.permissions import BasePermission,SAFE_METHODS
from .models import UserRole,StudentRegistrationPin,ClassTeacher


class IsStudentReadOnly(BasePermission):
    """
    Allows students to only perform GET requests.
    Restricts them from making POST, PUT, and DELETE requests.
    """

    def has_permission(self, request, view):
        # Allow GET requests for authenticated students only
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and hasattr(request.user, 'student')

        # Restrict all other methods (POST, PUT, DELETE) for students
        return False
    
class IsTeacherReadOnly(BasePermission):
    """
    Allows students to only perform GET requests.
    Restricts them from making POST, PUT, and DELETE requests.
    """

    def has_permission(self, request, view):
        # Allow GET requests for authenticated students only
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and hasattr(request.user, 'teacher')

        # Restrict all other methods (POST, PUT, DELETE) for students
        return False


class IsSchoolAdminReadOnly(BasePermission):
    """
    Allows School Admins to only perform GET requests.
    Restricts them from making POST, PUT, and DELETE requests.
    """

    def has_permission(self, request, view):
        # Allow GET requests for authenticated School Admins only
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated and hasattr(request.user, 'school_admin')

        # Restrict all other methods (POST, PUT, DELETE) for School Admins
        return False


class IsSuperAdmin(BasePermission):
    """
    Custom permission to allow only users with the SuperAdmin role to access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user has the SuperAdmin role
        try:
            user_roles = UserRole.objects.filter(user=request.user)
            return any(role.role.name == 'Super Admin' for role in user_roles)
        except UserRole.DoesNotExist:
            return False

class IsschoolAdmin(BasePermission):
    """
    Custom permission to allow only users with the SuperAdmin role to access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user has the SuperAdmin role
        try:
            user_roles = UserRole.objects.filter(user=request.user)
            return any(role.role.name == 'School Admin' for role in user_roles)
        except UserRole.DoesNotExist:
            return False

class ISteacher(BasePermission):
    """
    Custom permission to allow only users with the SuperAdmin role to access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user has the SuperAdmin role
        try:
            user_roles = UserRole.objects.filter(user=request.user)
            return any(role.role.name == 'Teacher' for role in user_roles)
        except UserRole.DoesNotExist:
            return False

class ISstudent(BasePermission):
    """
    Custom permission to allow only users with the SuperAdmin role to access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user has the SuperAdmin role
        try:
            user_roles = UserRole.objects.filter(user=request.user)
            return any(role.role.name == 'Student' for role in user_roles)
        except UserRole.DoesNotExist:
            return False


class IsSuperAdminOrSchoolAdmin(BasePermission):
    """
    Custom permission to allow either Super Admins or School Admins.
    """
    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        try:
            user_roles = UserRole.objects.filter(user=request.user)
            # Check if any of the user's roles are either Super Admin or School Admin
            is_super_admin = any(role.role.name == 'Super Admin' for role in user_roles)
            is_school_admin = any(role.role.name == 'School Admin' for role in user_roles)
            return is_super_admin or is_school_admin
        except UserRole.DoesNotExist:
            return False
        
class HasValidPinAndSchoolId(BasePermission):
    def has_permission(self, request, view):
        school_id = request.data.get('school_id')
        otp = request.data.get('otp')
        try:
            pin = StudentRegistrationPin.objects.get(school_id=school_id, otp=otp, is_used=False)
            pin.is_used = True
            pin.save()
            return True
        except StudentRegistrationPin.DoesNotExist:
            return False
        

class IsClassTeacher(BasePermission):
    """
    Custom permission to allow only teachers assigned as class teachers to access.
    """

    def has_permission(self, request, view):
        # Check if the user is authenticated
        if not request.user.is_authenticated:
            return False

        # Check if the user has the 'Teacher' role
        try:
            user_roles = UserRole.objects.filter(user=request.user)
            is_teacher = any(role.role.name == 'Teacher' for role in user_roles)
            if not is_teacher:
                return False
        except UserRole.DoesNotExist:
            return False

        # Check if the teacher is assigned as a class teacher
        try:
            teacher = request.user.teacher  # Assuming the `Teacher` model has a OneToOne relation with the `User` model
            is_class_teacher = ClassTeacher.objects.filter(teacher=teacher).exists()
            return is_class_teacher
        except Exception:
            return False


# from rest_framework.permissions import BasePermission
# from user_registration.models import UserRole, ClassTeacher

class SchoolAdminOrIsClassTeacherOrISstudent(BasePermission):
    """
    Grants access if the user is a School Admin, Class Teacher, or Student.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        try:
            user_roles = UserRole.objects.filter(user=request.user)
            role_names = [role.role.name for role in user_roles]

            is_school_admin = 'School Admin' in role_names
            is_student = 'Student' in role_names
            is_teacher = 'Teacher' in role_names

            is_class_teacher = False
            if is_teacher:
                teacher = getattr(request.user, 'teacher', None)
                is_class_teacher = ClassTeacher.objects.filter(teacher=teacher).exists() if teacher else False

            return is_school_admin or is_class_teacher or is_student

        except Exception:
            return False
