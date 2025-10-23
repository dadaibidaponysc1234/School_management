from django.shortcuts import render
from user_registration.models import (ComplianceVerification, School, Student, SuperAdmin, Year,Term,ClassYear,Class,Classroom,
                     Teacher,Department,Subject,ClassTeacher,
                     TeacherAssignment,StudentSubjectRegistration,
                     SubjectClass,ClassDepartment,StudentClass, 
                     SubjectRegistrationControl,Day,Period,SubjectPeriodLimit,Constraint)


from .serializers import (ComplianceVerificationMetricsSerializer, SuperAdminMetricsSerializer, YearSerializer,TermSerializer,ClassYearSerializer,
                          ClassSerializer,ClassroomSerializer,DepartmentSerializer,
                          SubjectSerializer,ClassTeacherSerializer,TeacherAssignmentSerializer,
                           StudentSubjectRegistrationSerializer, StudentClassSerializer,
                          SubjectClassSerializer,ClassDepartmentSerializer,
                          SubjectRegistrationControlUpdateSerializer,SubjectRegistrationControlSerializer,
                          StudentSubjectStatusUpdateSerializer,DaySerializer,PeriodSerializer,
                          SubjectPeriodLimitSerializer,ConstraintSerializer,BulkSubjectClassAssignmentSerializer,
                          )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics, permissions, filters, exceptions
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from user_registration.permissions import (IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,IsClassTeacher,
                          HasValidPinAndSchoolId,IsStudentReadOnly,
                          IsTeacherReadOnly,IsSchoolAdminReadOnly,SchoolAdminOrIsClassTeacherOrISstudent)
from rest_framework.generics import (ListAPIView,RetrieveUpdateDestroyAPIView,
                                     ListCreateAPIView,RetrieveUpdateAPIView,DestroyAPIView,
                                     RetrieveAPIView)
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework import generics
from django.db import transaction
from django.utils.crypto import get_random_string
import csv
from io import StringIO
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser
from user_registration.utils import generate_temp_token, validate_temp_token
from django.utils.crypto import get_random_string
from rest_framework.exceptions import ValidationError
from rest_framework.exceptions import PermissionDenied
from django.utils.timezone import now



class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class YearListCreateView(generics.ListCreateAPIView):
    """
    List and create Years for the authenticated School Admin's school.
    """
    serializer_class = YearSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Year.objects.none()
        return Year.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class YearDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific Year.
    """
    serializer_class = YearSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Year.objects.none()
        return Year.objects.filter(school=self.request.user.school_admin.school)

    def update(self, request, *args, **kwargs):
        """
        Allow updates to active years and manage status changes.
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        new_status = request.data.get("status")

        if new_status is True:  # Attempting to set this year as active
            # Deactivate all other years for the same school
            Year.objects.filter(school=instance.school).update(status=False)

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Prevent deletion of the active year.
        """
        instance = self.get_object()
        if instance.status:
            return Response(
                {"error": "Cannot delete the active year."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)


class TermListCreateView(generics.ListCreateAPIView):
    """
    List and create terms for the authenticated School Admin's school.
    """
    serializer_class = TermSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['status', 'year']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Term.objects.none()
        return Term.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class TermDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific term.
    """
    serializer_class = TermSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Term.objects.none()
        return Term.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        term = serializer.save()
        if term.status:
            # Ensure only one active term per year
            Term.objects.filter(year=term.year).exclude(pk=term.pk).update(status=False)


class ClassYearListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassYearSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ClassYear.objects.none()
        return ClassYear.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ClassYearDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassYearSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ClassYear.objects.none()
        return ClassYear.objects.filter(school=self.request.user.school_admin.school)
    


class ClassListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Class.objects.none()
        return Class.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Class.objects.none()
        return Class.objects.filter(school=self.request.user.school_admin.school)
    
    

class ClassroomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = PageNumberPagination
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Classroom.objects.none()
        return Classroom.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ClassroomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Classroom.objects.none()
        return Classroom.objects.filter(school=self.request.user.school_admin.school)


