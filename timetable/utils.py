# utils.py for the timetable module

from collections import defaultdict
import random
from django.db import transaction
from user_registration.models import (
    School, Class, Teacher, ClassTimetable, TeacherTimetable, Timetable, TeacherAssignment, SubjectPeriodLimit
)


# STEP 1: Fetch data from models
def fetch_data(school_id, days, periods_per_day, teacher_unavailability, constraints):
    school = School.objects.get(id=school_id)
    class_objs = Class.objects.filter(school=school)
    classes = [cls.arm_name for cls in class_objs]
    subjects = {cls.arm_name: set() for cls in class_objs}
    teacher_assignments = TeacherAssignment.objects.filter(school=school)
    teachers = {}

    for assign in teacher_assignments:
        if not assign.teacher:
            continue
        teacher_name = assign.teacher.user.username
        subject_name = assign.subject_class.subject.name
        class_arm = assign.class_department_assigned.classes.arm_name
        subjects[class_arm].add(subject_name)
        if teacher_name not in teachers:
            teachers[teacher_name] = {"subjects": {}, "availability": {}}
        teachers[teacher_name]["subjects"].setdefault(subject_name, set()).add(class_arm)

    subjects = {cls: list(subs) for cls, subs in subjects.items()}

    for teacher_name in teachers:
        teachers[teacher_name]["availability"] = {}
        for day in days:
            unavailable = teacher_unavailability.get(teacher_name, {}).get(day, [])
            teachers[teacher_name]["availability"][day] = (
                [] if "all" in unavailable else [p for p in periods_per_day[day] if p not in unavailable]
            )

    subject_period_limits = {cls.arm_name: {} for cls in class_objs}
    for limit in SubjectPeriodLimit.objects.filter(school=school):
        subject = limit.subject.name
        for cls in class_objs:
            if TeacherAssignment.objects.filter(subject__subject=limit.subject, class_assigned__classes=cls).exists():
                subject_period_limits[cls.arm_name][subject] = {
                    "periods_per_week": limit.periods_per_week,
                    "double_periods": limit.double_periods
                }

    return classes, subjects, teachers, constraints, days, periods_per_day, subject_period_limits


