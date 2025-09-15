from django.urls import path
from .views import LogoutView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from .views import (CustomTokenObtainPairView, RoleListView, SuperAdminRegistrationAPIView,
                    TeacherCreateView,SchoolCreateAPIView,SchoolListAPIView,
                    SchoolDetailAPIView,SuperAdminDetailAPIView,SuperAdminListAPIView,
                    SubscriptionListView, SubscriptionDetailUpdateView,ComplianceVerificationCreateView,
                    ComplianceVerificationDetailView,ComplianceVerificationListView,MessageListView,MessageCreateView,StudentCreateView,
                    StudentBulkCreateView,GenerateRegistrationPinsView, VerifyRegistrationPinView, StudentSelfRegistrationView,
                    StudentUpdateView, StudentListView, TeacherBulkCreateView,TeacherSelfRegistrationView,TeacherUpdateView,
                    TeacherListView,StudentDetailView, TeacherDetailView,DeleteMultipleStudentsView, DeleteMultipleTeachersView,
                    SchoolAdminCreateView,SchoolAdminListView,SchoolAdminDetailView,SchoolAdminUpdateDeleteView,
                    ListRegistrationPinsView)


urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('login/', TokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='token_logout'),

    # Password reset URLs
    path('password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # roles endpoint
    path('roles/', RoleListView.as_view(), name='role-list'),
    
    path('superadmins/create/', SuperAdminRegistrationAPIView.as_view(), name='register-superadmin'),
    path('superadmins/', SuperAdminListAPIView.as_view(), name='superadmin-list'),
    path('superadmins/<uuid:id>/', SuperAdminDetailAPIView.as_view(), name='superadmin-detail'),

    #school endpoint
    path('schools/create/', SchoolCreateAPIView.as_view(), name='school-create'),
    path('schools/', SchoolListAPIView.as_view(), name='school-list'),
    path('schools/<uuid:id>/', SchoolDetailAPIView.as_view(), name='school-detail'),

    
    path('schools/subscriptions/', SubscriptionListView.as_view(), name='subscription-list'),
    path('schools/subscriptions/<uuid:subscription_id>/', SubscriptionDetailUpdateView.as_view(), name='subscription-detail'),
    
    path('schools/compliance-verification/create/', ComplianceVerificationCreateView.as_view(), name='compliance-verification-create'),
    path('schools/compliance-verification/', ComplianceVerificationListView.as_view(), name='compliance-verification-list'),
    path('schools/compliance-verification/<uuid:school_id>/', ComplianceVerificationDetailView.as_view(), name='compliance-verification-detail'),
    
    path('messages/send/', MessageCreateView.as_view(), name='message-create'),
    path('messages/inbox/', MessageListView.as_view(), name='message-list'),
    
    
    path('school_admin/create/', SchoolAdminCreateView.as_view(), name='school-admin-create'),
    path('school_admin/', SchoolAdminListView.as_view(), name='school-admin-list'),
    path('school_admin/<uuid:schooladmin_id>/', SchoolAdminDetailView.as_view(), name='school-admin-detail'),
    path('school_admin/<uuid:schooladmin_id>/update/', SchoolAdminUpdateDeleteView.as_view(), name='school-admin-update-delete'),

    path('registration-pins/generate/', GenerateRegistrationPinsView.as_view(), name='generate-registration-pins'),
    path('registration/verify/', VerifyRegistrationPinView.as_view(), name='verify-registration-pin'),
    # List all generated registration pins for a school
    path('registration-pins/', ListRegistrationPinsView.as_view(), name='list-registration-pins'),

    path('students/create/', StudentCreateView.as_view(), name='student-create'),
    path('students/bulk_create/', StudentBulkCreateView.as_view(), name='student-bulk-create'),
    path('students/self-register/', StudentSelfRegistrationView.as_view(), name='student-self-register'),
    path('students/update/', StudentUpdateView.as_view(), name='student-update'),
    path('students/list/', StudentListView.as_view(), name='student-list'),
    path('students/detail/<uuid:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/delete-multiple/', DeleteMultipleStudentsView.as_view(), name='delete-multiple-students'),
    
    path('teachers/create/', TeacherCreateView.as_view(), name='teacher-create'),
    path('teachers/bulk_create/', TeacherBulkCreateView.as_view(), name='teacher-bulk-create'),
    path('teachers/self-register/', TeacherSelfRegistrationView.as_view(), name='teacher-self-register'),
    path('teachers/update/', TeacherUpdateView.as_view(), name='teacher-update'),
    path('teachers/list/', TeacherListView.as_view(), name='teacher-list'),
    path('teachers/detail/<uuid:pk>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('teachers/delete-multiple/', DeleteMultipleTeachersView.as_view(), name='delete-multiple-teachers'),
]
