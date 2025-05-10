from django.urls import path
from .views import (ResultVisibilityControlListCreateView, ResultVisibilityControlDetailUpdateView,
                    AssessmentCategoryListCreateView,AssessmentCategoryDetailView,
                    ResultConfigurationListCreateView,ResultConfigurationDetailView,
                    AnnualWeightConfigListCreateView,AnnualWeightConfigDetailView,
                    GradingSystemListCreateView, GradingSystemDetailView,ScorePerAssessmentListCreateView,
                    ScorePerAssessmentDetailView,ScoreObtainedPerAssessmentListView,ScoreObtainedPerAssessmentListView,
                    ExamScoreListCreateView, ExamScoreDetailView,ContinuousAssessmentListView,ContinuousAssessmentDetailView,
                    AnnualResultListView, AnnualResultDetailView, ResultListView, ResultDetailView,
                    FullStudentResultView, BroadsheetView, ClassTeacherCommentListCreateView, ClassTeacherCommentDetailView,
                    )

urlpatterns = [
    path('result/result-visibility/', ResultVisibilityControlListCreateView.as_view(), name='result_visibility_list_create'),
    path('result/result-visibility/<uuid:pk>/', ResultVisibilityControlDetailUpdateView.as_view(), name='result_visibility_detail_update'),

    path('result/assessment-categories/', AssessmentCategoryListCreateView.as_view(), name='assessment_category_list_create'),
    path('result/assessment-categories/<uuid:assessment_category_id>/', AssessmentCategoryDetailView.as_view(), name='assessment_category_detail'),

    path('result/result-configurations/', ResultConfigurationListCreateView.as_view(), name='result_config_list_create'),
    path('result/result-configurations/<uuid:id>/', ResultConfigurationDetailView.as_view(), name='result_config_detail'),

    path('result/annual-weight-configs/', AnnualWeightConfigListCreateView.as_view(), name='annual_weight_list_create'),
    path('result/annual-weight-configs/<uuid:id>/', AnnualWeightConfigDetailView.as_view(), name='annual_weight_detail'),

    path('result/grading-systems/', GradingSystemListCreateView.as_view(), name='grading_system_list_create'),
    path('result/grading-systems/<uuid:id>/', GradingSystemDetailView.as_view(), name='grading_system_detail'),

    path('result/assessment-scores/', ScorePerAssessmentListCreateView.as_view(), name='assessment_score_list_create'),
    path('result/assessment-scores/<uuid:scoreperassessment_id>/', ScorePerAssessmentDetailView.as_view(), name='assessment_score_detail'),

    path('result/assessment-score-totals/', ScoreObtainedPerAssessmentListView.as_view(), name='score_obtained_list'),

    path('result/exam-scores/', ExamScoreListCreateView.as_view(), name='exam_score_list_create'),
    path('result/exam-scores/<uuid:examscore_id>/', ExamScoreDetailView.as_view(), name='exam_score_detail'),

    path('result/continuous-assessments/', ContinuousAssessmentListView.as_view(), name='ca_list'),
    path('result/continuous-assessments/<uuid:continuous_assessment_id>/', ContinuousAssessmentDetailView.as_view(), name='ca_detail'),

    path('result/results/', ResultListView.as_view(), name='result_list'),
    path('result/results/<uuid:result_id>/', ResultDetailView.as_view(), name='result_detail'),

    path('result/annual-results/', AnnualResultListView.as_view(), name='annual_result_list'),
    path('result/annual-results/<uuid:annual_result_id>/', AnnualResultDetailView.as_view(), name='annual_result_detail'),

    path('result/classteacher-comments/', ClassTeacherCommentListCreateView.as_view(), name='classteacher_comment_list_create'),
    path('result/classteacher-comments/<uuid:classteacher_comment_id>/', ClassTeacherCommentDetailView.as_view(), name='classteacher_comment_detail'),

    path('result/full-student-result/<uuid:student_id>/', FullStudentResultView.as_view(), name='full_student_result'),
    path('result/broadsheet/', BroadsheetView.as_view(), name='broadsheet'),
]


