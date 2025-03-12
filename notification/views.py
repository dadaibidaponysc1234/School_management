from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from user_registration.models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationUpdateSerializer
)
from rest_framework.response import Response
from user_registration.permissions import (IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,
                          HasValidPinAndSchoolId)

class NotificationListCreateView(generics.ListCreateAPIView):
    """
    List all notifications and create a new notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Only show notifications for the authenticated user's school
        return Notification.objects.filter(school=self.request.user.schooladmin.school).order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        # Automatically associate the notification with the authenticated user's school
        serializer.save(school=self.request.user.schooladmin.school)

class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin,ISteacher,ISstudent]

    def get_queryset(self):
        # Only allow access to notifications in the authenticated user's school
        return Notification.objects.filter(school=self.request.user.schooladmin.school)

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return NotificationUpdateSerializer
        return NotificationSerializer

class RecentNotificationsView(generics.ListAPIView):
    """
    List the last 5 recently added notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Fetch the last 5 notifications for the authenticated user's school
        return Notification.objects.filter(school=self.request.user.schooladmin.school).order_by('-created_at')[:5]




class TeacherAndEveryoneNotificationView(generics.ListAPIView):
    """
    List notifications for Teachers and Everyone.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin,ISteacher]

    def get_queryset(self):
        return Notification.objects.filter(
            school=self.request.user.schooladmin.school,
            recipient_group__in=['Teacher', 'Everyone']
        ).order_by('-created_at')


class StudentAndEveryoneNotificationView(generics.ListAPIView):
    """
    List notifications for Students and Everyone.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin,ISstudent]

    def get_queryset(self):
        return Notification.objects.filter(
            school=self.request.user.schooladmin.school,
            recipient_group__in=['Student', 'Everyone']
        ).order_by('-created_at')
