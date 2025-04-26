from django.urls import path
from .views import SchoolStatsView

urlpatterns = [
    path('stats/school_stats/', SchoolStatsView.as_view(), name="school-stats"),
]
