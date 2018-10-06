"""artconomy URL Configuration
"""
from django.urls import path

from apps.profiles.views import SubmissionPreview

app_name = "profiles"

# These URLs/views are for the purpose of getting Meta tag preview information.


urlpatterns = [
    path('<int:submission_id>', SubmissionPreview.as_view(), name='submission_preview'),
]
