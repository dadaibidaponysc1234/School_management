from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import AttendanceSessionViewSet, AttendanceRecordViewSet

router = DefaultRouter()
router.register(r'sessions', AttendanceSessionViewSet, basename='attendance-session')

session_records_router = NestedDefaultRouter(router, r'sessions', lookup='session')
session_records_router.register(r'records', AttendanceRecordViewSet, basename='attendance-session-records')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(session_records_router.urls)),
]
