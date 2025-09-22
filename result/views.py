from rest_framework.views import APIView
from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from user_registration.models import (Student,ResultVisibilityControl,AssessmentCategory,
                                      ResultConfiguration, AnnualResultWeightConfig,
                                      GradingSystem,ScorePerAssessmentInstance, 
                                      StudentSubjectRegistration, TeacherAssignment,
                                      ScoreObtainedPerAssessment, StudentSubjectRegistration,Term, Year,
                                      ExamScore,ContinuousAssessment,Result,
                                      AnnualResult,ClassTeacher, ResultVisibilityControl, Term, Year,
                                      ClassYear, ClassDepartment,ClassTeacherComment
                                      )
from .serializers import (ResultVisibilityControlSerializer,AssessmentCategorySerializer, ResultConfigurationSerializer,
                           AnnualResultWeightConfigSerializer,GradingSystemSerializer,ScorePerAssessmentInstanceSerializer,
                           ScoreObtainedPerAssessmentSerializer,ExamScoreSerializer,ContinuousAssessmentSerializer,
                           ResultSerializer, AnnualResultSerializer,FullAnnualResultSerializer, FullTermResultSerializer,
                           BroadsheetSerializer,ClassTeacherCommentSerializer)
from rest_framework.permissions import IsAuthenticated
from user_registration.permissions import (IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,IsClassTeacher,
                          HasValidPinAndSchoolId,IsStudentReadOnly,
                          IsTeacherReadOnly,IsSchoolAdminReadOnly,SchoolAdminOrIsClassTeacherOrISstudent)
from .utils import (update_score_obtained_per_assessment,compute_continuous_assessment,
                    compute_result_for_registration,compute_annual_result, get_full_term_result_data, 
                    get_full_annual_result_data,get_broadsheet_data,export_broadsheet_to_excel)
from django.shortcuts import get_object_or_404
from .ai_comment_generator import generate_teacher_comment


