from django.contrib import admin
from .models import (Role, UserRole, SuperAdmin, School,Subscription,
                     ComplianceVerification,Message,SchoolAdmin,
                     Year,Term,ClassYear,Class,Classroom,
                     Student,Teacher,Department,Subject,ClassTeacher,
                     SubjectRegistrationControl,TeacherAssignment,AttendancePolicy,FeeCategory,
                     Fee,AssessmentCategory,ScorePerAssessmentInstance,ExamScore, 
                     ScoreObtainedPerAssessment, ContinuousAssessment,Result,AnnualResult,Notification, 
                     ClassTeacherComment,
                     StudentRegistrationPin,Timetable,ClassTimetable,
                     TeacherTimetable,SubjectClass,ClassDepartment,StudentClass,
                    StudentSubjectRegistration,ResultConfiguration, AnnualResultWeightConfig,
                    GradingSystem,Day,Period,SubjectPeriodLimit,Constraint
                     )
# (AssessmentCategory,ResultConfiguration, AnnualResultWeightConfig,
# GradingSystem,ScorePerAssessmentInstance,ScoreObtainedPerAssessment,
# ExamScore, ContinuousAssessment,Result, AnnualResult
# )
# admin.site.register(CustomUser)
admin.site.register(Day)
admin.site.register(Period)
admin.site.register(SubjectPeriodLimit)
admin.site.register(Constraint)

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
admin.site.register(StudentClass)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(Department)
admin.site.register(Subject)
admin.site.register(ClassTeacher)
admin.site.register(SubjectRegistrationControl)
admin.site.register(TeacherAssignment)
admin.site.register(AttendancePolicy)
admin.site.register(FeeCategory)
admin.site.register(Fee)
admin.site.register(AssessmentCategory)
# admin.site.register(ExamCategory)
admin.site.register(ScorePerAssessmentInstance)
admin.site.register(ExamScore)
admin.site.register(ScoreObtainedPerAssessment)
admin.site.register(ContinuousAssessment)
admin.site.register(Result)
admin.site.register(AnnualResult)
admin.site.register(Notification)
admin.site.register(ClassTeacherComment)
# admin.site.register(StudentSubjectAssignment)
admin.site.register(StudentRegistrationPin)
admin.site.register(StudentSubjectRegistration)
admin.site.register(Timetable)
admin.site.register(ClassTimetable)
admin.site.register(TeacherTimetable)
admin.site.register(SubjectClass)
admin.site.register(ClassDepartment)
admin.site.register(ResultConfiguration)
admin.site.register(AnnualResultWeightConfig)
admin.site.register(GradingSystem)

 
