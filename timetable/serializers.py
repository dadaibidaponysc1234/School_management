from rest_framework import serializers
from django.contrib.auth.models import User
from user_registration.models import (Class,Teacher,Timetable,ClassTimetable,TeacherTimetable)

class TimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Timetable
        fields = '__all__'

class ClassTimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassTimetable
        fields = ['class_arm', 'schedule']

class TeacherTimetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherTimetable
        fields = ['teacher', 'schedule']


class TeacherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['teacher_id', 'first_name', 'middle_name', 'last_name']


class ClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['class_id', 'arm_name']
