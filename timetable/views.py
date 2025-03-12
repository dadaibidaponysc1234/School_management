from django.shortcuts import render
from user_registration.models import (Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     Year,Term,ClassYear,Class,Classroom,
                     Student,Teacher,Department,Subject,ClassTeacher,
                     SubjectRegistrationControl,TeacherAssignment,Day,Period,
                     SubjectPeriodLimit,Constraint,AttendancePolicy,FeeCategory,
                     Fee,AssessmentCategory,ExamCategory,ScorePerAssessmentInstance,ExamScore, 
                     ScoreObtainedPerAssessment, ContinuousAssessment,Result,AnnualResult,Notification, 
                     ClassTeacherComment, Attendance, AttendanceFlag, StudentSubjectAssignment,
                     StudentRegistrationPin,StudentClassAndSubjectAssignment,Timetable,ClassTimetable,
                     TeacherTimetable
                     )
from user_registration.permissions import (IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,
                          HasValidPinAndSchoolId)
from .serializers import (TimetableSerializer,ClassTimetableSerializer,TeacherTimetableSerializer,
                          TeacherListSerializer,ClassListSerializer)

from .utils import generate_and_persist_timetable
from rest_framework.views import APIView

import numpy as np
from rest_framework import serializers, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from django.db import transaction
from django.urls import path


class GenerateTimetableView(views.APIView):
    permission_classes = [IsAuthenticated, ISstudent]

    def post(self, request, *args, **kwargs):
        school_id = request.user.schooladmin.school.id
        timetable = generate_and_persist_timetable(school_id)
        return Response({"message": "Timetable generated successfully", "timetable_id": timetable.timetable_id}, status=201)

class ClassArmTimetableView(views.APIView):
    permission_classes = [IsSuperAdmin,]

    def get(self, request, *args, **kwargs):
        class_arm_id = request.query_params.get("class_arm_id")
        if not class_arm_id:
            return Response({"error": "Class arm ID is required."}, status=400)

        try:
            class_timetable = ClassTimetable.objects.get(class_arm_id=class_arm_id)
            serializer = ClassTimetableSerializer(class_timetable)
            return Response(serializer.data, status=200)
        except ClassTimetable.DoesNotExist:
            return Response({"error": "Timetable not found for the specified class arm."}, status=404)

class TeacherTimetableView(views.APIView):
    permission_classes = [IsSuperAdmin,ISteacher]

    def get(self, request, *args, **kwargs):
        teacher_id = request.query_params.get("teacher_id")
        if not teacher_id:
            return Response({"error": "Teacher ID is required."}, status=400)

        try:
            teacher_timetable = TeacherTimetable.objects.get(teacher_id=teacher_id)
            serializer = TeacherTimetableSerializer(teacher_timetable)
            return Response(serializer.data, status=200)
        except TeacherTimetable.DoesNotExist:
            return Response({"error": "Timetable not found for the specified teacher."}, status=404)


class TeacherListView(APIView):
    permission_classes = [IsschoolAdmin]

    def get(self, request, *args, **kwargs):
        school = request.user.schooladmin.school
        teachers = Teacher.objects.filter(school=school)
        serializer = TeacherListSerializer(teachers, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ClassListView(APIView):
    permission_classes = [IsschoolAdmin]

    def get(self, request, *args, **kwargs):
        school = request.user.schooladmin.school
        classes = Class.objects.filter(school=school)
        serializer = ClassListSerializer(classes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
