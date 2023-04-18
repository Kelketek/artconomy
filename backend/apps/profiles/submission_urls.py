"""artconomy URL Configuration
"""
from apps.profiles.views import SubmissionPreview
from django.urls import path

app_name = "profiles"

# These URLs/views are for the purpose of getting Meta tag preview information.


urlpatterns = [
    path("<int:submission_id>", SubmissionPreview.as_view(), name="submission_preview"),
]