class ResultVisibilityControlListCreateView(generics.ListCreateAPIView):
    serializer_class = ResultVisibilityControlSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        user = getattr(self, 'request', None) and getattr(self.request, 'user', None)
        if getattr(self, 'swagger_fake_view', False) or not user or not getattr(user, 'is_authenticated', False):
            return ResultVisibilityControl.objects.none()
        if hasattr(user, 'school_admin'):
            return ResultVisibilityControl.objects.filter(school=user.school_admin.school)
        return ResultVisibilityControl.objects.none()

    def post(self, request, *args, **kwargs):
        school = request.user.school_admin.school
        # Check if a visibility control already exists for this school
        if ResultVisibilityControl.objects.filter(school=school).exists():
            return Response(
                {"detail": "Result visibility control already exists for this school."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

class ResultVisibilityControlDetailUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = ResultVisibilityControlSerializer
    permission_classes = [IsschoolAdmin]
    queryset = ResultVisibilityControl.objects.all()

    def perform_update(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

#=========================================================================================

class AssessmentCategoryListCreateView(generics.ListCreateAPIView):
    serializer_class = AssessmentCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return AssessmentCategory.objects.none()
        return AssessmentCategory.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class AssessmentCategoryDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = AssessmentCategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsschoolAdmin]
    lookup_field = 'assessment_category_id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return AssessmentCategory.objects.none()
        return AssessmentCategory.objects.filter(school=self.request.user.school_admin.school)

#=========================================================================================
class ResultConfigurationListCreateView(generics.ListCreateAPIView):
    serializer_class = ResultConfigurationSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ResultConfiguration.objects.none()
        return ResultConfiguration.objects.filter(school=self.request.user.school_admin.school)

    def post(self, request, *args, **kwargs):
        school = request.user.school_admin.school
        if ResultConfiguration.objects.filter(school=school).exists():
            return Response(
                {"detail": "Result configuration already exists for this school."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class ResultConfigurationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ResultConfigurationSerializer
    permission_classes = [IsschoolAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return ResultConfiguration.objects.none()
        return ResultConfiguration.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

#=========================================================================================
class AnnualWeightConfigListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnualResultWeightConfigSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return AnnualResultWeightConfig.objects.none()
        return AnnualResultWeightConfig.objects.filter(school=self.request.user.school_admin.school)

    def post(self, request, *args, **kwargs):
        school = request.user.school_admin.school
        class_year = request.data.get('class_year')
        department = request.data.get('department')

        if AnnualResultWeightConfig.objects.filter(school=school, class_year=class_year, department=department).exists():
            return Response(
                {"detail": "Annual weight config already exists for this class and department."},
                status=status.HTTP_400_BAD_REQUEST
            )

        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class AnnualWeightConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnualResultWeightConfigSerializer
    permission_classes = [IsschoolAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return AnnualResultWeightConfig.objects.none()
        return AnnualResultWeightConfig.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

#=========================================================================================

class GradingSystemListCreateView(generics.ListCreateAPIView):
    serializer_class = GradingSystemSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return GradingSystem.objects.none()
        return GradingSystem.objects.filter(school=self.request.user.school_admin.school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)


class GradingSystemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = GradingSystemSerializer
    permission_classes = [IsschoolAdmin]
    lookup_field = 'id'

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return GradingSystem.objects.none()
        return GradingSystem.objects.filter(school=self.request.user.school_admin.school)

    def perform_update(self, serializer):
        serializer.save(school=self.request.user.school_admin.school)

#=========================================================================================

class ScorePerAssessmentListCreateView(generics.ListCreateAPIView):
    serializer_class = ScorePerAssessmentInstanceSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsschoolAdmin() or ISstudent() or ISteacher()]
        return [ISteacher()]

    def get_queryset(self):
        user = self.request.user
        school = None

        if hasattr(user, 'school_admin'):
            school = user.school_admin.school
        elif hasattr(user, 'teacher'):
            school = user.teacher.school
        elif hasattr(user, 'student'):
            school = user.student.school

        active_year = Year.objects.filter(school=school, status=True).first()
        active_term = Term.objects.filter(school=school, status=True).first()

        if not active_year or not active_term:
            return ScorePerAssessmentInstance.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            return ScorePerAssessmentInstance.objects.filter(registration__in=registrations)

        return ScorePerAssessmentInstance.objects.filter(registration__term=active_term)

    def perform_create(self, serializer):
        user = self.request.user
        teacher = getattr(user, 'teacher', None)

        if not teacher:
            raise PermissionDenied("Only teachers can create assessment scores.")

        instance = serializer.save(commit=False)
        registration = instance.registration
        student_class = registration.student_class
        subject_class = registration.subject_class
        school = teacher.school

        # Active term/year check
        active_year = Year.objects.filter(school=school, status=True).first()
        active_term = Term.objects.filter(school=school, status=True).first()

        if not active_year or not active_term or registration.term != active_term:
            raise PermissionDenied("You can only record scores for the active term.")

        is_assigned = TeacherAssignment.objects.filter(
            teacher=teacher,
            subject=subject_class,
            class_assigned=student_class.class_arm
        ).exists()

        if not is_assigned:
            raise PermissionDenied("You are not assigned to this subject and class.")

        # Save and update total
        instance = serializer.save()
        update_score_obtained_per_assessment(instance.registration, instance.category)


class ScorePerAssessmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ScorePerAssessmentInstanceSerializer
    lookup_field = 'scoreperassessment_id'

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsschoolAdmin() or ISstudent() or ISteacher()]
        return [ISteacher()]

    def get_queryset(self):
        user = self.request.user
        school = None

        if hasattr(user, 'school_admin'):
            school = user.school_admin.school
        elif hasattr(user, 'teacher'):
            school = user.teacher.school
        elif hasattr(user, 'student'):
            school = user.student.school

        active_year = Year.objects.filter(school=school, status=True).first()
        active_term = Term.objects.filter(school=school, status=True).first()

        if not active_year or not active_term:
            return ScorePerAssessmentInstance.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            return ScorePerAssessmentInstance.objects.filter(registration__in=registrations)

        return ScorePerAssessmentInstance.objects.filter(registration__term=active_term)

    def perform_update(self, serializer):
        instance = serializer.save()
        update_score_obtained_per_assessment(instance.registration, instance.category)

    def perform_destroy(self, instance):
        registration = instance.registration
        category = instance.category
        instance.delete()
        update_score_obtained_per_assessment(registration, category)

#=========================================================================================

class ScoreObtainedPerAssessmentListView(generics.ListAPIView):
    serializer_class = ScoreObtainedPerAssessmentSerializer
    permission_classes = [ISteacher or ISstudent or IsschoolAdmin]

    def get_queryset(self):
        user = self.request.user

        # Determine school and active term
        if hasattr(user, 'student'):
            school = user.student.school
        elif hasattr(user, 'teacher'):
            school = user.teacher.school
        elif hasattr(user, 'school_admin'):
            school = user.school_admin.school
        else:
            return ScoreObtainedPerAssessment.objects.none()

        active_term = Term.objects.filter(school=school, status=True).first()
        active_year = Year.objects.filter(school=school, status=True).first()

        if not active_term or not active_year:
            return ScoreObtainedPerAssessment.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            return ScoreObtainedPerAssessment.objects.filter(registration__in=registrations)

        elif hasattr(user, 'teacher'):
            teacher = user.teacher
            # Get all TeacherAssignments
            assignments = TeacherAssignment.objects.filter(teacher=teacher)

            subject_classes = [a.subject_class for a in assignments]
            class_arms = [a.class_department_assigned for a in assignments]

            registrations = StudentSubjectRegistration.objects.filter(
                subject_class__in=subject_classes,
                student_class__class_arm__in=class_arms,
                term=active_term
            )
            return ScoreObtainedPerAssessment.objects.filter(registration__in=registrations)

        # SchoolAdmin
        return ScoreObtainedPerAssessment.objects.filter(registration__term=active_term)

#=========================================================================================

class ExamScoreListCreateView(generics.ListCreateAPIView):
    serializer_class = ExamScoreSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsschoolAdmin() or ISstudent() or ISteacher()]
        return [ISteacher()]

    def get_queryset(self):
        user = self.request.user
        school = (
            getattr(user, 'school_admin', None) or
            getattr(user, 'teacher', None) or
            getattr(user, 'student', None)
        ).school

        active_term = Term.objects.filter(school=school, status=True).first()
        if not active_term:
            return ExamScore.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            return ExamScore.objects.filter(registration__in=registrations)

        if hasattr(user, 'teacher'):
            teacher = user.teacher
            assignments = TeacherAssignment.objects.filter(teacher=teacher)
            subject_classes = [a.subject_class for a in assignments]
            class_arms = [a.class_department_assigned for a in assignments]

            registrations = StudentSubjectRegistration.objects.filter(
                subject_class__in=subject_classes,
                student_class__class_arm__in=class_arms,
                term=active_term
            )
            return ExamScore.objects.filter(registration__in=registrations)

        return ExamScore.objects.filter(registration__term=active_term)

    def perform_create(self, serializer):
        user = self.request.user
        teacher = getattr(user, 'teacher', None)
        if not teacher:
            raise PermissionDenied("Only teachers can create exam scores.")

        instance = serializer.save(commit=False)
        registration = instance.registration
        school = teacher.school

        active_term = Term.objects.filter(school=school, status=True).first()
        if not active_term or registration.term != active_term:
            raise PermissionDenied("You can only create scores for the active term.")

        is_assigned = TeacherAssignment.objects.filter(
            teacher=teacher,
            subject=registration.subject_class,
            class_assigned=registration.student_class.class_arm
        ).exists()

        if not is_assigned:
            raise PermissionDenied("You are not assigned to this subject or class.")

        serializer.save()


class ExamScoreDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ExamScoreSerializer
    lookup_field = 'examscore_id'

    def get_permissions(self):
        if self.request.method == "GET":
            return [IsschoolAdmin() or ISstudent() or ISteacher()]
        return [ISteacher()]

    def get_queryset(self):
        user = self.request.user
        school = (
            getattr(user, 'school_admin', None) or
            getattr(user, 'teacher', None) or
            getattr(user, 'student', None)
        ).school

        active_term = Term.objects.filter(school=school, status=True).first()
        if not active_term:
            return ExamScore.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            return ExamScore.objects.filter(registration__in=registrations)

        return ExamScore.objects.filter(registration__term=active_term)

    def perform_update(self, serializer):
        instance = serializer.save()
        # Optionally trigger CA recalculation if needed

    def perform_destroy(self, instance):
        instance.delete()

#=========================================================================================

class ContinuousAssessmentListView(generics.ListAPIView):
    serializer_class = ContinuousAssessmentSerializer
    permission_classes = [ISteacher or ISstudent or IsschoolAdmin]

    def get_queryset(self):
        user = self.request.user
        school = (
            getattr(user, 'school_admin', None) or
            getattr(user, 'teacher', None) or
            getattr(user, 'student', None)
        ).school

        active_term = Term.objects.filter(school=school, status=True).first()
        if not active_term:
            return ContinuousAssessment.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            self._generate_missing_cas(registrations)
            return ContinuousAssessment.objects.filter(registration__in=registrations)

        elif hasattr(user, 'teacher'):
            teacher = user.teacher
            assignments = TeacherAssignment.objects.filter(teacher=teacher)
            subject_classes = [a.subject_class for a in assignments]
            class_arms = [a.class_department_assigned for a in assignments]

            registrations = StudentSubjectRegistration.objects.filter(
                subject_class__in=subject_classes,
                student_class__class_arm__in=class_arms,
                term=active_term
            )
            self._generate_missing_cas(registrations)
            return ContinuousAssessment.objects.filter(registration__in=registrations)

        # SchoolAdmin
        registrations = StudentSubjectRegistration.objects.filter(term=active_term)
        self._generate_missing_cas(registrations)
        return ContinuousAssessment.objects.filter(registration__in=registrations)

    def _generate_missing_cas(self, registrations):
        for reg in registrations:
            obj, _ = ContinuousAssessment.objects.get_or_create(registration=reg)
            obj.ca_total = compute_continuous_assessment(reg)
            obj.save()


class ContinuousAssessmentDetailView(generics.RetrieveAPIView):
    serializer_class = ContinuousAssessmentSerializer
    lookup_field = 'continuous_assessment_id'
    permission_classes = [ISteacher or ISstudent or IsschoolAdmin]

    def get_queryset(self):
        user = self.request.user
        school = (
            getattr(user, 'school_admin', None) or
            getattr(user, 'teacher', None) or
            getattr(user, 'student', None)
        ).school

        active_term = Term.objects.filter(school=school, status=True).first()
        if not active_term:
            return ContinuousAssessment.objects.none()

        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=active_term
            )
            return ContinuousAssessment.objects.filter(registration__in=registrations)

        elif hasattr(user, 'teacher'):
            teacher = user.teacher
            assignments = TeacherAssignment.objects.filter(teacher=teacher)
            subject_classes = [a.subject_class for a in assignments]
            class_arms = [a.class_department_assigned for a in assignments]

            registrations = StudentSubjectRegistration.objects.filter(
                subject_class__in=subject_classes,
                student_class__class_arm__in=class_arms,
                term=active_term
            )
            return ContinuousAssessment.objects.filter(registration__in=registrations)

        return ContinuousAssessment.objects.filter(registration__term=active_term)

#=================================================================================

class ResultListView(generics.ListAPIView):
    serializer_class = ResultSerializer
    permission_classes = [ISteacher or ISstudent or IsschoolAdmin or IsClassTeacher]

    def get_queryset(self):
        user = self.request.user

        # Get school and active academic year
        school = (
            getattr(user, 'school_admin', None) or
            getattr(user, 'teacher', None) or
            getattr(user, 'student', None)
        ).school

        active_year = Year.objects.filter(school=school, status=True).first()
        if not active_year:
            return Result.objects.none()

        # Get term: either by param or fallback to active term
        term_id = self.request.query_params.get('term_id')
        if term_id:
            term = Term.objects.filter(year=active_year, id=term_id).first()
        else:
            term = Term.objects.filter(year=active_year, status=True).first()

        if not term:
            return Result.objects.none()

        # 1️⃣ STUDENT — own results
        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                term=term
            )
            self._generate_results(registrations)
            return Result.objects.filter(registration__in=registrations)

        # 2️⃣ CLASS TEACHER — all students in assigned class arms
        if hasattr(user, 'teacher') and IsClassTeacher().has_permission(self.request, self):
            teacher = user.teacher
            class_arms = ClassTeacher.objects.filter(teacher=teacher).values_list('class_assigned', flat=True)
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__class_arm__in=class_arms,
                term=term
            )
            self._generate_results(registrations)
            return Result.objects.filter(registration__in=registrations)

        # 3️⃣ SUBJECT TEACHER — students in assigned subjects and classes
        if hasattr(user, 'teacher'):
            teacher = user.teacher
            assignments = TeacherAssignment.objects.filter(teacher=teacher)
            subject_classes = [a.subject_class for a in assignments]
            class_arms = [a.class_department_assigned for a in assignments]

            registrations = StudentSubjectRegistration.objects.filter(
                subject_class__in=subject_classes,
                student_class__class_arm__in=class_arms,
                term=term
            )
            self._generate_results(registrations)
            return Result.objects.filter(registration__in=registrations)

        # 4️⃣ SCHOOL ADMIN — all results in active term
        registrations = StudentSubjectRegistration.objects.filter(term=term)
        self._generate_results(registrations)
        return Result.objects.filter(registration__in=registrations)

    def _generate_results(self, registrations):
        for reg in registrations:
            compute_result_for_registration(reg)