class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    List and Create Departments for a School.
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = PageNumberPagination
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Short-circuit during schema generation or when unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Department.objects.none()
        return Department.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class DepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update, and Delete a Department.
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Short-circuit during schema generation or when unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Department.objects.none()
        return Department.objects.filter(school=self.request.user.school_admin.school)


class SubjectListCreateView(generics.ListCreateAPIView):
    """
    List and Create Subjects for a School.
    Allows filtering subjects by department using the 'department_id' query parameter.
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly]
    pagination_class = PageNumberPagination
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        Retrieves subjects based on the authenticated school admin's school.
        Supports filtering by department ID.
        """
        # Short-circuit during schema generation or when unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or (hasattr(self.request.user,'super_admin') and not (any(hasattr(self.request.user, x) for x in ["teacher", "school_admin"]))):
            return Subject.objects.none()

        if hasattr(self.request.user, 'teacher'):
            school = self.request.user.teacher.school
        elif hasattr(self.request.user, 'school_admin'):
            school = self.request.user.school_admin.school
        elif hasattr(self.request.user, 'student'):
            school = self.request.user.student.school

        queryset = Subject.objects.filter(school=school)

        # Filter by department if department_id is provided in the query params
        department_id = self.request.query_params.get("department_id")
        if department_id:
            queryset = queryset.filter(department_id=department_id)

        return queryset

    def perform_create(self, serializer):
        """
        Automatically assigns the school of the authenticated admin when creating a subject.
        """
        serializer.save(school=self.request.user.school_admin.school)


class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, Update, and Delete a Subject.
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Short-circuit during schema generation or when unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Subject.objects.none()
        return Subject.objects.filter(school=self.request.user.school_admin.school)


##############################################################################################

class ClassTeacherListCreateView(generics.ListCreateAPIView):
    """
    List and create ClassTeacher mappings.
    """
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsschoolAdmin]
    filter_backends = [filters.SearchFilter]  # Enable search functionality
    search_fields = ['class_assigned.class_name']  # Allow searching by class name
    # pagination_class = PageNumberPagination
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        # Filter by the authenticated school admin's school
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ClassTeacher.objects.none()
        return ClassTeacher.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        # Automatically set the school to the admin's school
        school = self.request.user.school_admin.school
        class_assigned = serializer.validated_data['class_assigned']
        teacher = serializer.validated_data['teacher']

        # Ensure the class and teacher belong to the same school
        if class_assigned.school != school or teacher.school != school:
            raise ValidationError("Both the class and teacher must belong to the same school.")

        serializer.save(school=school)


class ClassTeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete ClassTeacher mappings.
    """
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Filter by the authenticated school admin's school
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ClassTeacher.objects.none()
        return ClassTeacher.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        # Automatically set the school to the admin's school during updates
        school = self.request.user.school_admin.school
        class_assigned = serializer.validated_data.get('class_assigned', serializer.instance.class_assigned)
        teacher = serializer.validated_data.get('teacher', serializer.instance.teacher)

        # Ensure the class and teacher belong to the same school
        if class_assigned.school != school or teacher.school != school:
            raise ValidationError("Both the class and teacher must belong to the same school.")

        serializer.save(school=school)

class BulkClassTeacherCreateView(APIView):
    """
    Bulk assign multiple teachers to multiple classes.
    Accessible only by School Admins.
    """
    permission_classes = [IsschoolAdmin]

    def post(self, request, *args, **kwargs):
        """
        Assign multiple teachers to multiple classes in a single request.
        Expected Request Body:
        {
            "assignments": [
                {"teacher_id": "teacher_uuid1", "class_id": "class_uuid1"},
                {"teacher_id": "teacher_uuid2", "class_id": "class_uuid2"}
            ]
        }
        """
        assignments = request.data.get("assignments", [])
        if not assignments:
            # print("🚨 ERROR: Assignments list is empty")
            return Response({"error": "Assignments list cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        school = request.user.school_admin.school  # Ensure admin is assigning within their school
        # print(f"✅ Authenticated School Admin: {request.user.username}, School ID: {school.id}")

        created_assignments = []
        errors = []

        teacher_ids = {a["teacher_id"] for a in assignments}
        class_ids = {a["class_id"] for a in assignments}

        # Fetch all teachers and classes in one query for efficiency
        teachers = {str(t.teacher_id): t for t in Teacher.objects.filter(teacher_id__in=teacher_ids, school=school)}
        classes = {str(c.class_id): c for c in Class.objects.filter(class_id__in=class_ids, school=school)}

        # print("🔎 Found Teachers:", teachers.keys())
        # print("🔎 Found Classes:", classes.keys())

        # Fetch existing assignments (to avoid duplicates)
        existing_assignments = {
            (str(ct.teacher.teacher_id), str(ct.class_assigned.class_id))
            for ct in ClassTeacher.objects.filter(teacher__in=teachers.values(), class_assigned__in=classes.values())
        }

        # print("📌 Existing Assignments:", existing_assignments)

        with transaction.atomic():
            for assignment in assignments:
                teacher_id = str(assignment.get("teacher_id"))
                class_id = str(assignment.get("class_id"))

                # print(f"🔍 Checking Assignment: Teacher {teacher_id} -> Class {class_id}")

                teacher = teachers.get(teacher_id)
                class_assigned = classes.get(class_id)

                if not teacher:
                    # print(f"❌ ERROR: Teacher {teacher_id} not found in this school!")
                    errors.append({"teacher_id": teacher_id, "error": "Teacher not found in this school."})
                    continue

                if not class_assigned:
                    # print(f"❌ ERROR: Class {class_id} not found in this school!")
                    errors.append({"class_id": class_id, "error": "Class not found in this school."})
                    continue

                if (teacher_id, class_id) in existing_assignments:
                    # print(f"⚠️ WARNING: Teacher {teacher_id} is already assigned to Class {class_id}")
                    errors.append({"teacher_id": teacher_id, "class_id": class_id, "error": "Already assigned."})
                    continue

                # Create new assignment
                class_teacher = ClassTeacher.objects.create(
                    teacher=teacher,
                    class_assigned=class_assigned,
                    school=school
                )

                created_assignments.append({
                    "class_teacher_id": str(class_teacher.class_teacher_id),
                    "teacher_id": str(teacher.teacher_id),
                    "teacher_name": f"{teacher.first_name} {teacher.last_name}",
                    "class_id": str(class_assigned.class_id),
                    "class_name": class_assigned.arm_name,
                    "school_id": str(school.id),
                    "school_name": school.school_name
                })

                # print(f"✅ SUCCESS: Assigned Teacher {teacher.first_name} {teacher.last_name} -> Class {class_assigned.arm_name}")

        response_data = {"message": "Teachers assigned successfully.", "data": created_assignments}
        if errors:
            response_data["errors"] = errors  # Include errors if any assignments failed

        # print("📤 Final Response:", response_data)
        return Response(response_data, status=status.HTTP_201_CREATED)


class ClassTeacherListView(generics.ListAPIView):
    """
    List all teacher-class assignments for a school.
    Accessible only by School Admins.
    """
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsschoolAdmin]
    # pagination_class = PageNumberPagination
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ClassTeacher.objects.none()
        school = self.request.user.school_admin.school
        return ClassTeacher.objects.filter(school=school)


class ClassTeacherUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update (PUT/PATCH), or delete a class-teacher assignment.
    """
    serializer_class   = ClassTeacherSerializer
    permission_classes = [IsschoolAdmin]
    lookup_field       = "class_teacher_id"
    lookup_url_kwarg   = "class_teacher_id"

    def get_queryset(self):
        if (getattr(self, 'swagger_fake_view', False) or
            not getattr(self.request, 'user', None) or
            not self.request.user.is_authenticated or
            not getattr(self.request.user, 'school_admin', None)):
            return ClassTeacher.objects.none()

        school = self.request.user.school_admin.school
        return ClassTeacher.objects.filter(school=school).select_related(
            "class_assigned", "teacher", "school"
        )

    # --- add these three ---

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Class-teacher assignment updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Class-teacher assignment deleted successfully."},
            status=status.HTTP_200_OK
        )


