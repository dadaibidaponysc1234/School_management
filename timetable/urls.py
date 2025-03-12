from django.urls import path
from .views import (GenerateTimetableView,ClassArmTimetableView,TeacherTimetableView,
                    TeacherListView, ClassListView)


urlpatterns = [
    path('timetable/generate/', GenerateTimetableView.as_view(), name='generate-timetable'),
    path('timetable/class-arm/', ClassArmTimetableView.as_view(), name='class-arm-timetable'),
    path('timetable/teacher/', TeacherTimetableView.as_view(), name='teacher-timetable'), 

    path('timetable/teachers/', TeacherListView.as_view(), name='teacher-list'),
    path('timetable/classes/', ClassListView.as_view(), name='class-list'),
]

