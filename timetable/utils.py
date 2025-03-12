from user_registration.models import (Role, UserRole, SuperAdmin, School,Subscription,
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
from django.db import transaction

# Utility Functions
def fetch_data(school_id):
    school = School.objects.get(id=school_id)

    classes = list(Class.objects.filter(school=school).values_list("name", flat=True))
    subjects = {
        cls.name: list(cls.subject_set.filter(school=school).values_list("name", flat=True))
        for cls in Class.objects.filter(school=school)
    }
    teachers = {
        teacher.user.username: {
            "subjects": {subject.name: list(subject.class_set.values_list("name", flat=True)) 
                         for subject in teacher.subjects.filter(school=school)},
            "availability": teacher.availability,
        }
        for teacher in Teacher.objects.filter(school=school)
    }
    days = list(Day.objects.filter(school=school).values_list("name", flat=True))
    periods = list(Period.objects.filter(school=school).values_list("start_time", "end_time"))
    subject_period_limits = {
        limit.subject.name: {
            "periods_per_week": limit.periods_per_week,
            "double_periods": limit.double_periods,
        }
        for limit in SubjectPeriodLimit.objects.filter(subject__school=school)
    }
    constraints = Constraint.objects.filter(school=school).first()

    return classes, subjects, teachers, constraints, days, periods, subject_period_limits

def generate_and_persist_timetable(school_id):
    """
    Generate and persist the timetable in the database.
    """
    classes, subjects, teachers, constraints, days, periods, subject_period_limits = fetch_data(school_id)
    timetable = generate_timetable_logic(classes, subjects, teachers, constraints, days, periods, subject_period_limits)

    with transaction.atomic():
        school = School.objects.get(id=school_id)
        timetable_record = Timetable.objects.create(school=school)

        for class_arm, schedule in timetable.items():
            class_obj = Class.objects.get(arm_name=class_arm, school=school)
            ClassTimetable.objects.create(
                timetable=timetable_record,
                class_arm=class_obj,
                schedule=schedule,
            )

        teacher_schedules = {}
        for cls, days_schedule in timetable.items():
            for day, periods_schedule in days_schedule.items():
                for period, subject in periods_schedule.items():
                    if subject:
                        for teacher_name in teachers.keys():
                            if teacher_name in subject:
                                if teacher_name not in teacher_schedules:
                                    teacher_schedules[teacher_name] = {}
                                if day not in teacher_schedules[teacher_name]:
                                    teacher_schedules[teacher_name][day] = {}
                                teacher_schedules[teacher_name][day][period] = f"{subject} ({cls})"

        for teacher_name, schedule in teacher_schedules.items():
            teacher_obj = Teacher.objects.get(user__username=teacher_name, school=school)
            TeacherTimetable.objects.create(
                timetable=timetable_record,
                teacher=teacher_obj,
                schedule=schedule,
            )

    return timetable_record

def generate_timetable_logic(classes, subjects, teachers, constraints, days, periods, subject_period_limits):
    """
    Simulated logic for timetable generation (e.g., using Ant Colony Optimization).
    """
    timetable = {}
    for cls in classes:
        timetable[cls] = {
            day: {period: None for period in periods} for day in days
        }

    # Example logic to fill the timetable (replace with actual logic)
    for cls in classes:
        for day in days:
            for period in periods:
                if subjects[cls]:
                    timetable[cls][day][period] = subjects[cls][0]  # Assign the first subject

    return timetable
