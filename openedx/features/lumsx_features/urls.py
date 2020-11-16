"""
Defines URLs for the lumsx features.
"""

from django.conf import settings
from django.conf.urls import url

import views

urlpatterns = [
    # for student access lumsx
    url(r'change_student_all_courses_access', views.StudentAccessStatus.as_view(),
        name='change_student_all_courses_access')
]
