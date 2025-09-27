from rest_framework import serializers
from django.contrib.auth.models import User
from user_registration.models import (Class,Teacher,Timetable,ClassTimetable,TeacherTimetable)

class ClassTimetableSerializer(serializers.ModelSerializer):
    class_name = serializers.SerializerMethodField()
    timetable_id = serializers.SerializerMethodField()

    class Meta:
        model = ClassTimetable
        fields = ['timetable_id', 'class_name', 'schedule']

    def get_class_name(self, obj):
        return obj.class_arm.arm_name

    def get_timetable_id(self, obj):
        return str(obj.timetable.timetable_id)


class TeacherTimetableSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    timetable_id = serializers.SerializerMethodField()

    class Meta:
        model = TeacherTimetable
        fields = ['timetable_id', 'teacher_name', 'schedule']

    def get_teacher_name(self, obj):
        return f"{obj.teacher.first_name} {obj.teacher.last_name}"

    def get_timetable_id(self, obj):
        return str(obj.timetable.timetable_id)