# STEP 2: ACO algorithm for timetable generation
class ACOTimetableGenerator:
    def __init__(self, classes, subjects, teachers, constraints, days, periods_per_day, subject_period_limits,
                 num_ants=10, num_iterations=30, alpha=1, beta=2, rho=0.1, Q=100):
        self.classes = classes
        self.subjects = subjects
        self.teachers = teachers
        self.constraints = constraints
        self.days = days
        self.periods_per_day = periods_per_day
        self.subject_period_limits = subject_period_limits
        self.num_ants = num_ants
        self.num_iterations = num_iterations
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.Q = Q
        self.pheromone = self._init_pheromone()
        self.visibility = self._init_visibility()

    def _init_pheromone(self):
        return {
            subject: {(d, p): 1.0 for d in self.days for p in self.periods_per_day[d]}
            for subject in {s for subs in self.subjects.values() for s in subs}
        }

    def _init_visibility(self):
        v = defaultdict(lambda: defaultdict(float))
        for cls, subs in self.subjects.items():
            for sub in subs:
                for d in self.days:
                    for p in self.periods_per_day[d]:
                        v[sub][(d, p)] = 1.0 if self._valid_slot(cls, d, p) else 0.01
        return v

    def _valid_slot(self, cls, d, p):
        for block in self.constraints.get("global", {}).get("break_times", []):
            if block["day"] == d and block["start"] <= p <= block["end"]:
                return False
        ft = self.constraints.get("global", {}).get("fellowship_time", {})
        if ft and ft.get("day") == d and ft["start"] <= p <= ft["end"]:
            return False
        for block in self.constraints.get("per_class", {}).get(cls, []):
            if block["day"] == d and block["start"] <= p <= block["end"]:
                return False
        return True

    def construct_solution(self):
        timetable = {cls: {d: {p: None for p in self.periods_per_day[d]} for d in self.days} for cls in self.classes}
        for cls in self.classes:
            for sub, limits in self.subject_period_limits.get(cls, {}).items():
                needed = limits['periods_per_week']
                while needed > 0:
                    available = [(d, p) for d in self.days for p in self.periods_per_day[d]
                                 if timetable[cls][d][p] is None and self._valid_slot(cls, d, p)]
                    if not available:
                        break
                    scores = [(slot, self.pheromone[sub][slot] ** self.alpha * self.visibility[sub][slot] ** self.beta)
                              for slot in available]
                    total = sum(score for _, score in scores)
                    if total == 0:
                        break
                    r = random.uniform(0, total)
                    upto = 0
                    for slot, score in scores:
                        upto += score
                        if upto >= r:
                            timetable[cls][slot[0]][slot[1]] = sub
                            needed -= 1
                            break
        return timetable

    def evaluate_solution(self, timetable):
        penalty = 0
        usage = defaultdict(set)
        for cls, schedule in timetable.items():
            for d, slots in schedule.items():
                for p, sub in slots.items():
                    if sub:
                        for teacher, info in self.teachers.items():
                            if sub in info["subjects"] and cls in info["subjects"][sub]:
                                if p not in info["availability"].get(d, []):
                                    penalty += 1
                                if (d, p) in usage[teacher]:
                                    penalty += 1
                                else:
                                    usage[teacher].add((d, p))
                        if not self._valid_slot(cls, d, p):
                            penalty += 2
        return penalty

    def update_pheromones(self, solutions):
        for sub in self.pheromone:
            for slot in self.pheromone[sub]:
                self.pheromone[sub][slot] *= (1 - self.rho)
        for sol, pen in solutions:
            for cls, sch in sol.items():
                for d, prds in sch.items():
                    for p, sub in prds.items():
                        if sub:
                            self.pheromone[sub][(d, p)] += self.Q / (1 + pen)

    def run(self):
        best_sol = None
        best_pen = float("inf")
        for _ in range(self.num_iterations):
            solutions = []
            for _ in range(self.num_ants):
                sol = self.construct_solution()
                pen = self.evaluate_solution(sol)
                if pen < best_pen:
                    best_sol = sol
                    best_pen = pen
                solutions.append((sol, pen))
            self.update_pheromones(solutions)

        enriched = {}
        for cls, sch in best_sol.items():
            enriched[cls] = {}
            for d, slots in sch.items():
                enriched[cls][d] = {}
                for p, sub in slots.items():
                    teacher = next((t for t, i in self.teachers.items() if sub in i["subjects"] and cls in i["subjects"][sub]), None)
                    enriched[cls][d][p] = {"subject": sub, "teacher": teacher} if sub else None
        return enriched


# STEP 3: Run ACO and return enriched result
def generate_timetable_logic(school_id, days, periods_per_day, teacher_unavailability, constraints):
    data = fetch_data(school_id, days, periods_per_day, teacher_unavailability, constraints)
    aco = ACOTimetableGenerator(*data)
    return aco.run()


# STEP 4: Save timetable and schedules
def generate_and_persist_timetable(school_id, days, periods_per_day, teacher_unavailability, constraints):
    timetable_data = generate_timetable_logic(school_id, days, periods_per_day, teacher_unavailability, constraints)
    with transaction.atomic():
        school = School.objects.get(id=school_id)
        t = Timetable.objects.create(school=school)

        for cls_name, schedule in timetable_data.items():
            cls_obj = Class.objects.get(arm_name=cls_name, school=school)
            ClassTimetable.objects.create(timetable=t, class_arm=cls_obj, schedule=schedule)

        teacher_schedules = {}
        for cls, daily in timetable_data.items():
            for d, prds in daily.items():
                for p, info in prds.items():
                    if info and info["teacher"]:
                        tname = info["teacher"]
                        teacher_schedules.setdefault(tname, {}).setdefault(d, {})[p] = f"{info['subject']} ({cls})"

        for tname, sched in teacher_schedules.items():
            teacher_obj = Teacher.objects.get(user__username=tname, school=school)
            TeacherTimetable.objects.create(timetable=t, teacher=teacher_obj, schedule=sched)

    return t
