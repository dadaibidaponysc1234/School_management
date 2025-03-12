from django.shortcuts import render
from user_registration.models import (User,Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     Year,Term,ClassYear,Class,Classroom,
                     Student,Teacher,Department,Subject,ClassTeacher,
                     TeacherAssignment,Day,Period,
                     SubjectPeriodLimit,Constraint,AttendancePolicy,FeeCategory,
                     Fee,AssessmentCategory,ExamCategory,ScorePerAssessmentInstance,ExamScore, 
                     ScoreObtainedPerAssessment, ContinuousAssessment,Result,AnnualResult,Notification, 
                     ClassTeacherComment, Attendance, AttendanceFlag, StudentSubjectAssignment, 
                     StudentRegistrationPin,SubjectRegistrationControl,StudentClassAndSubjectAssignment)


from .serializers import (YearSerializer,TermSerializer,ClassYearSerializer,
                          ClassSerializer,ClassroomSerializer,DepartmentSerializer,
                          SubjectSerializer,ClassTeacherSerializer,TeacherAssignmentSerializer,
                          StudentClassAndSubjectAssignmentSerializer, SubjectRegistrationControlSerializer,
                          DaySerializer,PeriodSerializer,SubjectPeriodLimitSerializer,
                          ConstraintSerializer
                          )

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,generics, permissions, parsers,filters
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from user_registration.permissions import (IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,IsClassTeacher,
                          HasValidPinAndSchoolId,IsStudentReadOnly,IsTeacherReadOnly,IsSchoolAdminReadOnly)
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
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'year']

    def get_queryset(self):
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
        return Term.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        term = serializer.save()
        if term.status:
            # Ensure only one active term per year
            Term.objects.filter(year=term.year).exclude(pk=term.pk).update(status=False)


class ClassYearListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassYearSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = PageNumberPagination
    filter_backends = [DjangoFilterBackend]

    def get_queryset(self):
        return ClassYear.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ClassYearDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassYearSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        return ClassYear.objects.filter(school=self.request.user.school_admin.school)
    


class ClassListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    # pagination_class = PageNumberPagination

    def get_queryset(self):
        return Class.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ClassDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        return Class.objects.filter(school=self.request.user.school_admin.school)
    
    

class ClassroomListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return Classroom.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ClassroomDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassroomSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        return Classroom.objects.filter(school=self.request.user.school_admin.school)


class DepartmentListCreateView(generics.ListCreateAPIView):
    """
    List and Create Departments for a School.
    """
    serializer_class = DepartmentSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly|IsSchoolAdminReadOnly]

    def get_queryset(self):
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
        return Department.objects.filter(school=self.request.user.school_admin.school)


class SubjectListCreateView(generics.ListCreateAPIView):
    """
    List and Create Subjects for a School.
    Allows filtering subjects by department using the 'department_id' query parameter.
    """
    serializer_class = SubjectSerializer
    permission_classes = [IsschoolAdmin |IsStudentReadOnly|IsTeacherReadOnly]

    def get_queryset(self):
        """
        Retrieves subjects based on the authenticated school admin's school.
        Supports filtering by department ID.
        """
        school = self.request.user.school_admin.school
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

    def get_queryset(self):
        # Filter by the authenticated school admin's school
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

    def get_queryset(self):
        school = self.request.user.school_admin.school
        return ClassTeacher.objects.filter(school=school)


class ClassTeacherUpdateView(generics.RetrieveUpdateAPIView):
    """
    Update a class-teacher assignment.
    """
    serializer_class = ClassTeacherSerializer
    permission_classes = [IsschoolAdmin]
    lookup_field = 'pk'

    def get_queryset(self):
        return ClassTeacher.objects.filter(school=self.request.user.school_admin.school)


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

class TeacherAssignmentListCreateView(generics.ListCreateAPIView):
    """
    List and create teacher assignments.
    """
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsschoolAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['teacher', 'subject', 'class_assigned', 'school']
    search_fields = ['teacher.first_name', 'teacher.last_name', 'subject.name', 'class_assigned.arm_name']

    def get_queryset(self):
        # Filter assignments by the school of the authenticated School Admin
        return TeacherAssignment.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        # Automatically associate the assignment with the school of the School Admin
        school = self.request.user.school_admin.school
        teacher = serializer.validated_data['teacher']
        subject = serializer.validated_data['subject']
        class_assigned = serializer.validated_data['class_assigned']

        # Validate that teacher, subject, and class belong to the same school
        if teacher.school != school or subject.school != school or class_assigned.school != school:
            raise ValidationError("Teacher, subject, and class must belong to the same school.")

        serializer.save(school=school)


