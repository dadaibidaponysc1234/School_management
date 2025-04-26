from rest_framework import serializers
from user_registration.models import (ResultVisibilityControl,AssessmentCategory,ResultConfiguration,
                                      AnnualResultWeightConfig, GradingSystem,ScorePerAssessmentInstance,
                                     ScoreObtainedPerAssessment, ExamScore,Result,ContinuousAssessment,
                                     AnnualResult 
                                     )

#=========================================================================================
class ResultVisibilityControlSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = ResultVisibilityControl
        fields = ['id', 'school_name', 'term_result_open', 'annual_result_open', 'updated_at']
        read_only_fields = ['updated_at', 'school_name']
#=========================================================================================

class AssessmentCategorySerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = AssessmentCategory
        fields = ['assessment_category_id', 'school_name', 'assessment_name', 'number_of_times', 'max_score_per_one', 'created_at', 'updated_at']
        read_only_fields = ['school_name', 'created_at', 'updated_at']
#=========================================================================================

class ResultConfigurationSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = ResultConfiguration
        fields = ['id', 'school_name', 'total_ca_score', 'total_exam_score']
        read_only_fields = ['school_name']

    def validate(self, data):
        ca = data.get('total_ca_score', getattr(self.instance, 'total_ca_score', None))
        exam = data.get('total_exam_score', getattr(self.instance, 'total_exam_score', None))
        
        if ca is not None and exam is not None and (ca + exam) != 100:
            raise serializers.ValidationError("Total CA and Exam scores must sum up to 100.")
        
        return data

#=========================================================================================

class AnnualResultWeightConfigSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)
    class_year_name = serializers.CharField(source='class_year.class_name', read_only=True)
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = AnnualResultWeightConfig
        fields = [
            'id', 'school_name', 'class_year', 'class_year_name',
            'department', 'department_name',
            'first_term_weight', 'second_term_weight', 'third_term_weight'
        ]
        read_only_fields = ['school_name', 'class_year_name', 'department_name']

    def validate(self, data):
        total = (
            data.get('first_term_weight', getattr(self.instance, 'first_term_weight', 0)) +
            data.get('second_term_weight', getattr(self.instance, 'second_term_weight', 0)) +
            data.get('third_term_weight', getattr(self.instance, 'third_term_weight', 0))
        )
        if round(total, 2) != 1.0:
            raise serializers.ValidationError("Sum of term weights must be equal to 1.0")
        return data

#=========================================================================================
class GradingSystemSerializer(serializers.ModelSerializer):
    school_name = serializers.CharField(source='school.school_name', read_only=True)

    class Meta:
        model = GradingSystem
        fields = ['id', 'school_name', 'min_score', 'max_score', 'grade', 'remarks']
        read_only_fields = ['school_name']

    def validate(self, data):
        if data['min_score'] >= data['max_score']:
            raise serializers.ValidationError("Minimum score must be less than maximum score.")
        return data

#=========================================================================================

class ScorePerAssessmentInstanceSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assessment_name = serializers.CharField(source='category.assessment_name', read_only=True)

    class Meta:
        model = ScorePerAssessmentInstance
        fields = [
            'scoreperassessment_id', 'registration', 'category', 'assessment_name',
            'instance_number', 'score', 'student_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['student_name', 'assessment_name', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        student = obj.registration.student_class.student
        return f"{student.first_name} {student.last_name}"


#=========================================================================================

class ScoreObtainedPerAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    assessment_name = serializers.CharField(source='category.assessment_name', read_only=True)

    class Meta:
        model = ScoreObtainedPerAssessment
        fields = [
            'scoreperassessment_id', 'registration', 'category', 'assessment_name',
            'total_score', 'student_name', 'created_at', 'updated_at'
        ]
        read_only_fields = fields  # view-only

    def get_student_name(self, obj):
        student = obj.registration.student_class.student
        return f"{student.first_name} {student.last_name}"

#=========================================================================================

class ExamScoreSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='registration.subject_class.subject.name', read_only=True)

    class Meta:
        model = ExamScore
        fields = [
            'examscore_id', 'registration', 'subject_name', 'score',
            'student_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['subject_name', 'student_name', 'created_at', 'updated_at']

    def get_student_name(self, obj):
        student = obj.registration.student_class.student
        return f"{student.first_name} {student.last_name}"
#=========================================================================================

class ContinuousAssessmentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(source='registration.subject_class.subject.name', read_only=True)

    class Meta:
        model = ContinuousAssessment
        fields = [
            'continuous_assessment_id', 'registration', 'subject_name', 'ca_total',
            'student_name', 'created_at', 'updated_at'
        ]
        read_only_fields = fields

    def get_student_name(self, obj):
        student = obj.registration.student_class.student
        return f"{student.first_name} {student.last_name}"

#=========================================================================================

class StudentInfoSerializer(serializers.Serializer):
    student_id = serializers.UUIDField(source='registration.student_class.student.student_id')
    first_name = serializers.CharField(source='registration.student_class.student.first_name')
    last_name = serializers.CharField(source='registration.student_class.student.last_name')
    gender = serializers.CharField(source='registration.student_class.student.gender')
    admission_number = serializers.IntegerField(source='registration.student_class.student.admission_number')
    status = serializers.CharField(source='registration.student_class.student.status')

    class Meta:
        ref_name = "StudentInfoForResult" 

class SubjectInfoSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField(source='registration.subject_class.subject.subject_id')
    name = serializers.CharField(source='registration.subject_class.subject.name')

    class Meta:
        ref_name = "SubjectInfoForResult" 

class ResultSerializer(serializers.ModelSerializer):
    student = StudentInfoSerializer(source='*', read_only=True)
    subject = SubjectInfoSerializer(source='*', read_only=True)
    term = serializers.CharField(source='registration.term.name', read_only=True)

    class Meta:
        model = Result
        fields = [
            'result_id', 'registration', 'student', 'subject', 'term',
            'ca_total', 'exam_score', 'total_score', 'grade', 'remarks',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields
#=========================================================================================

class StudentInfoSerializer(serializers.Serializer):
    student_id = serializers.UUIDField(source='registration.student_class.student.student_id')
    first_name = serializers.CharField(source='registration.student_class.student.first_name')
    last_name = serializers.CharField(source='registration.student_class.student.last_name')
    gender = serializers.CharField(source='registration.student_class.student.gender')
    admission_number = serializers.IntegerField(source='registration.student_class.student.admission_number')
    status = serializers.CharField(source='registration.student_class.student.status')

class SubjectInfoSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField(source='registration.subject_class.subject.subject_id')
    name = serializers.CharField(source='registration.subject_class.subject.name')


class AssessmentScoreSerializer(serializers.Serializer):
    assessment_name = serializers.CharField()
    obtained_score = serializers.FloatField()
    max_score = serializers.FloatField()

class ThirdTermDetailSerializer(serializers.Serializer):
    ca_total = serializers.FloatField()
    exam_score = serializers.FloatField()
    assessment_scores = AssessmentScoreSerializer(many=True)


class AnnualResultSerializer(serializers.ModelSerializer):
    student = StudentInfoSerializer(source='*', read_only=True)
    subject = SubjectInfoSerializer(source='*', read_only=True)
    third_term_detail = serializers.SerializerMethodField()

    class Meta:
        model = AnnualResult
        fields = [
            'annual_result_id',
            'registration',
            'student',
            'subject',
            'first_term_score',
            'second_term_score',
            'third_term_score',
            'third_term_detail',
            'annual_average',
            'grade',
            'remarks',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields

    def get_third_term_detail(self, obj):
        registration = obj.registration

        # Get CA and exam for third term
        ca = ContinuousAssessment.objects.filter(registration=registration, registration__term__name__iexact='Third Term').first()
        exam = ExamScore.objects.filter(registration=registration, registration__term__name__iexact='Third Term').first()

        ca_total = ca.ca_total if ca else None
        exam_score = exam.score if exam else None

        # Get detailed assessment scores
        assessment_totals = ScoreObtainedPerAssessment.objects.filter(
            registration=registration,
            registration__term__name__iexact='Third Term'
        )

        assessment_data = []
        for score in assessment_totals:
            category = score.category
            max_score = category.number_of_times * category.max_score_per_one
            assessment_data.append({
                'assessment_name': category.assessment_name,
                'obtained_score': score.total_score,
                'max_score': max_score
            })

        return {
            'ca_total': ca_total,
            'exam_score': exam_score,
            'assessment_scores': assessment_data
        }
##########Full Result Serializer###############
##########Full Result Serializer###############

class AssessmentSerializer(serializers.Serializer):
    assessment_name = serializers.CharField()
    obtained_score = serializers.FloatField()
    max_score = serializers.FloatField()

class SubjectSerializer(serializers.Serializer):
    subject_id = serializers.UUIDField()
    name = serializers.CharField()

class StudentInfoSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    gender = serializers.CharField()
    admission_number = serializers.IntegerField()

class SchoolInfoSerializer(serializers.Serializer):
    school_id = serializers.UUIDField()
    school_name = serializers.CharField()
    short_name = serializers.CharField()
    school_type = serializers.CharField()
    education_level = serializers.CharField()
    city = serializers.CharField()
    state = serializers.CharField()
    country = serializers.CharField()
    logo_url = serializers.URLField(allow_null=True)

class FullTermResultSerializer(serializers.Serializer):
    school = SchoolInfoSerializer()
    student = StudentInfoSerializer()
    year = serializers.CharField()
    term = serializers.CharField()
    term_results = serializers.ListField()

class FullAnnualResultSerializer(serializers.Serializer):
    school = SchoolInfoSerializer()
    student = StudentInfoSerializer()
    year = serializers.CharField()
    annual_results = serializers.ListField()

##########Broadsheet Serializer###############

class SubjectScoreSerializer(serializers.Serializer):
    score = serializers.FloatField(required=False)
    grade = serializers.CharField()

class AnnualScoreSerializer(serializers.Serializer):
    annual_average = serializers.FloatField()
    grade = serializers.CharField()

class BroadsheetStudentSerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    name = serializers.CharField()
    scores = serializers.DictField(child=serializers.DictField())
    average_score = serializers.FloatField(required=False)
    position_in_class_year = serializers.CharField(required=False)
    position_in_class_arm = serializers.CharField(required=False)
    passed_subjects = serializers.IntegerField()
    failed_subjects = serializers.IntegerField()

class BroadsheetSerializer(serializers.Serializer):
    broadsheet_type = serializers.ChoiceField(choices=["term", "annual"])
    year = serializers.CharField()
    term = serializers.CharField(required=False)
    class_year = serializers.CharField(required=False)
    class_arm = serializers.CharField(required=False)
    department = serializers.CharField()
    pass_mark = serializers.FloatField()
    subjects = serializers.ListField(child=serializers.CharField())
    students = BroadsheetStudentSerializer(many=True)

##############################################
