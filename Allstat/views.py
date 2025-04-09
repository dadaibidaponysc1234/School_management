from django.shortcuts import render
from user_registration.models import (User,Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     Year,Term,ClassYear,Class,Classroom,
                     Student,Teacher,Department,Subject,ClassTeacher,
                     TeacherAssignment,Day,Period,
                     SubjectPeriodLimit,Constraint,AttendancePolicy,FeeCategory,
                     Fee,AssessmentCategory,ExamCategory,ScorePerAssessmentInstance,ExamScore, 
                     ScoreObtainedPerAssessment, ContinuousAssessment,Result,AnnualResult,Notification, 
                     ClassTeacherComment, Attendance, AttendanceFlag, StudentSubjectAssignment, SubjectClass,
                     StudentRegistrationPin,SubjectRegistrationControl,StudentClassAndSubjectAssignment,
                     ClassDepartment)


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

class SchoolStatsView(APIView):
    """
    API View to get statistics for teachers and students, including total, male, and female counts.
    """
    permission_classes = [IsAuthenticated]  # Restrict access to authenticated users

    def get(self, request, *args, **kwargs):
        school = request.user.school_admin.school  # Get the current user's school
        
        # Teacher Stats
        total_teachers = Teacher.objects.filter(school=school).count()
        male_teachers = Teacher.objects.filter(school=school, gender='Male').count()
        female_teachers = Teacher.objects.filter(school=school, gender='Female').count()

        # Student Stats
        total_students = Student.objects.filter(school=school).count()
        male_students = Student.objects.filter(school=school, gender='Male').count()
        female_students = Student.objects.filter(school=school, gender='Female').count()

        data = {
            "teachers": {
                "total": total_teachers,
                "male": male_teachers,
                "female": female_teachers
            },
            "students": {
                "total": total_students,
                "male": male_students,
                "female": female_students
            }
        }
        
        return Response(data)