class BulkTeacherAssignmentCreateView(APIView):
    """
    Bulk assign multiple teachers to multiple subjects and classes.
    Accessible only by School Admins.
    """
    permission_classes = [IsschoolAdmin]

    def post(self, request, *args, **kwargs):
        """
        Assign multiple teachers to subjects and classes.
        Expected Request Body:
        {
            "assignments": [
                {"teacher_id": "teacher_uuid1", "subject_id": "subject_uuid1", "class_id": "class_uuid1"},
                {"teacher_id": "teacher_uuid2", "subject_id": "subject_uuid2", "class_id": "class_uuid2"}
            ]
        }
        """
        assignments = request.data.get("assignments", [])
        if not assignments:
            return Response({"error": "Assignments list cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        school = request.user.school_admin.school
        created_assignments = []
        errors = []

        # Extract unique teacher IDs, subject IDs, and class IDs
        teacher_ids = {a["teacher_id"] for a in assignments}
        subject_ids = {a["subject_id"] for a in assignments}
        class_ids = {a["class_id"] for a in assignments}

        print(f"Authenticated School Admin: {request.user.username}, School ID: {school.id}")

        # Fetch teachers, subjects, and classes in one query
        teachers = {t.teacher_id: t for t in Teacher.objects.filter(teacher_id__in=teacher_ids, school=school)}
        subjects = {s.subject_id: s for s in Subject.objects.filter(subject_id__in=subject_ids, school=school)}
        classes = {c.class_id: c for c in Class.objects.filter(class_id__in=class_ids, school=school)}

        print(f"🔎 Found Teachers: {teachers.keys()}")
        print(f"🔎 Found Subjects: {subjects.keys()}")
        print(f"🔎 Found Classes: {classes.keys()}")

        # Fetch existing assignments to avoid duplicates
        existing_assignments = {
            (ta.teacher.teacher_id, ta.subject.subject_id, ta.class_assigned.class_id)
            for ta in TeacherAssignment.objects.filter(
                teacher__in=teachers.values(),
                subject__in=subjects.values(),
                class_assigned__in=classes.values(),
            )
        }
        print(f"📌 Existing Assignments: {existing_assignments}")

        with transaction.atomic():
            for assignment in assignments:
                teacher_id = assignment.get("teacher_id")
                subject_id = assignment.get("subject_id")
                class_id = assignment.get("class_id")

                teacher = teachers.get(teacher_id)
                subject = subjects.get(subject_id)
                class_assigned = classes.get(class_id)

                print(f"🔍 Checking Assignment: Teacher {teacher_id} -> Subject {subject_id} -> Class {class_id}")

                if not teacher:
                    errors.append({"teacher_id": teacher_id, "error": "Teacher not found in this school."})
                    continue
                if not subject:
                    errors.append({"subject_id": subject_id, "error": "Subject not found in this school."})
                    continue
                if not class_assigned:
                    errors.append({"class_id": class_id, "error": "Class not found in this school."})
                    continue

                if (teacher_id, subject_id, class_id) in existing_assignments:
                    errors.append({"teacher_id": teacher_id, "subject_id": subject_id, "class_id": class_id, "error": "Already assigned."})
                    continue

                # Create new assignment
                teacher_assignment = TeacherAssignment.objects.create(
                    teacher=teacher,
                    subject=subject,
                    class_assigned=class_assigned,
                    school=school
                )

                print(f"✅ SUCCESS: Assigned {teacher.user.first_name} {teacher.user.last_name} -> {subject.name} -> {class_assigned.arm_name}")

                created_assignments.append({
                    "teacher_subject_id": teacher_assignment.teacher_subject_id,
                    "teacher_id": teacher.teacher_id,
                    "teacher_name": f"{teacher.user.first_name} {teacher.user.last_name}",
                    "subject_id": subject.subject_id,
                    "subject_name": subject.name,
                    "class_id": class_assigned.class_id,
                    "class_name": class_assigned.arm_name,
                    "school_id": school.id,
                    "school_name": school.school_name
                })

        response_data = {"message": "Teachers assigned successfully.", "data": created_assignments}
        if errors:
            response_data["errors"] = errors  # Include errors if any assignments failed

        print(f"📤 Final Response: {response_data}")

        return Response(response_data, status=status.HTTP_201_CREATED)



class TeacherAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific teacher assignment.
    """
    serializer_class = TeacherAssignmentSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Filter assignments by the school of the authenticated School Admin
        return TeacherAssignment.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        school = self.request.user.school_admin.school
        teacher = serializer.validated_data.get('teacher', serializer.instance.teacher)
        subject = serializer.validated_data.get('subject', serializer.instance.subject)
        class_assigned = serializer.validated_data.get('class_assigned', serializer.instance.class_assigned)

        # Validate that teacher, subject, and class belong to the same school
        if teacher.school != school or subject.school != school or class_assigned.school != school:
            raise ValidationError("Teacher, subject, and class must belong to the same school.")

        serializer.save()


# Create, Read, Update, and Delete for StudentClassAndSubjectAssignment
class StudentClassAndSubjectAssignmentListCreateView(generics.ListCreateAPIView):
    """
    List all assignments for the authenticated student's school or create a new assignment.
    """
    serializer_class = StudentClassAndSubjectAssignmentSerializer
    permission_classes = [ISstudent]

    def get_queryset(self):
        return StudentClassAndSubjectAssignment.objects.filter(student=self.request.user.student)

    def perform_create(self, serializer):
        student = self.request.user.student
        school = student.school

        # Check if registration is open for the school
        control = SubjectRegistrationControl.objects.filter(school=school).first()
        if not control or not control.is_open:
            raise serializers.ValidationError("Subject registration is currently closed.")

        serializer.save(student=student, school=school)


class StudentClassAndSubjectAssignmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific assignment.
    """
    serializer_class = StudentClassAndSubjectAssignmentSerializer
    permission_classes = [IsschoolAdmin,ISteacher]

    def get_queryset(self):
        return StudentClassAndSubjectAssignment.objects.filter(student=self.request.user.student)


# Create, Read, Update, and Delete for SubjectRegistrationControl
class SubjectRegistrationControlView(generics.RetrieveUpdateAPIView):
    """
    Retrieve or update the registration control for the authenticated school.
    """
    serializer_class = SubjectRegistrationControlSerializer
    permission_classes = [IsschoolAdmin]  # Add custom permission to restrict to School Admins

    def get_queryset(self):
        return SubjectRegistrationControl.objects.filter(school=self.request.user.school_admin.school)


class SubjectRegistrationControlListView(generics.ListAPIView):
    """
    List all subject registration controls for the school admin's school.
    """
    serializer_class = SubjectRegistrationControlSerializer
    permission_classes = [IsschoolAdmin]  # Add custom permission for School Admins

    def get_queryset(self):
        return SubjectRegistrationControl.objects.filter(school=self.request.user.school_admin.school)

# class SubjectApprovalView(generics.UpdateAPIView):
#     """
#     Allow teachers to approve or reject subject registrations.
#     """
#     serializer_class = TeacherApprovalSerializer
#     permission_classes = [permissions.IsAuthenticated]  # Ensure only teachers can approve

#     def get_queryset(self):
#         teacher = self.request.user.teacher
#         return StudentClassAndSubjectAssignment.objects.filter(school=teacher.school, status="Pending")

class SubjectApprovalView(APIView):
    """
    Approve or reject subject registration for students.
    Accessible by Class Teachers or School Admins.
    """
    permission_classes = [IsClassTeacher]  # Customize with a specific permission for Class Teachers or School Admins

    def post(self, request, *args, **kwargs):
        """
        Approve or reject a student's subject registration.
        """
        assignment_id = request.data.get('assignment_id')
        action = request.data.get('action')  # Expected values: 'approve' or 'reject'

        if not assignment_id or action not in ['approve', 'reject']:
            return Response(
                {'error': 'Invalid input. Provide assignment_id and action (approve or reject).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Fetch the student's assignment
            assignment = StudentClassAndSubjectAssignment.objects.get(pk=assignment_id)

            # Check if the user is authorized to approve/reject (e.g., Class Teacher or School Admin)
            if request.user.school_admin.school != assignment.school:
                return Response({'error': 'You are not authorized to approve/reject this assignment.'}, status=status.HTTP_403_FORBIDDEN)

            # Update the status based on the action
            assignment.status = 'Approved' if action == 'approve' else 'Rejected'
            assignment.save()

            return Response(
                {'message': f'Subject registration {action}d successfully.', 'assignment': StudentClassAndSubjectAssignmentSerializer(assignment).data},
                status=status.HTTP_200_OK
            )
        except StudentClassAndSubjectAssignment.DoesNotExist:
            return Response({'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)


class MultipleSubjectApprovalView(APIView):
    """
    Approve or reject multiple subject registrations for students.
    Accessible by Class Teachers or School Admins.
    """
    permission_classes = [IsClassTeacher]  # Customize for Class Teachers or School Admins

    def post(self, request, *args, **kwargs):
        """
        Approve or reject multiple student subject registrations.
        """
        data = request.data.get('assignments')  # List of assignments with actions

        if not isinstance(data, list) or not data:
            return Response(
                {'error': 'Invalid input. Provide a list of assignments with assignment_id and action (approve/reject).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        results = []
        errors = []

        for item in data:
            assignment_id = item.get('assignment_id')
            action = item.get('action')

            if not assignment_id or action not in ['approve', 'reject']:
                errors.append({'assignment_id': assignment_id, 'error': 'Invalid data or action.'})
                continue

            try:
                assignment = StudentClassAndSubjectAssignment.objects.get(pk=assignment_id)

                # Check if the user is authorized to approve/reject
                if request.user.school_admin.school != assignment.school:
                    errors.append({'assignment_id': assignment_id, 'error': 'Not authorized.'})
                    continue

                # Update the status based on the action
                assignment.status = 'Approved' if action == 'approve' else 'Rejected'
                assignment.save()

                results.append({
                    'assignment_id': assignment_id,
                    'status': assignment.status,
                    'assignment': StudentClassAndSubjectAssignmentSerializer(assignment).data
                })

            except StudentClassAndSubjectAssignment.DoesNotExist:
                errors.append({'assignment_id': assignment_id, 'error': 'Assignment not found.'})

        response = {
            'results': results,
            'errors': errors
        }

        return Response(response, status=status.HTTP_200_OK)


class DayListCreateView(generics.ListCreateAPIView):
    """
    List and create Days for the authenticated School Admin's school.
    """
    serializer_class = DaySerializer
    permission_classes = [IsschoolAdmin]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
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