from rest_framework.permissions import BasePermission
from user_registration.permissions import IsschoolAdmin, ISteacher


class IsSchoolAdminOrTeacher(BasePermission):
    def has_permission(self, request, view):
        return IsschoolAdmin().has_permission(request, view) or ISteacher().has_permission(request, view)
