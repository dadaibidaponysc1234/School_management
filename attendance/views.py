from rest_framework import viewsets, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from user_registration.models import AttendanceSession, AttendanceRecord
from .serializers import AttendanceSessionSerializer, AttendanceRecordSerializer, AttendanceSessionListSerializer
from .permissions import IsSchoolAdminOrTeacher
from user_registration.models import Class, Student, StudentClass, UserRole
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class DefaultPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200

class AttendanceSessionViewSet(viewsets.ModelViewSet):
    queryset = AttendanceSession.objects.all().prefetch_related("records__student")
    serializer_class = AttendanceSessionSerializer
    permission_classes = [IsSchoolAdminOrTeacher]
    pagination_class = DefaultPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        class_id = self.request.query_params.get("class")
        date = self.request.query_params.get("date")
        if class_id:
            queryset = queryset.filter(class_obj_id=class_id)
        if date:
            queryset = queryset.filter(date=date)
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return AttendanceSessionListSerializer
        return AttendanceSessionSerializer

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["class", "date"],
            properties={
                "class": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
                "date": openapi.Schema(type=openapi.TYPE_STRING, format="date"),
                "records": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        required=["student", "status"],
                        properties={
                            "student": openapi.Schema(type=openapi.TYPE_STRING, format="uuid"),
                            "status": openapi.Schema(type=openapi.TYPE_STRING, enum=["present", "absent"]),
                        },
                    ),
                    description="Only send absentees; others default to present.",
                ),
            },
        ),
        responses={201: AttendanceSessionSerializer},
    )
    def create(self, request, *args, **kwargs):
        data = request.data
        class_id = data.get("class")
        date = data.get("date")
        absentees = data.get("records", [])
        if not class_id or not date:
            return Response({"detail": "class and date are required."}, status=400)

        class_obj = get_object_or_404(Class, pk=class_id)
        # Students enrolled in this class via StudentClass mapping
        student_ids = StudentClass.objects.filter(
            class_arm__classes=class_obj #gght
        ).values_list("student_id", flat=True)
        students = Student.objects.filter(pk__in=student_ids)
        absentees_map = {str(r.get("student")): r for r in absentees if r.get("student")}

        with transaction.atomic():
            session, created = AttendanceSession.objects.get_or_create(
                class_obj=class_obj,
                date=date,
                defaults={
                    "taken_by": request.user,
                    "taken_by_role": self._get_user_role(request.user),
                },
            )
            if not created:
                return Response({"detail": "Attendance for this class and date already exists."}, status=400)

            records = []
            now_ts = timezone.now()
            for student in students:
                status_val = absentees_map.get(str(student.pk), {}).get("status", "present")
                if status_val not in ("present", "absent"):
                    status_val = "present"
                records.append(
                    AttendanceRecord(
                        session=session,
                        student=student,
                        student_name=f"{student.first_name} {student.last_name}",
                        admission_number=str(student.admission_number),
                        status=status_val,
                        marked_at=now_ts,
                    )
                )
            AttendanceRecord.objects.bulk_create(records)
            session = AttendanceSession.objects.prefetch_related("records__student").get(pk=session.pk)
            serializer = self.get_serializer(session)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _get_user_role(self, user):
        roles = list(UserRole.objects.filter(user=user).values_list("role__name", flat=True))
        if "School Admin" in roles:
            return "school_admin"
        return "teacher"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class AttendanceRecordViewSet(viewsets.ModelViewSet):
    queryset = AttendanceRecord.objects.all().select_related("student", "session")
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsSchoolAdminOrTeacher]
    pagination_class = DefaultPagination

    def get_queryset(self):
        qs = super().get_queryset()
        session_pk = self.kwargs.get('session_pk')
        if session_pk:
            qs = qs.filter(session_id=session_pk)
        return qs