class DeleteMultipleClassTeachersView(APIView):
    """
    API to delete multiple teacher-class assignments.
    Accessible only by School Admins.
    """
    permission_classes = [IsschoolAdmin]

    def delete(self, request, *args, **kwargs):
        assignment_ids = request.data.get('assignment_ids', [])
        if not assignment_ids or not isinstance(assignment_ids, list):
            return Response({"error": "A list of assignment IDs is required."}, status=status.HTTP_400_BAD_REQUEST)

        deleted_count = ClassTeacher.objects.filter(class_teacher_id__in=assignment_ids).delete()[0]
        return Response({"message": f"{deleted_count} teacher-class assignment(s) deleted successfully."}, status=status.HTTP_200_OK)


#===========================================================================================================
class SubjectClassListCreateView(generics.ListCreateAPIView):
    """
    List and create SubjectClass entries.
    Accessible by School Admins.
    """
    serializer_class = SubjectClassSerializer
    permission_classes = [IsschoolAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['subject', 'department']  # Exact matching for filtering
    search_fields = ['subject__name', 'department__name'] 
    
    def get_queryset(self):
        """
        Returns SubjectClasses only for the authenticated School Admin's school.
        """
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return SubjectClass.objects.none()
        return SubjectClass.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        """
        Ensures that the subject, department, and school belong to the same institution.
        """
        school = self.request.user.school_admin.school
        subject = serializer.validated_data['subject']
        department = serializer.validated_data.get('department', None)  # Optional

        # Ensure all assigned entities belong to the same school
        if subject.school != school or (department and department.school != school):
            raise ValidationError("Subject and department must belong to the same school.")

        serializer.save(school=school)


class BulkSubjectClassAssignmentView(APIView):
    """
    Assign multiple subjects to a department (bulk create).
    Accessible only by School Admins.
    """
    permission_classes = [IsschoolAdmin]

    def post(self, request):
        serializer = BulkSubjectClassAssignmentSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        school = request.user.school_admin.school
        department = serializer.validated_data['department']
        subjects = serializer.validated_data['subjects']

        created = []
        for subject in subjects:
            obj, created_flag = SubjectClass.objects.get_or_create(
                subject=subject,
                department=department,
                school=school
            )
            if created_flag:
                created.append(obj)

        return Response(
            {"message": f"{len(created)} subject(s) successfully assigned to {department.name}."},
            status=status.HTTP_201_CREATED
        )


class SubjectClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific SubjectClass mapping.
    Accessible by School Admins.
    """
    serializer_class = SubjectClassSerializer
    permission_classes = [IsschoolAdmin]
    lookup_field = 'subject_class_id'  # Ensure it matches the URL param

    def get_queryset(self):
        """
        Returns only SubjectClass mappings for the authenticated School Admin's school.
        """
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return SubjectClass.objects.none()
        return SubjectClass.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        """
        Ensures that the updated subject, class, and department belong to the same school.
        """
        school = self.request.user.school_admin.school
        subject = serializer.validated_data.get('subject', serializer.instance.subject)
        department = serializer.validated_data.get('department', serializer.instance.department)

        if any(obj.school != school for obj in [subject, department] if obj is not None):
            raise ValidationError("Subject and department must belong to the same school.")

        serializer.save(school=school)

#################################################################################################################

class ClassDepartmentListCreateView(generics.ListCreateAPIView):
    serializer_class   = ClassDepartmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]

    # allow filtering by class, class_year, and department
    filterset_fields = ['classes', 'classes__class_year', 'department']
    # allow searching by arm name and class year name
    search_fields    = ['classes__arm_name', 'classes__class_year__class_name', 'department__name']

    def get_queryset(self):
        if (getattr(self, 'swagger_fake_view', False) or
            not getattr(self.request, 'user', None) or
            not self.request.user.is_authenticated or
            not getattr(self.request.user, 'school_admin', None)):
            return ClassDepartment.objects.none()

        school = self.request.user.school_admin.school
        return (ClassDepartment.objects
                .filter(school=school)
                .select_related('school', 'department', 'classes', 'classes__class_year'))

    def perform_create(self, serializer):
        school    = self.request.user.school_admin.school
        classes   = serializer.validated_data['classes']
        department = serializer.validated_data.get('department')

        # ensure all belong to same school
        if classes.school_id != school.id:
            raise ValidationError("Selected class must belong to the same school.")
        if department and department.school_id != school.id:
            raise ValidationError("Department must belong to the same school.")

        serializer.save(school=school)

class ClassDepartmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassDepartmentSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'subject_class_id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ClassDepartment.objects.none()
        return ClassDepartment.objects.filter(school=self.request.user.school_admin.school)
    
    def perform_update(self, serializer):
        school = self.request.user.school_admin.school
        classes = serializer.validated_data.get('classes', serializer.instance.classes)
        department = serializer.validated_data.get('department', serializer.instance.department)
        
        if department and department.school != school:
            raise ValidationError("Department must belong to the same school.")

        serializer.save(school=school)

#################################################################################################################

class TeacherAssignmentListCreateView(generics.ListCreateAPIView):
    serializer_class   = TeacherAssignmentSerializer
    permission_classes = [IsschoolAdmin]
    filter_backends    = [DjangoFilterBackend, filters.SearchFilter]

    # ✅ Allow filtering by class year too
    filterset_fields = [
        'teacher', 'subject_class', 'class_department_assigned', 'school',
        'class_department_assigned__classes__class_year'  # 👈 added
    ]
    # ✅ Allow searching by class year name
    search_fields = [
        'teacher__first_name', 'teacher__last_name',
        'subject_class__subject__name',
        'class_department_assigned__classes__arm_name',
        'subject_class__department__name',
        'class_department_assigned__classes__class_year__class_name',  # 👈 added
    ]

    def get_queryset(self):
        if (getattr(self, 'swagger_fake_view', False) or
            not getattr(self.request, 'user', None) or
            not self.request.user.is_authenticated or
            not getattr(self.request.user, 'school_admin', None)):
            return TeacherAssignment.objects.none()

        school = self.request.user.school_admin.school
        return (
            TeacherAssignment.objects
            .filter(school=school)
            .select_related(
                'school',
                'teacher',
                'subject_class', 'subject_class__subject', 'subject_class__department',
                'class_department_assigned',
                'class_department_assigned__classes',
                'class_department_assigned__classes__class_year'  # 👈 eager-load year
            )
        )

    def perform_create(self, serializer):
        school = self.request.user.school_admin.school
        teacher = serializer.validated_data['teacher']
        subject_class = serializer.validated_data['subject_class']
        class_dept = serializer.validated_data['class_department_assigned']

        if teacher.school_id != school.id:
            raise ValidationError("Teacher must belong to your school.")
        if subject_class.school_id != school.id:
            raise ValidationError("Subject class must belong to your school.")
        if class_dept.school_id != school.id:
            raise ValidationError("Class/department must belong to your school.")

        serializer.save(school=school)

class TeacherAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific teacher assignment.
    Accessible by School Admins.
    """
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        """
        Returns assignments only for the authenticated School Admin's school.
        """
        # Short-circuit during schema generation or when unauthenticated
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return TeacherAssignment.objects.none()
        return TeacherAssignment.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        """
        Ensures that updated teacher, subject, and class belong to the same school.
        """
        school = self.request.user.school_admin.school
        teacher = serializer.validated_data.get('teacher', serializer.instance.teacher)
        subject = serializer.validated_data.get('subject', serializer.instance.subject)
        class_assigned = serializer.validated_data.get('class_assigned', serializer.instance.class_assigned)

        if any(obj.school != school for obj in [teacher, subject, class_assigned]):
            raise ValidationError("Teacher, subject, and class must belong to the same school.")

        serializer.save(school=school)

#####################################################################################################

# views.py
# class StudentClassListView(generics.ListAPIView):
#     serializer_class   = StudentClassSerializer
#     permission_classes = [IsAuthenticated, SchoolAdminOrIsClassTeacherOrISstudent]
    
#     def _current_school(self, user):
#         for rel in ("school_admin", "teacher", "student"):
#             obj = getattr(user, rel, None)
#             if obj:
#                 return getattr(obj, "school", None)
#         return None

#     def get_queryset(self):
#         if getattr(self, "swagger_fake_view", False):
#             return StudentClass.objects.none()

#         u = getattr(self.request, "user", None)
#         if not (u and u.is_authenticated):
#             return StudentClass.objects.none()

#         school = self._current_school(u)
#         base = StudentClass.objects.filter(student__school=school)\
#             .select_related("student", "class_year", "class_arm", "class_year__school")

#         # School Admin → all in school
#         if getattr(u, "school_admin", None):
#             return base

#         # Teacher → students in teacher's classes (try common schemas safely)
#         teacher = getattr(u, "teacher", None)
#         if teacher:
#             # Try a through model like TeacherClass(teacher, class_arm)
#             try:
#                 class_ids = list(teacher.assigned_classes.values_list("class_assigned__class_id", flat=True))
#                 if class_ids:
#                     return base.filter(class_arm_id__in=class_ids)
#             except Exception:
#                 pass
#             # Try direct M2M: Class.teachers
#             try:
#                 return base.filter(class_arm__teachers=teacher)
#             except Exception:
#                 pass
#             # Optional single pointer
#             try:
#                 current = getattr(teacher, "current_class_arm", None)
#                 if current:
#                     return base.filter(class_arm=current)
#             except Exception:
#                 pass
#             return StudentClass.objects.none()

#         # Student → only their record(s)
#         student = getattr(u, "student", None)
#         if student:
#             return base.filter(student=student)

#         return StudentClass.objects.none()

class StudentClassListView(generics.ListAPIView):
    serializer_class   = StudentClassSerializer
    permission_classes = [IsAuthenticated, SchoolAdminOrIsClassTeacherOrISstudent]

    def _current_school(self, user):
        for rel in ("school_admin", "teacher", "student"):
            obj = getattr(user, rel, None)
            if obj:
                return getattr(obj, "school", None)
        return None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return StudentClass.objects.none()

        u = getattr(self.request, "user", None)
        if not (u and u.is_authenticated):
            return StudentClass.objects.none()

        school = self._current_school(u)
        if not school:
            return StudentClass.objects.none()

        # Optional URL param: /student-classes/<student_id>/
        student_id = self.kwargs.get("student_id")

        base = (
            StudentClass.objects
            .filter(student__school=school)
            .select_related("student", "class_year", "class_arm", "class_year__school")
        )

        # If a specific student_id is requested, narrow first
        if student_id:
            base = base.filter(student__student_id=student_id)

        # --- Role-based scoping ---
        # School Admin → can see whatever 'base' currently holds (all or the specific student)
        if getattr(u, "school_admin", None):
            return base

        # Teacher → only students in teacher's assigned classes
        teacher = getattr(u, "teacher", None)
        if teacher:
            # Prefer robust filtering; try different relationship shapes safely
            # 1) through model where FK is class_assigned -> Class (or ClassArm)
            try:
                class_ids = list(
                    teacher.assigned_classes.values_list("class_assigned__class_id", flat=True)
                )
                if class_ids:
                    return base.filter(class_arm_id__in=class_ids)
            except Exception:
                pass
            # 2) direct M2M: ClassArm.teachers
            try:
                return base.filter(class_arm__teachers=teacher)
            except Exception:
                pass
            # 3) single FK pointer on teacher
            try:
                current = getattr(teacher, "current_class_arm", None)
                if current:
                    return base.filter(class_arm=current)
            except Exception:
                pass
            return StudentClass.objects.none()

        # Student → only their own records
        student = getattr(u, "student", None)
        if student:
            if student_id and str(student.student_id) != str(student_id):
                # Requesting someone else — deny
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only view your own class records.")
            return base.filter(student=student)

        return StudentClass.objects.none()


class StudentClassUpdateView(generics.UpdateAPIView):
    serializer_class   = StudentClassSerializer
    permission_classes = [IsAuthenticated, SchoolAdminOrIsClassTeacherOrISstudent]
    lookup_field       = "student_class_id"

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return StudentClass.objects.none()
        u = getattr(self.request, "user", None)
        if not (u and u.is_authenticated and getattr(u, "school_admin", None)):
            return StudentClass.objects.none()
        school = u.school_admin.school
        return StudentClass.objects.filter(student__school=school)\
            .select_related("student", "class_year", "class_arm", "class_year__school")


#####################################################################################################

class StudentSubjectRegistrationListCreateView(generics.ListCreateAPIView):
    """
    Allows School Admin, Class Teacher, and Student to create or view subject registrations.
    School Admins can register any student.
    Class Teachers can register only students in their class.
    Students can register only themselves.
    """
    serializer_class = StudentSubjectRegistrationSerializer
    permission_classes = [IsschoolAdmin | ISstudent | IsClassTeacher]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'school_admin'):
            return StudentSubjectRegistration.objects.filter(school=user.school_admin.school)

        elif hasattr(user, 'teacher'):
            teacher = user.teacher
            student_classes = teacher.assigned_classes.values_list('class_assigned__class_id', flat=True)
            return StudentSubjectRegistration.objects.filter(student_class__class_arm__classes__in=student_classes)

        elif hasattr(user, 'student'):
            student = user.student
            return StudentSubjectRegistration.objects.filter(student_class__student=student)

        return StudentSubjectRegistration.objects.none()

    def perform_create(self, serializer):
        user = self.request.user
        student_class = serializer.validated_data['student_class']

        if hasattr(user, 'school_admin'):
            serializer.save()

        elif hasattr(user, 'teacher'):
            # Check if teacher is assigned to the class
            if not user.teacher.assigned_classes.filter(class_assigned=student_class.class_arm.classes).exists():
                raise PermissionDenied("You can only register students in your assigned classes.")
            serializer.save()

        elif hasattr(user, 'student'):
            if student_class.student != user.student:
                raise PermissionDenied("Students can only register themselves.")
            serializer.save()


class StudentSubjectRegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View, update, or delete a specific student subject registration.
    Only School Admins and Class Teachers can update/delete.
    Students can view only.
    """
    serializer_class = StudentSubjectRegistrationSerializer
    lookup_field = 'registration_id'
    permission_classes = [IsschoolAdmin | IsClassTeacher | ISstudent]

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'school_admin'):
            return StudentSubjectRegistration.objects.filter(school=user.school_admin.school)

        elif hasattr(user, 'teacher'):
            class_ids = user.teacher.assigned_classes.values_list('class_assigned__id', flat=True)
            return StudentSubjectRegistration.objects.filter(student_class__class_arm__classes__in=class_ids)

        elif hasattr(user, 'student'):
            return StudentSubjectRegistration.objects.filter(student_class__student=user.student)

        return StudentSubjectRegistration.objects.none()

    def perform_update(self, serializer):
        user = self.request.user
        if hasattr(user, 'student'):
            raise PermissionDenied("Students are not allowed to update registration status.")

        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if hasattr(user, 'student'):
            raise PermissionDenied("Students are not allowed to delete registrations.")
        instance.delete()

##################################################################################################################################
class SubjectRegistrationControlView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsschoolAdmin]

    def get_object(self):
        # get the admin's school
        school = getattr(self.request.user.school_admin, "school", None)
        if not school:
            raise exceptions.PermissionDenied("No school found for this admin.")

        # auto-create if missing
        obj, _created = SubjectRegistrationControl.objects.get_or_create(
            school=school,
            defaults={"is_open": False, "start_date": None, "end_date": None},
        )
        return obj

    def get_serializer_class(self):
        return (
            SubjectRegistrationControlSerializer
            if self.request.method == "GET"
            else SubjectRegistrationControlUpdateSerializer
        )


class UpdateSubjectRegistrationStatusView(generics.UpdateAPIView):
    """
    Allows only School Admin or Class Teacher to update status of a registration.
    Class Teachers can only update students in their assigned classes.
    """
    queryset = StudentSubjectRegistration.objects.all()
    serializer_class = StudentSubjectStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsschoolAdmin | IsClassTeacher]
    lookup_field = 'registration_id'

    def get_object(self):
        obj = super().get_object()

        # If the user is a Class Teacher, check class ownership
        user = self.request.user
        if hasattr(user, 'teacher') and not hasattr(user, 'school_admin'):
            teacher = user.teacher
            # Fetch all class IDs the teacher is assigned to
            assigned_class_ids = teacher.assigned_classes.values_list('class_assigned_id', flat=True)

            # Get the class assigned to the student
            student_class = obj.student_class.class_arm.classes

            if student_class.pk not in assigned_class_ids:
                raise PermissionDenied("You do not have permission to update this student's subject registration.")

        return obj

#######################################################################################################
class DayListCreateView(generics.ListCreateAPIView):
    """
    List and create Days for the authenticated School Admin's school.
    """
    serializer_class = DaySerializer
    permission_classes = [IsschoolAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Day.objects.none()
        return Day.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class DayDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific Day.
    """
    serializer_class = DaySerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Day.objects.none()
        return Day.objects.filter(school=self.request.user.school_admin.school)


