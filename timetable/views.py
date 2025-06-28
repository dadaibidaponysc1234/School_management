# views.py for the timetable module

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_registration.models import Class, Teacher, ClassTimetable, TeacherTimetable
from .serializers import ClassTimetableSerializer, TeacherTimetableSerializer
from .utils import generate_and_persist_timetable
from user_registration.permissions import IsschoolAdmin, IsSuperAdmin, ISteacher


class GenerateTimetableView(APIView):
    permission_classes = [IsAuthenticated, IsschoolAdmin]

    def post(self, request, *args, **kwargs):
        school_id = request.user.school_admin.school.id
        days = request.data.get("days")
        periods_per_day = request.data.get("periods_per_day")
        teacher_unavailability = request.data.get("teacher_unavailability", {})
        constraints = request.data.get("constraints", {})

        timetable = generate_and_persist_timetable(
            school_id=school_id,
            days=days,
            periods_per_day=periods_per_day,
            teacher_unavailability=teacher_unavailability,
            constraints=constraints
        )

        return Response({
            "message": "Timetable generated successfully",
            "timetable_id": str(timetable.timetable_id)
        }, status=status.HTTP_201_CREATED)


class ClassTimetableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        class_arm_id = request.query_params.get("class_arm_id")
        if not class_arm_id:
            return Response({"error": "class_arm_id is required"}, status=400)

        try:
            class_timetable = ClassTimetable.objects.get(class_arm_id=class_arm_id)
        except ClassTimetable.DoesNotExist:
            return Response({"error": "Timetable not found for this class"}, status=404)

        user = request.user
        is_admin = hasattr(user, 'school_admin') and user.school_admin.school.id == class_timetable.class_arm.school.id
        is_student = hasattr(user, 'student') and user.student.school.id == class_timetable.class_arm.school.id

        if is_student:
            student = user.student
            student_class_ids = student.subject_class.values_list("class_arm__classes__class_id", flat=True)
            if class_timetable.class_arm.class_id not in student_class_ids:
                return Response({"error": "You do not have permission to view this class timetable."}, status=403)

        if not (is_admin or is_student):
            return Response({"error": "Unauthorized"}, status=403)

        serializer = ClassTimetableSerializer(class_timetable)
        return Response(serializer.data, status=200)


class TeacherTimetableView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        teacher_id = request.query_params.get("teacher_id")
        if not teacher_id:
            return Response({"error": "teacher_id is required"}, status=400)

        try:
            teacher_timetable = TeacherTimetable.objects.get(teacher_id=teacher_id)
        except TeacherTimetable.DoesNotExist:
            return Response({"error": "Timetable not found for this teacher"}, status=404)

        user = request.user
        is_superadmin = hasattr(user, 'super_admin')
        is_teacher = hasattr(user, 'teacher') and str(user.teacher.teacher_id) == teacher_id

        if not (is_teacher or is_superadmin):
            return Response({"error": "Unauthorized"}, status=403)

        serializer = TeacherTimetableSerializer(teacher_timetable)
        return Response(serializer.data, status=200)
