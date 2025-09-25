from django.urls import path
from .views import (ComplianceVerificationMetricsView, SuperAdminMetricsView, YearListCreateView, YearDetailView, TermListCreateView, 
                    TermDetailView,    ClassYearListCreateView, ClassYearDetailView,
                    ClassListCreateView, ClassDetailView,ClassroomListCreateView, ClassroomDetailView,
                    DepartmentListCreateView, DepartmentDetailView,SubjectListCreateView, SubjectDetailView,
                    ClassTeacherListCreateView,TeacherAssignmentListCreateView, 
                    TeacherAssignmentDetailView,BulkClassTeacherCreateView,ClassTeacherListView,ClassTeacherUpdateDeleteView,DeleteMultipleClassTeachersView,
                    SubjectClassListCreateView, SubjectClassDetailView, ClassDepartmentListCreateView,
                    ClassDepartmentDetailView, StudentClassListView, StudentClassUpdateView,StudentSubjectRegistrationListCreateView,
                    StudentSubjectRegistrationDetailView, SubjectRegistrationControlView,UpdateSubjectRegistrationStatusView,
                    BulkSubjectClassAssignmentView,

                    )
#BulkTeacherAssignmentCreateView,

urlpatterns = [
    path('school_config/years/', YearListCreateView.as_view(), name='year-list-create'),
    path('school_config/years/<uuid:pk>/', YearDetailView.as_view(), name='year-detail'),

    path('school_config/terms/', TermListCreateView.as_view(), name='term-list-create'),
    path('school_config/terms/<uuid:pk>/', TermDetailView.as_view(), name='term-detail'),

    path('school_config/class_years/', ClassYearListCreateView.as_view(), name='class-year-list-create'),
    path('school_config/class_years/<uuid:pk>/', ClassYearDetailView.as_view(), name='class-year-detail'),

    path('school_config/classes/', ClassListCreateView.as_view(), name='class-list-create'),
    path('school_config/classes/<uuid:pk>/', ClassDetailView.as_view(), name='class-detail'),

    path('school_config/classrooms/', ClassroomListCreateView.as_view(), name='classroom-list-create'),
    path('school_config/classrooms/<uuid:pk>/', ClassroomDetailView.as_view(), name='classroom-detail'),

    path('school_config/departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('school_config/departments/<uuid:pk>/', DepartmentDetailView.as_view(), name='department-detail'),

    path('school_config/subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('school_config/subjects/<uuid:pk>/', SubjectDetailView.as_view(), name='subject-detail'),


    
    path('assignments/class_teachers/bulk_create/', BulkClassTeacherCreateView.as_view(), name='class-teacher-bulk-create'),

    # List All Class-Teacher Assignments
    path('assignments/class_teachers/', ClassTeacherListView.as_view(), name='class-teacher-list'),

    # Update a Single Class-Teacher Assignment
    path('assignments/class_teachers/<uuid:pk>/', ClassTeacherUpdateDeleteView.as_view(), name='class-teacher-update'),

    # Delete Multiple Class-Teacher Assignments
    path('assignments/class_teachers/delete-multiple/', DeleteMultipleClassTeachersView.as_view(), name='delete-multiple-class-teachers'),


    path('assignments/class_departments/', ClassDepartmentListCreateView.as_view(), name='class_department_list_create'),
    path('assignments/class_departments/<uuid:subject_class_id>/', ClassDepartmentDetailView.as_view(), name='class_department_detail'),
    
    path('assignments/subject_department/', SubjectClassListCreateView.as_view(), name='subject-class-list-create'),
    path('assignments/subject_department_bulk/', BulkSubjectClassAssignmentView.as_view(), name='subject-class-bulk-assign'),
    path('assignments/subject_department/<uuid:subject_class_id>/', SubjectClassDetailView.as_view(), name='subject-class-detail'),
    
    path('assignments/teacher_assignments/', TeacherAssignmentListCreateView.as_view(), name='teacher-assignment-list-create'),
    path('assignments/teacher_assignments/<uuid:pk>/', TeacherAssignmentDetailView.as_view(), name='teacher-assignment-detail'),

    path('assignments/student-classes/', StudentClassListView.as_view(), name='student-class-list'),
    path('assignments/student-classes/<uuid:student_class_id>/update/', StudentClassUpdateView.as_view(), name='student-class-update'),

    path('assignments/student-subject-registrations/', StudentSubjectRegistrationListCreateView.as_view(), name='student-subject-registration-list-create'),
    path('assignments/student-subject-registrations/<uuid:registration_id>/', StudentSubjectRegistrationDetailView.as_view(), name='student-subject-registration-detail'),

    path('assignments/registration-control/', SubjectRegistrationControlView.as_view(), name='registration-control'),
    path('assignments/subject-registration-status/<uuid:registration_id>/', UpdateSubjectRegistrationStatusView.as_view(), name='update-subject-registration-status'),

    path('metrics/superadmin/', SuperAdminMetricsView.as_view(), name="superadmin-metrics"),
    path("metrics/compliance-verification/", ComplianceVerificationMetricsView.as_view(), name="compliance-metrics"),
]