class ResultDetailView(generics.RetrieveAPIView):
    serializer_class = ResultSerializer
    lookup_field = 'result_id'
    permission_classes = [ISteacher or ISstudent or IsschoolAdmin or IsClassTeacher]

    def get_queryset(self):
        return Result.objects.all()
#=================================================================================

class AnnualResultListView(generics.ListAPIView):
    serializer_class = AnnualResultSerializer
    permission_classes = [ISstudent or ISteacher or IsschoolAdmin or IsClassTeacher]

    def get_queryset(self):
        user = self.request.user
        school = (
            getattr(user, 'student', None) or
            getattr(user, 'teacher', None) or
            getattr(user, 'school_admin', None)
        ).school

        active_year = Year.objects.filter(school=school, status=True).first()
        if not active_year:
            return AnnualResult.objects.none()

        # Student View
        if hasattr(user, 'student'):
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__student=user.student,
                student_class__class_year__year=active_year
            )
            self._generate_annual_results(registrations)
            return AnnualResult.objects.filter(registration__in=registrations)

        # Class Teacher View
        if hasattr(user, 'teacher') and IsClassTeacher().has_permission(self.request, self):
            class_arms = ClassTeacher.objects.filter(teacher=user.teacher).values_list('class_assigned', flat=True)
            registrations = StudentSubjectRegistration.objects.filter(
                student_class__class_arm__in=class_arms,
                student_class__class_year__year=active_year
            )
            self._generate_annual_results(registrations)
            return AnnualResult.objects.filter(registration__in=registrations)

        # Subject Teacher View
        if hasattr(user, 'teacher'):
            assignments = TeacherAssignment.objects.filter(teacher=user.teacher)
            subject_classes = [a.subject_class for a in assignments]
            class_arms = [a.class_department_assigned for a in assignments]

            registrations = StudentSubjectRegistration.objects.filter(
                subject_class__in=subject_classes,
                student_class__class_arm__in=class_arms,
                student_class__class_year__year=active_year
            )
            self._generate_annual_results(registrations)
            return AnnualResult.objects.filter(registration__in=registrations)

        # SchoolAdmin View
        registrations = StudentSubjectRegistration.objects.filter(
            school=school,
            student_class__class_year__year=active_year
        )
        self._generate_annual_results(registrations)
        return AnnualResult.objects.filter(registration__in=registrations)

    def _generate_annual_results(self, registrations):
        for reg in registrations:
            compute_annual_result(reg)


