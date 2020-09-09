"""
Signal handlers for the course-rating djangoapp
"""
from django.db import models
from django.dispatch import receiver

from openedx.features.course_rating.models import (
    CourseRatings,
    CourseRatingOverview,
)


@receiver(models.signals.post_save, sender=CourseRatings)
def update_course_rating_overview(**kwargs):
    """
    Receives the CourseRatings signal and triggers the
    updation of CourseRatingOverview.
    """
    pass