# Period Views
class PeriodListCreateView(generics.ListCreateAPIView):
    """
    List and create Periods for the authenticated School Admin's school.
    """ 
    serializer_class = PeriodSerializer
    permission_classes = [IsschoolAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Period.objects.none()
        return Period.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class PeriodDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific Period.
    """
    serializer_class = PeriodSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Period.objects.none()
        return Period.objects.filter(school=self.request.user.school_admin.school)


# SubjectPeriodLimit Views
class SubjectPeriodLimitListCreateView(generics.ListCreateAPIView):
    """
    List and create SubjectPeriodLimits for the authenticated School Admin's school.
    """
    serializer_class = SubjectPeriodLimitSerializer
    permission_classes = [IsschoolAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return SubjectPeriodLimit.objects.none()
        return SubjectPeriodLimit.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class SubjectPeriodLimitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific SubjectPeriodLimit.
    """
    serializer_class = SubjectPeriodLimitSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return SubjectPeriodLimit.objects.none()
        return SubjectPeriodLimit.objects.filter(school=self.request.user.school_admin.school)


# Constraint Views
class ConstraintDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update Constraints for the authenticated School Admin's school.
    """
    serializer_class = ConstraintSerializer
    permission_classes = [IsschoolAdmin]

    def get_object(self):
        school = self.request.user.school_admin.school
        return Constraint.objects.get_or_create(school=school)[0]
    

class SuperAdminMetricsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        data = {
            "school_count": School.objects.count(),
            "teacher_count": Teacher.objects.count(),
            "student_count": Student.objects.count(),
            "superadmin_count": SuperAdmin.objects.count(),
            "student_male": Student.objects.filter(gender="M").count(),
            "student_female": Student.objects.filter(gender="F").count(),
        }

        serializer = SuperAdminMetricsSerializer(data)
        return Response(serializer.data)
    


class ComplianceVerificationMetricsView(APIView):
    permission_classes = [IsSuperAdmin]
    
    def get(self, request):
        # Pending counts
        pending_tax_id = ComplianceVerification.objects.filter(
            tax_identification_number__isnull=True
        ).count() + ComplianceVerification.objects.filter(
            tax_identification_number=""
        ).count()

        pending_accreditation_cert = ComplianceVerification.objects.filter(
            accreditation_certificates__isnull=True
        ).count()

        pending_proof_of_reg = ComplianceVerification.objects.filter(
            proof_of_registration__isnull=True
        ).count()

        # Completed counts
        completed_tax_id = ComplianceVerification.objects.exclude(
            tax_identification_number__isnull=True
        ).exclude(tax_identification_number="").count()

        completed_accreditation_cert = ComplianceVerification.objects.exclude(
            accreditation_certificates__isnull=True
        ).count()

        completed_proof_of_reg = ComplianceVerification.objects.exclude(
            proof_of_registration__isnull=True
        ).count()

        data = {
            "pending_tax_id": pending_tax_id,
            "pending_accreditation_cert": pending_accreditation_cert,
            "pending_proof_of_reg": pending_proof_of_reg,
            "completed_tax_id": completed_tax_id,
            "completed_accreditation_cert": completed_accreditation_cert,
            "completed_proof_of_reg": completed_proof_of_reg,
        }

        serializer = ComplianceVerificationMetricsSerializer(data)
        return Response(serializer.data)