class AnnualResultDetailView(generics.RetrieveAPIView):
    serializer_class = AnnualResultSerializer
    lookup_field = 'annual_result_id'
    permission_classes = [ISstudent or ISteacher or IsschoolAdmin or IsClassTeacher]

    def get_queryset(self):
        return AnnualResult.objects.all()

#=================================================================================
class ClassTeacherCommentListCreateView(generics.ListCreateAPIView):
    serializer_class = ClassTeacherCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsClassTeacher]

    def get_queryset(self):
        user = self.request.user
        assigned_class = user.classteacher.assigned_class
        return ClassTeacherComment.objects.filter(
            classteacher=user.classteacher,
            term__is_active=True,
            student__student_classes__klass=assigned_class #gght
        )

    def perform_create(self, serializer):
        user = self.request.user
        active_term = Term.objects.get(is_active=True)
        assigned_class = user.classteacher.assigned_class

        student = serializer.validated_data['student']
        skills = serializer.validated_data.pop('skills', None)

        if not skills:
            raise serializers.ValidationError({"skills": "This field is required."})

        if student.student_classes.klass != assigned_class: #gght
            raise serializers.ValidationError("This student is not in your assigned class.")

        generated_comment = "generate_teacher_comment(skills, gender=student.gender)"
        # generated_comment = generate_teacher_comment(skills, gender=student.gender)

        serializer.save(
            classteacher=user.classteacher,
            school=user.classteacher.school,
            term=active_term,
            comment=generated_comment
        )


class ClassTeacherCommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClassTeacherCommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsClassTeacher]
    lookup_field = 'classteacher_comment_id'

    def get_queryset(self):
        user = self.request.user
        return ClassTeacherComment.objects.filter(classteacher=user.classteacher, term__is_active=True)

#============================FULL RESULTS=========================================


class FullStudentResultView(APIView):
    permission_classes = [IsAuthenticated, ISstudent | IsClassTeacher | IsschoolAdmin]

    def get(self, request, student_id):
        year_id = request.query_params.get("year_id")
        term_id = request.query_params.get("term_id")

        student = get_object_or_404(Student, student_id=student_id)
        school = student.school

        visibility = get_object_or_404(ResultVisibilityControl, school=school)

        if term_id and not visibility.term_result_open:
            return Response({"detail": "Term results are not visible yet."}, status=status.HTTP_403_FORBIDDEN)
        if not term_id and not visibility.annual_result_open:
            return Response({"detail": "Annual results are not visible yet."}, status=status.HTTP_403_FORBIDDEN)

        if term_id:
            term = get_object_or_404(Term, term_id=term_id)
            result_data = get_full_term_result_data(student, year_id, term)
            return Response(FullTermResultSerializer(result_data).data)
        else:
            result_data = get_full_annual_result_data(student, year_id)
            return Response(FullAnnualResultSerializer(result_data).data)

#=================================================================================
#================================BROADSHEET=======================================

class BroadsheetView(APIView):
    permission_classes = [IsAuthenticated, IsschoolAdmin | IsClassTeacher]

    def get(self, request):
        year_id = request.query_params.get("year_id")
        term_id = request.query_params.get("term_id")
        class_year_id = request.query_params.get("class_year_id")
        class_arm_id = request.query_params.get("class_arm_id")
        download = request.query_params.get("download")

        if not year_id:
            return Response({"detail": "year_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        year = get_object_or_404(Year, year_id=year_id)
        term = get_object_or_404(Term, term_id=term_id) if term_id else None
        class_year = get_object_or_404(ClassYear, class_year_id=class_year_id) if class_year_id else None
        class_arm = get_object_or_404(ClassDepartment, subject_class_id=class_arm_id) if class_arm_id else None

        data = get_broadsheet_data(
            class_year=class_year,
            class_arm=class_arm,
            year=year,
            term=term
        )

        if download == "excel":
            return export_broadsheet_to_excel(data)

        return Response(data)

#=================================================================================
#=================================================================================
