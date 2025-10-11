from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from user_registration.models import Notification
from .serializers import (
    NotificationSerializer,
    NotificationCreateSerializer,
    NotificationUpdateSerializer
)
from rest_framework.response import Response
from user_registration.permissions import (IsSchoolAdminOrIsTeacher, IsSchoolAdminOrIsTeacherOrIsStudent, IsSuperAdmin,IsschoolAdmin,ISteacher,
                          ISstudent,IsSuperAdminOrSchoolAdmin,
                          HasValidPinAndSchoolId, SchoolAdminOrIsClassTeacherOrISstudent)
from rest_framework.exceptions import PermissionDenied

class NotificationListCreateView(generics.ListCreateAPIView):
    """
    List all notifications and create a new notification.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Only show notifications for the authenticated user's school
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Notification.objects.none()
        return Notification.objects.filter(school=self.request.user.school_admin.school).order_by('-created_at')

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NotificationCreateSerializer
        return NotificationSerializer

    def perform_create(self, serializer):
        # Automatically associate the notification with the authenticated user's school
        serializer.save(school=self.request.user.school_admin.school)


# class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     Retrieve, update, or delete a notification.
#     - Read: any authenticated user in the same school
#     - Update/Delete: SchoolAdmin OR the creator (owner)
#     """
#     serializer_class = NotificationSerializer
#     permission_classes = [IsAuthenticated, (ISteacher | ISstudent | IsschoolAdmin)]
#     lookup_field = "notification_id"  # change to "pk" if you use default int PKs
#     lookup_url_kwarg = "notification_id"

#     def _current_school(self, user):
#         """Get the user's school regardless of role."""
#         if hasattr(user, "school_admin") and user.school_admin:
#             return user.school_admin.school
#         if hasattr(user, "teacher") and user.teacher:
#             return user.teacher.school
#         if hasattr(user, "student") and user.student:
#             return user.student.school
#         return None

#     def get_queryset(self):
#         if getattr(self, 'swagger_fake_view', False):
#             return Notification.objects.none()

#         user = getattr(self.request, "user", None)
#         if not (user and user.is_authenticated):
#             return Notification.objects.none()

#         school = self._current_school(user)  # your helper
#         if not school:
#             return Notification.objects.none()

#         # ✅ Only select_related fields that exist on the model
#         return (
#             Notification.objects
#         .filter(school=school)
#         .select_related("school", "recipient_user")  # remove "created_by"
#         )


#     def get_serializer_class(self):
#         if self.request.method in ("PUT", "PATCH"):
#             return NotificationUpdateSerializer
#         return NotificationSerializer

#     def perform_update(self, serializer):
#         obj = self.get_object()
#         user = self.request.user
#         same_school = obj.school_id == getattr(self._current_school(user), "id", None)
#         is_admin = hasattr(user, "school_admin") and user.school_admin is not None
#         is_owner = obj.created_by_id == getattr(user, "id", None)

#         if not (same_school and (is_admin or is_owner)):
#             raise PermissionDenied("You do not have permission to edit this notification.")
#         serializer.save()

#     def perform_destroy(self, instance):
#         user = self.request.user
#         same_school = instance.school_id == getattr(self._current_school(user), "id", None)
#         is_admin = hasattr(user, "school_admin") and user.school_admin is not None
#         is_owner = instance.created_by_id == getattr(user, "id", None)

#         if not (same_school and (is_admin or is_owner)):
#             raise PermissionDenied("You do not have permission to delete this notification.")
#         instance.delete()



class NotificationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated, (ISteacher | ISstudent | IsschoolAdmin)]
    lookup_field = "notification_id"
    lookup_url_kwarg = "notification_id"  # match your URL kwarg

    def _current_school(self, user):
        for rel in ("school_admin", "teacher", "student"):
            if hasattr(user, rel) and getattr(user, rel):
                return getattr(user, rel).school
        return None

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Notification.objects.none()
        u = self.request.user
        if not (u and u.is_authenticated):
            return Notification.objects.none()
        school = self._current_school(u)
        return Notification.objects.filter(school=school).select_related("school", "recipient_user")

    def get_serializer_class(self):
        return NotificationUpdateSerializer if self.request.method in ("PUT", "PATCH") else NotificationSerializer

    def _is_admin_same_school(self, user, school_id):
        return (
            hasattr(user, "school_admin") and user.school_admin
            and user.school_admin.school_id == school_id
        )

    def perform_update(self, serializer):
        obj = self.get_object()
        if not self._is_admin_same_school(self.request.user, obj.school_id):
            raise PermissionDenied("Only School Admins can edit notifications.")
        serializer.save()  # <-- no return here

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(
            {"message": "Notification updated successfully.", "data": serializer.data},
            status=status.HTTP_200_OK
        )

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def perform_destroy(self, instance):
        if not self._is_admin_same_school(self.request.user, instance.school_id):
            raise PermissionDenied("Only School Admins can delete notifications.")
        instance.delete()  # <-- no return here

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Notification deleted successfully."},
            status=status.HTTP_200_OK
        )

    # def perform_update(self, serializer):
    #     obj = self.get_object()
    #     if not self._is_admin_same_school(self.request.user, obj.school_id):
    #         raise PermissionDenied("Only School Admins can edit notifications.")
    #     serializer.save()
    #     return Response(
    #         {"message": "Notification updated successfully.", "data": serializer.data},
    #         status=status.HTTP_200_OK
    #     )

    # def perform_destroy(self, instance):
    #     if not self._is_admin_same_school(self.request.user, instance.school_id):
    #         raise PermissionDenied("Only School Admins can delete notifications.")
    #     instance.delete()
    #     return Response(
    #         {"message": "Notification deleted successfully."},
    #         status=status.HTTP_200_OK
    #     )


class RecentNotificationsView(generics.ListAPIView):
    """
    List the last 5 recently added notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsschoolAdmin]

    def get_queryset(self):
        # Fetch the last 5 notifications for the authenticated user's school
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Notification.objects.none()
        return Notification.objects.filter(school=self.request.user.school_admin.school).order_by('-created_at')[:5]




class TeacherAndEveryoneNotificationView(generics.ListAPIView):
    """
    List notifications for Teachers and Everyone.
    """
    serializer_class = NotificationSerializer
    # School Admins or Teachers can view
    permission_classes = [IsSchoolAdminOrIsTeacher]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Notification.objects.none()
        return Notification.objects.filter(
            school=self.request.user.school_admin.school,
            recipient_group__in=['Teacher', 'Everyone']
        ).order_by('-created_at')


class StudentAndEveryoneNotificationView(generics.ListAPIView):
    """
    List notifications for Students and Everyone.
    """
    serializer_class = NotificationSerializer
    # School Admins or Students can view
    permission_classes = [IsSchoolAdminOrIsTeacherOrIsStudent]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False) or not getattr(self, 'request', None) or not getattr(self.request, 'user', None) or not getattr(self.request.user, 'is_authenticated', False) or not hasattr(self.request.user, 'school_admin'):
            return Notification.objects.none()
        return Notification.objects.filter(
            school=self.request.user.school_admin.school,
            recipient_group__in=['Student', 'Everyone']
        ).order_by('-created_at')
