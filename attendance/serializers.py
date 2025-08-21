from rest_framework import serializers
from user_registration.models import AttendanceSession, AttendanceRecord, Student, StudentClass

class AttendanceRecordSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(read_only=True)
    admission_number = serializers.CharField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.all(), required=False, allow_null=True)

    class Meta:
        model = AttendanceRecord
        fields = ["id", "student", "student_name", "admission_number", "status", "marked_at"]
        read_only_fields = ["id", "student_name", "admission_number", "marked_at"]

class AttendanceSessionSerializer(serializers.ModelSerializer):
    records = AttendanceRecordSerializer(many=True, required=False, read_only=True)
    taken_by_id = serializers.IntegerField(source='taken_by.id', read_only=True)
    taken_by_role = serializers.CharField(read_only=True)

    class Meta:
        model = AttendanceSession
        fields = ["id", "class_obj", "date", "taken_by_id", "taken_by_role", "records"]
        read_only_fields = ["id", "taken_by_id", "taken_by_role"]


class AttendanceSessionListSerializer(serializers.ModelSerializer):
    taken_by_id = serializers.IntegerField(source='taken_by.id', read_only=True)
    taken_by_role = serializers.CharField(read_only=True)

    class Meta:
        model = AttendanceSession
        fields = ["id", "class_obj", "date", "taken_by_id", "taken_by_role"]
        read_only_fields = ["id", "taken_by_id", "taken_by_role"]
