from django.contrib import admin
from .models import (Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     Year,Term,ClassYear,Class,Classroom,
                     Student,Teacher,Department,Subject,ClassTeacher,
                     SubjectRegistrationControl,TeacherAssignment,Day,Period,
                     SubjectPeriodLimit,Constraint,AttendancePolicy,FeeCategory,
                     Fee,AssessmentCategory,ExamCategory,ScorePerAssessmentInstance,ExamScore, 
                     ScoreObtainedPerAssessment, ContinuousAssessment,Result,AnnualResult,Notification, 
                     ClassTeacherComment, Attendance, AttendanceFlag, StudentSubjectAssignment,
                     StudentRegistrationPin,StudentClassAndSubjectAssignment,Timetable,ClassTimetable,
                     TeacherTimetable
                     )

# admin.site.register(CustomUser)
admin.site.register(Role)
admin.site.register(UserRole)
admin.site.register(SuperAdmin)
admin.site.register(School)
admin.site.register(Subscription)
admin.site.register(ComplianceVerification)
admin.site.register(Message)
admin.site.register(SchoolAdmin)
admin.site.register(Year)
admin.site.register(Term)
admin.site.register(ClassYear)
admin.site.register(Class)
admin.site.register(Classroom)
# admin.site.register(Parent)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(ClassTeacher)
admin.site.register(SubjectRegistrationControl)
admin.site.register(TeacherAssignment)
admin.site.register(Day)
admin.site.register(Period)
admin.site.register(SubjectPeriodLimit)
admin.site.register(Constraint)
admin.site.register(AttendancePolicy)
admin.site.register(FeeCategory)
admin.site.register(Fee)
admin.site.register(AssessmentCategory)
admin.site.register(ExamCategory)
admin.site.register(ScorePerAssessmentInstance)
admin.site.register(ExamScore)
admin.site.register(ScoreObtainedPerAssessment)
admin.site.register(ContinuousAssessment)
admin.site.register(Result)
admin.site.register(AnnualResult)
admin.site.register(Notification)
admin.site.register(ClassTeacherComment)
admin.site.register(Attendance)
admin.site.register(AttendanceFlag)
admin.site.register(StudentSubjectAssignment)
admin.site.register(StudentRegistrationPin)
admin.site.register(StudentClassAndSubjectAssignment)
admin.site.register(Timetable)
admin.site.register(ClassTimetable)
admin.site.register(TeacherTimetable)

 
