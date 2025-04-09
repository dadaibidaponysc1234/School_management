from django.urls import path
from .views import SchoolStatsView

urlpatterns = [
    path('school_stats/', SchoolStatsView.as_view(), name="school-stats"),
]
