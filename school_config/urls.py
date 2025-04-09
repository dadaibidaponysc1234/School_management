from django.urls import path
from .views import (YearListCreateView, YearDetailView, TermListCreateView, 
                    TermDetailView,    ClassYearListCreateView, ClassYearDetailView,
                    ClassListCreateView, ClassDetailView,ClassroomListCreateView, ClassroomDetailView,
                    DepartmentListCreateView, DepartmentDetailView,SubjectListCreateView, SubjectDetailView,
                    ClassTeacherListCreateView,TeacherAssignmentListCreateView, 
                    TeacherAssignmentDetailView,StudentClassAndSubjectAssignmentListCreateView,
                    StudentClassAndSubjectAssignmentDetailView,SubjectRegistrationControlView,
                    SubjectRegistrationControlListView,SubjectApprovalView,MultipleSubjectApprovalView,
                    BulkClassTeacherCreateView,ClassTeacherListView,ClassTeacherUpdateView,DeleteMultipleClassTeachersView,
                    SubjectClassListCreateView, SubjectClassDetailView, ClassDepartmentListCreateView,
                    ClassDepartmentDetailView, StudentClassListCreateView, StudentClassDetailView

                    )
#BulkTeacherAssignmentCreateView,

urlpatterns = [
    path('years/', YearListCreateView.as_view(), name='year-list-create'),
    path('years/<uuid:pk>/', YearDetailView.as_view(), name='year-detail'),

    path('terms/', TermListCreateView.as_view(), name='term-list-create'),
    path('terms/<uuid:pk>/', TermDetailView.as_view(), name='term-detail'),

    path('class_years/', ClassYearListCreateView.as_view(), name='class-year-list-create'),
    path('class_years/<uuid:pk>/', ClassYearDetailView.as_view(), name='class-year-detail'),

    path('classes/', ClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<uuid:pk>/', ClassDetailView.as_view(), name='class-detail'),

    path('classrooms/', ClassroomListCreateView.as_view(), name='classroom-list-create'),
    path('classrooms/<uuid:pk>/', ClassroomDetailView.as_view(), name='classroom-detail'),

    path('departments/', DepartmentListCreateView.as_view(), name='department-list-create'),
    path('departments/<uuid:pk>/', DepartmentDetailView.as_view(), name='department-detail'),

    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<uuid:pk>/', SubjectDetailView.as_view(), name='subject-detail'),

###################################################################################################    
    # path('class_teachers/', ClassTeacherListCreateView.as_view(), name='class-teacher-list-create'),
    # path('class_teachers/<uuid:pk>/', ClassTeacherDetailView.as_view(), name='class-teacher-detail'),
    
    # Bulk Assign Multiple Teachers to Multiple Classes
    path('class_teachers/bulk_create/', BulkClassTeacherCreateView.as_view(), name='class-teacher-bulk-create'),

    # List All Class-Teacher Assignments
    path('class_teachers/', ClassTeacherListView.as_view(), name='class-teacher-list'),

    # Update a Single Class-Teacher Assignment
    path('class_teachers/<uuid:pk>/', ClassTeacherUpdateView.as_view(), name='class-teacher-update'),

    # Delete Multiple Class-Teacher Assignments
    path('class_teachers/delete-multiple/', DeleteMultipleClassTeachersView.as_view(), name='delete-multiple-class-teachers'),

###################################################################################################    
    path('class_departments/', ClassDepartmentListCreateView.as_view(), name='class_department_list_create'),
    path('class_departments/<uuid:subject_class_id>/', ClassDepartmentDetailView.as_view(), name='class_department_detail'),
    
    path('subject_classes/', SubjectClassListCreateView.as_view(), name='subject-class-list-create'),
    path('subject_classes/<uuid:subject_class_id>/', SubjectClassDetailView.as_view(), name='subject-class-detail'),
    
    path('teacher_assignments/', TeacherAssignmentListCreateView.as_view(), name='teacher-assignment-list-create'),
    path('teacher_assignments/<uuid:pk>/', TeacherAssignmentDetailView.as_view(), name='teacher-assignment-detail'),
####################################################################################################
    path('student_classes/', StudentClassListCreateView.as_view(), name='studentclass-list-create'),
    path('student_classes/<uuid:student_class_id>/', StudentClassDetailView.as_view(), name='studentclass-detail'),

####################################################################################################
     # Student Assignments
    path('subject-registration/', StudentClassAndSubjectAssignmentListCreateView.as_view(), name='student-subject-registration'),
    path('subject-registration/<uuid:pk>/', StudentClassAndSubjectAssignmentDetailView.as_view(), name='subject-registration-detail'),

    # Subject Registration Control
    path('subject-registration/control/', SubjectRegistrationControlView.as_view(), name='subject-registration-control'),
    path('subject-registration/control/list/', SubjectRegistrationControlListView.as_view(), name='subject-registration-control-list'),

    path('subject-registration/approval/', SubjectApprovalView.as_view(), name='subject-approval'),
    path('subject-registration/multiple-approval/', MultipleSubjectApprovalView.as_view(), name='multiple-subject-approval'),
]
