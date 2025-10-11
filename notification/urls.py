from django.urls import path
from .views import (
    NotificationListCreateView,
    NotificationDetailView,
    RecentNotificationsView,
    TeacherAndEveryoneNotificationView,
    StudentAndEveryoneNotificationView,
)

urlpatterns = [
    path('notifications/', NotificationListCreateView.as_view(), name='notification-list-create'),
    path('notifications/<uuid:notification_id>/', NotificationDetailView.as_view(), name='notification-detail'),
    path('notifications/recent/', RecentNotificationsView.as_view(), name='recent-notifications'),

    path('notifications/teacher-and-everyone/', TeacherAndEveryoneNotificationView.as_view(), name='teacher-and-everyone-notifications'),
    path('notifications/student-and-everyone/', StudentAndEveryoneNotificationView.as_view(), name='student-and-everyone-notifications'),
]
