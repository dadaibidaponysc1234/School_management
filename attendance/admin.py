from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from user_registration.models import AttendanceSession, AttendanceRecord

class AttendanceSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "class_obj", "date", "taken_by", "taken_by_role")
    search_fields = ("class_obj__arm_name", "date", "taken_by__username")
    list_filter = ("date", "taken_by_role")

class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "student_name", "admission_number", "status", "marked_at")
    search_fields = ("student_name", "admission_number")
    list_filter = ("status", "marked_at")

admin.site.register(AttendanceSession, AttendanceSessionAdmin)
admin.site.register(AttendanceRecord, AttendanceRecordAdmin)