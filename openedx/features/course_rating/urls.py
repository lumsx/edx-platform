"""
URL patterns for course rating application.
"""

from django.conf.urls import url, include
from openedx.features.course_rating import views

urlpatterns = [
    url(
        r'^$',
        views.home,
        name='home-page'
    ),
]
