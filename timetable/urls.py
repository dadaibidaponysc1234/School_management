from django.urls import path
from .views import GenerateTimetableView, ClassTimetableView, TeacherTimetableView

urlpatterns = [
    path('generate-timetable/', GenerateTimetableView.as_view(), name='generate-timetable'),
    path('class-timetable/', ClassTimetableView.as_view(), name='class-timetable'),
    path('teacher-timetable/', TeacherTimetableView.as_view(), name='teacher-timetable'),
]
